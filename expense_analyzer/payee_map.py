"""Helpers for working with Payee <-> Block/Flat mappings."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Dict, List, Sequence


_LABEL_PATTERN = re.compile(r"([A-Z])0*(\d{1,3})")


def normalize_label(value: str | None) -> str:
    """Return labels in the canonical form ``"B 402"``."""

    if not value:
        return ""
    cleaned = re.sub(r"\s+", "", str(value).upper())
    cleaned = cleaned.replace("-", "")
    match = _LABEL_PATTERN.search(cleaned)
    if not match:
        return str(value).strip().upper()
    block, number = match.groups()
    return f"{block} {int(number):03d}"


def format_label_from_cells(block_value, flat_value) -> str | None:
    """Turn spreadsheet Block/Flat cells into a canonical label."""

    block = (str(block_value).strip().upper() if block_value not in (None, "") else "")
    flat = (str(flat_value).strip() if flat_value not in (None, "") else "")
    if not block or not flat:
        return None
    flat = flat.replace(".0", "")
    try:
        number = int(float(flat))
    except ValueError:
        number = None
    if number is not None:
        return f"{block} {number:03d}"
    return normalize_label(f"{block} {flat}") or None


def _split_payees(cell: str) -> List[str]:
    parts: List[str] = []
    for chunk in re.split(r"[;|]", cell or ""):
        name = chunk.strip()
        if name:
            parts.append(name)
    return parts


def load_payee_mapping(path: Path) -> Dict[str, List[str]]:
    """Load the CSV mapping file into ``{label: [payee, ...]}``."""

    if not path.exists():
        raise FileNotFoundError(f"Payee mapping file not found: {path}")

    mapping: Dict[str, List[str]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            label = normalize_label(row.get("row_label") or "")
            if not label:
                continue
            mapping[label] = _split_payees(row.get("payees") or "")
    return mapping


def payees_for_label(mapping: Dict[str, Sequence[str]], label: str | None) -> Sequence[str]:
    if not label:
        return []
    return mapping.get(normalize_label(label), [])