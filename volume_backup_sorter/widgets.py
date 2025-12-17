from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout


class DropArea(QFrame):
    pathsDropped = pyqtSignal(list)
    addRequested = pyqtSignal()  # Klick = Dateidialog öffnen (im MainWindow)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("DropArea")
        self.setMinimumHeight(220)

        self.title = QLabel("⬇ Drop Zone", self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setObjectName("DropTitle")

        self.hint = QLabel("Ordner/Dateien hierher ziehen\noder klicken zum Hinzufügen", self)
        self.hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint.setWordWrap(True)
        self.hint.setObjectName("DropHint")

        layout = QVBoxLayout(self)
        layout.addStretch(1)
        layout.addWidget(self.title)
        layout.addWidget(self.hint)
        layout.addStretch(1)

        self._set_hover(False)

    def _set_hover(self, hover: bool) -> None:
        self.setProperty("hover", hover)
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.addRequested.emit()

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
            local_path = url.toLocalFile()
            if local_path:
                paths.append(local_path)

        if paths:
            self.pathsDropped.emit(paths)
        event.acceptProposedAction()

