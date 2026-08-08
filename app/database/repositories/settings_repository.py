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

    def save_shop_settings(self, shop_settings: ShopSettings) -> ShopSettings:
        with get_connection(self.database_path) as connection:
            existing = connection.execute(
                """
                SELECT id
                FROM shop_settings
                ORDER BY id
                LIMIT 1
                """
            ).fetchone()
            if existing is not None:
                settings_id = int(existing["id"])
                connection.execute(
                    """
                    UPDATE shop_settings
                    SET shop_name = ?, address = ?, phone_1 = ?, phone_2 = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        shop_settings.shop_name,
                        shop_settings.address,
                        shop_settings.phone_1,
                        shop_settings.phone_2,
                        settings_id,
                    ),
                )
            else:
                cursor = connection.execute(
                    """
                    INSERT INTO shop_settings (shop_name, address, phone_1, phone_2)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        shop_settings.shop_name,
                        shop_settings.address,
                        shop_settings.phone_1,
                        shop_settings.phone_2,
                    ),
                )
                settings_id = int(cursor.lastrowid)

            row = connection.execute(
                """
                SELECT id, shop_name, address, phone_1, phone_2, created_at, updated_at
                FROM shop_settings
                WHERE id = ?
                """,
                (settings_id,),
            ).fetchone()

        if row is None:
            raise RuntimeError("Shop settings were saved but could not be reloaded.")
        return self._row_to_settings(row)

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
