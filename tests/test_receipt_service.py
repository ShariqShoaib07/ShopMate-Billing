from __future__ import annotations

from decimal import Decimal

from app.database.repositories.settings_repository import SettingsRepository
from app.database.schema import initialize_database
from app.services.billing_service import BillingService
from app.services.invoice_service import InvoiceService
from app.services.product_service import ProductService
from app.services.receipt_service import ReceiptService
from app.services.settings_service import SettingsService
from app.utils.number_words import rupees_in_words


def _saved_invoice(database_path, shortcut: int = 1, quantity: str | None = None, rate: str | None = None):
    product_service = ProductService(database_path)
    product = product_service.find_active_by_shortcut(shortcut)
    assert product is not None

    billing = BillingService()
    billing.add_product(product)
    if quantity is not None:
        billing.update_quantity(0, quantity)
    if rate is not None:
        billing.update_rate(0, rate)

    return InvoiceService(database_path).save_current_bill(billing.current_bill)


def test_receipt_uses_saved_invoice_and_shop_settings(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    SettingsService(database_path).save_shop_settings(
        "Test Collection",
        "Test Address",
        "111",
        "222",
    )
    saved = _saved_invoice(database_path, quantity="2", rate="3300")

    receipt = ReceiptService(database_path).build_receipt(saved)

    assert receipt.shop_name == "Test Collection"
    assert receipt.address == "Test Address"
    assert receipt.phone_1 == "111"
    assert receipt.phone_2 == "222"
    assert receipt.invoice_number == saved.invoice_number
    assert receipt.invoice_date == "09-08-2026"
    assert receipt.invoice_time == saved.invoice_time[:5]
    assert receipt.customer_name is None
    assert receipt.customer_mobile is None
    assert receipt.items[0].quantity == 2
    assert receipt.items[0].rate == Decimal("3300")
    assert receipt.items[0].amount == Decimal("6600")
    assert receipt.total == Decimal("6600")


def test_receipt_preserves_historical_price_after_product_change(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    saved = _saved_invoice(database_path, quantity="1", rate="3500")

    product_service = ProductService(database_path)
    product = product_service.find_active_by_shortcut(1)
    assert product is not None
    product_service.update_product(product.id or 0, "1", product.name, "3000")

    receipt = ReceiptService(database_path).build_receipt(saved)

    assert receipt.items[0].rate == Decimal("3500")
    assert receipt.items[0].amount == Decimal("3500")


def test_receipt_html_includes_footer_and_items(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    saved = _saved_invoice(database_path, quantity="2")

    receipt = ReceiptService(database_path).build_receipt(saved)
    html = ReceiptService(database_path).render_html(receipt)

    assert "Thank you for shopping with us!" in html
    assert saved.invoice_number in html
    assert "Qty" in html
    assert "Amount" in html


def test_rupees_in_words_supports_zero_and_large_numbers():
    assert rupees_in_words(0) == "Zero Rupees Only"
    assert rupees_in_words(1000) == "One Thousand Rupees Only"
    assert rupees_in_words(12500) == "Twelve Thousand Five Hundred Rupees Only"
    assert rupees_in_words(100000) == "One Lakh Rupees Only"
    assert rupees_in_words(1000000) == "Ten Lakh Rupees Only"
    assert rupees_in_words(10000000) == "One Crore Rupees Only"