from sqlalchemy import Column, Numeric, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.database import Base
from decimal import Decimal
import uuid


class Wallet(Base):
    __tablename__ = "wallets"

    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
        unique=True,
        comment='Уникальный ключ кошелька'
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        comment='Уникальный ключ пользователя этого кошелька'
    )
    balance = Column(Numeric(10, 2), default=Decimal('100.00'), comment="Текущий баланс счёта")
    currency = Column(String, default="RUB", comment='Валюта')

    user = relationship("User", back_populates="wallets")