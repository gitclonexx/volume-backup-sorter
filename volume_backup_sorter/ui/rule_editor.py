from __future__ import annotations

import re

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QCheckBox,
    QPushButton, QSpinBox, QFormLayout, QMessageBox
)

from ..models import Rule
from ..i18n import I18N


def _split_csv(s: str) -> list[str]:
    out = []
    for x in (s or "").split(","):
        x = x.strip()
        if x:
            out.append(x)
    return out


class RuleEditorDialog(QDialog):
    def __init__(self, i18n: I18N, title: str, rule: Rule | None = None, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.setWindowTitle(title)
        self.setModal(True)

        self._rule = rule if rule else Rule()

        root = QVBoxLayout(self)
        form = QFormLayout()

        self.chk_enabled = QCheckBox()
        self.chk_enabled.setChecked(bool(self._rule.enabled))

        self.ed_name = QLineEdit(self._rule.name)
        self.ed_folder = QLineEdit(self._rule.target_folder)

        self.ed_ext = QLineEdit(", ".join(self._rule.extensions))
        self.ed_mime = QLineEdit(", ".join(self._rule.mime_prefixes))
        self.ed_regex = QLineEdit(self._rule.name_regex)
        self.ed_path = QLineEdit(self._rule.path_contains)

        self.sp_min = QSpinBox()
        self.sp_min.setRange(0, 1024 * 1024)
        self.sp_min.setValue(int(self._rule.size_min_mb or 0))

        self.sp_max = QSpinBox()
        self.sp_max.setRange(0, 1024 * 1024)
        self.sp_max.setValue(int(self._rule.size_max_mb or 0))

        form.addRow("Enabled", self.chk_enabled)
        form.addRow("Name", self.ed_name)
        form.addRow("Target folder", self.ed_folder)
        form.addRow("Extensions (comma)", self.ed_ext)
        form.addRow("MIME prefixes (comma)", self.ed_mime)
        form.addRow("Name regex", self.ed_regex)
        form.addRow("Path contains", self.ed_path)
        form.addRow("Min size (MB)", self.sp_min)
        form.addRow("Max size (MB)", self.sp_max)

        root.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch(1)
        self.btn_ok = QPushButton(self.i18n.t("rule_editor.ok"))
        self.btn_cancel = QPushButton(self.i18n.t("rule_editor.cancel"))
        self.btn_ok.clicked.connect(self.on_ok)
        self.btn_cancel.clicked.connect(self.reject)
        btns.addWidget(self.btn_ok)
        btns.addWidget(self.btn_cancel)
        root.addLayout(btns)

    def on_ok(self):
        # Validate regex
        pat = (self.ed_regex.text() or "").strip()
        if pat:
            try:
                re.compile(pat)
            except Exception:
                QMessageBox.warning(self, "Info", self.i18n.t("rule_editor.invalid_regex"))
                return

        # Validate size range (max=0 means no max)
        mn = int(self.sp_min.value())
        mx = int(self.sp_max.value())
        if mx != 0 and mn > mx:
            QMessageBox.warning(self, "Info", self.i18n.t("rule_editor.invalid_size"))
            return

        self.accept()

    def get_rule(self) -> Rule:
        r = Rule()
        r.enabled = self.chk_enabled.isChecked()
        r.name = (self.ed_name.text() or "Rule").strip()
        r.target_folder = (self.ed_folder.text() or "misc").strip() or "misc"

        r.extensions = [x.lower().lstrip(".") for x in _split_csv(self.ed_ext.text())]
        r.mime_prefixes = [x.lower() for x in _split_csv(self.ed_mime.text())]
        r.name_regex = (self.ed_regex.text() or "").strip()
        r.path_contains = (self.ed_path.text() or "").strip()
        r.size_min_mb = int(self.sp_min.value())
        r.size_max_mb = int(self.sp_max.value())
        return r

