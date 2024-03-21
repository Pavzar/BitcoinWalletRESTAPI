from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Transactions(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String, unique=True)
    amount = Column(Float)
    spent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
