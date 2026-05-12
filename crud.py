from database import AsyncSessionLocal
from sqlalchemy import select
from model import Wallet


async def get_wallet_by_uuid(db: AsyncSessionLocal, wallet_uuid: str):
    """Находит кошелёк по UUID. Возвращает объект Wallet или None."""
    result = await db.execute(
        select(Wallet).where(Wallet.uuid == wallet_uuid)
    )
    return result.scalar_one_or_none