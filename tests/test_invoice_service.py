from __future__ import annotations

from decimal import Decimal

import pytest

from app.database.repositories.invoice_repository import InvoiceRepository
from app.database.schema import initialize_database
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.product import Product
from app.services.billing_service import BillingService
from app.services.invoice_service import InvoiceService, InvoiceValidationError
from app.services.product_service import ProductService


def build_bill(database_path, shortcuts: list[int] | None = None) -> BillingService:
    product_service = ProductService(database_path)
    billing_service = BillingService()
    for shortcut in shortcuts or [1]:
        product = product_service.find_active_by_shortcut(shortcut)
        assert product is not None
        billing_service.add_product(product)
    return billing_service


def test_save_invoice_with_one_item(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    billing_service = build_bill(database_path, [1])

    saved = InvoiceService(database_path).save_current_bill(billing_service.current_bill)
    reloaded = InvoiceService(database_path).get_invoice_by_number(saved.invoice_number)

    assert saved.invoice_number == "1"
    assert reloaded is not None
    assert reloaded.total == Decimal("3500")
    assert len(reloaded.items) == 1
    assert reloaded.items[0].product_shortcut == 1
    assert reloaded.items[0].product_name == "Fancy Three Piece"
    assert reloaded.items[0].quantity == 1
    assert reloaded.items[0].rate == Decimal("3500")
    assert reloaded.items[0].amount == Decimal("3500")


def test_save_invoice_with_multiple_items_and_total(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    billing_service = build_bill(database_path, [1, 2])

    saved = InvoiceService(database_path).save_current_bill(billing_service.current_bill)

    assert saved.total == Decimal("6500")
    assert [item.product_shortcut for item in saved.items] == [1, 2]
    assert [item.amount for item in saved.items] == [Decimal("3500"), Decimal("3000")]


def test_invoice_numbers_are_unique_and_sequential(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    service = InvoiceService(database_path)

    first = service.save_current_bill(build_bill(database_path, [1]).current_bill)
    second = service.save_current_bill(build_bill(database_path, [2]).current_bill)

    assert first.invoice_number == "1"
    assert second.invoice_number == "2"


def test_invoice_number_continues_after_service_restart(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)

    first = InvoiceService(database_path).save_current_bill(build_bill(database_path, [1]).current_bill)
    second = InvoiceService(database_path).save_current_bill(build_bill(database_path, [2]).current_bill)

    assert first.invoice_number == "1"
    assert second.invoice_number == "2"


def test_customer_name_and_mobile_are_saved(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    billing_service = build_bill(database_path, [1])
    billing_service.set_customer("Ayesha", "03000000000")

    saved = InvoiceService(database_path).save_current_bill(billing_service.current_bill)

    assert saved.customer_name == "Ayesha"
    assert saved.customer_mobile == "03000000000"


def test_empty_customer_name_and_mobile_are_allowed(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    billing_service = build_bill(database_path, [1])

    saved = InvoiceService(database_path).save_current_bill(billing_service.current_bill)

    assert saved.customer_name is None
    assert saved.customer_mobile is None


def test_invoice_saves_description_and_rate_snapshots(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    billing_service = build_bill(database_path, [1])
    billing_service.update_description(0, "Fancy 3 Piece - Blue")
    billing_service.update_quantity(0, "2")
    billing_service.update_rate(0, "3300")

    saved = InvoiceService(database_path).save_current_bill(billing_service.current_bill)

    assert saved.items[0].product_name == "Fancy 3 Piece - Blue"
    assert saved.items[0].quantity == 2
    assert saved.items[0].rate == Decimal("3300")
    assert saved.items[0].amount == Decimal("6600")
    assert saved.total == Decimal("6600")


def test_master_product_price_remains_unchanged_after_saving_overridden_rate(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    product_service = ProductService(database_path)
    product = product_service.find_active_by_shortcut(1)
    assert product is not None
    billing_service = build_bill(database_path, [1])
    billing_service.update_rate(0, "3300")

    InvoiceService(database_path).save_current_bill(billing_service.current_bill)

    reloaded_product = product_service.get_product(product.id or 0)
    assert reloaded_product is not None
    assert reloaded_product.default_price == Decimal("3500")


def test_empty_bill_cannot_be_saved(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)

    with pytest.raises(InvoiceValidationError, match="empty bill"):
        InvoiceService(database_path).save_current_bill(BillingService().current_bill)

    assert InvoiceRepository(database_path).count() == 0


def test_invoice_and_items_are_saved_atomically(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    bad_invoice = Invoice(
        id=None,
        invoice_number="",
        customer_name=None,
        customer_mobile=None,
        invoice_date="2026-08-09",
        invoice_time="10:00:00",
        total=Decimal("100"),
        items=[
            InvoiceItem(
                id=None,
                invoice_id=None,
                product_id=1,
                product_shortcut=1,
                product_name="Bad Item",
                quantity=0,
                rate=Decimal("100"),
                amount=Decimal("100"),
            )
        ],
    )

    with pytest.raises(Exception):
        InvoiceRepository(database_path).save_with_next_number(bad_invoice)

    assert InvoiceRepository(database_path).count() == 0

    saved = InvoiceService(database_path).save_current_bill(build_bill(database_path, [1]).current_bill)
    assert saved.invoice_number == "1"


def test_failed_save_does_not_destroy_current_bill_state():
    class FailingRepository:
        def count(self):
            return 0

        def save_with_next_number(self, invoice):
            raise RuntimeError("database unavailable")

    billing_service = BillingService()
    billing_service.add_product(
        Product(id=1, shortcut=1, name="Fancy Three Piece", default_price=Decimal("3500"))
    )
    service = InvoiceService(repository=FailingRepository())  # type: ignore[arg-type]

    with pytest.raises(RuntimeError):
        service.save_current_bill(billing_service.current_bill)

    assert len(billing_service.items) == 1
    assert billing_service.total == Decimal("3500")


def test_new_bill_clear_resets_all_current_state():
    billing_service = BillingService()
    billing_service.set_customer("Ayesha", "03000000000")
    billing_service.add_product(
        Product(id=1, shortcut=1, name="Fancy Three Piece", default_price=Decimal("3500"))
    )

    billing_service.clear_bill()

    assert billing_service.current_bill.customer_name == ""
    assert billing_service.current_bill.customer_mobile == ""
    assert billing_service.items == []
    assert billing_service.total == Decimal("0")


def test_total_matches_current_items_after_add_remove_and_edit():
    billing_service = BillingService()
    first = Product(id=1, shortcut=1, name="Fancy Three Piece", default_price=Decimal("3500"))
    second = Product(id=2, shortcut=2, name="Lawn Cotton Three Piece", default_price=Decimal("3000"))

    billing_service.add_product(first)
    billing_service.add_product(second)
    billing_service.add_product(first)
    billing_service.update_quantity(0, "3")
    billing_service.update_rate(1, "2800")
    billing_service.remove_item(0)

    expected_total = sum(item.quantity * item.rate for item in billing_service.items)
    assert billing_service.total == expected_total
