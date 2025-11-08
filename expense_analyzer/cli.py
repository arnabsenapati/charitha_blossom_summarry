"""Command line entry point for generating monthly expense summaries."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Iterable

from .formatting import format_account_summary, format_collection_summary
from .loader import filter_by_date, load_transactions
from .periods import last_month_range
from .summary import build_account_summary, build_collection_summary


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
    return output_text


def main() -> None:
    run()


if __name__ == "__main__":
    main()
