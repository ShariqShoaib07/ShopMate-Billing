from __future__ import annotations

from decimal import Decimal

import pytest

from app.models.product import Product
from app.database.schema import initialize_database
from app.services.billing_service import BillingService, BillingValidationError
from app.services.product_service import ProductService


def make_product(
    product_id: int = 1,
    shortcut: int = 1,
    name: str = "Fancy Three Piece",
    price: str = "3500",
    active: bool = True,
) -> Product:
    return Product(
        id=product_id,
        shortcut=shortcut,
        name=name,
        default_price=Decimal(price),
        active=active,
    )


def test_empty_bill_total_is_zero():
    service = BillingService()

    assert service.total == Decimal("0")


def test_adding_one_product_creates_one_item_with_defaults():
    service = BillingService()
    product = make_product()

    service.add_product(product)

    assert len(service.items) == 1
    assert service.items[0].quantity == 1
    assert service.items[0].rate == Decimal("3500")
    assert service.items[0].amount == Decimal("3500")
    assert service.total == Decimal("3500")


def test_add_product_by_shortcut():
    service = BillingService()

    service.add_product_by_shortcut("1", [make_product()])

    assert len(service.items) == 1
    assert service.items[0].product_name == "Fancy Three Piece"


def test_add_multiple_products_by_shortcut():
    service = BillingService()
    products = [
        make_product(),
        make_product(2, 2, "Lawn Cotton Three Piece", "3000"),
    ]

    service.add_product_by_shortcut("1", products)
    service.add_product_by_shortcut("2", products)

    assert [item.shortcut for item in service.items] == [1, 2]
    assert service.total == Decimal("6500")


def test_quantity_changes_update_amount_and_total():
    service = BillingService()
    service.add_product(make_product())

    service.update_quantity(0, "3")

    assert service.items[0].quantity == 3
    assert service.items[0].amount == Decimal("10500")
    assert service.total == Decimal("10500")


def test_rate_changes_update_amount_and_do_not_change_product_default_price():
    service = BillingService()
    product = make_product()
    service.add_product(product)

    service.update_rate(0, "3300")

    assert service.items[0].rate == Decimal("3300")
    assert service.items[0].amount == Decimal("3300")
    assert product.default_price == Decimal("3500")


def test_database_product_price_remains_unchanged_after_bill_rate_edit(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    product_service = ProductService(database_path)
    product = product_service.find_active_by_shortcut(1)
    assert product is not None

    billing_service = BillingService()
    billing_service.add_product(product)
    billing_service.update_rate(0, "3300")

    reloaded_product = product_service.get_product(product.id or 0)
    assert reloaded_product is not None
    assert reloaded_product.default_price == Decimal("3500")


def test_description_changes_only_current_bill_line():
    service = BillingService()
    product = make_product()
    service.add_product(product)

    service.update_description(0, "Fancy 3 Piece - Blue")

    assert service.items[0].product_name == "Fancy 3 Piece - Blue"
    assert product.name == "Fancy Three Piece"
    assert service.total == Decimal("3500")


def test_removing_item_updates_total():
    service = BillingService()
    service.add_product(make_product())
    service.add_product(make_product(2, 3, "Bin Saeed Three Piece", "4500"))

    service.remove_item(0)

    assert len(service.items) == 1
    assert service.total == Decimal("4500")


def test_clearing_bill_removes_items_and_customer_information():
    service = BillingService()
    service.set_customer("Ayesha", "03000000000")
    service.add_product(make_product())

    service.clear_bill()

    assert service.items == []
    assert service.total == Decimal("0")
    assert service.current_bill.customer_name == ""
    assert service.current_bill.customer_mobile == ""


def test_adding_same_product_with_same_rate_increments_quantity():
    service = BillingService()
    product = make_product()

    service.add_product(product)
    service.add_product(product)

    assert len(service.items) == 1
    assert service.items[0].quantity == 2
    assert service.items[0].amount == Decimal("7000")


def test_adding_same_product_after_rate_change_creates_separate_line():
    service = BillingService()
    product = make_product()

    service.add_product(product)
    service.update_rate(0, "3300")
    service.add_product(product)

    assert len(service.items) == 2
    assert service.items[0].rate == Decimal("3300")
    assert service.items[1].rate == Decimal("3500")
    assert service.total == Decimal("6800")


def test_disabled_product_cannot_be_added_by_shortcut():
    service = BillingService()
    disabled_product = make_product(active=False)

    with pytest.raises(BillingValidationError):
        service.add_product_by_shortcut("1", [disabled_product])


def test_disabled_database_product_cannot_be_found_for_billing_shortcut(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    product_service = ProductService(database_path)
    product = product_service.find_active_by_shortcut(1)
    assert product is not None

    product_service.disable_product(product.id or 0)

    assert product_service.find_active_by_shortcut(1) is None


@pytest.mark.parametrize("quantity", ["", "abc", "1.5", "0", "-1"])
def test_invalid_quantity_is_rejected(quantity):
    service = BillingService()
    service.add_product(make_product())

    with pytest.raises(BillingValidationError):
        service.update_quantity(0, quantity)


@pytest.mark.parametrize("rate", ["", "abc", "-1"])
def test_invalid_rate_is_rejected(rate):
    service = BillingService()
    service.add_product(make_product())

    with pytest.raises(BillingValidationError):
        service.update_rate(0, rate)
