import asyncio
import pytest
import pytest_asyncio
import uuid

from api.main import app
from api.database import AsyncSessionLocal, engine
from api.model import Wallet
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete
from decimal import Decimal


@pytest_asyncio.fixture
async def client():
    """Фикстура для тестового клиента"""
    async with engine.begin() as conn:
        from api.database import Base

        await conn.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    async with engine.begin() as conn:
        await conn.execute(delete(Wallet))
        await conn.commit()

    await engine.dispose()


async def wallets_generation(balance=Decimal("100.00")):
    """Создаем уникальный uuid для тестов"""
    async with AsyncSessionLocal() as db:
        wallet_key = uuid.uuid4()
        wallet = Wallet(uuid=wallet_key, balance=balance)
        db.add(wallet)
        await db.commit()
        return wallet_key


@pytest.mark.asyncio
async def test_get_existing_wallet(client):
    """Проверка существующего кошелька"""
    wallet_key = await wallets_generation()
    response = await client.get(f"/api/v1/wallets/{wallet_key}")
    assert response.status_code == 200
    assert response.json() == {"balance": "100.00"}


@pytest.mark.asyncio
async def test_get_nonexistent_wallet(client):
    """Проверка не существующего кошелька"""
    random_uuid = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/wallets/{random_uuid}")
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
    client, operation_type, amount, expected_status, expected_balance
):
    """Проверяем операции с балансом"""
    wallet_key = await wallets_generation()

    response = await client.post(
        f"/api/v1/wallets/{wallet_key}/operation",
        json={"operation_type": operation_type, "amount": amount},
    )

    assert response.status_code == expected_status
    if expected_status == 200:
        assert Decimal(response.json()["balance"]) == Decimal(expected_balance)
    else:
        assert response.json()["detail"] == "Insufficient funds"


@pytest.mark.asyncio
async def test_get_wallet_invalid_uuid(client):
    """Проверка, что API возвращает 422 на невалидный UUID"""
    response = await client.get("/api/v1/wallets/not-a-uuid")
    assert response.status_code == 422
    assert "valid UUID" in response.json()["detail"][0]["msg"]


@pytest.mark.asyncio
async def test_operation_invalid_uuid(client):
    """Проверка, что операция возвращает 422 на невалидный UUID"""
    response = await client.post(
        "/api/v1/wallets/not-a-uuid/operation",
        json={"operation_type": "DEPOSIT", "amount": "100.00"}
    )
    assert response.status_code == 422
    assert "valid UUID" in response.json()["detail"][0]["msg"]


@pytest.mark.asyncio
async def test_concurrent_deposit_withdraw(client):
    wallet_key = await wallets_generation()

    async def deposit():
        return await client.post(
                f"/api/v1/wallets/{wallet_key}/operation",
                json={"operation_type": "DEPOSIT", "amount": "50.00"}
            )

    async def withdraw():
        return await client.post(
                f"/api/v1/wallets/{wallet_key}/operation",
                json={"operation_type": "WITHDRAW", "amount": "100.00"}
            )

    results = await asyncio.gather(deposit(), withdraw())

    success_count = sum(1 for r in results if r.status_code == 200)
    assert success_count >= 1

    final_balance = await client.get(f"/api/v1/wallets/{wallet_key}")
    assert final_balance.json()["balance"] in ("50.00", '150.00')