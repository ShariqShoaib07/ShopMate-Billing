from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class InvoiceItem:
    id: int | None
    invoice_id: int | None
    product_id: int | None
    product_shortcut: int
    product_name: str
    quantity: int
    rate: Decimal
    amount: Decimal
