from __future__ import annotations

from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
)

from app.models.product import Product


class ProductDialog(QDialog):
    def __init__(self, parent=None, product: Product | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Edit Product" if product else "Add Product")
        self.setMinimumWidth(420)

        self.shortcut_input = QLineEdit()
        self.shortcut_input.setPlaceholderText("5")
        self.shortcut_input.setValidator(QIntValidator(0, 999999, self))

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Maria B Three Piece")

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("4000")

        if product is not None:
            self.shortcut_input.setText(str(product.shortcut))
            self.name_input.setText(product.name)
            self.price_input.setText(f"{product.default_price:g}")

        form = QFormLayout()
        form.setLabelAlignment(form.labelAlignment())
        form.setSpacing(14)
        form.addRow("Shortcut:", self.shortcut_input)
        form.addRow("Product Name:", self.name_input)
        form.addRow("Default Price:", self.price_input)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Save
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        layout.addLayout(form)
        layout.addWidget(self.buttons)

    @property
    def shortcut(self) -> str:
        return self.shortcut_input.text()

    @property
    def product_name(self) -> str:
        return self.name_input.text()

    @property
    def default_price(self) -> str:
        return self.price_input.text()
