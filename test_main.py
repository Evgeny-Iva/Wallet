import pytest_asyncio
import uuid
from main import app
from database import AsyncSessionLocal
from model import Wallet
from httpx import AsyncClient
from sqlalchemy import delete
from asgi_lifespan import LifespanManager


@pytest_asyncio.fixture()
async def client():
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac


async def generation_wallets(balance=100.0):
    """Создаем уникальный uuid для тестов"""
    async with AsyncSessionLocal() as db:
        wallet_key = str(uuid.uuid4())
        wallet = Wallet(uuid=wallet_key, balance=balance)
        db.add(wallet)
        await db.commit()
        return wallet_key


async def test_get_existing_wallet(client):
    """Проверка существующего кошелька"""
    wallet_key = await generation_wallets()
    response = await client.get(f"/api/v1/wallets/{wallet_key}")
    assert response.status_code == 200
    assert response.json() == {"balance": 100.0}

    async with AsyncSessionLocal() as db:
        await db.execute(delete(Wallet).where(Wallet.uuid == wallet_key))
        await db.commit()


async def test_get_nonexistent_wallet(client):
    """Проверка не существующего кошелька"""
    random_uuid = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/wallets/{random_uuid}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Wallet not found"


async def test_make_operation(client):
    """Проверяем операции с балансом"""
    async with AsyncSessionLocal() as db:
        wallet_key = await generation_wallets()

        response = await client.post(
            f"/api/v1/wallets/{wallet_key}/operation",
            json={"operation_type": "DEPOSIT", "amount": 50.0}
        )

        assert response.status_code == 200
        assert response.json() == {"balance": 150.0}

        response = await client.post(
            f"/api/v1/wallets/{wallet_key}/operation",
            json={"operation_type": "WITHDRAW", "amount": 50.0}
        )

        assert response.status_code == 200
        assert response.json() == {"balance": 100.0}

        response = await client.post(
            f"/api/v1/wallets/{wallet_key}/operation",
            json={"operation_type": "WITHDRAW", "amount": 1000.0}
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Insufficient funds"

        await db.execute(delete(Wallet).where(Wallet.uuid == wallet_key))