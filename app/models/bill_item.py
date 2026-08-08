from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class BillItem:
    product_id: int
    shortcut: int
    product_name: str
    quantity: int
    rate: Decimal

    @property
    def amount(self) -> Decimal:
        return self.rate * self.quantity
