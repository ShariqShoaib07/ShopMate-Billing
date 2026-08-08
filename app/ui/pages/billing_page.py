from __future__ import annotations

from decimal import Decimal

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.database.repositories.settings_repository import SettingsRepository
from app.models.product import Product
from app.services.billing_service import BillingService, BillingValidationError
from app.services.invoice_service import InvoiceService, InvoiceValidationError
from app.services.product_service import ProductService
from app.utils.currency import format_rupees


class BillTableWidget(QTableWidget):
    shortcut_pressed = Signal(str)

    def keyPressEvent(self, event) -> None:
        text = event.text().strip()
        if text.isdigit() and self.state() == QAbstractItemView.State.NoState:
            self.shortcut_pressed.emit(text)
            event.accept()
            return
        super().keyPressEvent(event)


class BillingPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.billing_service = BillingService()
        self.invoice_service = InvoiceService()
        self.product_service = ProductService()
        self.settings_repository = SettingsRepository()
        self.is_updating_table = False

        self.shop_name_label = QLabel("Billing POS")
        self.shop_name_label.setObjectName("ShopName")

        self.page_title = QLabel("New Bill")
        self.page_title.setObjectName("PageTitle")

        self.customer_name_input = QLineEdit()
        self.customer_name_input.setPlaceholderText("Customer name")
        self.customer_mobile_input = QLineEdit()
        self.customer_mobile_input.setPlaceholderText("Customer mobile")
        self.customer_name_input.returnPressed.connect(self.customer_mobile_input.setFocus)
        self.customer_mobile_input.returnPressed.connect(self.focus_billing_table)
        self.customer_name_input.textChanged.connect(self.update_customer)
        self.customer_mobile_input.textChanged.connect(self.update_customer)

        self.bill_table = BillTableWidget(0, 5)
        self.bill_table.setObjectName("BillTable")
        self.bill_table.setHorizontalHeaderLabels(["Code", "Product", "Qty", "Rate", "Amount"])
        self.bill_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.bill_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.bill_table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.bill_table.setTabKeyNavigation(True)
        self.bill_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.bill_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.bill_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.bill_table.verticalHeader().setVisible(False)
        self.bill_table.verticalHeader().setDefaultSectionSize(44)
        self.bill_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.bill_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.bill_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.bill_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.bill_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.bill_table.itemChanged.connect(self.on_bill_item_changed)
        self.bill_table.itemSelectionChanged.connect(self.update_action_buttons)
        self.bill_table.shortcut_pressed.connect(self.add_product_by_shortcut)
        self.bill_table.itemDelegate().closeEditor.connect(
            lambda editor, hint: self._restore_shortcut_mode()
        )

        self.empty_bill_label = QLabel("No items added yet.")
        self.empty_bill_label.setObjectName("PageMessage")
        self.empty_bill_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.total_label = QLabel("Rs. 0")
        self.total_label.setObjectName("TotalAmount")
        total_caption = QLabel("TOTAL")
        total_caption.setObjectName("TotalCaption")
        total_layout = QVBoxLayout()
        total_layout.setSpacing(2)
        total_layout.addWidget(total_caption, alignment=Qt.AlignmentFlag.AlignRight)
        total_layout.addWidget(self.total_label, alignment=Qt.AlignmentFlag.AlignRight)

        self.remove_button = QPushButton("Remove Selected")
        self.clear_button = QPushButton("Clear Bill")
        self.new_bill_button = QPushButton("New Bill")
        self.save_print_button = QPushButton("SAVE INVOICE")
        self.save_print_button.setToolTip("Printing will be added after the printer model is known.")

        self.remove_button.clicked.connect(self.remove_selected_item)
        self.clear_button.clicked.connect(self.clear_bill)
        self.new_bill_button.clicked.connect(self.start_new_bill)
        self.save_print_button.clicked.connect(self.save_invoice)

        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(14)
        form_layout.setVerticalSpacing(10)
        form_layout.addWidget(QLabel("Customer Name:"), 0, 0)
        form_layout.addWidget(self.customer_name_input, 0, 1)
        form_layout.addWidget(QLabel("Mobile:"), 1, 0)
        form_layout.addWidget(self.customer_mobile_input, 1, 1)

        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.addWidget(self.shop_name_label)
        header_text.addWidget(self.page_title)
        header_layout.addLayout(header_text)
        header_layout.addStretch()

        bill_title = QLabel("Current Bill")
        bill_title.setObjectName("SectionTitle")

        action_layout = QHBoxLayout()
        action_layout.setSpacing(12)
        action_layout.addWidget(self.remove_button)
        action_layout.addWidget(self.clear_button)
        action_layout.addWidget(self.new_bill_button)
        action_layout.addStretch()
        action_layout.addLayout(total_layout)

        main_action_layout = QHBoxLayout()
        main_action_layout.addStretch()
        main_action_layout.addWidget(self.save_print_button)

        content = QWidget()
        content.setObjectName("BillingPageContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(34, 28, 34, 34)
        content_layout.setSpacing(14)
        content_layout.addLayout(header_layout)
        content_layout.addLayout(form_layout)
        content_layout.addWidget(self._separator())
        content_layout.addWidget(bill_title)
        content_layout.addWidget(self.empty_bill_label)
        content_layout.addWidget(self.bill_table)
        content_layout.addLayout(action_layout)
        content_layout.addLayout(main_action_layout)
        content_layout.addStretch()

        page_scroll = QScrollArea()
        page_scroll.setObjectName("BillingPageScroll")
        page_scroll.setWidgetResizable(True)
        page_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        page_scroll.setWidget(content)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(page_scroll)

        self.setTabOrder(self.customer_name_input, self.customer_mobile_input)
        self.setTabOrder(self.customer_mobile_input, self.bill_table)

        self.load_header()
        self.refresh_bill_table()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.load_header()

    def load_header(self) -> None:
        shop_settings = self.settings_repository.get_shop_settings()
        if shop_settings is not None:
            self.shop_name_label.setText(shop_settings.shop_name)

    def update_customer(self) -> None:
        self.billing_service.set_customer(
            self.customer_name_input.text(),
            self.customer_mobile_input.text(),
        )
        self.update_action_buttons()

    def focus_billing_table(self) -> None:
        self.bill_table.setFocus(Qt.FocusReason.TabFocusReason)

    def add_product_by_shortcut(self, shortcut: str) -> None:
        product = self.product_service.find_active_by_shortcut(int(shortcut))
        if product is None:
            self._show_validation_message("No active product is assigned to this shortcut.")
            return
        self.add_product_to_bill(product)

    def add_product_to_bill(self, product: Product) -> None:
        try:
            self.billing_service.add_product(product)
        except BillingValidationError as exc:
            self._show_validation_message(str(exc))
            return
        self.refresh_bill_table()
        self.focus_billing_table()

    def on_bill_item_changed(self, item: QTableWidgetItem) -> None:
        if self.is_updating_table or item.row() >= len(self.billing_service.items):
            return
        if item.column() not in (1, 2, 3):
            return

        try:
            if item.column() == 1:
                self.billing_service.update_description(item.row(), item.text())
            elif item.column() == 2:
                self.billing_service.update_quantity(item.row(), item.text())
            else:
                self.billing_service.update_rate(item.row(), item.text())
        except BillingValidationError as exc:
            self._show_validation_message(str(exc))

        self.refresh_bill_table(select_row=min(item.row(), len(self.billing_service.items) - 1))
        self._restore_shortcut_mode()

    def remove_selected_item(self) -> None:
        row = self._selected_bill_row()
        if row is None:
            return
        try:
            self.billing_service.remove_item(row)
        except BillingValidationError as exc:
            self._show_validation_message(str(exc))
            return
        self.refresh_bill_table()
        self._restore_shortcut_mode()

    def clear_bill(self) -> None:
        if not self.billing_service.has_unsaved_data():
            return
        if not self._confirm("Clear Bill", "Clear the current bill?", "Clear Bill"):
            return
        self._reset_bill_inputs()

    def start_new_bill(self) -> None:
        if self.billing_service.has_unsaved_data():
            if not self._confirm(
                "New Bill",
                "Start a new bill? Unsaved bill information will be cleared.",
                "New Bill",
            ):
                return
        self._reset_bill_inputs()

    def save_invoice(self) -> None:
        try:
            saved_invoice = self.invoice_service.save_current_bill(self.billing_service.current_bill)
        except InvoiceValidationError as exc:
            self._show_validation_message(str(exc))
            return
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Save Failed",
                f"Invoice could not be saved. The current bill is still on screen.\n\n{exc}",
            )
            return

        QMessageBox.information(
            self,
            "Invoice Saved",
            f"Invoice #{saved_invoice.invoice_number} saved successfully.",
        )
        self._reset_bill_inputs()

    def confirm_navigation_away(self) -> bool:
        if not self.billing_service.has_unsaved_data():
            return True
        return self._confirm("Unsaved Bill", "Current bill has unsaved changes.", "Leave", cancel_text="Stay")

    def refresh_bill_table(self, select_row: int | None = None) -> None:
        self.is_updating_table = True
        self.bill_table.clearSpans()
        self.bill_table.setRowCount(0)
        items = self.billing_service.items

        self.empty_bill_label.setVisible(not items)
        if items:
            for row, item in enumerate(items):
                self.bill_table.insertRow(row)
                self._set_bill_table_item(row, 0, str(item.shortcut), editable=False, center=True)
                self._set_bill_table_item(row, 1, item.product_name, editable=True)
                self._set_bill_table_item(row, 2, str(item.quantity), editable=True, center=True)
                self._set_bill_table_item(row, 3, self._format_number(item.rate), editable=True, center=True)
                self._set_bill_table_item(row, 4, self._format_number(item.amount), editable=False, center=True)

        self.total_label.setText(format_rupees(self.billing_service.total))
        self._resize_bill_table_to_rows()
        self.is_updating_table = False
        self.update_action_buttons()

        if select_row is not None and items and select_row >= 0:
            self.bill_table.selectRow(select_row)

    def update_action_buttons(self) -> None:
        has_selected_item = self._selected_bill_row() is not None
        has_unsaved_data = self.billing_service.has_unsaved_data()
        self.remove_button.setEnabled(has_selected_item)
        self.clear_button.setEnabled(has_unsaved_data)

    def _set_bill_table_item(
        self,
        row: int,
        column: int,
        text: str,
        editable: bool,
        center: bool = False,
    ) -> None:
        item = QTableWidgetItem(text)
        flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        if editable:
            flags |= Qt.ItemFlag.ItemIsEditable
        item.setFlags(flags)
        if center:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bill_table.setItem(row, column, item)

    def _selected_bill_row(self) -> int | None:
        selected_rows = self.bill_table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        if row >= len(self.billing_service.items):
            return None
        return row

    def _reset_bill_inputs(self) -> None:
        self.is_updating_table = True
        self.bill_table.clearSelection()
        current_item = self.bill_table.currentItem()
        if current_item is not None:
            self.bill_table.closePersistentEditor(current_item)
        self.bill_table.setCurrentItem(None)
        self.is_updating_table = False
        self.customer_name_input.clear()
        self.customer_mobile_input.clear()
        self.billing_service.clear_bill()
        self.refresh_bill_table()
        self._restore_shortcut_mode()

    def _restore_shortcut_mode(self) -> None:
        QTimer.singleShot(0, self._activate_table_shortcuts)

    def _activate_table_shortcuts(self) -> None:
        self.bill_table.setState(QAbstractItemView.State.NoState)
        self.focus_billing_table()

    def _resize_bill_table_to_rows(self) -> None:
        header_height = self.bill_table.horizontalHeader().height()
        row_height = sum(self.bill_table.rowHeight(row) for row in range(self.bill_table.rowCount()))
        frame_width = self.bill_table.frameWidth() * 2
        table_height = header_height + row_height + frame_width + 6
        self.bill_table.setFixedHeight(table_height)

    def _confirm(
        self,
        title: str,
        message: str,
        accept_text: str,
        cancel_text: str = "Cancel",
    ) -> bool:
        message_box = QMessageBox(self)
        message_box.setWindowTitle(title)
        message_box.setText(message)
        message_box.setIcon(QMessageBox.Icon.Question)
        cancel_button = message_box.addButton(cancel_text, QMessageBox.ButtonRole.RejectRole)
        accept_button = message_box.addButton(accept_text, QMessageBox.ButtonRole.AcceptRole)
        message_box.setDefaultButton(cancel_button)
        message_box.exec()
        return message_box.clickedButton() == accept_button

    @staticmethod
    def _separator() -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Plain)
        return line

    @staticmethod
    def _format_number(value: Decimal) -> str:
        return f"{value:,.0f}"

    def _show_validation_message(self, message: str) -> None:
        QMessageBox.warning(self, "Please Check", message)
