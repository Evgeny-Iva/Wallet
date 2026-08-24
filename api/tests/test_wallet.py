import asyncio
import pytest
import pytest_asyncio

from api.database import AsyncSessionLocal
from decimal import Decimal

from api.tests.conftest import wallet_balance


@pytest.mark.asyncio
async def test_get_existing_wallet(client, test_wallet, auth_headers):
    """Проверка существующего кошелька"""
    response = await client.get(
        f"/wallets/{test_wallet}",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json() == {"balance": "100.00"}


@pytest.mark.asyncio
async def test_get_nonexistent_wallet(client, auth_headers):
    """Проверка не существующего кошелька"""
    random_uuid = "00000000-0000-0000-0000-000000000000"
    response = await client.get(
        f"/wallets/{random_uuid}",
        headers=auth_headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Wallet not found"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "operation_type, amount, expected_status, expected_balance",
    [
        ("DEPOSIT", "50.00", 200, "150.00"),
        ("WITHDRAW", "50.00", 200, "50.00"),
        ("WITHDRAW", "1000.00", 402, "Insufficient funds"),
    ],
)
async def test_make_operation(
    client, operation_type, amount,
    expected_status, expected_balance,
    test_wallet, auth_headers
):
    """Проверяем операции с балансом"""
    response = await client.post(
        f"/wallets/{test_wallet}/operation",
        json={"operation_type": operation_type, "amount": amount},
        headers=auth_headers
    )

    assert response.status_code == expected_status
    if expected_status == 200:
        assert Decimal(response.json()["balance"]) == Decimal(expected_balance)
    else:
        assert response.json()["detail"] == "Insufficient funds"


@pytest.mark.asyncio
async def test_get_wallet_invalid_uuid(client, auth_headers):
    """Проверка, что API возвращает 422 на невалидный UUID"""
    response = await client.get(
        "/wallets/not-a-uuid",
        headers=auth_headers
    )
    assert response.status_code == 422
    assert "valid UUID" in response.json()["detail"][0]["msg"]


@pytest.mark.asyncio
async def test_operation_invalid_uuid(client, auth_headers):
    """Проверка, что операция возвращает 422 на невалидный UUID"""
    response = await client.post(
        "/wallets/not-a-uuid/operation",
        json={"operation_type": "DEPOSIT", "amount": "100.00"},
        headers=auth_headers
    )
    assert response.status_code == 422
    assert "valid UUID" in response.json()["detail"][0]["msg"]


@pytest.mark.asyncio
async def test_concurrent_deposit_withdraw(client, test_wallet, auth_headers):
    """Проверка, на конкурентность"""
    deposit_task = client.post(
        f"/wallets/{test_wallet}/operation",
        json={"operation_type": "DEPOSIT", "amount": "50.00"},
        headers=auth_headers
    )

    withdraw_task = client.post(
        f"/wallets/{test_wallet}/operation",
        json={"operation_type": "WITHDRAW", "amount": "100.00"},
        headers=auth_headers
    )

    results = await asyncio.gather(deposit_task, withdraw_task)

    success_count = sum(1 for r in results if r.status_code == 200)
    assert success_count >= 1

    wallet_uuid = test_wallet
    balance = await wallet_balance(client, wallet_uuid, auth_headers)
    assert str(balance) in ("50.00", '150.00')


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "operation_type, amount, expected_status, expected_detail",
    [
        ("DEPOSIT", "-50.00", 422, "amount"),
        ("WITHDRAW", "-50.00", 422, "amount"),
        ("DEPOSIT", "0.00", 422, "amount"),
        ("WITHDRAW", "0.00", 422, "amount"),
    ],
)
async def test_operation_negative_or_zero_amount(
        client, test_wallet, auth_headers, operation_type,
        amount, expected_status, expected_detail
):
    """Проверка, что API не принимает отрицательные или нулевые суммы"""
    wallet_uuid = test_wallet
    old_balance = await wallet_balance(client, wallet_uuid, auth_headers)

    response = await client.post(
        f"/wallets/{test_wallet}/operation",
        json={"operation_type": operation_type, "amount": amount},
        headers=auth_headers
    )
    new_balance = await wallet_balance(client, wallet_uuid, auth_headers)
    assert response.status_code == 422
    assert old_balance == new_balance