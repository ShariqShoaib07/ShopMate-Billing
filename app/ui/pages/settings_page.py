from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.settings_service import SettingsService, ShopSettingsValidationError


class SettingsPage(QWidget):
    manage_products_requested = Signal()

    def __init__(self, settings_service: SettingsService | None = None) -> None:
        super().__init__()
        self.settings_service = settings_service or SettingsService()

        self.title = QLabel("Settings")
        self.title.setObjectName("PageTitle")

        self.subtitle = QLabel("Update the shop information used throughout the application.")
        self.subtitle.setObjectName("PageMessage")
        self.subtitle.setWordWrap(True)

        self.shop_name_input = QLineEdit()
        self.shop_name_input.setPlaceholderText("Maha's Collection")

        self.address_input = QPlainTextEdit()
        self.address_input.setPlaceholderText("Shop #4 Street #39 Madina Bazar\nMustafaabad Dharampura Lahore")
        self.address_input.setFixedHeight(104)

        self.phone_1_input = QLineEdit()
        self.phone_1_input.setPlaceholderText("0321-8499801")

        self.phone_2_input = QLineEdit()
        self.phone_2_input.setPlaceholderText("0324-8436410")

        self.save_button = QPushButton("Save Settings")
        self.manage_products_button = QPushButton("Manage Products")

        self.save_button.clicked.connect(self.save_settings)
        self.manage_products_button.clicked.connect(self.manage_products_requested.emit)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(12)
        form.addRow("Shop Name:", self.shop_name_input)
        form.addRow("Address:", self.address_input)
        form.addRow("Phone 1:", self.phone_1_input)
        form.addRow("Phone 2:", self.phone_2_input)

        actions = QHBoxLayout()
        actions.setSpacing(12)
        actions.addWidget(self.manage_products_button)
        actions.addStretch()
        actions.addWidget(self.save_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 36, 40, 40)
        layout.setSpacing(16)
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addLayout(form)
        layout.addLayout(actions)
        layout.addStretch()

        self.load_settings()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.load_settings()

    def load_settings(self) -> None:
        settings = self.settings_service.get_shop_settings()
        if settings is None:
            self.shop_name_input.clear()
            self.address_input.clear()
            self.phone_1_input.clear()
            self.phone_2_input.clear()
            return

        self.shop_name_input.setText(settings.shop_name)
        self.address_input.setPlainText(settings.address)
        self.phone_1_input.setText(settings.phone_1)
        self.phone_2_input.setText(settings.phone_2)

    def save_settings(self) -> None:
        try:
            saved_settings = self.settings_service.save_shop_settings(
                self.shop_name_input.text(),
                self.address_input.toPlainText(),
                self.phone_1_input.text(),
                self.phone_2_input.text(),
            )
        except ShopSettingsValidationError as exc:
            QMessageBox.warning(self, "Please Check", str(exc))
            return
        except Exception as exc:
            QMessageBox.critical(self, "Save Failed", f"Shop settings could not be saved.\n\n{exc}")
            return

        self.shop_name_input.setText(saved_settings.shop_name)
        self.address_input.setPlainText(saved_settings.address)
        self.phone_1_input.setText(saved_settings.phone_1)
        self.phone_2_input.setText(saved_settings.phone_2)
        QMessageBox.information(self, "Settings Saved", "Shop settings saved successfully.")
