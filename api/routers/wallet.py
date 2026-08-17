from fastapi import APIRouter, Depends, HTTPException
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from api.crud import get_wallet_by_uuid, get_wallet_for_update
from api.core.logger import logger
from api.schemas.wallet import WalletCreated, OperationRequest, TransferRequest, TransferResponse
from api.dependencies.dependencies import get_current_user
from api.database import get_db, AsyncSessionLocal
from api.models.user import User
from api.models.wallet import Wallet
from api.models.transaction import Transaction


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
    POST /wallet/
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
    GET /wallets/123e4567-e89b-12d3-a456-426614174000

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


@router.post("/{wallet_id}/transfer", response_model=TransferResponse)
async def transaction(
        wallet_id: UUID,
        transfer_data: TransferRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Выполняет операцию перевода между кошельками

    Пример запроса:
    POST /wallets/123e4567-e89b-12d3-a456-426614174000/transfer
    {
        to_wallet_id: 123e4567-e89b-12d3-a456-789123456000
        amount: 100
        currency: RUB
    }

    Успешный ответ(200):
    {
        "message": "Transfer completed",
        "transaction_id": 123,
        "from_balance": 2000,
        "to_balance": 1100
    }

    Ошибки:
    - 400: Не соответствие валют
    - 400: Недостаточно средств
    - 403: Доступ запрещен
    - 404: Кошелек не найден
    - 404: Кошелек получателя не найден
    """
    from_wallet = await db.get(Wallet, wallet_id)

    if not from_wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if from_wallet.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    to_wallet = await db.get(Wallet, transfer_data.to_wallet_id)
    if not to_wallet:
        raise HTTPException(status_code=404, detail="Recipient wallet not found")

    if to_wallet.currency != transfer_data.currency:
        raise HTTPException(status_code=400, detail="Currency mismatch")

    if from_wallet.balance < transfer_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    from_wallet.balance -= transfer_data.amount
    to_wallet.balance += transfer_data.amount

    new_transaction = Transaction(
        from_wallet_id=from_wallet.uuid,
        to_wallet_id=to_wallet.uuid,
        amount=transfer_data.amount,
        currency=from_wallet.currency,
        status="completed"
    )
    db.add(new_transaction)
    await db.commit()

    return {
        "message": "Transfer completed",
        "transaction_id": new_transaction.id,
        "from_balance": from_wallet.balance,
        "to_balance": to_wallet.balance
    }