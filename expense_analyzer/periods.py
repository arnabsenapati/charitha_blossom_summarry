"""Utilities for working with reporting periods."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Tuple


def last_month_range(today: date | None = None) -> Tuple[date, date]:
    """Return the first and last day of the calendar month before ``today``."""

    today = today or date.today()
    first_of_this_month = today.replace(day=1)
    last_day_previous_month = first_of_this_month - timedelta(days=1)
    first_day_previous_month = last_day_previous_month.replace(day=1)
    return first_day_previous_month, last_day_previous_month
