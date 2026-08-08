from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from app.models.bill_item import BillItem


@dataclass
class CurrentBill:
    customer_name: str = ""
    customer_mobile: str = ""
    items: list[BillItem] = field(default_factory=list)

    @property
    def total(self) -> Decimal:
        return sum((item.amount for item in self.items), Decimal("0"))

    @property
    def has_unsaved_data(self) -> bool:
        return bool(self.customer_name.strip() or self.customer_mobile.strip() or self.items)
