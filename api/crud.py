from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.model import Wallet
from uuid import UUID


async def get_wallet_by_uuid(db: AsyncSession, wallet_uuid: UUID):
    """Находит кошелёк по UUID. Возвращает объект Wallet или None."""
    result = await db.execute(select(Wallet).where(Wallet.uuid == wallet_uuid))
    return result.scalar_one_or_none()


async def get_wallet_for_update(db: AsyncSession, wallet_uuid: UUID):
    """Находит кошелёк по UUID с блокировкой строки для UPDATE."""
    result = await db.execute(
        select(Wallet).where(Wallet.uuid == wallet_uuid).with_for_update(nowait=True)
    )
    return result.scalar_one_or_none()
