from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import UUID
from model import Wallet
from database import Base, engine, SessionLocal

app = FastAPI()

Base.metadata.create_all(bind=engine)

class OperationRequest(BaseModel):
    operation_type: str
    amount: float


@app.get("/api/v1/wallets/{wallet_id}")
def get_wallet(wallet_id: UUID):
    db = SessionLocal()
    try:
        wallet_key = str(wallet_id)
        wallet = db.query(Wallet).filter(Wallet.uuid == wallet_key).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")

        return {"balance": wallet.balance}
    finally:
        db.close()


@app.post("/api/v1/wallets/{wallet_id}/operation")
def make_operation(wallet_id: UUID, request: OperationRequest):
    db = SessionLocal()
    try:
        wallet_key = str(wallet_id)
        wallet = db.query(Wallet).filter(Wallet.uuid == wallet_key).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")

        operation_type = request.operation_type
        if operation_type == "DEPOSIT":
            wallet.balance += request.amount

        elif operation_type == "WITHDRAW":
            if request.amount > wallet.balance:
                raise HTTPException(status_code=400, detail="Insufficient funds")
            wallet.balance -= request.amount

        else:
            raise HTTPException(status_code=400, detail="Invalid operation_type. Use DEPOSIT or WITHDRAW")

        db.commit()
        return {"balance": wallet.balance}
    finally:
        db.close()