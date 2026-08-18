from pydantic import BaseModel, Field
from decimal import Decimal
from uuid import UUID



class WalletCreated(BaseModel):
    """Схема для операции создания кошелька"""
    currency: str = "RUB"


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


class TransferRequest(BaseModel):
    to_wallet_id: UUID
    amount: Decimal
    currency: str = "RUB"


class TransferResponse(BaseModel):
    message: str
    transaction_id: int
    from_balance: Decimal
    to_balance: Decimal