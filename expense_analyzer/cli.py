"""Command line entry point for generating monthly expense summaries."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Iterable

from .formatting import format_account_summary, format_collection_summary
from .loader import filter_by_date, load_transactions
from .payee_map import load_payee_mapping, normalize_label
from .payments_map import load_payment_rules
from .periods import last_month_range
from .summary import build_account_summary, build_collection_summary
from .excel import update_paid_columns

ALWAYS_PAID_LABELS = {
    normalize_label(label)
    for label in [
        "A 002",
        "A 003",
        "A 004",
        "A 005",
        "A 101",
        "A 102",
        "A 104",
        "A 105",
        "A 106",
        "A 201",
        "A 203",
        "A 204",
        "A 205",
        "A 206",
        "A 302",
        "A 304",
        "A 305",
        "A 306",
        "A 401",
        "A 403",
        "A 404",
        "A 405",
        "A 406",
        "B 003",
        "B 005",
        "B 102",
        "B 106",
        "B 201",
        "B 304",
        "B 306",
        "B 401",
        "B 403",
        "B 405",
    ]
}

def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Summarise the previous month's income and expenses based on an "
            "Expense Manager CSV export."
        )
    )
    parser.add_argument(
        "csv_path",
        nargs="?",
        default="expensemanager.csv",
        help="Path to the expense manager CSV export.",
    )
    parser.add_argument(
        "--as-of",
        type=date.fromisoformat,
        help="Override the date used to determine the reporting month.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help=(
            "Write the summaries to the specified file instead of printing to "
            "stdout."
        ),
    )
    parser.add_argument(
        "--excel-template",
        type=Path,
        help=(
            "Path to an existing Excel workbook to update (e.g. Statements-*.xlsx)."
        ),
    )
    parser.add_argument(
        "--excel-output",
        type=Path,
        help=(
            "Path to write the updated Excel workbook with Paid columns filled."
        ),
    )
    parser.add_argument(
        "--fixed-paid-amount",
        type=float,
        default=3500.0,
        help=(
            "Amount to force into the Paid columns for designated flats (default: 3500)."
        ),
    )
    parser.add_argument(
        "--payee-map",
        type=Path,
        help=(
            "CSV mapping file describing which Payee/Payer belongs to each Block/Flat. "
            "Defaults to payee_mapping.csv in the current directory."
        ),
    )
    parser.add_argument(
        "--payments-map",
        type=Path,
        help=(
            "CSV mapping file describing how expenses feed the Account sheet Payments column. "
            "Defaults to account_payments_mapping.csv in the current directory."
        ),
    )
    return parser.parse_args(argv)


def run(argv: Iterable[str] | None = None) -> str:
    args = parse_args(argv)
    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        raise SystemExit(f"CSV file not found: {csv_path}")

    transactions = load_transactions(csv_path)
    if not transactions:
        raise SystemExit("No transactions found in the CSV export.")

    period_start, period_end = last_month_range(args.as_of)
    period_transactions = filter_by_date(transactions, period_start, period_end)
    if not period_transactions:
        raise SystemExit(
            "No transactions found for the previous month. "
            "Use --as-of to analyse an earlier period if required."
        )

    collection_rows = build_collection_summary(period_transactions)
    account_summary = build_account_summary(
        transactions, period_transactions, period_start, period_end
    )

    collection_text = format_collection_summary(collection_rows)
    account_text = format_account_summary(account_summary)
    output_text = (
        "Collection Summary\n" + collection_text + "\n\n" + account_text + "\n"
    )

    if args.output:
        args.output.write_text(output_text, encoding="utf-8")
    else:
        print(output_text)

    # Optionally update Excel workbook Paid columns based on a mapping file
    if args.excel_template and args.excel_output:
        map_path = args.payee_map or Path("payee_mapping.csv")
        if not map_path.exists():
            raise SystemExit(f"Payee mapping file not found: {map_path}")
        try:
            payee_map = load_payee_mapping(map_path)
            payments_map_path = args.payments_map or Path("account_payments_mapping.csv")
            payment_rules = load_payment_rules(payments_map_path)
            fixed_paid_overrides = {label: args.fixed_paid_amount for label in ALWAYS_PAID_LABELS}
            update_paid_columns(
                Path(args.excel_template),
                Path(args.excel_output),
                collection_rows,
                period_transactions,
                payee_map=payee_map,
                payment_rules=payment_rules,
                fixed_paid_overrides=fixed_paid_overrides,
                period_start=period_start,
                period_end=period_end,
            )
        except Exception as exc:
            raise SystemExit(f"Failed to update Excel workbook: {exc}")
    return output_text


def main() -> None:
    run()


if __name__ == "__main__":
    main()
