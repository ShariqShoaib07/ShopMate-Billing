from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class PlaceholderPage(QWidget):
    def __init__(self, title: str, message: str) -> None:
        super().__init__()

        title_label = QLabel(title)
        title_label.setObjectName("PageTitle")

        message_label = QLabel(message)
        message_label.setObjectName("PageMessage")
        message_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 36, 40, 40)
        layout.setSpacing(14)
        layout.addWidget(title_label)
        layout.addWidget(message_label)
        layout.addStretch()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
