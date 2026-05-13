import asyncio
from api.database import async_engine, Base

async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблицы созданы (или уже существуют)")

if __name__ == "__main__":
    asyncio.run(create_tables())