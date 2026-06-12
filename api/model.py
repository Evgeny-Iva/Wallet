from sqlalchemy import Column, Numeric
from api.database import Base
from sqlalchemy.dialects.postgresql import UUID
from decimal import Decimal
import uuid


class Wallet(Base):
    __tablename__ = "wallets"
    uuid = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True)
    balance = Column(Numeric(10, 2), default=Decimal('100.00'))
