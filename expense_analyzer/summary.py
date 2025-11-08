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
class AccountBalanceRow:
    account: str
    opening_balance: float
    receipts: float
    payments: float
    closing_balance: float


@dataclass(frozen=True)
class AccountSummary:
    period_start: date
    period_end: date
    opening_balance: float
    closing_balance: float
    total_receipts: float
    total_payments: float
    categories: Sequence[AccountCategoryRow]
    expenses_by_category: Dict[str, Sequence["ExpenseDetail"]]
    account_balances: Sequence[AccountBalanceRow]


@dataclass(frozen=True)
class ExpenseDetail:
    date: date
    description: str
    payee_payer: str
    account: str
    amount: float


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
    expenses_by_category: Dict[str, List[ExpenseDetail]] = defaultdict(list)
    account_balance_data: Dict[str, Dict[str, float]] = defaultdict(
        lambda: {"opening": 0.0, "receipts": 0.0, "payments": 0.0}
    )

    for tx in all_transactions:
        if tx.date >= start:
            continue
        account = tx.account or "Unspecified"
        account_balance_data[account]["opening"] += tx.amount

    for tx in period_transactions:
        category = tx.category or "Uncategorised"
        account = tx.account or "Unspecified"
        if tx.is_receipt:
            category_totals[category]["receipts"] += tx.amount
            account_balance_data[account]["receipts"] += tx.amount
        else:
            amount = abs(tx.amount)
            category_totals[category]["payments"] += amount
            expenses_by_category[category].append(
                ExpenseDetail(
                    date=tx.date,
                    description=tx.description or tx.payee_payer or "",
                    payee_payer=tx.payee_payer or "Unspecified",
                    account=account,
                    amount=round(amount, 2),
                )
            )
            account_balance_data[account]["payments"] += amount

    categories = [
        AccountCategoryRow(
            category=category,
            receipts=round(values["receipts"], 2),
            payments=round(values["payments"], 2),
        )
        for category, values in sorted(category_totals.items())
    ]

    account_balances = [
        AccountBalanceRow(
            account=account,
            opening_balance=round(data["opening"], 2),
            receipts=round(data["receipts"], 2),
            payments=round(data["payments"], 2),
            closing_balance=round(data["opening"] + data["receipts"] - data["payments"], 2),
        )
        for account, data in sorted(account_balance_data.items())
    ]

    return AccountSummary(
        period_start=start,
        period_end=end,
        opening_balance=round(opening_balance, 2),
        closing_balance=round(closing_balance, 2),
        total_receipts=round(receipts, 2),
        total_payments=round(payments, 2),
        categories=categories,
        expenses_by_category={category: tuple(details) for category, details in expenses_by_category.items()},
        account_balances=account_balances,
    )
