import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from decimal import Decimal
from uuid import UUID
from api.database import AsyncSessionLocal
from api.crud import get_wallet_by_uuid, get_wallet_for_update


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()


class OperationRequest(BaseModel):
    """
    Схема запроса для операций с кошельком

    - operation_type: тип операции (DEPOSIT или WITHDRAW)
    - amount: сумма операции (положительное число)
    """

    operation_type: str
    amount: Decimal = Field(..., gt=0, description="Сумма должна быть положительной")


@app.get("/api/v1/wallets/{wallet_id}")
async def get_wallet(wallet_id: UUID):
    """
    Находит кошелек по uuid и возвращает баланс

    В случае ошибки возвращает соответсвующий HTTP статус 404
    """
    async with AsyncSessionLocal() as db:
        wallet = await get_wallet_by_uuid(db, wallet_id)

        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")

        return {"balance": wallet.balance}


@app.post("/api/v1/wallets/{wallet_id}/operation")
async def make_operation(wallet_id: UUID, request: OperationRequest):
    """
    Выполняет операцию пополнения (DEPOSIT) или снятия (WITHDRAW) с кошелька.

    - DEPOSIT: увеличивает баланс
    - WITHDRAW: уменьшает баланс (с проверкой достаточности средств)

    В случае успеха возвращает обновлённый баланс.
    В случае ошибки возвращает соответствующий HTTP статус (404, 400).
    """
    async with AsyncSessionLocal() as db:
        await db.begin()
        wallet = await get_wallet_for_update(db, wallet_id)

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
