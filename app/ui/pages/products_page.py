from __future__ import annotations

from decimal import Decimal

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.models.product import Product
from app.services.product_service import ProductService, ProductValidationError
from app.ui.pages.product_dialog import ProductDialog


class ProductsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.product_service = ProductService()
        self.products: list[Product] = []

        self.title = QLabel("Products & Shortcuts")
        self.title.setObjectName("PageTitle")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products...")
        self.search_input.textChanged.connect(self.refresh_products)

        self.filter_input = QComboBox()
        self.filter_input.addItems(["All", "Active", "Disabled"])
        self.filter_input.setCurrentText("Active")
        self.filter_input.currentTextChanged.connect(self.refresh_products)

        self.add_button = QPushButton("+ Add Product")
        self.edit_button = QPushButton("Edit")
        self.status_button = QPushButton("Disable")

        self.add_button.clicked.connect(self.add_product)
        self.edit_button.clicked.connect(self.edit_selected_product)
        self.status_button.clicked.connect(self.toggle_selected_product_status)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Shortcut", "Product Name", "Default Price", "Status"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.itemSelectionChanged.connect(self.update_action_buttons)
        self.table.itemDoubleClicked.connect(lambda item: self.edit_selected_product())

        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)
        toolbar.addWidget(self.search_input, 1)
        toolbar.addWidget(self.filter_input)

        buttons = QHBoxLayout()
        buttons.setSpacing(12)
        buttons.addWidget(self.add_button)
        buttons.addWidget(self.edit_button)
        buttons.addWidget(self.status_button)
        buttons.addStretch()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 36, 40, 40)
        layout.setSpacing(18)
        layout.addWidget(self.title)
        layout.addLayout(toolbar)
        layout.addWidget(self.table, 1)
        layout.addLayout(buttons)

        self.refresh_products()

    def refresh_products(self) -> None:
        self.products = self.product_service.search_products(
            self.search_input.text(),
            status_filter=self.filter_input.currentText(),
        )
        self.table.setRowCount(0)
        for product in self.products:
            self._add_product_row(product)
        self.update_action_buttons()

    def add_product(self) -> None:
        dialog = ProductDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            self.product_service.create_product(
                dialog.shortcut,
                dialog.product_name,
                dialog.default_price,
            )
        except ProductValidationError as exc:
            self._show_validation_message(str(exc))
            return

        self.refresh_products()
        QMessageBox.information(self, "Product Saved", "Product saved successfully.")

    def edit_selected_product(self) -> None:
        product = self._selected_product()
        if product is None:
            self._show_validation_message("Please select a product first.")
            return

        dialog = ProductDialog(self, product)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            self.product_service.update_product(
                product.id or 0,
                dialog.shortcut,
                dialog.product_name,
                dialog.default_price,
            )
        except ProductValidationError as exc:
            self._show_validation_message(str(exc))
            return

        self.refresh_products()
        QMessageBox.information(self, "Product Saved", "Product saved successfully.")

    def toggle_selected_product_status(self) -> None:
        product = self._selected_product()
        if product is None:
            self._show_validation_message("Please select a product first.")
            return

        action = "Disable" if product.active else "Activate"
        message_box = QMessageBox(self)
        message_box.setWindowTitle(f"{action} Product")
        message_box.setText(f"{action} '{product.name}'?")
        message_box.setIcon(QMessageBox.Icon.Question)
        cancel_button = message_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        action_button = message_box.addButton(action, QMessageBox.ButtonRole.AcceptRole)
        message_box.setDefaultButton(cancel_button)
        message_box.exec()

        if message_box.clickedButton() != action_button:
            return

        try:
            self.product_service.set_product_active(product.id or 0, active=not product.active)
        except ProductValidationError as exc:
            self._show_validation_message(str(exc))
            return

        self.refresh_products()

    def update_action_buttons(self) -> None:
        product = self._selected_product()
        has_selection = product is not None
        self.edit_button.setEnabled(has_selection)
        self.status_button.setEnabled(has_selection)
        self.status_button.setText("Activate" if product is not None and not product.active else "Disable")

    def _add_product_row(self, product: Product) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)

        values = [
            str(product.shortcut),
            product.name,
            self._format_price(product.default_price),
            "Active" if product.active else "Disabled",
        ]
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            item.setData(Qt.ItemDataRole.UserRole, product.id)
            if column in (0, 2, 3):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, column, item)

    def _selected_product(self) -> Product | None:
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        product_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        return next((product for product in self.products if product.id == product_id), None)

    @staticmethod
    def _format_price(price: Decimal) -> str:
        return f"Rs.{price:,.0f}"

    def _show_validation_message(self, message: str) -> None:
        QMessageBox.warning(self, "Please Check", message)
