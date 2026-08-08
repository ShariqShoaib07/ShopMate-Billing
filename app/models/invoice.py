from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from app.models.invoice_item import InvoiceItem


@dataclass(frozen=True)
class Invoice:
    id: int | None
    invoice_number: str
    customer_name: str | None
    customer_mobile: str | None
    invoice_date: str
    invoice_time: str
    total: Decimal
    created_at: str | None = None
    items: list[InvoiceItem] = field(default_factory=list)
