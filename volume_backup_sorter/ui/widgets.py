from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout


class DropArea(QFrame):
    pathsDropped = pyqtSignal(list)
    clicked = pyqtSignal()

    def __init__(self, title: str, hint: str, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("DropArea")
        self.setMinimumHeight(240)

        self.title = QLabel(title, self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setObjectName("DropTitle")

        self.hint = QLabel(hint, self)
        self.hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint.setWordWrap(True)
        self.hint.setObjectName("DropHint")

        lay = QVBoxLayout(self)
        lay.addStretch(1)
        lay.addWidget(self.title)
        lay.addWidget(self.hint)
        lay.addStretch(1)

        self._set_hover(False)

    def set_texts(self, title: str, hint: str) -> None:
        self.title.setText(title)
        self.hint.setText(hint)

    def _set_hover(self, hover: bool) -> None:
        self.setProperty("hover", hover)
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self._set_hover(True)
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self._set_hover(False)
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        self._set_hover(False)
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        paths = []
        for url in event.mimeData().urls():
            p = url.toLocalFile()
            if p:
                paths.append(p)

        if paths:
            self.pathsDropped.emit(paths)
        event.acceptProposedAction()


DROP_QSS = """
#DropArea {
  border: 2px dashed palette(mid);
  border-radius: 14px;
  background: palette(base);
}
#DropArea[hover="true"] {
  border: 2px solid palette(highlight);
  background: palette(alternate-base);
}
#DropTitle {
  font-size: 18px;
  font-weight: 700;
}
#DropHint {
  font-size: 13px;
  color: palette(mid);
}
"""

