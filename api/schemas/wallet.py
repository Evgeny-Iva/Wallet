from pydantic import BaseModel, Field
from decimal import Decimal


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
