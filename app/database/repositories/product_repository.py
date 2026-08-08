from __future__ import annotations

import sqlite3
from decimal import Decimal
from pathlib import Path

from app.database.connection import get_connection
from app.models.product import Product


class ProductRepository:
    def __init__(self, database_path: Path | None = None) -> None:
        self.database_path = database_path

    def add(self, product: Product) -> int:
        with get_connection(self.database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO products (shortcut, name, default_price, active)
                VALUES (?, ?, ?, ?)
                """,
                (
                    product.shortcut,
                    product.name,
                    str(product.default_price),
                    int(product.active),
                ),
            )
            return int(cursor.lastrowid)

    def update(self, product: Product) -> None:
        if product.id is None:
            raise ValueError("Product id is required for updates.")

        with get_connection(self.database_path) as connection:
            connection.execute(
                """
                UPDATE products
                SET shortcut = ?,
                    name = ?,
                    default_price = ?,
                    active = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    product.shortcut,
                    product.name,
                    str(product.default_price),
                    int(product.active),
                    product.id,
                ),
            )

    def set_active(self, product_id: int, active: bool) -> None:
        with get_connection(self.database_path) as connection:
            connection.execute(
                """
                UPDATE products
                SET active = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (int(active), product_id),
            )

    def disable(self, product_id: int) -> None:
        self.set_active(product_id, False)

    def activate(self, product_id: int) -> None:
        self.set_active(product_id, True)

    def list_all(self) -> list[Product]:
        with get_connection(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT id, shortcut, name, default_price, active, created_at, updated_at
                FROM products
                ORDER BY active DESC, shortcut
                """
            ).fetchall()
        return [self._row_to_product(row) for row in rows]

    def list_active(self) -> list[Product]:
        with get_connection(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT id, shortcut, name, default_price, active, created_at, updated_at
                FROM products
                WHERE active = 1
                ORDER BY shortcut
                """
            ).fetchall()
        return [self._row_to_product(row) for row in rows]

    def list_disabled(self) -> list[Product]:
        with get_connection(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT id, shortcut, name, default_price, active, created_at, updated_at
                FROM products
                WHERE active = 0
                ORDER BY shortcut
                """
            ).fetchall()
        return [self._row_to_product(row) for row in rows]

    def get_by_id(self, product_id: int) -> Product | None:
        with get_connection(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT id, shortcut, name, default_price, active, created_at, updated_at
                FROM products
                WHERE id = ?
                """,
                (product_id,),
            ).fetchone()
        return self._row_to_product(row) if row else None

    def get_by_shortcut(self, shortcut: int) -> Product | None:
        with get_connection(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT id, shortcut, name, default_price, active, created_at, updated_at
                FROM products
                WHERE shortcut = ?
                """,
                (shortcut,),
            ).fetchone()
        return self._row_to_product(row) if row else None

    def get_active_by_shortcut(self, shortcut: int) -> Product | None:
        with get_connection(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT id, shortcut, name, default_price, active, created_at, updated_at
                FROM products
                WHERE shortcut = ? AND active = 1
                """,
                (shortcut,),
            ).fetchone()
        return self._row_to_product(row) if row else None

    def search(self, search_text: str, active: bool | None = True) -> list[Product]:
        pattern = f"%{search_text.strip()}%"
        active_filter = ""
        parameters: tuple[object, ...] = (pattern, pattern)
        if active is not None:
            active_filter = "AND active = ?"
            parameters = (pattern, pattern, int(active))

        with get_connection(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT id, shortcut, name, default_price, active, created_at, updated_at
                FROM products
                WHERE (name LIKE ? OR CAST(shortcut AS TEXT) LIKE ?)
                """ + active_filter + """
                ORDER BY active DESC, shortcut
                """,
                parameters,
            ).fetchall()
        return [self._row_to_product(row) for row in rows]

    @staticmethod
    def _row_to_product(row: sqlite3.Row) -> Product:
        return Product(
            id=int(row["id"]),
            shortcut=int(row["shortcut"]),
            name=str(row["name"]),
            default_price=Decimal(str(row["default_price"])),
            active=bool(row["active"]),
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
        )
