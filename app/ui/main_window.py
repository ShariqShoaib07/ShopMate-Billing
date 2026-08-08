from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.config.settings import settings
from app.ui.pages.billing_page import BillingPage
from app.ui.pages.history_page import HistoryPage
from app.ui.pages.products_page import ProductsPage
from app.ui.pages.settings_page import SettingsPage
from app.ui.styles import APP_STYLESHEET


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(settings.app_name)
        self.setMinimumSize(980, 640)
        self.setStyleSheet(APP_STYLESHEET)

        self.nav_buttons: list[QPushButton] = []
        self.current_page_index = 0
        self.pages = QStackedWidget()
        self.pages.addWidget(BillingPage())
        self.pages.addWidget(HistoryPage())
        self.pages.addWidget(ProductsPage())
        settings_page = SettingsPage()
        settings_page.manage_products_requested.connect(lambda: self.navigate_to(2))
        self.pages.addWidget(settings_page)

        sidebar = self._build_sidebar()

        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(sidebar)
        layout.addWidget(self.pages, 1)

        self.setCentralWidget(root)

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)

        title = QLabel(settings.app_name)
        title.setObjectName("AppTitle")
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)

        buttons = [
            ("New Bill", 0),
            ("Sales History", 1),
            ("Products", 2),
            ("Settings", 3),
        ]

        button_group = QButtonGroup(sidebar)
        button_group.setExclusive(True)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(22, 28, 22, 22)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addSpacing(18)

        for label, page_index in buttons:
            button = QPushButton(label)
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, index=page_index: self.navigate_to(index))
            button_group.addButton(button)
            self.nav_buttons.append(button)
            layout.addWidget(button)
            if page_index == 0:
                button.setChecked(True)

        layout.addStretch()
        return sidebar

    def navigate_to(self, page_index: int) -> None:
        if page_index == self.current_page_index:
            self._sync_navigation_buttons()
            return

        current_page = self.pages.widget(self.current_page_index)
        if hasattr(current_page, "confirm_navigation_away") and not current_page.confirm_navigation_away():
            self._sync_navigation_buttons()
            return

        self.current_page_index = page_index
        self.pages.setCurrentIndex(page_index)
        self._sync_navigation_buttons()

    def _sync_navigation_buttons(self) -> None:
        for index, button in enumerate(self.nav_buttons):
            button.setChecked(index == self.current_page_index)
