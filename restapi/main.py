from typing import Annotated, List

import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Boolean, cast
from sqlalchemy.orm import Session
from starlette import status
from .models import Transactions
from .database import get_db
from .schemas import TransactionsIn, TransferRequest, TransactionsOut
from .utils import generate_transaction_id, fetch_exchange_rate, process_transfer_transaction

app = FastAPI()
db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/transactions", status_code=status.HTTP_200_OK, response_model=List[TransactionsOut])
async def list_all_transactions(db: db_dependency):
    transactions = db.query(Transactions).all()
    transactions_out = []
    for tx in transactions:
        transactions_out.append({
            "transaction_id": tx.transaction_id,
            "amount": tx.amount,
            "spent": tx.spent,
            "created_at": tx.created_at
        })
    return transactions_out


@app.post("/transactions", status_code=status.HTTP_201_CREATED)
async def create_transaction(db: db_dependency, create_tx: TransactionsIn):
    try:
        new_transaction = Transactions(
            transaction_id=generate_transaction_id(),
            amount=create_tx.amount_btc,
            spent=create_tx.spent
        )
        db.add(new_transaction)
        db.commit()

        return {"message": "Transaction created successfully"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/balance", status_code=status.HTTP_200_OK)
async def get_balance(db: db_dependency):
    unspent_txs = db.query(Transactions).filter(cast(Transactions.spent.__eq__(False), Boolean)).all()
    total_btc = sum(tx.amount for tx in unspent_txs)
    exchange_rate = fetch_exchange_rate()
    balance_eur = round(total_btc * exchange_rate, 2)
    return {"balance": {"btc": total_btc, "eur": balance_eur}}


@app.post("/transfer", status_code=status.HTTP_201_CREATED)
async def create_transfer(transfer_request: TransferRequest, db: db_dependency):
    try:
        unspent_txs = db.query(Transactions).filter(cast(Transactions.spent.__eq__(False), Boolean)).all()
        used_txs, new_unspent_txs = process_transfer_transaction(transfer_request.amount_eur, unspent_txs)
        for tx in used_txs:
            tx.spent = True
        if new_unspent_txs:
            db.add(new_unspent_txs)

        db.commit()
        return {"message": "Transfer successful"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
