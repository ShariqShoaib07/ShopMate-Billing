from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class ReceiptLineItem:
    product_name: str
    quantity: int
    rate: Decimal
    amount: Decimal


@dataclass(frozen=True)
class Receipt:
    shop_name: str
    address: str
    phone_1: str
    phone_2: str
    invoice_number: str
    invoice_date: str
    invoice_time: str
    customer_name: str | None
    customer_mobile: str | None
    items: list[ReceiptLineItem] = field(default_factory=list)
    total: Decimal = Decimal("0")
    total_in_words: str = "Zero Rupees Only"
    thank_you_message: str = "Thank you for shopping with us!"