from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from app.config.settings import settings
from app.database.connection import connect
from app.utils.paths import ensure_directory


class BackupService:
    def __init__(self, database_path: Path | None = None, backup_dir: Path | None = None) -> None:
        self.database_path = database_path or settings.database_path
        self.backup_dir = backup_dir or settings.backup_dir

    def backup_database(self) -> Path:
        """Create a consistent SQLite backup and return its file path."""
        ensure_directory(self.backup_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"ladies_billing_pos_backup_{timestamp}.db"

        source = connect(self.database_path)
        try:
            destination = sqlite3.connect(backup_path)
            try:
                source.backup(destination)
            finally:
                destination.close()
        finally:
            source.close()

        return backup_path

    def restore_database(self, backup_path: Path) -> None:
        raise NotImplementedError("Database restore will be implemented with confirmation UI later.")
