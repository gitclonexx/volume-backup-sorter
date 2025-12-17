from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox,
    QPushButton, QSpinBox, QFormLayout
)

from ..models import Rule


def _split_csv(s: str) -> list[str]:
    out = []
    for x in (s or "").split(","):
        x = x.strip()
        if x:
            out.append(x)
    return out


class RuleEditorDialog(QDialog):
    def __init__(self, title: str, rule: Rule | None = None, parent=None):
        super().__init__(parent)
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
        self.btn_ok = QPushButton("OK")
        self.btn_cancel = QPushButton("Cancel")
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        btns.addWidget(self.btn_ok)
        btns.addWidget(self.btn_cancel)
        root.addLayout(btns)

    def get_rule(self) -> Rule:
        r = Rule()
        r.enabled = self.chk_enabled.isChecked()
        r.name = (self.ed_name.text() or "Rule").strip()
        r.target_folder = (self.ed_folder.text() or "misc").strip()

        r.extensions = [x.lower().lstrip(".") for x in _split_csv(self.ed_ext.text())]
        r.mime_prefixes = [x.lower() for x in _split_csv(self.ed_mime.text())]
        r.name_regex = (self.ed_regex.text() or "").strip()
        r.path_contains = (self.ed_path.text() or "").strip()
        r.size_min_mb = int(self.sp_min.value())
        r.size_max_mb = int(self.sp_max.value())
        return r

