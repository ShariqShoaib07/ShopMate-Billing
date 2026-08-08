from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from app.database.connection import get_connection
from app.models.product import Product
from app.models.shop_settings import ShopSettings


EXAMPLE_SHOP_SETTINGS = ShopSettings(
    id=None,
    shop_name="Maha's Collection",
    address="Shop #4 Street #39 Madina Bazar\nMustafaabad Dharampura Lahore",
    phone_1="0321-8499801",
    phone_2="0324-8436410",
)

EXAMPLE_PRODUCTS = [
    Product(id=None, shortcut=1, name="Fancy Three Piece", default_price=Decimal("3500")),
    Product(id=None, shortcut=2, name="Lawn Cotton Three Piece", default_price=Decimal("3000")),
    Product(id=None, shortcut=3, name="Bin Saeed Three Piece", default_price=Decimal("4500")),
    Product(id=None, shortcut=4, name="Bin Saeed Two Piece", default_price=Decimal("3500")),
]


def seed_initial_data(database_path: Path | None = None) -> None:
    with get_connection(database_path) as connection:
        settings_count = connection.execute("SELECT COUNT(*) FROM shop_settings").fetchone()[0]
        if settings_count == 0:
            connection.execute(
                """
                INSERT INTO shop_settings (shop_name, address, phone_1, phone_2)
                VALUES (?, ?, ?, ?)
                """,
                (
                    EXAMPLE_SHOP_SETTINGS.shop_name,
                    EXAMPLE_SHOP_SETTINGS.address,
                    EXAMPLE_SHOP_SETTINGS.phone_1,
                    EXAMPLE_SHOP_SETTINGS.phone_2,
                ),
            )

        products_count = connection.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if products_count == 0:
            connection.executemany(
                """
                INSERT INTO products (shortcut, name, default_price, active)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (
                        product.shortcut,
                        product.name,
                        str(product.default_price),
                        int(product.active),
                    )
                    for product in EXAMPLE_PRODUCTS
                ],
            )
