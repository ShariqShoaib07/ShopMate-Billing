from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.config.settings import settings
from app.utils.paths import ensure_directory


def connect(database_path: Path | None = None) -> sqlite3.Connection:
    """Create a SQLite connection with project defaults enabled."""
    path = database_path or settings.database_path
    ensure_directory(path.parent)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def get_connection(database_path: Path | None = None) -> Iterator[sqlite3.Connection]:
    connection = connect(database_path)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
