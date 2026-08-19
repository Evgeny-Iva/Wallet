import pytest
import pytest_asyncio
import uuid

from api.main import app
from api.database import engine
from httpx import AsyncClient, ASGITransport
from decimal import Decimal


@pytest_asyncio.fixture
async def client():
    """
    Фикстура выполняет:
    - Создание всех таблиц в БД перед тестом
    - Предоставляет тестовый клиент для отправки HTTP-запросов
    - Удаляет все данные из таблиц после теста
    - Закрывает подключение к БД после теста
    """
    async with engine.begin() as conn:
        from api.database import Base

        await conn.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
        await conn.commit()

    await engine.dispose()


@pytest_asyncio.fixture
async def test_user(client):
    """Фикстура создает тестового пользователя и возвращает его данные"""
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": f"{uuid.uuid4()}@example.com",
        "password": "secret123"
    }
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    return user_data


@pytest_asyncio.fixture
async def auth_token(client, test_user):
    """Фикстура авторизует пользователя и возвращает токен"""
    login_data = {"email": test_user["email"], "password": test_user["password"]}
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def auth_headers(auth_token):
    """Фикстура возвращает заголовок токена"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest_asyncio.fixture
async def test_wallet(client, auth_headers):
    """Создает тестовый кошелек и возвращает его UUID"""
    wallet_data = {"currency": "RUB"}
    response = await client.post("/wallets/", json=wallet_data, headers=auth_headers)
    assert response.status_code == 200
    return response.json()["wallet_uuid"]


@pytest_asyncio.fixture
async def test_user2(client):
    """Фикстура создает второго тестового пользователя и возвращает его данные"""
    user_data = {
        "first_name": "Test2",
        "last_name": "User2",
        "email": f"{uuid.uuid4()}@example.com",
        "password": "secret123"
    }
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 200

    return user_data


@pytest_asyncio.fixture
async def auth_token2(client, test_user2):
    """Фикстура авторизует второго пользователя и возвращает токен"""
    login_data = {"email": test_user2["email"], "password": test_user2["password"]}
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def auth_headers2(auth_token2):
    """Фикстура возвращает заголовок токена для второго пользователя"""
    return {"Authorization": f"Bearer {auth_token2}"}


@pytest_asyncio.fixture
async def test_wallet2(client, auth_headers2):
    """Создает тестовый кошелек для второго пользователя и возвращает его UUID"""
    wallet_data = {"currency": "RUB"}
    response = await client.post("/wallets/", json=wallet_data, headers=auth_headers2)
    assert response.status_code == 200
    return response.json()["wallet_uuid"]


async def wallet_balance(client, wallet_uuid, headers):
    response1 = await client.get(f"/wallets/{wallet_uuid}", headers=headers)
    assert response1.status_code == 200
    return Decimal(response1.json()["balance"])
