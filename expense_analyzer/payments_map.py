"""Load mapping rules for Account sheet payments."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class PaymentRule:
    row_label: str
    category: str | None
    subcategory: str | None
    description_contains: str | None
    payee_contains: str | None

    def matches(self, transaction) -> bool:
        if not transaction.is_payment:
            return False
        if self.category and (transaction.category or "").strip().lower() != self.category:
            return False
        if self.subcategory and (transaction.subcategory or "").strip().lower() != self.subcategory:
            return False
        if self.description_contains:
            desc = (transaction.description or "").lower()
            if self.description_contains not in desc:
                return False
        if self.payee_contains:
            payee = (transaction.payee_payer or "").lower()
            if self.payee_contains not in payee:
                return False
        return True


def _to_lower(value: str | None) -> str | None:
    if not value:
        return None
    return value.strip().lower()


def load_payment_rules(path: Path) -> List[PaymentRule]:
    if not path.exists():
        raise FileNotFoundError(f"Payments mapping file not found: {path}")
    rules: List[PaymentRule] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            row_label = (row.get("row_label") or "").strip()
            if not row_label:
                continue
            rules.append(
                PaymentRule(
                    row_label=row_label,
                    category=_to_lower(row.get("category")),
                    subcategory=_to_lower(row.get("subcategory")),
                    description_contains=_to_lower(row.get("description_contains")),
                    payee_contains=_to_lower(row.get("payee_contains")),
                )
            )
    return rules
