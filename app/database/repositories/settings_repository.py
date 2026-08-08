from __future__ import annotations

import sqlite3
from pathlib import Path

from app.database.connection import get_connection
from app.models.shop_settings import ShopSettings


class SettingsRepository:
    def __init__(self, database_path: Path | None = None) -> None:
        self.database_path = database_path

    def get_shop_settings(self) -> ShopSettings | None:
        with get_connection(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT id, shop_name, address, phone_1, phone_2, created_at, updated_at
                FROM shop_settings
                ORDER BY id
                LIMIT 1
                """
            ).fetchone()
        return self._row_to_settings(row) if row else None

    @staticmethod
    def _row_to_settings(row: sqlite3.Row) -> ShopSettings:
        return ShopSettings(
            id=int(row["id"]),
            shop_name=str(row["shop_name"]),
            address=str(row["address"]),
            phone_1=str(row["phone_1"]),
            phone_2=str(row["phone_2"]),
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
        )
