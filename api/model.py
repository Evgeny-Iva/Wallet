from sqlalchemy import Column, String, Numeric
from api.database import Base


class Wallet(Base):
    __tablename__ = "wallets"
    uuid = Column(String, primary_key=True, index=True)
    balance = Column(Numeric(10, 2), default=100.0)
