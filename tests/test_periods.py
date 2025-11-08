from datetime import date

from expense_analyzer.periods import last_month_range


def test_last_month_range_handles_year_transition():
    start, end = last_month_range(date(2025, 1, 5))
    assert start == date(2024, 12, 1)
    assert end == date(2024, 12, 31)
