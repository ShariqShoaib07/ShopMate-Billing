from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.utils.paths import project_root


@dataclass(frozen=True)
class AppSettings:
    app_name: str = "Ladies Billing POS"
    database_filename: str = "ladies_billing_pos.db"

    @property
    def data_dir(self) -> Path:
        return project_root() / "data"

    @property
    def backup_dir(self) -> Path:
        return project_root() / "backups"

    @property
    def database_path(self) -> Path:
        return self.data_dir / self.database_filename


settings = AppSettings()
