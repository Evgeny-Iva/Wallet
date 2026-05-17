from sqlalchemy import Column, Numeric
from api.database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Wallet(Base):
    __tablename__ = "wallets"
    uuid = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4,)
    balance = Column(Numeric(10, 2), default=100.0)
