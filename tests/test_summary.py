from datetime import date

from expense_analyzer.models import Transaction
from expense_analyzer.summary import (
    build_account_summary,
    build_collection_summary,
)


def make_transaction(**kwargs):
    base = dict(
        date=date(2025, 1, 15),
        amount=0.0,
        category="",
        subcategory="",
        payment_method="",
        description="",
        ref_check_no="",
        payee_payer="",
        status="",
        receipt_picture="",
        account="",
        tag="",
        tax="",
        quantity="",
        split_total="",
        row_id=None,
        type_id="",
    )
    base.update(kwargs)
    return Transaction(**base)


def test_collection_summary_groups_by_account_and_payee():
    transactions = [
        make_transaction(account="A", payee_payer="John", amount=100),
        make_transaction(account="A", payee_payer="John", amount=-25),
        make_transaction(account="B", payee_payer="Anna", amount=50),
    ]

    rows = build_collection_summary(transactions)
    assert len(rows) == 2
    first = rows[0]
    second = rows[1]
    assert first.account == "A"
    assert first.payee_payer == "John"
    assert first.receipts == 100
    assert first.payments == 25
    assert first.net == 75
    assert second.account == "B"
    assert second.payee_payer == "Anna"


def test_account_summary_calculates_balances_and_totals():
    all_tx = [
        make_transaction(date=date(2024, 12, 31), amount=200),
        make_transaction(date=date(2025, 1, 10), amount=100, category="Income"),
        make_transaction(date=date(2025, 1, 11), amount=-30, category="Expense"),
    ]
    period_tx = all_tx[1:]

    summary = build_account_summary(all_tx, period_tx, date(2025, 1, 1), date(2025, 1, 31))

    assert summary.opening_balance == 200
    assert summary.closing_balance == 270
    assert summary.total_receipts == 100
    assert summary.total_payments == 30
    categories = {row.category: row for row in summary.categories}
    assert categories["Income"].receipts == 100
    assert categories["Expense"].payments == 30
    expenses = summary.expenses_by_category.get("Expense")
    assert expenses is not None
    assert len(expenses) == 1
    detail = expenses[0]
    assert detail.amount == 30
    assert detail.account == "Unspecified"
    balances = {b.account: b for b in summary.account_balances}
    assert balances["Unspecified"].opening_balance == 200
    assert balances["Unspecified"].closing_balance == 270
