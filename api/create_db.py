import asyncio
import asyncpg
import os
from dotenv import load_dotenv


async def create_database():
    """Создает базу данных если она не существует"""
    conn = await asyncpg.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database="postgres",
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
    load_dotenv()

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    asyncio.run(create_database())
