from __future__ import annotations

from pathlib import Path

from app.database.repositories.invoice_repository import InvoiceRepository
from app.models.current_bill import CurrentBill
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.utils.date_time import current_date, current_time


class InvoiceValidationError(ValueError):
    """Raised when an invoice cannot be saved."""


class InvoiceService:
    """Invoice persistence workflow."""

    def __init__(
        self,
        database_path: Path | None = None,
        repository: InvoiceRepository | None = None,
    ) -> None:
        self.repository = repository or InvoiceRepository(database_path)

    def invoice_count(self) -> int:
        return self.repository.count()

    def save_current_bill(self, current_bill: CurrentBill) -> Invoice:
        if not current_bill.items:
            raise InvoiceValidationError("Cannot save an empty bill.")

        invoice = Invoice(
            id=None,
            invoice_number="",
            customer_name=current_bill.customer_name.strip() or None,
            customer_mobile=current_bill.customer_mobile.strip() or None,
            invoice_date=current_date(),
            invoice_time=current_time(),
            total=current_bill.total,
            items=[
                InvoiceItem(
                    id=None,
                    invoice_id=None,
                    product_id=item.product_id,
                    product_shortcut=item.shortcut,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    rate=item.rate,
                    amount=item.amount,
                )
                for item in current_bill.items
            ],
        )
        return self.repository.save_with_next_number(invoice)

    def get_invoice_by_number(self, invoice_number: str) -> Invoice | None:
        return self.repository.get_by_number(invoice_number)

    def search_invoices(
        self,
        search_text: str = "",
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> list[Invoice]:
        if from_date and to_date and from_date > to_date:
            raise InvoiceValidationError("From date cannot be after To date.")
        return self.repository.search(search_text, from_date, to_date)
