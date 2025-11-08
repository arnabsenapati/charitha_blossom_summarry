"""Utility helpers for turning summary objects into text tables."""

from __future__ import annotations

from typing import Iterable, Sequence

from .summary import (
    AccountCategoryRow,
    AccountSummary,
    CollectionSummaryRow,
)


def _column_widths(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> Sequence[int]:
    widths = [len(h) for h in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(cell))
    return widths


def _format_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    widths = _column_widths(headers, rows)

    def format_row(row: Sequence[str]) -> str:
        return " | ".join(cell.ljust(widths[idx]) for idx, cell in enumerate(row))

    header_line = format_row(headers)
    separator = "-+-".join("-" * w for w in widths)
    body = "\n".join(format_row(row) for row in rows)
    return "\n".join([header_line, separator, body]) if body else "\n".join(
        [header_line, separator]
    )


def format_collection_summary(rows: Iterable[CollectionSummaryRow]) -> str:
    headers = ["Account", "Payee/Payer", "Receipts", "Payments", "Net"]
    data_rows = [
        [
            row.account or "Unspecified",
            row.payee_payer or "Unspecified",
            f"{row.receipts:,.2f}",
            f"{row.payments:,.2f}",
            f"{row.net:,.2f}",
        ]
        for row in rows
    ]
    return _format_table(headers, data_rows)


def format_account_summary(summary: AccountSummary) -> str:
    header_lines = [
        "Statement of Accounts",
        f"Period: {summary.period_start:%Y-%m-%d} to {summary.period_end:%Y-%m-%d}",
        f"Opening Balance: {summary.opening_balance:,.2f}",
        f"Closing Balance: {summary.closing_balance:,.2f}",
        f"Total Receipts: {summary.total_receipts:,.2f}",
        f"Total Payments: {summary.total_payments:,.2f}",
    ]
    table_rows = [
        [
            category.category,
            f"{category.receipts:,.2f}",
            f"{category.payments:,.2f}",
            f"{category.net:,.2f}",
        ]
        for category in summary.categories
    ]
    table_text = _format_table(["Category", "Receipts", "Payments", "Net"], table_rows)
    return "\n".join(header_lines + ["", table_text])
