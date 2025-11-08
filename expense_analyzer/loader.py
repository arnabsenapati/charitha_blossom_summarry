"""Helpers for loading transactions from the CSV export."""

from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Iterator, List

from .models import Transaction


CSV_HEADER = [
    "Date",
    "Amount",
    "Category",
    "Subcategory",
    "Payment Method",
    "Description",
    "Ref/Check No",
    "Payee/Payer",
    "Status",
    "Receipt Picture",
    "Account",
    "Tag",
    "Tax",
    "Quantity",
    "Split Total",
    "Row Id",
    "Type Id",
]


def _iter_clean_rows(path: Path) -> Iterator[List[str]]:
    with path.open(newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not any(field.strip() for field in row):
                continue
            yield row


def load_transactions(path: str | Path) -> List[Transaction]:
    """Load transactions from ``expensemanager.csv``."""

    path = Path(path)
    rows = list(_iter_clean_rows(path))
    if not rows:
        return []

    header, *data_rows = rows
    if header != CSV_HEADER:
        # The first non-empty row might already be data when the export contains
        # an empty header row. In that situation ``header`` will be the first
        # data row, and the second row should contain the header names.
        if data_rows and data_rows[0] == CSV_HEADER:
            data_rows = data_rows[1:]
        else:
            raise ValueError("Unexpected CSV header")

    transactions: List[Transaction] = []
    for raw in data_rows:
        record = dict(zip(CSV_HEADER, raw))
        if not record["Date"]:
            continue
        date = datetime.strptime(record["Date"], "%Y-%m-%d").date()
        amount = float(record["Amount"] or 0)
        row_id = int(record["Row Id"]) if record["Row Id"] else None
        transactions.append(
            Transaction(
                date=date,
                amount=amount,
                category=record["Category"],
                subcategory=record["Subcategory"],
                payment_method=record["Payment Method"],
                description=record["Description"],
                ref_check_no=record["Ref/Check No"],
                payee_payer=record["Payee/Payer"],
                status=record["Status"],
                receipt_picture=record["Receipt Picture"],
                account=record["Account"],
                tag=record["Tag"],
                tax=record["Tax"],
                quantity=record["Quantity"],
                split_total=record["Split Total"],
                row_id=row_id,
                type_id=record["Type Id"],
            )
        )
    return transactions


def filter_by_date(
    transactions: Iterable[Transaction], start: date, end: date
) -> List[Transaction]:
    """Return transactions that occurred between ``start`` and ``end``."""

    return [t for t in transactions if start <= t.date <= end]
