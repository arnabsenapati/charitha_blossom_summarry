"""Data models used by the expense analyzer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class Transaction:
    """Represents a single row loaded from ``expensemanager.csv``."""

    date: date
    amount: float
    category: str
    subcategory: str
    payment_method: str
    description: str
    ref_check_no: str
    payee_payer: str
    status: str
    receipt_picture: str
    account: str
    tag: str
    tax: str
    quantity: str
    split_total: str
    row_id: Optional[int]
    type_id: str

    @property
    def is_receipt(self) -> bool:
        """Return ``True`` when the transaction represents money received."""

        return self.amount >= 0

    @property
    def is_payment(self) -> bool:
        """Return ``True`` when the transaction represents money paid out."""

        return self.amount < 0
