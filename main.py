from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import UUID

app = FastAPI()

wallets = {
    "123e4567-e89b-12d3-a456-426614174000": 100.0
}


class OperationRequest(BaseModel):
    operation_type: str
    amount: float


@app.get("/api/v1/wallets/{wallet_uuid}")
def get_wallet(wallets_id: UUID):
    if str(wallets_id) in wallets:
        return {"balance": wallets[str(wallets_id)]}
    else:
        raise HTTPException(status_code=404, detail="Wallet not found")


@app.post("/api/v1/wallets/{wallet_uuid}/operation")
def make_operation(wallet_id: UUID, request: OperationRequest):
    wallet = str(wallet_id)
    if not wallet_id in wallets:
        raise HTTPException(status_code=404, detail="Wallet not found")

    operation_type = request.operation_type
    if operation_type == "DEPOSIT":
        wallet += request.amount

    elif operation_type == "WITHDRAW":
        if request.amount > wallets[wallet]:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        wallet -= request.amount

    else:
        raise HTTPException(status_code=400, detail="Invalid operation_type. Use DEPOSIT or WITHDRAW")


    return {"balance": wallet}