import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from decimal import Decimal
from uuid import UUID
from api.database import AsyncSessionLocal
from api.crud import get_wallet_by_uuid, get_wallet_for_update
from api.routers.auto import router as auth_router
from api.config import settings
from api.routers.users import router as users_router
from sqlalchemy.exc import OperationalError
from logging.handlers import RotatingFileHandler


log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

os.makedirs("logs", exist_ok=True)

file_handler = RotatingFileHandler(
    settings.LOG_FILE,
    maxBytes=20000000,
    backupCount=5,
    encoding="utf-8"
)
file_handler.setFormatter(logging.Formatter(log_format))

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(log_format))

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    handlers=[file_handler, console_handler],
    format=log_format
)

logger = logging.getLogger(__name__)

app = FastAPI(debug=settings.DEBUG)

app.include_router(auth_router)
app.include_router(users_router)

class OperationRequest(BaseModel):
    """
    Схема запроса для операций с кошельком

    Пример:
    {"operation_type": "DEPOSIT", "amount": 100}

    - operation_type: тип операции (DEPOSIT или WITHDRAW)
    - amount: сумма операции (положительное число)
    """

    operation_type: str
    amount: Decimal = Field(..., gt=0, description="Сумма должна быть положительной")


@app.get("/api/v1/wallets/{wallet_id}")
async def get_wallet(wallet_id: UUID) -> dict[str, Decimal]:
    """
    Находит кошелек по uuid и возвращает баланс

    Пример запроса:
    GET /api/v1/wallets/123e4567-e89b-12d3-a456-426614174000

    Успешный ответ (200):
    {"balance": 100.50}

    Ошибки:
    - 404: Кошелек не найден
    """
    async with AsyncSessionLocal() as db:
        wallet = await get_wallet_by_uuid(db, wallet_id)

        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")

        return {"balance": wallet.balance}


@app.post("/api/v1/wallets/{wallet_id}/operation")
async def make_operation(wallet_id: UUID, request: OperationRequest) -> dict[str, Decimal]:
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
    - 404: Кошелек не найден
    - 409: Кошелек заблокирован
    """
    async with AsyncSessionLocal() as db:
        await db.begin()

        try:
            wallet = await get_wallet_for_update(db, wallet_id)
        except OperationalError as e:
            if "could not obtain lock" in str(e):
                raise HTTPException(status_code=409, detail="Wallet is busy, please retry")
            raise

        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")

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
