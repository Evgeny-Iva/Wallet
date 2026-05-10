import pytest
import uuid
from fastapi.testclient import TestClient
from main import app, wallets


client = TestClient(app)

def test_get_existing_wallet():
    """Проверка существующего кошелька"""
    wallet_key = gen_wallets()
    response = client.get(f"/api/v1/wallets/{wallet_key}")
    assert response.status_code == 200
    assert response.json() == {"balance": 100.0}
    del wallets[wallet_key]


def test_get_nonexistent_wallet():
    """Проверка не существующего кошелька"""
    random_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/wallets/{random_uuid}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Wallet not found"


def gen_wallets():
    """Создаем уникальный uuid для тестов"""
    wallet_uuid = uuid.uuid4()
    wallet_key = str(wallet_uuid)
    wallets[wallet_key] = 100.0
    return wallet_key


def test_make_operation():
    """Проверяем операции с балансом"""
    wallet_key = gen_wallets()

    response = client.post(
        f"/api/v1/wallets/{wallet_key}/operation",
        json={"operation_type": "DEPOSIT", "amount": 50.0}
    )

    assert response.status_code == 200
    assert response.json() == {"balance": 150.0}

    response = client.post(
        f"/api/v1/wallets/{wallet_key}/operation",
        json={"operation_type": "WITHDRAW", "amount": 50.0}
    )

    assert response.status_code == 200
    assert response.json() == {"balance": 100.0}

    response = client.post(
        f"/api/v1/wallets/{wallet_key}/operation",
        json={"operation_type": "WITHDRAW", "amount": 1000.0}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient funds"

    del wallets[wallet_key]