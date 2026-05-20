import pytest
import pytest_asyncio
import uuid
from api.main import app
from api.database import AsyncSessionLocal, engine
from api.model import Wallet
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete


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


async def generation_wallets(balance=100.0):
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
    wallet_key = await generation_wallets()
    response = await client.get(f"/api/v1/wallets/{wallet_key}")
    assert response.status_code == 200
    assert response.json() == {"balance": 100.0}


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
        ("DEPOSIT", 50.0, 200, 150.0),
        ("WITHDRAW", 50.0, 200, 50.0),
        ("WITHDRAW", 1000.0, 402, "Insufficient funds"),
    ],
)
async def test_make_operation(
    client, operation_type, amount, expected_status, expected_balance
):
    """Проверяем операции с балансом"""
    wallet_key = await generation_wallets()

    response = await client.post(
        f"/api/v1/wallets/{wallet_key}/operation",
        json={"operation_type": operation_type, "amount": amount},
    )

    assert response.status_code == expected_status
    if not isinstance(expected_balance, str):
        assert response.json() == {"balance": expected_balance}
    else:
        assert response.json()["detail"] == "Insufficient funds"
