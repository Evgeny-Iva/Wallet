import asyncio
import pytest
import pytest_asyncio
import uuid

from api.database import AsyncSessionLocal
from api.tests.conftest import wallet_balance
from decimal import Decimal


@pytest.mark.asyncio
async def test_transfer_success(
        client, test_wallet, auth_headers2,
        test_wallet2, auth_headers
):
    """
    Проверяем успешный перевод:
    денежное списание с отправителя и зачисление получателю
    """
    wallet1_uuid = test_wallet

    wallet2_uuid = test_wallet2

    initial_balance1 = await wallet_balance(client, wallet1_uuid, auth_headers)
    initial_balance2 = await wallet_balance(client, wallet2_uuid, auth_headers2)

    transfer_data = {
        "to_wallet_id": wallet2_uuid,
        "amount": 30.00,
        "currency": "RUB"
    }
    transfer_response = await client.post(
        f"/wallets/{wallet1_uuid}/transfer",
        json=transfer_data,
        headers=auth_headers
    )
    assert transfer_response.status_code == 200

    new_balance1 = await wallet_balance(client, wallet1_uuid, auth_headers)
    new_balance2 = await wallet_balance(client, wallet2_uuid, auth_headers2)

    assert new_balance1 == initial_balance1 - Decimal("30.00")
    assert new_balance2 == initial_balance2 + Decimal("30.00")


@pytest.mark.asyncio
async def test_transfer_insufficient_funds(
        client, test_wallet, auth_headers2,
        test_wallet2, auth_headers
):
    """Недостаточно средств на балансе для перевода"""
    wallet1_uuid = test_wallet

    wallet2_uuid = test_wallet2

    initial_balance1 = await wallet_balance(client, wallet1_uuid, auth_headers)
    initial_balance2 = await wallet_balance(client, wallet2_uuid, auth_headers2)

    transfer_data = {
        "to_wallet_id": wallet2_uuid,
        "amount": 3000.00,
        "currency": "RUB"
    }
    transfer_response = await client.post(
        f"/wallets/{wallet1_uuid}/transfer",
        json=transfer_data,
        headers=auth_headers
    )
    assert transfer_response.status_code == 400

    new_balance1 = await wallet_balance(client, wallet1_uuid, auth_headers)
    new_balance2 = await wallet_balance(client, wallet2_uuid, auth_headers2)

    assert new_balance1 == initial_balance1
    assert new_balance2 == initial_balance2


@pytest.mark.asyncio
async def test_transfer_recipient_not_found(client, test_wallet, auth_headers):
    """Кошелек получателя не найден"""
    wallet1_uuid = test_wallet

    initial_balance1 = await wallet_balance(client, wallet1_uuid, auth_headers)

    transfer_data = {
        "to_wallet_id": str(uuid.uuid4()),
        "amount": 50.00,
        "currency": "RUB"
    }
    transfer_response = await client.post(
        f"/wallets/{wallet1_uuid}/transfer",
        json=transfer_data,
        headers=auth_headers
    )
    assert transfer_response.status_code == 404

    new_balance1 = await wallet_balance(client, wallet1_uuid, auth_headers)

    assert new_balance1 == initial_balance1


@pytest.mark.asyncio
async def test_transfer_currency_mismatch(client, auth_headers, auth_headers2):
    """Проверка несовпадение валюты кошельков не совпадают"""
    wallet_data = {"currency": "RUB"}
    response = await client.post("/wallets/", json=wallet_data, headers=auth_headers)
    assert response.status_code == 200
    wallet1_uuid = response.json()["wallet_uuid"]

    wallet_data2 = {"currency": "USD"}
    response2 = await client.post("/wallets/", json=wallet_data2, headers=auth_headers2)
    assert response2.status_code == 200
    wallet2_uuid = response2.json()["wallet_uuid"]

    initial_balance1 = await wallet_balance(client, wallet1_uuid, auth_headers)
    initial_balance2 = await wallet_balance(client, wallet2_uuid, auth_headers2)

    transfer_data = {
        "to_wallet_id": wallet2_uuid,
        "amount": 30.00,
        "currency": "RUB"
    }
    transfer_response = await client.post(
        f"/wallets/{wallet1_uuid}/transfer",
        json=transfer_data,
        headers=auth_headers
    )
    assert transfer_response.status_code == 400

    new_balance1 = await wallet_balance(client, wallet1_uuid, auth_headers)
    new_balance2 = await wallet_balance(client, wallet2_uuid, auth_headers2)

    assert new_balance1 == initial_balance1
    assert new_balance2 == initial_balance2


@pytest.mark.asyncio
async def test_transfer_access_denied(
        client, test_wallet, auth_headers2,
        test_wallet2, auth_headers
):
    """Проверка попытки перевода с чужого кошелька"""
    wallet1_uuid = test_wallet

    wallet2_uuid = test_wallet2

    initial_balance1 = await wallet_balance(client, wallet1_uuid, auth_headers)
    initial_balance2 = await wallet_balance(client, wallet2_uuid, auth_headers2)

    transfer_data = {
        "to_wallet_id": wallet2_uuid,
        "amount": 30.00,
        "currency": "RUB"
    }
    transfer_response = await client.post(
        f"/wallets/{wallet1_uuid}/transfer",
        json=transfer_data,
        headers=auth_headers2
    )
    assert transfer_response.status_code == 403

    new_balance1 = await wallet_balance(client, wallet1_uuid, auth_headers)
    new_balance2 = await wallet_balance(client, wallet2_uuid, auth_headers2)

    assert new_balance1 == initial_balance1
    assert new_balance2 == initial_balance2


@pytest.mark.asyncio
async def test_transfer_negative_amount(client, test_wallet, test_wallet2, auth_headers):
    """Проверка на отрицательный запрос перевода"""
    wallet1_uuid = test_wallet
    wallet2_uuid = test_wallet2

    transfer_data = {
        "to_wallet_id": wallet2_uuid,
        "amount": -10.00,
        "currency": "RUB"
    }

    response = await client.post(
        f"/wallets/{wallet1_uuid}/transfer",
        json=transfer_data,
        headers=auth_headers
    )

    assert response.status_code == 422
