from fastapi import APIRouter, Depends, HTTPException
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from api.crud import get_wallet_by_uuid, get_wallet_for_update
from api.core.logger import logger
from api.schemas.wallet import WalletCreated, OperationRequest
from api.models.wallet import Wallet
from api.dependencies.dependencies import get_current_user
from api.database import get_db, AsyncSessionLocal
from api.models.user import User


router = APIRouter(prefix="/wallets", tags=["wallets"])

logger.info("Wallet created")


@router.post("/")
async def wallet_created(
        wallet_data: WalletCreated,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> dict[str, str | UUID]:
    """
    Выполняет операцию по созданию кошелька

    Пример запроса:
    POST /api/v1/wallet/
    {
        "currency": "USD"
    }

    Успешный ответ (200):
    {
        "message": "Wallet created",
        "wallet_uuid": "123e4567-e89b-12d3-a456-426614174000"
    }

    Ошибки:
    - 400: Кошелек уже создан под данную валюту
    """
    result = await db.execute(
        select(Wallet).filter_by(
            currency=wallet_data.currency,
            user_id=current_user.id
        )
    )
    existing_wallet = result.scalar_one_or_none()

    if existing_wallet:
        raise HTTPException(status_code=400, detail="Wallet already been created")

    # if wallet_data.user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Access denied")

    new_wallet = Wallet(
        user_id=current_user.id,
        currency=wallet_data.currency,
        balance=Decimal("100.00"),
    )
    db.add(new_wallet)
    await db.commit()
    await db.refresh(new_wallet)

    logger.info(f"User {current_user.id} created wallet {new_wallet.uuid}")

    return {"message": "Wallet created", "wallet_uuid": new_wallet.uuid}


@router.get("/{wallet_id}")
async def get_wallet(
        wallet_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> dict[str, Decimal]:
    """
    Находит кошелек по uuid и возвращает баланс

    Пример запроса:
    GET /api/v1/wallets/123e4567-e89b-12d3-a456-426614174000

    Успешный ответ (200):
    {"balance": 100.50}

    Ошибки:
    - 403: Доступ запрещен
    - 404: Кошелек не найден
    """
    wallet = await get_wallet_by_uuid(db, wallet_id)

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if wallet.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return {"balance": wallet.balance}


@router.post("/{wallet_id}/operation")
async def make_operation(
        wallet_id: UUID, request: OperationRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> dict[str, Decimal]:
    """
    Выполняет операцию пополнения (DEPOSIT) или снятия (WITHDRAW) с кошелька.

    - DEPOSIT: увеличивает баланс
    - WITHDRAW: уменьшает баланс (с проверкой достаточности средств)

    Пример запроса:
    {"operation_type": "DEPOSIT", "amount": 100}

    Успешный ответ (200):
    {"balance": 200.00}

    Ошибки:
    - 400: Неверный тип операции (DEPOSIT/WITHDRAW)
    - 402: Недостаточно средств
    - 403: Доступ запрещен
    - 404: Кошелек не найден
    - 409: Кошелек заблокирован
    """

    try:
        wallet = await get_wallet_for_update(db, wallet_id)
    except OperationalError as e:
        if "could not obtain lock" in str(e):
            raise HTTPException(status_code=409, detail="Wallet is busy, please retry")
        raise

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if wallet.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    operation_type = request.operation_type
    if operation_type == "DEPOSIT":
        wallet.balance += request.amount

    elif operation_type == "WITHDRAW":
        if request.amount > wallet.balance:
            raise HTTPException(status_code=402, detail="Insufficient funds")
        wallet.balance -= request.amount

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid operation_type. Use DEPOSIT or WITHDRAW",
        )

    await db.commit()
    logger.info(
        f"Wallet {wallet_id}: {operation_type} {request.amount}, new balance {wallet.balance}"
    )
    return {"balance": wallet.balance}
