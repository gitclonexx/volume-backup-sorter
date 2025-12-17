from __future__ import annotations

import os
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QListWidget,
    QListWidgetItem,
)

from .config import load_config, save_config
from .widgets import DropArea
from .worker import BackupWorker


_DROP_QSS = """
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
QGroupBox {
  font-weight: 600;
}
QTextEdit {
  font-family: monospace;
}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker: BackupWorker | None = None

        self.setWindowTitle("Volume Backup Sorter")
        self.resize(900, 650)

        self.config = load_config()
        self.recent_targets: list[str] = self.config.get("recent_targets", [])

        central = QWidget(self)
        self.setCentralWidget(central)

        root = QVBoxLayout(central)

        # --- Zielgruppe
        target_box = QGroupBox("Ziel")
        target_layout = QHBoxLayout(target_box)

        self.target_combo = QComboBox()
        self.target_combo.setEditable(True)
        for p in self.recent_targets:
            self.target_combo.addItem(p)

        self.btn_browse_target = QPushButton("Ziel wählen…")
        self.btn_browse_target.clicked.connect(self.choose_target)

        self.btn_open_target = QPushButton("Öffnen")
        self.btn_open_target.clicked.connect(self.open_target_in_filemanager)

        target_layout.addWidget(QLabel("Zielordner:"))
        target_layout.addWidget(self.target_combo, 1)
        target_layout.addWidget(self.btn_browse_target)
        target_layout.addWidget(self.btn_open_target)

        root.addWidget(target_box)

        # --- Quellen + Drop
        sources_box = QGroupBox("Quellen")
        sources_layout = QVBoxLayout(sources_box)

        self.drop_area = DropArea()
        self.drop_area.setStyleSheet(_DROP_QSS)
        self.drop_area.pathsDropped.connect(self.add_sources)
        self.drop_area.addRequested.connect(self.add_sources_via_dialog)

        sources_layout.addWidget(self.drop_area)

        self.sources_list = QListWidget()
        self.sources_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.sources_list.setMinimumHeight(140)
        sources_layout.addWidget(self.sources_list)

        controls = QHBoxLayout()
        self.btn_add_files = QPushButton("Dateien hinzufügen…")
        self.btn_add_files.clicked.connect(self.add_files_dialog)

        self.btn_add_folder = QPushButton("Ordner hinzufügen…")
        self.btn_add_folder.clicked.connect(self.add_folder_dialog)

        self.btn_remove_selected = QPushButton("Auswahl entfernen")
        self.btn_remove_selected.clicked.connect(self.remove_selected_sources)

        self.btn_clear_sources = QPushButton("Alle löschen")
        self.btn_clear_sources.clicked.connect(self.sources_list.clear)

        controls.addWidget(self.btn_add_files)
        controls.addWidget(self.btn_add_folder)
        controls.addStretch(1)
        controls.addWidget(self.btn_remove_selected)
        controls.addWidget(self.btn_clear_sources)

        sources_layout.addLayout(controls)
        root.addWidget(sources_box, 1)

        # --- Progress
        prog_box = QGroupBox("Fortschritt")
        prog_layout = QVBoxLayout(prog_box)
        self.progress = QProgressBar()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.lbl_progress = QLabel("Bereit.")
        prog_layout.addWidget(self.progress)
        prog_layout.addWidget(self.lbl_progress)
        root.addWidget(prog_box)

        # --- Log
        log_box = QGroupBox("Log")
        log_layout = QVBoxLayout(log_box)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        log_layout.addWidget(self.log)
        root.addWidget(log_box, 2)

        # --- Bottom Buttons
        bottom = QHBoxLayout()
        self.btn_start = QPushButton("Start")
        self.btn_start.clicked.connect(self.start_backup)

        self.btn_cancel = QPushButton("Abbrechen")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancel_backup)

        self.btn_clear_log = QPushButton("Log leeren")
        self.btn_clear_log.clicked.connect(self.log.clear)

        bottom.addWidget(self.btn_start)
        bottom.addWidget(self.btn_cancel)
        bottom.addStretch(1)
        bottom.addWidget(self.btn_clear_log)

        root.addLayout(bottom)

        # Menü (klein, aber praktisch)
        act_quit = QAction("Beenden", self)
        act_quit.triggered.connect(self.close)

        menu = self.menuBar().addMenu("Datei")
        menu.addAction(act_quit)

    # ---------- helpers

    def _current_target(self) -> str:
        return self.target_combo.currentText().strip()

    def _set_target(self, directory: str) -> None:
        directory = str(Path(directory).expanduser().resolve())
        idx = self.target_combo.findText(directory)
        if idx >= 0:
            self.target_combo.removeItem(idx)
        self.target_combo.insertItem(0, directory)
        self.target_combo.setCurrentIndex(0)
        self.log.append(f"Ziel gesetzt: {directory}")

    def choose_target(self) -> None:
        start_dir = self._current_target() or str(Path.home())
        directory = QFileDialog.getExistingDirectory(self, "Zielordner wählen", start_dir)
        if directory:
            self._set_target(directory)

    def open_target_in_filemanager(self) -> None:
        target = self._current_target()
        if not target:
            return
        p = Path(target).expanduser()
        if not p.exists():
            return
        # Linux: xdg-open, macOS: open (du bist primär Linux)
        os.system(f'xdg-open "{p}" >/dev/null 2>&1 &')

    # ---------- sources

    def _normalize_paths(self, paths: list[str]) -> list[str]:
        out = []
        seen = set()
        for p in paths:
            try:
                rp = str(Path(p).expanduser().resolve())
            except Exception:
                rp = p
            if rp not in seen:
                seen.add(rp)
                out.append(rp)
        return out

    def add_sources(self, paths: list[str]) -> None:
        paths = self._normalize_paths(paths)
        if not paths:
            return

        existing = {self.sources_list.item(i).text() for i in range(self.sources_list.count())}
        added = 0
        for p in paths:
            if p in existing:
                continue
            self.sources_list.addItem(QListWidgetItem(p))
            added += 1

        if added:
            self.log.append(f"Quellen hinzugefügt: {added}")
        else:
            self.log.append("Keine neuen Quellen (alles schon drin).")

    def add_sources_via_dialog(self) -> None:
        # Klick auf DropArea: Mischdialog (Dateien) + optional Ordner über separaten Button ist eh da
        self.add_files_dialog()

    def add_files_dialog(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(self, "Dateien auswählen", str(Path.home()))
        if files:
            self.add_sources(files)

    def add_folder_dialog(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Ordner auswählen", str(Path.home()))
        if folder:
            self.add_sources([folder])

    def remove_selected_sources(self) -> None:
        for item in self.sources_list.selectedItems():
            self.sources_list.takeItem(self.sources_list.row(item))

    def _get_sources(self) -> list[str]:
        return [self.sources_list.item(i).text() for i in range(self.sources_list.count())]

    # ---------- worker lifecycle

    def start_backup(self) -> None:
        target = self._current_target()
        if not target:
            QMessageBox.warning(self, "Fehlt", "Bitte Zielordner auswählen.")
            return

        sources = self._get_sources()
        if not sources:
            QMessageBox.warning(self, "Fehlt", "Bitte mindestens eine Quelle hinzufügen (Drop oder Buttons).")
            return

        if self.worker is not None and self.worker.isRunning():
            return

        self.log.append("=== Start ===")
        self.lbl_progress.setText("Starte…")

        self.worker = BackupWorker(target, sources)
        self.worker.message.connect(self.on_message)
        self.worker.error.connect(self.on_error)
        self.worker.finished.connect(self.on_finished)
        self.worker.progress.connect(self.on_progress)

        self._set_ui_running(True)

        self.progress.setRange(0, 1)
        self.progress.setValue(0)

        self.worker.start()

    def cancel_backup(self) -> None:
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()
            self.log.append("Abbruch angefordert…")
            self.lbl_progress.setText("Abbruch angefordert…")

    def on_message(self, msg: str) -> None:
        self.log.append(msg)

    def on_error(self, msg: str) -> None:
        self.log.append(f"[ERROR] {msg}")

    def on_progress(self, current: int, total: int) -> None:
        if total <= 0:
            self.progress.setRange(0, 1)
            self.progress.setValue(0)
            self.lbl_progress.setText("…")
            return

        if self.progress.maximum() != total:
            self.progress.setRange(0, total)

        current = max(0, min(current, total))
        self.progress.setValue(current)
        self.lbl_progress.setText(f"{current}/{total} Dateien")

    def on_finished(self) -> None:
        self.lbl_progress.setText("Fertig.")
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self._set_ui_running(False)
        self.log.append("--- Vorgang beendet ---")

    def _set_ui_running(self, running: bool) -> None:
        self.btn_start.setEnabled(not running)
        self.btn_cancel.setEnabled(running)

        self.drop_area.setEnabled(not running)
        self.sources_list.setEnabled(not running)

        self.btn_browse_target.setEnabled(not running)
        self.btn_open_target.setEnabled(not running)
        self.target_combo.setEnabled(not running)

        self.btn_add_files.setEnabled(not running)
        self.btn_add_folder.setEnabled(not running)
        self.btn_remove_selected.setEnabled(not running)
        self.btn_clear_sources.setEnabled(not running)

    # ---------- persist config

    def closeEvent(self, event):
        # Worker stoppen
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(2000)

        # recent targets speichern (max 10)
        items = []
        for i in range(self.target_combo.count()):
            t = self.target_combo.itemText(i).strip()
            if t and t not in items:
                items.append(t)
        items = items[:10]
        self.config["recent_targets"] = items
        save_config(self.config)

        super().closeEvent(event)

