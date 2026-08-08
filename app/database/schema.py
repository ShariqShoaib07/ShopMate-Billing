from __future__ import annotations

from pathlib import Path

from app.database.connection import get_connection
from app.database.seed import seed_initial_data


CREATE_PRODUCTS_TABLE = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shortcut INTEGER NOT NULL UNIQUE,
    name TEXT NOT NULL,
    default_price NUMERIC NOT NULL CHECK(default_price >= 0),
    active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_SHOP_SETTINGS_TABLE = """
CREATE TABLE IF NOT EXISTS shop_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shop_name TEXT NOT NULL,
    address TEXT NOT NULL,
    phone_1 TEXT NOT NULL,
    phone_2 TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_INVOICES_TABLE = """
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT NOT NULL UNIQUE,
    customer_name TEXT,
    customer_mobile TEXT,
    invoice_date TEXT NOT NULL,
    invoice_time TEXT NOT NULL,
    total NUMERIC NOT NULL CHECK(total >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_INVOICE_ITEMS_TABLE = """
CREATE TABLE IF NOT EXISTS invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    product_id INTEGER,
    product_shortcut INTEGER NOT NULL DEFAULT 0,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    rate NUMERIC NOT NULL CHECK(rate >= 0),
    amount NUMERIC NOT NULL CHECK(amount >= 0),
    FOREIGN KEY(invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
    FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE SET NULL
);
"""


def create_schema(database_path: Path | None = None) -> None:
    with get_connection(database_path) as connection:
        connection.executescript(
            "\n".join(
                [
                    CREATE_PRODUCTS_TABLE,
                    CREATE_SHOP_SETTINGS_TABLE,
                    CREATE_INVOICES_TABLE,
                    CREATE_INVOICE_ITEMS_TABLE,
                ]
            )
        )
        _run_migrations(connection)


def _run_migrations(connection) -> None:
    invoice_item_columns = {
        row["name"] for row in connection.execute("PRAGMA table_info(invoice_items)").fetchall()
    }
    if "product_shortcut" not in invoice_item_columns:
        connection.execute(
            "ALTER TABLE invoice_items ADD COLUMN product_shortcut INTEGER NOT NULL DEFAULT 0"
        )


def initialize_database(database_path: Path | None = None) -> None:
    """Create the database schema and insert first-run example data."""
    create_schema(database_path)
    seed_initial_data(database_path)
