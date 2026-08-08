from __future__ import annotations

from decimal import Decimal

import pytest

from app.database.repositories.product_repository import ProductRepository
from app.database.schema import initialize_database
from app.models.product import Product
from app.services.product_service import ProductService, ProductValidationError


def test_product_insertion_and_retrieval(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    repository = ProductRepository(database_path)

    product_id = repository.add(
        Product(
            id=None,
            shortcut=10,
            name="Test Three Piece",
            default_price=Decimal("2500"),
        )
    )
    product = repository.get_by_shortcut(10)

    assert product_id > 0
    assert product is not None
    assert product.name == "Test Three Piece"
    assert product.default_price == Decimal("2500")
    assert product.active is True


def test_active_products_are_returned_by_shortcut_order(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    repository = ProductRepository(database_path)

    products = repository.list_active()

    assert [product.shortcut for product in products[:4]] == [1, 2, 3, 4]
    assert products[0].name == "Fancy Three Piece"


def test_create_product_with_service(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    service = ProductService(database_path)

    product = service.create_product("5", "Maria B Three Piece", "4000")

    assert product.id is not None
    assert product.shortcut == 5
    assert product.name == "Maria B Three Piece"
    assert product.default_price == Decimal("4000")


def test_update_product_with_service(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    service = ProductService(database_path)
    product = service.create_product("5", "Maria B Three Piece", "4000")

    updated = service.update_product(product.id or 0, "6", "Maria B Two Piece", "3200")

    assert updated.shortcut == 6
    assert updated.name == "Maria B Two Piece"
    assert updated.default_price == Decimal("3200")


def test_disable_product_excludes_it_from_active_products(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    service = ProductService(database_path)
    product = service.create_product("5", "Maria B Three Piece", "4000")

    service.disable_product(product.id or 0)

    assert service.get_product(product.id or 0).active is False
    assert all(item.id != product.id for item in service.list_active_products())
    assert any(item.id == product.id for item in service.list_all_products())


def test_activate_disabled_product_restores_active_status(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    service = ProductService(database_path)
    product = service.create_product("5", "Maria B Three Piece", "4000")

    service.disable_product(product.id or 0)
    service.activate_product(product.id or 0)

    reloaded = service.get_product(product.id or 0)
    assert reloaded is not None
    assert reloaded.active is True
    assert any(item.id == product.id for item in service.list_active_products())


def test_product_data_remains_unchanged_after_disable_and_activate(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    service = ProductService(database_path)
    product = service.create_product("5", "Maria B Three Piece", "4000")

    service.disable_product(product.id or 0)
    service.activate_product(product.id or 0)

    reloaded = service.get_product(product.id or 0)
    assert reloaded is not None
    assert reloaded.id == product.id
    assert reloaded.shortcut == product.shortcut
    assert reloaded.name == product.name
    assert reloaded.default_price == product.default_price


def test_duplicate_active_shortcut_is_rejected(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    service = ProductService(database_path)

    with pytest.raises(ProductValidationError, match="shortcut"):
        service.create_product("1", "Duplicate Shortcut Product", "1000")


def test_empty_product_name_is_rejected(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    service = ProductService(database_path)

    with pytest.raises(ProductValidationError, match="Product name"):
        service.create_product("5", "   ", "1000")


def test_invalid_price_is_rejected(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    service = ProductService(database_path)

    with pytest.raises(ProductValidationError, match="number"):
        service.create_product("5", "Test Product", "abc")


def test_negative_price_is_rejected(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    service = ProductService(database_path)

    with pytest.raises(ProductValidationError, match="negative"):
        service.create_product("5", "Test Product", "-1")


def test_search_products_by_name_and_shortcut(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    service = ProductService(database_path)
    service.create_product("15", "Maria B Three Piece", "4000")

    name_results = service.search_products("Maria")
    shortcut_results = service.search_products("15")

    assert [product.name for product in name_results] == ["Maria B Three Piece"]
    assert [product.shortcut for product in shortcut_results] == [15]


def test_active_disabled_and_all_filters_return_expected_statuses(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    service = ProductService(database_path)
    product = service.create_product("5", "Maria B Three Piece", "4000")

    service.disable_product(product.id or 0)

    active_products = service.search_products("", status_filter="Active")
    disabled_products = service.search_products("", status_filter="Disabled")
    all_products = service.search_products("", status_filter="All")

    assert all(item.active for item in active_products)
    assert all(not item.active for item in disabled_products)
    assert product.id not in {item.id for item in active_products}
    assert product.id in {item.id for item in disabled_products}
    assert product.id in {item.id for item in all_products}
    assert any(item.active for item in all_products)
    assert any(not item.active for item in all_products)


def test_disabled_filter_search_excludes_active_products(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    service = ProductService(database_path)
    active_product = service.create_product("5", "Maria Active Three Piece", "4000")
    disabled_product = service.create_product("6", "Maria Disabled Three Piece", "4100")
    service.disable_product(disabled_product.id or 0)

    results = service.search_products("Maria", status_filter="Disabled")

    assert [product.id for product in results] == [disabled_product.id]
    assert active_product.id not in {product.id for product in results}


def test_all_filter_search_shows_active_and_disabled_products(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    service = ProductService(database_path)
    active_product = service.create_product("5", "Maria Active Three Piece", "4000")
    disabled_product = service.create_product("6", "Maria Disabled Three Piece", "4100")
    service.disable_product(disabled_product.id or 0)

    results = service.search_products("Maria", status_filter="All")
    result_ids = {product.id for product in results}

    assert active_product.id in result_ids
    assert disabled_product.id in result_ids
