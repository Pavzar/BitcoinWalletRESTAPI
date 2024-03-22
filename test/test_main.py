import uuid
from datetime import datetime

import pytest
from sqlalchemy import StaticPool, create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from fastapi import status

from restapi.database import get_db
from restapi.main import app

from restapi.models import Base, Transactions
from restapi.utils import generate_transaction_id, fetch_exchange_rate

SQLACHEMY_DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(SQLACHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

transaction_id = generate_transaction_id()
time_now = datetime.now()
one_btc = fetch_exchange_rate()


@pytest.fixture
def test_main():
    main = Transactions(
        transaction_id=transaction_id,
        amount=1,
        created_at=time_now
    )
    db = TestingSessionLocal()
    db.add(main)
    db.commit()
    yield main
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM transactions;"))
        conn.commit()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


client = TestClient(app)

app.dependency_overrides = {get_db: override_get_db}


def test_read_all_transactions(test_main):
    response = client.get('/transactions')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {'transaction_id': transaction_id,
         'amount': 1.0,
         'spent': False,
         'created_at': time_now.strftime("%Y-%m-%dT%H:%M:%S.%f")}]


def test_read_all_transactions_empty_db():
    response = client.get('/transactions')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_balance(test_main):
    response = client.get('/balance')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'balance': {'btc': 1.0, 'eur': round(one_btc, 2)}}


def test_get_balance_empty_db():
    response = client.get('/balance')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'balance': {'btc': 0.0, 'eur': 0.0}}


def test_create_transaction_invalid_amount():
    response = client.post("/transactions", json={"amount_btc": -1.0, "spent": False})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {
        "detail": [
            {
                "type": "greater_than",
                "loc": [
                    "body",
                    "amount_btc"
                ],
                "msg": "Input should be greater than 0",
                "input": -1,
                "ctx": {
                    "gt": 0
                },
                "url": "https://errors.pydantic.dev/2.6/v/greater_than"
            }
        ]
    }


def test_transfer_insufficient_funds_empty_db():
    response = client.post("/transfer", json={"amount_eur": 100000})
    assert response.status_code == status.HTTP_418_IM_A_TEAPOT
    assert response.json() == {'detail':'Insufficient funds'}
