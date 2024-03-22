from datetime import datetime
from pydantic import BaseModel, Field


class TransferRequest(BaseModel):
    amount_eur: float = Field(gt=0, default=10000, description="Transfer amount in EUR (must be greater than 0)")


class TransactionsOut(BaseModel):
    transaction_id: str = Field(description="Unique transaction identifier")
    amount: float = Field(description="Transaction amount in BTC")
    spent: bool = Field(description="Whether the transaction has been used in a transfer")
    created_at: datetime = Field(description="Timestamp of transaction creation")


class TransactionsIn(BaseModel):
    amount_btc: float = Field(gt=0, default=1, description="Transaction amount in BTC")
    spent: bool = Field(default=False, description="Whether the transaction has been used in a transfer")

