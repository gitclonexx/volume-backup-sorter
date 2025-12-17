from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLabel, QPushButton, QHBoxLayout

from ..i18n import I18N
from ..worker import RunResult


def _human_bytes(n: int) -> str:
    n = int(n or 0)
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    x = float(n)
    i = 0
    while x >= 1024.0 and i < len(units) - 1:
        x /= 1024.0
        i += 1
    if i == 0:
        return f"{int(x)} {units[i]}"
    return f"{x:.2f} {units[i]}"


class PreviewDialog(QDialog):
    def __init__(self, i18n: I18N, res: RunResult, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.res = res

        self.setWindowTitle(self.i18n.t("preview.dialog.title"))
        self.setModal(True)
        self.resize(520, 240)

        root = QVBoxLayout(self)
        form = QFormLayout()

        form.addRow(QLabel(self.i18n.t("preview.files_total")), QLabel(str(res.total_sources)))
        form.addRow(QLabel(self.i18n.t("preview.copy")), QLabel(str(res.copied)))
        form.addRow(QLabel(self.i18n.t("preview.skip_dup")), QLabel(str(res.skipped_duplicates)))
        form.addRow(QLabel(self.i18n.t("preview.skip_missing")), QLabel(str(res.skipped_missing_sources)))
        form.addRow(QLabel(self.i18n.t("preview.delete_mirror")), QLabel(str(res.deleted_mirror)))
        form.addRow(QLabel(self.i18n.t("preview.bytes")), QLabel(_human_bytes(res.bytes_copied)))

        root.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch(1)
        b = QPushButton(self.i18n.t("preview.close"))
        b.clicked.connect(self.accept)
        btns.addWidget(b)
        root.addLayout(btns)

