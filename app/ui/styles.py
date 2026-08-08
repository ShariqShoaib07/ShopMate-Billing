from __future__ import annotations


APP_STYLESHEET = """
QMainWindow {
    background: #f6f4ef;
}

QWidget {
    color: #202124;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 16px;
}

QScrollArea#BillingPageScroll,
QScrollArea#BillingPageScroll QWidget#BillingPageContent,
QScrollArea#BillingPageScroll > QWidget {
    background: #f6f4ef;
    border: none;
}

QFrame#Sidebar {
    background: #ffffff;
    border-right: 1px solid #dedbd2;
}

QLabel#AppTitle {
    font-size: 25px;
    font-weight: 700;
    color: #222222;
}

QLabel#PageTitle {
    font-size: 28px;
    font-weight: 700;
    color: #222222;
}

QLabel#PageMessage {
    font-size: 18px;
    color: #555555;
}

QLabel#ShopName {
    font-size: 30px;
    font-weight: 800;
    color: #222222;
}

QLabel#SectionTitle {
    font-size: 20px;
    font-weight: 700;
    color: #2f2f2f;
    text-transform: uppercase;
}

QLabel#TotalCaption {
    font-size: 16px;
    font-weight: 700;
    color: #555555;
}

QLabel#TotalAmount {
    font-size: 34px;
    font-weight: 800;
    color: #1f5d40;
}

QPushButton {
    min-height: 48px;
    padding: 10px 16px;
    border-radius: 8px;
    border: 1px solid transparent;
    background: #ffffff;
    color: #222222;
    text-align: left;
}

QPushButton:hover {
    background: #f0ede6;
}

QPushButton:checked {
    background: #2f6f73;
    color: #ffffff;
    font-weight: 600;
}

QLineEdit, QComboBox {
    min-height: 44px;
    padding: 8px 12px;
    border-radius: 8px;
    border: 1px solid #cfcac0;
    background: #ffffff;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #2f6f73;
}

QTableWidget {
    background: #ffffff;
    border: 1px solid #dedbd2;
    border-radius: 8px;
    gridline-color: #ece8df;
    selection-background-color: #d9eeee;
    selection-color: #202124;
}

QHeaderView::section {
    min-height: 42px;
    padding: 8px;
    background: #eeeae1;
    border: none;
    border-bottom: 1px solid #dedbd2;
    font-weight: 700;
}

QTableWidget::item {
    padding: 8px;
}

QDialog {
    background: #f6f4ef;
}

QDialogButtonBox QPushButton {
    text-align: center;
    min-width: 96px;
}

QPushButton:disabled {
    color: #8f8f8f;
    background: #e8e5dd;
}
"""
