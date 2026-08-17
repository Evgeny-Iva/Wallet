from sqlalchemy import Column, Numeric, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, comment="Уникальный номер транзакции")
    from_wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.uuid"), nullable=False)
    to_wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.uuid"), nullable=False)
    amount = Column(Numeric(10, 2), comment="Сумма перевода")
    currency = Column(String, comment="Валюта (RUB, USD)")
    status = Column(String, default="completed", comment="Статус транзакции")
    created_at = Column(DateTime, server_default=func.now(), comment="Время совершения транзакции")

    from_wallet = relationship("Wallet", foreign_keys=[from_wallet_id])
    to_wallet = relationship("Wallet", foreign_keys=[to_wallet_id])