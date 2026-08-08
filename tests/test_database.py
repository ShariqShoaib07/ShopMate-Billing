from __future__ import annotations

import sqlite3
from contextlib import closing

from app.database.schema import initialize_database


def test_database_initialization_creates_required_tables(tmp_path):
    database_path = tmp_path / "test_pos.db"

    initialize_database(database_path)

    with closing(sqlite3.connect(database_path)) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

    assert "products" in tables
    assert "shop_settings" in tables
    assert "invoices" in tables
    assert "invoice_items" in tables


def test_database_initialization_seeds_example_data(tmp_path):
    database_path = tmp_path / "test_pos.db"

    initialize_database(database_path)

    with closing(sqlite3.connect(database_path)) as connection:
        product_count = connection.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        settings_count = connection.execute("SELECT COUNT(*) FROM shop_settings").fetchone()[0]

    assert product_count == 4
    assert settings_count == 1
