"""Produce summaries that mirror the supplied Excel workbook."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List, Sequence, Tuple

from .models import Transaction


@dataclass(frozen=True)
class CollectionSummaryRow:
    account: str
    payee_payer: str
    receipts: float
    payments: float

    @property
    def net(self) -> float:
        return self.receipts - self.payments


@dataclass(frozen=True)
class AccountCategoryRow:
    category: str
    receipts: float
    payments: float

    @property
    def net(self) -> float:
        return self.receipts - self.payments


@dataclass(frozen=True)
class AccountSummary:
    period_start: date
    period_end: date
    opening_balance: float
    closing_balance: float
    total_receipts: float
    total_payments: float
    categories: Sequence[AccountCategoryRow]


def build_collection_summary(
    transactions: Iterable[Transaction],
) -> List[CollectionSummaryRow]:
    buckets: Dict[Tuple[str, str], Dict[str, float]] = defaultdict(
        lambda: {"receipts": 0.0, "payments": 0.0}
    )
    for tx in transactions:
        key = (tx.account or "Unspecified", tx.payee_payer or "Unspecified")
        if tx.is_receipt:
            buckets[key]["receipts"] += tx.amount
        else:
            buckets[key]["payments"] += abs(tx.amount)

    rows = [
        CollectionSummaryRow(
            account=account,
            payee_payer=payee,
            receipts=round(values["receipts"], 2),
            payments=round(values["payments"], 2),
        )
        for (account, payee), values in buckets.items()
    ]
    rows.sort(key=lambda row: (row.account.lower(), row.payee_payer.lower()))
    return rows


def build_account_summary(
    all_transactions: Sequence[Transaction],
    period_transactions: Sequence[Transaction],
    start: date,
    end: date,
) -> AccountSummary:
    opening_balance = sum(
        tx.amount for tx in all_transactions if tx.date < start
    )
    period_total = sum(tx.amount for tx in period_transactions)
    closing_balance = opening_balance + period_total
    receipts = sum(tx.amount for tx in period_transactions if tx.is_receipt)
    payments = sum(-tx.amount for tx in period_transactions if tx.is_payment)

    category_totals: Dict[str, Dict[str, float]] = defaultdict(
        lambda: {"receipts": 0.0, "payments": 0.0}
    )
    for tx in period_transactions:
        category = tx.category or "Uncategorised"
        if tx.is_receipt:
            category_totals[category]["receipts"] += tx.amount
        else:
            category_totals[category]["payments"] += abs(tx.amount)

    categories = [
        AccountCategoryRow(
            category=category,
            receipts=round(values["receipts"], 2),
            payments=round(values["payments"], 2),
        )
        for category, values in sorted(category_totals.items())
    ]

    return AccountSummary(
        period_start=start,
        period_end=end,
        opening_balance=round(opening_balance, 2),
        closing_balance=round(closing_balance, 2),
        total_receipts=round(receipts, 2),
        total_payments=round(payments, 2),
        categories=categories,
    )
