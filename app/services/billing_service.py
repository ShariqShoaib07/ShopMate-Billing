from __future__ import annotations

from decimal import Decimal, InvalidOperation

from app.models.bill_item import BillItem
from app.models.current_bill import CurrentBill
from app.models.product import Product


class BillingValidationError(ValueError):
    """Raised when current bill input cannot be accepted."""


class BillingService:
    """In-memory billing workflow for the current unsaved bill."""

    def __init__(self) -> None:
        self.current_bill = CurrentBill()

    @property
    def items(self) -> list[BillItem]:
        return list(self.current_bill.items)

    @property
    def total(self) -> Decimal:
        return self.current_bill.total

    def set_customer(self, name: str, mobile: str) -> None:
        self.current_bill.customer_name = name
        self.current_bill.customer_mobile = mobile

    def has_unsaved_data(self) -> bool:
        return self.current_bill.has_unsaved_data

    def add_product(self, product: Product) -> None:
        if product.id is None:
            raise BillingValidationError("Please select a valid product.")

        default_rate = Decimal(str(product.default_price))
        for index, item in enumerate(self.current_bill.items):
            if item.product_id == product.id and item.rate == default_rate:
                self.current_bill.items[index] = BillItem(
                    product_id=item.product_id,
                    shortcut=item.shortcut,
                    product_name=item.product_name,
                    quantity=item.quantity + 1,
                    rate=item.rate,
                )
                return

        self.current_bill.items.append(
            BillItem(
                product_id=product.id,
                shortcut=product.shortcut,
                product_name=product.name,
                quantity=1,
                rate=default_rate,
            )
        )

    def add_product_by_shortcut(self, shortcut: str | int, products: list[Product]) -> None:
        clean_shortcut = self._validate_shortcut(shortcut)
        product = next(
            (item for item in products if item.active and item.shortcut == clean_shortcut),
            None,
        )
        if product is None:
            raise BillingValidationError("No active product is assigned to this shortcut.")
        self.add_product(product)

    def update_description(self, item_index: int, description: str) -> None:
        clean_description = description.strip()
        if not clean_description:
            raise BillingValidationError("Product description is required.")
        item = self._get_item(item_index)
        self.current_bill.items[item_index] = BillItem(
            product_id=item.product_id,
            shortcut=item.shortcut,
            product_name=clean_description,
            quantity=item.quantity,
            rate=item.rate,
        )

    def update_quantity(self, item_index: int, quantity: str | int) -> None:
        clean_quantity = self._validate_quantity(quantity)
        item = self._get_item(item_index)
        self.current_bill.items[item_index] = BillItem(
            product_id=item.product_id,
            shortcut=item.shortcut,
            product_name=item.product_name,
            quantity=clean_quantity,
            rate=item.rate,
        )

    def update_rate(self, item_index: int, rate: str | Decimal | int) -> None:
        clean_rate = self._validate_rate(rate)
        item = self._get_item(item_index)
        self.current_bill.items[item_index] = BillItem(
            product_id=item.product_id,
            shortcut=item.shortcut,
            product_name=item.product_name,
            quantity=item.quantity,
            rate=clean_rate,
        )

    def remove_item(self, item_index: int) -> None:
        self._get_item(item_index)
        del self.current_bill.items[item_index]

    def clear_bill(self) -> None:
        self.current_bill = CurrentBill()

    def _get_item(self, item_index: int) -> BillItem:
        if item_index < 0 or item_index >= len(self.current_bill.items):
            raise BillingValidationError("Please select a valid bill item.")
        return self.current_bill.items[item_index]

    @staticmethod
    def _validate_quantity(quantity: str | int) -> int:
        value = str(quantity).strip()
        if not value:
            raise BillingValidationError("Quantity is required.")
        if not value.isdigit():
            raise BillingValidationError("Quantity must be a whole number.")
        clean_quantity = int(value)
        if clean_quantity <= 0:
            raise BillingValidationError("Quantity must be greater than zero.")
        return clean_quantity

    @staticmethod
    def _validate_rate(rate: str | Decimal | int) -> Decimal:
        value = str(rate).replace(",", "").strip()
        if not value:
            raise BillingValidationError("Rate is required.")
        try:
            clean_rate = Decimal(value)
        except InvalidOperation as exc:
            raise BillingValidationError("Rate must be a number.") from exc
        if clean_rate < 0:
            raise BillingValidationError("Rate cannot be negative.")
        return clean_rate

    @staticmethod
    def _validate_shortcut(shortcut: str | int) -> int:
        value = str(shortcut).strip()
        if not value or not value.isdigit():
            raise BillingValidationError("Product shortcut must be a whole number.")
        return int(value)
