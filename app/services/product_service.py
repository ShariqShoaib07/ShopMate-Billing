from __future__ import annotations

import sqlite3
from decimal import Decimal, InvalidOperation
from pathlib import Path

from app.database.repositories.product_repository import ProductRepository
from app.models.product import Product


class ProductValidationError(ValueError):
    """Raised when product data cannot be saved."""


class ProductService:
    def __init__(self, database_path: Path | None = None) -> None:
        self.repository = ProductRepository(database_path)

    def list_active_products(self) -> list[Product]:
        return self.repository.list_active()

    def list_disabled_products(self) -> list[Product]:
        return self.repository.list_disabled()

    def list_all_products(self) -> list[Product]:
        return self.repository.list_all()

    def get_product(self, product_id: int) -> Product | None:
        return self.repository.get_by_id(product_id)

    def find_by_shortcut(self, shortcut: int) -> Product | None:
        return self.repository.get_by_shortcut(shortcut)

    def find_active_by_shortcut(self, shortcut: int) -> Product | None:
        return self.repository.get_active_by_shortcut(shortcut)

    def create_product(self, shortcut: str, name: str, default_price: str) -> Product:
        clean_shortcut = self._validate_shortcut(shortcut)
        clean_name = self._validate_name(name)
        clean_price = self._validate_price(default_price)
        self._validate_unique_active_shortcut(clean_shortcut)

        try:
            product_id = self.repository.add(
                Product(
                    id=None,
                    shortcut=clean_shortcut,
                    name=clean_name,
                    default_price=clean_price,
                    active=True,
                )
            )
        except sqlite3.IntegrityError as exc:
            raise ProductValidationError("This shortcut is already used by another product.") from exc

        product = self.repository.get_by_id(product_id)
        if product is None:
            raise RuntimeError("Product was saved but could not be loaded.")
        return product

    def update_product(
        self,
        product_id: int,
        shortcut: str,
        name: str,
        default_price: str,
    ) -> Product:
        existing = self.repository.get_by_id(product_id)
        if existing is None:
            raise ProductValidationError("Please select a valid product.")

        clean_shortcut = self._validate_shortcut(shortcut)
        clean_name = self._validate_name(name)
        clean_price = self._validate_price(default_price)
        self._validate_unique_active_shortcut(clean_shortcut, ignore_product_id=product_id)

        updated = Product(
            id=existing.id,
            shortcut=clean_shortcut,
            name=clean_name,
            default_price=clean_price,
            active=existing.active,
            created_at=existing.created_at,
            updated_at=existing.updated_at,
        )
        try:
            self.repository.update(updated)
        except sqlite3.IntegrityError as exc:
            raise ProductValidationError("This shortcut is already used by another product.") from exc

        product = self.repository.get_by_id(product_id)
        if product is None:
            raise RuntimeError("Product was updated but could not be loaded.")
        return product

    def disable_product(self, product_id: int) -> None:
        product = self.repository.get_by_id(product_id)
        if product is None:
            raise ProductValidationError("Please select a valid product.")
        if not product.active:
            raise ProductValidationError("This product is already disabled.")
        self.repository.disable(product_id)

    def activate_product(self, product_id: int) -> None:
        product = self.repository.get_by_id(product_id)
        if product is None:
            raise ProductValidationError("Please select a valid product.")
        if product.active:
            raise ProductValidationError("This product is already active.")
        self._validate_unique_active_shortcut(product.shortcut, ignore_product_id=product_id)
        self.repository.activate(product_id)

    def set_product_active(self, product_id: int, active: bool) -> None:
        if active:
            self.activate_product(product_id)
        else:
            self.disable_product(product_id)

    def search_products(self, search_text: str, status_filter: str = "Active") -> list[Product]:
        normalized_filter = status_filter.strip().lower()
        if search_text.strip():
            if normalized_filter == "all":
                return self.repository.search(search_text, active=None)
            if normalized_filter == "disabled":
                return self.repository.search(search_text, active=False)
            return self.repository.search(search_text, active=True)

        if normalized_filter == "all":
            return self.list_all_products()
        if normalized_filter == "disabled":
            return self.list_disabled_products()
        return self.list_active_products()

    def _validate_unique_active_shortcut(
        self,
        shortcut: int,
        ignore_product_id: int | None = None,
    ) -> None:
        existing = self.repository.get_active_by_shortcut(shortcut)
        if existing is not None and existing.id != ignore_product_id:
            raise ProductValidationError("This shortcut is already used by an active product.")

    @staticmethod
    def _validate_shortcut(shortcut: str) -> int:
        value = shortcut.strip()
        if not value:
            raise ProductValidationError("Shortcut is required.")
        if not value.isdigit():
            raise ProductValidationError("Shortcut must be a whole number.")
        return int(value)

    @staticmethod
    def _validate_name(name: str) -> str:
        value = name.strip()
        if not value:
            raise ProductValidationError("Product name is required.")
        return value

    @staticmethod
    def _validate_price(default_price: str) -> Decimal:
        value = default_price.strip()
        if not value:
            raise ProductValidationError("Default price is required.")
        try:
            price = Decimal(value)
        except InvalidOperation as exc:
            raise ProductValidationError("Default price must be a number.") from exc
        if price < 0:
            raise ProductValidationError("Default price cannot be negative.")
        return price
