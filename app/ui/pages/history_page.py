from __future__ import annotations

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
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

from app.models.invoice import Invoice
from app.services.invoice_service import InvoiceService, InvoiceValidationError
from app.services.receipt_service import ReceiptService
from app.utils.currency import format_rupees
from app.ui.pages.receipt_preview_dialog import ReceiptPreviewDialog


class HistoryPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.invoice_service = InvoiceService()
        self.receipt_service = ReceiptService()
        self.invoices: list[Invoice] = []

        title = QLabel("Sales History")
        title.setObjectName("PageTitle")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search invoices...")
        self.search_input.textChanged.connect(self.refresh_invoices)

        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDisplayFormat("yyyy-MM-dd")
        self.from_date.setSpecialValueText("From Date")
        self.from_date.setMinimumDate(QDate(2000, 1, 1))
        self.from_date.setDate(self.from_date.minimumDate())
        self.from_date.dateChanged.connect(self.refresh_invoices)

        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDisplayFormat("yyyy-MM-dd")
        self.to_date.setSpecialValueText("To Date")
        self.to_date.setMinimumDate(QDate(2000, 1, 1))
        self.to_date.setDate(self.to_date.minimumDate())
        self.to_date.dateChanged.connect(self.refresh_invoices)

        clear_button = QPushButton("Clear Filters")
        clear_button.clicked.connect(self.clear_filters)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Invoice #", "Date", "Time", "Customer", "Mobile", "Total"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.itemSelectionChanged.connect(self.update_buttons)
        self.table.itemDoubleClicked.connect(lambda item: self.view_details())

        self.empty_label = QLabel("")
        self.empty_label.setObjectName("PageMessage")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.view_button = QPushButton("View Details")
        self.reprint_button = QPushButton("Preview Receipt")
        self.view_button.clicked.connect(self.view_details)
        self.reprint_button.clicked.connect(self.preview_receipt)

        filters = QHBoxLayout()
        filters.setSpacing(12)
        filters.addWidget(self.from_date)
        filters.addWidget(self.to_date)
        filters.addWidget(clear_button)
        filters.addStretch()

        actions = QHBoxLayout()
        actions.setSpacing(12)
        actions.addWidget(self.view_button)
        actions.addWidget(self.reprint_button)
        actions.addStretch()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 36, 40, 40)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addWidget(self.search_input)
        layout.addLayout(filters)
        layout.addWidget(self.empty_label)
        layout.addWidget(self.table, 1)
        layout.addLayout(actions)

        self.refresh_invoices()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.refresh_invoices()

    def refresh_invoices(self) -> None:
        try:
            self.invoices = self.invoice_service.search_invoices(
                self.search_input.text(),
                self._date_value(self.from_date),
                self._date_value(self.to_date),
            )
        except InvoiceValidationError as exc:
            QMessageBox.warning(self, "Please Check", str(exc))
            return
        self.table.setRowCount(0)
        for invoice in self.invoices:
            self._add_invoice_row(invoice)
        self.empty_label.setText(self._empty_message())
        self.empty_label.setVisible(not self.invoices)
        self.update_buttons()

    def clear_filters(self) -> None:
        self.search_input.clear()
        self.from_date.setDate(self.from_date.minimumDate())
        self.to_date.setDate(self.to_date.minimumDate())
        self.refresh_invoices()

    def view_details(self) -> None:
        invoice = self._selected_invoice_with_items()
        if invoice is None:
            return
        InvoiceDetailsDialog(invoice, self).exec()

    def preview_receipt(self) -> None:
        invoice = self._selected_invoice_with_items()
        if invoice is None:
            return
        receipt = self.receipt_service.build_receipt(invoice)
        ReceiptPreviewDialog(receipt, self).exec()

    def update_buttons(self) -> None:
        enabled = self._selected_invoice() is not None
        self.view_button.setEnabled(enabled)
        self.reprint_button.setEnabled(enabled)

    def _add_invoice_row(self, invoice: Invoice) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        values = [
            invoice.invoice_number,
            invoice.invoice_date,
            invoice.invoice_time,
            invoice.customer_name or "-",
            invoice.customer_mobile or "-",
            format_rupees(invoice.total),
        ]
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            item.setData(Qt.ItemDataRole.UserRole, invoice.invoice_number)
            if column in (0, 1, 2, 5):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, column, item)

    def _selected_invoice(self) -> Invoice | None:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        invoice_number = self.table.item(rows[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        return next((invoice for invoice in self.invoices if invoice.invoice_number == invoice_number), None)

    def _selected_invoice_with_items(self) -> Invoice | None:
        invoice = self._selected_invoice()
        if invoice is None:
            return None
        return self.invoice_service.get_invoice_by_number(invoice.invoice_number)

    def _empty_message(self) -> str:
        if self.search_input.text().strip() or self._date_value(self.from_date) or self._date_value(self.to_date):
            return "No invoices found."
        return "No sales recorded yet."

    @staticmethod
    def _date_value(widget: QDateEdit) -> str | None:
        if widget.date() == widget.minimumDate():
            return None
        return widget.date().toString("yyyy-MM-dd")

    @staticmethod
    def _invoice_text(invoice: Invoice) -> str:
        lines = [f"Invoice #{invoice.invoice_number}", f"{invoice.invoice_date} {invoice.invoice_time}"]
        for item in invoice.items:
            lines.append(f"{item.product_shortcut} {item.product_name} x{item.quantity} @ {item.rate}")
        lines.append(f"Total: {format_rupees(invoice.total)}")
        return "\n".join(lines)


class InvoiceDetailsDialog(QDialog):
    def __init__(self, invoice: Invoice, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Invoice #{invoice.invoice_number}")
        self.setMinimumWidth(720)

        form = QFormLayout()
        form.addRow("Invoice #:", QLabel(invoice.invoice_number))
        form.addRow("Date:", QLabel(invoice.invoice_date))
        form.addRow("Time:", QLabel(invoice.invoice_time))
        if invoice.customer_name:
            form.addRow("Customer:", QLabel(invoice.customer_name))
        if invoice.customer_mobile:
            form.addRow("Mobile:", QLabel(invoice.customer_mobile))

        table = QTableWidget(0, 5)
        table.setHorizontalHeaderLabels(["Code", "Product", "Qty", "Rate", "Amount"])
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for item in invoice.items:
            row = table.rowCount()
            table.insertRow(row)
            for column, value in enumerate(
                [
                    str(item.product_shortcut),
                    item.product_name,
                    str(item.quantity),
                    format_rupees(item.rate),
                    format_rupees(item.amount),
                ]
            ):
                table.setItem(row, column, QTableWidgetItem(value))

        total = QLabel(f"TOTAL: {format_rupees(invoice.total)}")
        total.setObjectName("TotalCaption")
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(table)
        layout.addWidget(total, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(buttons)
