import asyncio
import asyncpg
from api.database import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME


async def create_database():
    """Создает базу данных если она не существует"""
    conn = await asyncpg.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database='postgres'
    )

    result = await conn.fetchval(
        "SELECT 1 FROM pg_database WHERE datname = $1", DB_NAME
    )

    if not result:
        await conn.execute(f'CREATE DATABASE "{DB_NAME}"')
        print(f"База данных {DB_NAME} создана")
    else:
        print(f"База данных {DB_NAME} уже существует")

    await conn.close()


if __name__ == "__main__":
    asyncio.run(create_database())