import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError
from sqlalchemy import select
from api.model import Wallet
from uuid import UUID


logger = logging.getLogger(__name__)

async def get_wallet_by_uuid(db: AsyncSession, wallet_uuid: UUID) -> Wallet | None:
    """Находит кошелёк по UUID. Возвращает объект Wallet или None."""
    logger.debug(f"Searching for wallet with uuid: {wallet_uuid}")

    result = await db.execute(select(Wallet).where(Wallet.uuid == wallet_uuid))
    wallet = result.scalar_one_or_none()

    if not wallet:
        logger.warning(f"Wallet not found: {wallet_uuid}")

    return wallet


async def get_wallet_for_update(db: AsyncSession, wallet_uuid: UUID) -> Wallet | None:
    """
    Находит кошелёк по UUID с блокировкой строки для UPDATE.

    Использует nowait=True — если строка уже заблокирована,
    сразу вызывает ошибку вместо ожидания.

    Возвращает объект Wallet или None, если не найден.
    """
    try:
        result = await db.execute(
            select(Wallet).where(Wallet.uuid == wallet_uuid).with_for_update(nowait=True)
        )
        return result.scalar_one_or_none()
    except OperationalError as e:
        if "could not obtain lock" in str(e):
            logger.warning(f"Wallet {wallet_uuid} is locked, skipping")
        else:
            logger.error(f"Database error: {e}")
        raise
