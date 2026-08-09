from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QTextBrowser, QVBoxLayout

from app.models.receipt import Receipt
from app.services.receipt_service import ReceiptService


class ReceiptPreviewDialog(QDialog):
    def __init__(self, receipt: Receipt, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Receipt Preview - Invoice #{receipt.invoice_number}")
        self.setMinimumSize(440, 640)

        self.browser = QTextBrowser()
        self.browser.setObjectName("ReceiptPreviewBrowser")
        self.browser.setOpenExternalLinks(False)
        self.browser.setHtml(ReceiptService().render_html(receipt))

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(self.browser)
        layout.addWidget(buttons)