# Expense summary generator

This repository now contains a small Python project that reads the `expensemanager.csv`
export and produces a monthly report that mirrors the "Collection Summary" and
"Statement of Accounts" sheets that appear in the provided Excel workbook.

## Requirements

The project relies only on the Python standard library and works with Python 3.11+
(which is the version available in the execution environment used to develop the
solution).

## Usage

```bash
python -m expense_analyzer --as-of 2025-09-15
```

Running the command will:

1. Determine the calendar month immediately before the provided `--as-of` date
   (or before today when the flag is omitted).
2. Filter transactions in `expensemanager.csv` to that month.
3. Print a *Collection Summary* table that aggregates receipts and payments by
   account and payee.
4. Print a *Statement of Accounts* section that displays opening/closing balances
   and totals per transaction category.

Use `--output path/to/file.txt` to write the combined report to disk instead of
printing it to the console. The script reads `expensemanager.csv` from the current
working directory by default, but you can pass a custom path as the first
positional argument.

## Running tests

The unit tests exercise the period calculations and the two summary builders.
Execute them with:

```bash
pytest
```
