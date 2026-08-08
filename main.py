from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.database.schema import initialize_database
from app.ui.main_window import MainWindow


def main() -> int:
    """Start the desktop application."""
    initialize_database()

    app = QApplication(sys.argv)
    app.setApplicationName("Billing POS")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
