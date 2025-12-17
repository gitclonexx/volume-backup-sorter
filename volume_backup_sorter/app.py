from __future__ import annotations

import sys
from PyQt6.QtWidgets import QApplication

from .config_store import load_config
from .i18n import I18N
from .ui.main_window import MainWindow


def run_gui() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    cfg = load_config()
    i18n = I18N(cfg.language)

    w = MainWindow(cfg, i18n)
    w.show()
    return app.exec()

