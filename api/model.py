from sqlalchemy import Column, Numeric, Integer, String, DateTime, func, ForeignKey
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
        index=True, default=uuid.uuid4,
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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment='Уникальный номер пользователя')
    first_name = Column(String, nullable=False, comment='Имя пользователя')
    last_name = Column(String, nullable=False, comment='Фамилия пользователя')
    middle_name = Column(String, nullable=True, comment='Отчество пользователя')
    email = Column(String, unique=True, index=True, nullable=False, comment='Электронная почта пользователя')
    created_at = Column(DateTime, server_default=func.now(), comment='Дата создания профиля')

    wallets = relationship("wallet", back_populates="User")