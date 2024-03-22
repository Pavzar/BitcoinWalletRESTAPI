import uuid
from decimal import Decimal, getcontext

import requests
from fastapi import HTTPException
from starlette import status

from .models import Transactions

EXCHANGE_RATE_URL = "http://api-cryptopia.adca.sh/v1/prices/ticker"
getcontext().prec = 8


def generate_transaction_id():
    return str(uuid.uuid4())


def fetch_exchange_rate():
    try:
        response = requests.get(EXCHANGE_RATE_URL, params={"symbol": "BTC/EUR"})
        response.raise_for_status()
        data = response.json()
        return float(data['data'][0]['value'])

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


def process_transfer_transaction(amount_eur, transactions):
    exchange_rate = Decimal(fetch_exchange_rate())
    amount_btc = Decimal(amount_eur) / exchange_rate

    if amount_btc < Decimal('0.00001'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Transfer amount is smaller than 0.00001 btc")

    total_btc = Decimal()
    used_txs = []
    for tx in transactions:
        if not tx.spent:
            used_txs.append(tx)
            total_btc += Decimal(tx.amount)
            if Decimal(total_btc) >= amount_btc:
                break

    if total_btc < amount_btc:
        raise HTTPException(status_code=status.HTTP_418_IM_A_TEAPOT, detail="Insufficient funds")

    leftover_btc = total_btc - amount_btc
    new_unspent_tx = None

    if leftover_btc > 0:
        new_unspent_tx = Transactions(
            transaction_id=generate_transaction_id(),
            amount=float(leftover_btc)
        )
    return used_txs, new_unspent_tx
