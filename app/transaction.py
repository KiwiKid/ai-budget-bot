from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID


class Transaction(BaseModel):
    t_id: str
    ts_id: str
    user_id: str
    date: datetime
    description: str
    amount: Decimal
    status: str
    created_at: datetime
    category: Optional[str] = None

    def __init__(self, t_id: UUID, ts_id: UUID, user_id: UUID, date: datetime, description: str,
                 amount: Decimal, status: str, created_at: datetime, category: Optional[str] = None):
        super().__init__(
            t_id=str(t_id),
            ts_id=str(ts_id),
            user_id=str(user_id),
            date=date,
            description=description,
            amount=amount,
            status=status,
            created_at=created_at,
            category=category
        )

# If you need a wrapper for multiple transactions:


class TransactionList(BaseModel):
    transactions: List[Transaction]
