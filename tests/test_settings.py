from __future__ import annotations

from PySide6.QtWidgets import QApplication

from app.database.repositories.settings_repository import SettingsRepository
from app.database.schema import initialize_database
from app.services.settings_service import SettingsService
from app.ui.main_window import MainWindow
from app.ui.pages.billing_page import BillingPage
from app.ui.pages.settings_page import SettingsPage


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_settings_page_loads_saved_shop_settings(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    service = SettingsService(database_path)
    service.save_shop_settings("Al-Noor Collection", "Blue Area\nIslamabad", "111-111", "222-222")

    app = _app()
    page = SettingsPage(service)

    assert page.shop_name_input.text() == "Al-Noor Collection"
    assert page.address_input.toPlainText() == "Blue Area\nIslamabad"
    assert page.phone_1_input.text() == "111-111"
    assert page.phone_2_input.text() == "222-222"


def test_settings_service_updates_and_persists_shop_settings(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    service = SettingsService(database_path)

    saved = service.save_shop_settings(
        "Al-Noor Collection",
        "Blue Area\nIslamabad",
        "111-111",
        "222-222",
    )

    reloaded = SettingsRepository(database_path).get_shop_settings()

    assert saved.shop_name == "Al-Noor Collection"
    assert saved.address == "Blue Area\nIslamabad"
    assert reloaded is not None
    assert reloaded.shop_name == "Al-Noor Collection"
    assert reloaded.address == "Blue Area\nIslamabad"
    assert reloaded.phone_1 == "111-111"
    assert reloaded.phone_2 == "222-222"


def test_initialize_database_preserves_saved_shop_settings(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    service = SettingsService(database_path)
    service.save_shop_settings("Al-Noor Collection", "Blue Area", "111-111", "222-222")

    initialize_database(database_path)

    reloaded = SettingsRepository(database_path).get_shop_settings()

    assert reloaded is not None
    assert reloaded.shop_name == "Al-Noor Collection"
    assert reloaded.address == "Blue Area"
    assert reloaded.phone_1 == "111-111"
    assert reloaded.phone_2 == "222-222"
    assert (
        SettingsRepository(database_path).get_shop_settings() is not None
    )


def test_billing_page_uses_saved_shop_name(tmp_path):
    database_path = tmp_path / "test_pos.db"
    initialize_database(database_path)
    SettingsService(database_path).save_shop_settings(
        "Al-Noor Collection",
        "Blue Area",
        "111-111",
        "222-222",
    )

    app = _app()
    page = BillingPage(settings_repository=SettingsRepository(database_path))

    assert page.shop_name_label.text() == "Al-Noor Collection"


def test_settings_can_open_products_page_via_signal():
    app = _app()
    window = MainWindow()
    settings_page = window.pages.widget(3)

    settings_page.manage_products_requested.emit()

    assert window.current_page_index == 2