from __future__ import annotations

import sys
from PyQt6.QtWidgets import QApplication

from .main_window import MainWindow


def run() -> int:
    app = QApplication(sys.argv)
    # Fusion wirkt meist “cleaner” als native, ohne dein Theme komplett zu zerstören
    app.setStyle("Fusion")

    w = MainWindow()
    w.show()
    return app.exec()

