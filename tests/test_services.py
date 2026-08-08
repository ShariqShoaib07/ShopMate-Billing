from __future__ import annotations

import pytest

from app.database.repositories.settings_repository import SettingsRepository
from app.database.schema import initialize_database
from app.services.backup_service import BackupService
from app.services.print_service import PrintJob, PrintService
from app.services.product_service import ProductService


def test_shop_settings_retrieval(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)

    shop_settings = SettingsRepository(database_path).get_shop_settings()

    assert shop_settings is not None
    assert shop_settings.shop_name == "Maha's Collection"
    assert "Madina Bazar" in shop_settings.address


def test_product_service_retrieves_seed_product(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)

    product = ProductService(database_path).find_by_shortcut(2)

    assert product is not None
    assert product.name == "Lawn Cotton Three Piece"


def test_print_service_has_no_real_printer_dependency():
    service = PrintService()
    job = PrintJob(title="Preview", content="Receipt preview text")

    assert service.preview_receipt(job) == "Receipt preview text"
    with pytest.raises(NotImplementedError):
        service.print_receipt(job)


def test_backup_service_creates_sqlite_backup(tmp_path):
    database_path = tmp_path / "test_pos.db"
    backup_dir = tmp_path / "backups"
    initialize_database(database_path)

    backup_path = BackupService(database_path, backup_dir).backup_database()

    assert backup_path.exists()
    assert backup_path.parent == backup_dir
