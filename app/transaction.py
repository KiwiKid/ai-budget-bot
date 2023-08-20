from typing import List, Dict
from pydantic import BaseModel


class RawTransactionRow(BaseModel):
    rows: Dict[str, Dict[str, str]]


class Transaction(BaseModel):
    date: str
    amount: int
    description: str


class TransactionsList(BaseModel):
    transactions: List[Transaction]
    overrideCategories: str
