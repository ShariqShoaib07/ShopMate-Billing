from __future__ import annotations

from decimal import Decimal


def format_rupees(amount: Decimal | int | float | str) -> str:
    value = Decimal(str(amount))
    return f"Rs. {value:,.0f}"
