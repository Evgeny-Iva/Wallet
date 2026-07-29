import pytest_asyncio

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