from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit, QProgressBar,
    QFileDialog, QMessageBox, QToolButton, QGroupBox
)
from PyQt6.QtGui import QDesktopServices

from ..models import AppConfig, Profile
from ..config_store import save_config
from ..i18n import I18N
from .widgets import DropArea, DROP_QSS
from .settings_dialog import SettingsDialog
from ..worker import BackupWorker, RunResult


class MainWindow(QMainWindow):
    def __init__(self, cfg: AppConfig, i18n: I18N):
        super().__init__()
        self.cfg = cfg
        self.i18n = i18n

        self.worker: BackupWorker | None = None
        self._target = ""

        self.setWindowTitle(self.i18n.t("app.title"))
        self.resize(980, 720)

        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # Top: profile + settings
        top = QHBoxLayout()
        top.addWidget(QLabel(self.i18n.t("profiles.active")))

        self.cmb_profile = QComboBox()
        self._reload_profiles_combo()
        self.cmb_profile.currentIndexChanged.connect(self.on_profile_changed)
        top.addWidget(self.cmb_profile, 1)

        self.btn_settings = QToolButton()
        self.btn_settings.setToolTip(self.i18n.t("ui.settings"))
        self.btn_settings.setText("⚙")
        icon = QIcon.fromTheme("settings")
        if not icon.isNull():
            self.btn_settings.setIcon(icon)
            self.btn_settings.setText("")
        self.btn_settings.clicked.connect(self.open_settings)
        top.addWidget(self.btn_settings)

        root.addLayout(top)

        # Target group
        g_target = QGroupBox(self.i18n.t("ui.target"))
        lay_t = QHBoxLayout(g_target)

        self.cmb_target = QComboBox()
        self.cmb_target.setEditable(True)
        self.cmb_target.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.btn_choose_target = QPushButton(self.i18n.t("ui.choose"))
        self.btn_open_target = QPushButton(self.i18n.t("ui.open"))

        self.btn_choose_target.clicked.connect(self.choose_target)
        self.btn_open_target.clicked.connect(self.open_target)

        lay_t.addWidget(QLabel(self.i18n.t("ui.target_folder")))
        lay_t.addWidget(self.cmb_target, 1)
        lay_t.addWidget(self.btn_choose_target)
        lay_t.addWidget(self.btn_open_target)

        root.addWidget(g_target)

        # Sources group
        g_src = QGroupBox(self.i18n.t("ui.sources"))
        lay_s = QVBoxLayout(g_src)

        self.drop = DropArea(self.i18n.t("ui.drop.title"), self.i18n.t("ui.drop.hint"))
        self.drop.setStyleSheet(DROP_QSS)
        self.drop.pathsDropped.connect(self.add_sources)
        self.drop.clicked.connect(self.add_files_dialog)
        lay_s.addWidget(self.drop)

        self.list_sources = QListWidget()
        self.list_sources.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.list_sources.setMinimumHeight(160)
        lay_s.addWidget(self.list_sources, 1)

        btns = QHBoxLayout()
        self.btn_add_files = QPushButton(self.i18n.t("ui.add_files"))
        self.btn_add_folder = QPushButton(self.i18n.t("ui.add_folder"))
        self.btn_remove = QPushButton(self.i18n.t("ui.remove_selected"))
        self.btn_clear_sources = QPushButton(self.i18n.t("ui.clear_all"))

        self.btn_add_files.clicked.connect(self.add_files_dialog)
        self.btn_add_folder.clicked.connect(self.add_folder_dialog)
        self.btn_remove.clicked.connect(self.remove_selected)
        self.btn_clear_sources.clicked.connect(self.list_sources.clear)

        btns.addWidget(self.btn_add_files)
        btns.addWidget(self.btn_add_folder)
        btns.addStretch(1)
        btns.addWidget(self.btn_remove)
        btns.addWidget(self.btn_clear_sources)
        lay_s.addLayout(btns)

        root.addWidget(g_src, 2)

        # Progress + log
        g_prog = QGroupBox(self.i18n.t("ui.progress"))
        lay_p = QVBoxLayout(g_prog)

        self.progress = QProgressBar()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)

        self.lbl_state = QLabel(self.i18n.t("ui.ready"))
        lay_p.addWidget(self.progress)
        lay_p.addWidget(self.lbl_state)
        root.addWidget(g_prog)

        g_log = QGroupBox(self.i18n.t("ui.log"))
        lay_l = QVBoxLayout(g_log)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        lay_l.addWidget(self.log)
        root.addWidget(g_log, 2)

        bottom = QHBoxLayout()
        self.btn_start = QPushButton(self.i18n.t("ui.start"))
        self.btn_preview = QPushButton(self.i18n.t("ui.preview"))
        self.btn_cancel = QPushButton(self.i18n.t("ui.cancel"))
        self.btn_clear_log = QPushButton(self.i18n.t("ui.clear_log"))

        self.btn_cancel.setEnabled(False)

        self.btn_start.clicked.connect(self.start_run)
        self.btn_preview.clicked.connect(self.start_preview)
        self.btn_cancel.clicked.connect(self.cancel_run)
        self.btn_clear_log.clicked.connect(self.log.clear)

        bottom.addWidget(self.btn_start)
        bottom.addWidget(self.btn_preview)
        bottom.addWidget(self.btn_cancel)
        bottom.addStretch(1)
        bottom.addWidget(self.btn_clear_log)

        root.addLayout(bottom)

        # menu
        act_quit = QAction("Quit", self)
        act_quit.triggered.connect(self.close)
        self.menuBar().addMenu("File").addAction(act_quit)

    def active_profile(self) -> Profile:
        pid = self.cfg.active_profile_id
        for p in self.cfg.profiles:
            if p.id == pid:
                return p
        self.cfg.active_profile_id = self.cfg.profiles[0].id
        return self.cfg.profiles[0]

    def _reload_profiles_combo(self):
        self.cmb_profile.clear()
        for p in self.cfg.profiles:
            self.cmb_profile.addItem(p.name, p.id)
        idx = self.cmb_profile.findData(self.cfg.active_profile_id)
        if idx >= 0:
            self.cmb_profile.setCurrentIndex(idx)

    def on_profile_changed(self):
        pid = self.cmb_profile.currentData()
        if pid:
            self.cfg.active_profile_id = str(pid)
            save_config(self.cfg)

    # ---------- Target

    def choose_target(self):
        start = self.cmb_target.currentText().strip() or str(Path.home())
        d = QFileDialog.getExistingDirectory(self, self.i18n.t("ui.target"), start)
        if d:
            self._set_target(d)

    def _set_target(self, d: str):
        p = str(Path(d).expanduser().resolve())
        self._target = p
        # keep at top
        idx = self.cmb_target.findText(p)
        if idx >= 0:
            self.cmb_target.removeItem(idx)
        self.cmb_target.insertItem(0, p)
        self.cmb_target.setCurrentIndex(0)
        self._append(f"Target set: {p}")

    def open_target(self):
        t = self.cmb_target.currentText().strip()
        if not t:
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(t))

    # ---------- Sources

    def _append(self, s: str):
        self.log.append(s)

    def add_sources(self, paths: list[str]):
        existing = {self.list_sources.item(i).text() for i in range(self.list_sources.count())}
        add = 0
        for raw in paths:
            p = str(Path(raw).expanduser().resolve())
            if p in existing:
                continue
            self.list_sources.addItem(QListWidgetItem(p))
            add += 1
        if add:
            self._append(f"Added sources: {add}")

    def add_files_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, self.i18n.t("ui.add_files"), str(Path.home()))
        if files:
            self.add_sources(files)

    def add_folder_dialog(self):
        d = QFileDialog.getExistingDirectory(self, self.i18n.t("ui.add_folder"), str(Path.home()))
        if d:
            self.add_sources([d])

    def remove_selected(self):
        for it in self.list_sources.selectedItems():
            self.list_sources.takeItem(self.list_sources.row(it))

    def _sources(self) -> list[str]:
        return [self.list_sources.item(i).text() for i in range(self.list_sources.count())]

    # ---------- Run

    def _validate(self) -> tuple[str, list[str]] | None:
        target = self.cmb_target.currentText().strip()
        if not target:
            QMessageBox.warning(self, "Info", self.i18n.t("msg.missing_target"))
            return None
        sources = self._sources()
        if not sources:
            QMessageBox.warning(self, "Info", self.i18n.t("msg.missing_sources"))
            return None
        if self.worker and self.worker.isRunning():
            QMessageBox.information(self, "Info", self.i18n.t("msg.running"))
            return None
        return target, sources

    def start_preview(self):
        v = self._validate()
        if not v:
            return
        target, sources = v
        self._append(self.i18n.t("msg.preview_start"))
        self._start_worker(target, sources, dry_run=True)

    def start_run(self):
        v = self._validate()
        if not v:
            return
        target, sources = v
        self._append(self.i18n.t("msg.run_start"))
        self._start_worker(target, sources, dry_run=False)

    def _start_worker(self, target: str, sources: list[str], dry_run: bool):
        prof = self.active_profile()
        self.worker = BackupWorker(prof, target, sources, dry_run, self)
        self.worker.message.connect(self._append)
        self.worker.error.connect(lambda s: self._append("[ERROR] " + s))
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.phase.connect(self.on_phase)

        self._set_running(True)
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.worker.start()

    def cancel_run(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self._append(self.i18n.t("msg.cancel_requested"))
            self.lbl_state.setText(self.i18n.t("msg.cancel_requested"))

    def on_phase(self, ph: str):
        self.lbl_state.setText(ph)

    def on_progress(self, cur: int, total: int):
        if total <= 0:
            total = 1
        if self.progress.maximum() != total:
            self.progress.setRange(0, total)
        self.progress.setValue(max(0, min(cur, total)))
        self.lbl_state.setText(f"{cur}/{total}")

    def on_finished(self, res: RunResult):
        self._set_running(False)
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.lbl_state.setText(self.i18n.t("msg.done"))

        prof = self.active_profile()
        save_config(self.cfg)

        # Auto open
        if prof.auto_open_target and not (self.worker and self.worker.dry_run):
            t = self.cmb_target.currentText().strip()
            if t:
                QDesktopServices.openUrl(QUrl.fromLocalFile(t))

        self._append(f"Copied: {res.copied}, dup skipped: {res.skipped_duplicates}, mirror deleted: {res.deleted_mirror}")

    def _set_running(self, running: bool):
        self.btn_start.setEnabled(not running)
        self.btn_preview.setEnabled(not running)
        self.btn_cancel.setEnabled(running)

        self.drop.setEnabled(not running)
        self.list_sources.setEnabled(not running)
        self.cmb_target.setEnabled(not running)
        self.btn_choose_target.setEnabled(not running)
        self.btn_open_target.setEnabled(not running)
        self.cmb_profile.setEnabled(not running)
        self.btn_settings.setEnabled(not running)

        self.btn_add_files.setEnabled(not running)
        self.btn_add_folder.setEnabled(not running)
        self.btn_remove.setEnabled(not running)
        self.btn_clear_sources.setEnabled(not running)

    # ---------- Settings

    def open_settings(self):
        dlg = SettingsDialog(self.cfg, self.i18n, self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            # reload config and refresh i18n
            self.cfg = self.cfg  # already updated by dialog
            self.i18n = I18N(self.cfg.language)

            # refresh UI texts
            self.setWindowTitle(self.i18n.t("app.title"))
            self.btn_choose_target.setText(self.i18n.t("ui.choose"))
            self.btn_open_target.setText(self.i18n.t("ui.open"))
            self.btn_add_files.setText(self.i18n.t("ui.add_files"))
            self.btn_add_folder.setText(self.i18n.t("ui.add_folder"))
            self.btn_remove.setText(self.i18n.t("ui.remove_selected"))
            self.btn_clear_sources.setText(self.i18n.t("ui.clear_all"))
            self.btn_start.setText(self.i18n.t("ui.start"))
            self.btn_preview.setText(self.i18n.t("ui.preview"))
            self.btn_cancel.setText(self.i18n.t("ui.cancel"))
            self.btn_clear_log.setText(self.i18n.t("ui.clear_log"))
            self.btn_settings.setToolTip(self.i18n.t("ui.settings"))
            self.drop.set_texts(self.i18n.t("ui.drop.title"), self.i18n.t("ui.drop.hint"))

            self._reload_profiles_combo()

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(1500)
        save_config(self.cfg)
        super().closeEvent(event)

