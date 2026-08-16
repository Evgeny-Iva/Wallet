import pytest
import pytest_asyncio
import uuid

from api.main import app
from api.database import engine
from httpx import AsyncClient, ASGITransport


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
    """Фикстура создает пользователя и возвращает токен"""
    login_data = {"email": test_user["email"], "password": test_user["password"]}
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def auth_handlers(auth_token):
    """Фикстура возвращает заголовок токена"""
    return {"Authorization": f"Bearer {auth_token}"}