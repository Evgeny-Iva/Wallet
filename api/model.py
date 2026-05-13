from sqlalchemy import Column, String, Float
from api.database import Base


class Wallet(Base):
    __tablename__ = "wallets"
    uuid = Column(String, primary_key=True, index=True)
    balance = Column(Float, default=100.0)