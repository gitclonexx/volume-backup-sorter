from __future__ import annotations

import re

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel,
    QComboBox, QCheckBox, QPushButton, QSpinBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QListWidget, QListWidgetItem, QFormLayout, QLineEdit
)

from ..i18n import I18N, LANGUAGES
from ..models import (
    AppConfig, Profile, Rule,
    BackupMode, ConflictStrategy, SymlinkMode,
    MirrorDeleteScope
)
from ..config_store import save_config
from .rule_editor import RuleEditorDialog


def _mode_items(i18n: I18N):
    return [
        (BackupMode.ARCHIVE_RULES, i18n.t("mode.archive")),
        (BackupMode.INCREMENTAL_RULES, i18n.t("mode.incremental")),
        (BackupMode.MIRROR_TREE, i18n.t("mode.mirror")),
    ]


def _conflict_items(i18n: I18N):
    return [
        (ConflictStrategy.RENAME_COUNTER, i18n.t("conflict.rename_counter")),
        (ConflictStrategy.OVERWRITE, i18n.t("conflict.overwrite")),
        (ConflictStrategy.SKIP, i18n.t("conflict.skip")),
        (ConflictStrategy.RENAME_HASH, i18n.t("conflict.rename_hash")),
        (ConflictStrategy.RENAME_TIME, i18n.t("conflict.rename_time")),
    ]


def _symlink_items(i18n: I18N):
    return [
        (SymlinkMode.SKIP, i18n.t("symlink.skip")),
        (SymlinkMode.FOLLOW, i18n.t("symlink.follow")),
        (SymlinkMode.LINK, i18n.t("symlink.link")),
    ]


def _mirror_scope_items(i18n: I18N):
    return [
        (MirrorDeleteScope.SUBFOLDER, i18n.t("mirror.scope.subfolder")),
        (MirrorDeleteScope.WHOLE_TARGET, i18n.t("mirror.scope.whole")),
        (MirrorDeleteScope.NO_DELETE, i18n.t("mirror.scope.none")),
    ]


def _split_csv(s: str) -> list[str]:
    out = []
    for x in (s or "").split(","):
        x = x.strip()
        if x:
            out.append(x)
    return out


class SettingsDialog(QDialog):
    def __init__(self, cfg: AppConfig, i18n: I18N, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.i18n = i18n

        self.setWindowTitle(self.i18n.t("settings.title"))
        self.setModal(True)
        self.resize(900, 560)

        root = QVBoxLayout(self)

        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        self.tab_general = QWidget()
        self.tab_rules = QWidget()
        self.tab_perf = QWidget()
        self.tab_profiles = QWidget()

        self.tabs.addTab(self.tab_general, self.i18n.t("settings.general"))
        self.tabs.addTab(self.tab_rules, self.i18n.t("settings.rules"))
        self.tabs.addTab(self.tab_perf, self.i18n.t("settings.performance"))
        self.tabs.addTab(self.tab_profiles, self.i18n.t("settings.profiles"))

        self._build_general()
        self._build_rules()
        self._build_perf()
        self._build_profiles()

        btns = QHBoxLayout()
        btns.addStretch(1)
        self.btn_save = QPushButton(self.i18n.t("settings.save"))
        self.btn_close = QPushButton(self.i18n.t("settings.close"))
        self.btn_save.clicked.connect(self.on_save)
        self.btn_close.clicked.connect(self.reject)
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_close)
        root.addLayout(btns)

        self._load_from_cfg()

    def active_profile(self) -> Profile:
        for p in self.cfg.profiles:
            if p.id == self.cfg.active_profile_id:
                return p
        return self.cfg.profiles[0]

    def _build_general(self):
        lay = QVBoxLayout(self.tab_general)
        form = QFormLayout()

        self.cmb_lang = QComboBox()
        for code, name in LANGUAGES.items():
            self.cmb_lang.addItem(name, code)

        self.cmb_mode = QComboBox()
        self.cmb_conflict = QComboBox()
        self.cmb_symlinks = QComboBox()

        self.chk_meta = QCheckBox(self.i18n.t("settings.metadata"))
        self.chk_open = QCheckBox(self.i18n.t("settings.auto_open"))

        self.cmb_mirror_scope = QComboBox()
        self.ed_mirror_subdir = QLineEdit()
        self.ed_mirror_whitelist = QLineEdit()

        form.addRow(QLabel(self.i18n.t("settings.language")), self.cmb_lang)
        form.addRow(QLabel(self.i18n.t("settings.mode")), self.cmb_mode)
        form.addRow(QLabel(self.i18n.t("settings.conflict")), self.cmb_conflict)
        form.addRow(QLabel(self.i18n.t("settings.symlink")), self.cmb_symlinks)

        form.addRow(QLabel(self.i18n.t("settings.mirror_scope")), self.cmb_mirror_scope)
        form.addRow(QLabel(self.i18n.t("settings.mirror_subdir")), self.ed_mirror_subdir)
        form.addRow(QLabel(self.i18n.t("settings.mirror_whitelist")), self.ed_mirror_whitelist)

        form.addRow(self.chk_meta)
        form.addRow(self.chk_open)

        lay.addLayout(form)
        lay.addStretch(1)

    def _build_rules(self):
        lay = QVBoxLayout(self.tab_rules)

        self.tbl_rules = QTableWidget()
        self.tbl_rules.setColumnCount(4)
        self.tbl_rules.setHorizontalHeaderLabels([
            self.i18n.t("rules.enabled"),
            self.i18n.t("rules.name"),
            self.i18n.t("rules.target"),
            self.i18n.t("rules.match"),
        ])
        self.tbl_rules.horizontalHeader().setStretchLastSection(True)
        self.tbl_rules.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_rules.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        lay.addWidget(self.tbl_rules, 1)

        btns = QHBoxLayout()
        self.btn_add_rule = QPushButton(self.i18n.t("rules.add"))
        self.btn_edit_rule = QPushButton(self.i18n.t("rules.edit"))
        self.btn_del_rule = QPushButton(self.i18n.t("rules.delete"))
        self.btn_up_rule = QPushButton(self.i18n.t("rules.up"))
        self.btn_down_rule = QPushButton(self.i18n.t("rules.down"))

        self.btn_add_rule.clicked.connect(self.on_add_rule)
        self.btn_edit_rule.clicked.connect(self.on_edit_rule)
        self.btn_del_rule.clicked.connect(self.on_del_rule)
        self.btn_up_rule.clicked.connect(self.on_up_rule)
        self.btn_down_rule.clicked.connect(self.on_down_rule)

        btns.addWidget(self.btn_add_rule)
        btns.addWidget(self.btn_edit_rule)
        btns.addWidget(self.btn_del_rule)
        btns.addStretch(1)
        btns.addWidget(self.btn_up_rule)
        btns.addWidget(self.btn_down_rule)
        lay.addLayout(btns)

    def _is_valid_regex(self, pat: str) -> bool:
        if not pat:
            return True
        try:
            re.compile(pat)
            return True
        except Exception:
            return False

    def _rule_match_text(self, r: Rule) -> str:
        parts = []
        if r.extensions:
            parts.append("ext=" + ",".join(r.extensions[:8]) + ("…" if len(r.extensions) > 8 else ""))
        if r.mime_prefixes:
            parts.append("mime=" + ",".join(r.mime_prefixes[:4]) + ("…" if len(r.mime_prefixes) > 4 else ""))
        if r.name_regex:
            ok = self._is_valid_regex(r.name_regex)
            parts.append(("re=" + r.name_regex) if ok else ("re=INVALID(" + r.name_regex + ")"))
        if r.path_contains:
            parts.append("path~" + r.path_contains)
        if r.size_min_mb:
            parts.append(f">={r.size_min_mb}MB")
        if r.size_max_mb:
            parts.append(f"<={r.size_max_mb}MB")
        if not parts:
            return "any"
        return "; ".join(parts)

    def _reload_rules_table(self):
        prof = self.active_profile()
        self.tbl_rules.setRowCount(len(prof.rules))

        for row, r in enumerate(prof.rules):
            it0 = QTableWidgetItem("✓" if r.enabled else "")
            it0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it1 = QTableWidgetItem(r.name)
            it2 = QTableWidgetItem(r.target_folder)
            it3 = QTableWidgetItem(self._rule_match_text(r))

            self.tbl_rules.setItem(row, 0, it0)
            self.tbl_rules.setItem(row, 1, it1)
            self.tbl_rules.setItem(row, 2, it2)
            self.tbl_rules.setItem(row, 3, it3)

    def _selected_rule_index(self) -> int:
        rows = {i.row() for i in self.tbl_rules.selectionModel().selectedRows()}
        return next(iter(rows), -1)

    def on_add_rule(self):
        dlg = RuleEditorDialog(self.i18n, self.i18n.t("rule_editor.title_add"), None, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.active_profile().rules.append(dlg.get_rule())
            self._reload_rules_table()

    def on_edit_rule(self):
        idx = self._selected_rule_index()
        if idx < 0:
            return
        prof = self.active_profile()
        dlg = RuleEditorDialog(self.i18n, self.i18n.t("rule_editor.title_edit"), prof.rules[idx], self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            prof.rules[idx] = dlg.get_rule()
            self._reload_rules_table()

    def on_del_rule(self):
        idx = self._selected_rule_index()
        if idx < 0:
            return
        prof = self.active_profile()
        prof.rules.pop(idx)
        self._reload_rules_table()

    def on_up_rule(self):
        idx = self._selected_rule_index()
        if idx <= 0:
            return
        prof = self.active_profile()
        prof.rules[idx - 1], prof.rules[idx] = prof.rules[idx], prof.rules[idx - 1]
        self._reload_rules_table()
        self.tbl_rules.selectRow(idx - 1)

    def on_down_rule(self):
        idx = self._selected_rule_index()
        prof = self.active_profile()
        if idx < 0 or idx >= len(prof.rules) - 1:
            return
        prof.rules[idx + 1], prof.rules[idx] = prof.rules[idx], prof.rules[idx + 1]
        self._reload_rules_table()
        self.tbl_rules.selectRow(idx + 1)

    def _build_perf(self):
        lay = QVBoxLayout(self.tab_perf)
        form = QFormLayout()

        self.sp_hash = QSpinBox()
        self.sp_hash.setRange(1, 64)

        self.sp_copy = QSpinBox()
        self.sp_copy.setRange(1, 16)

        self.sp_chunk = QSpinBox()
        self.sp_chunk.setRange(1, 64)

        form.addRow(QLabel(self.i18n.t("perf.hash_threads")), self.sp_hash)
        form.addRow(QLabel(self.i18n.t("perf.copy_threads")), self.sp_copy)
        form.addRow(QLabel(self.i18n.t("perf.chunk_mb")), self.sp_chunk)

        lay.addLayout(form)
        lay.addStretch(1)

    def _build_profiles(self):
        lay = QVBoxLayout(self.tab_profiles)

        top = QHBoxLayout()
        top.addWidget(QLabel(self.i18n.t("profiles.active")))
        self.cmb_active = QComboBox()
        top.addWidget(self.cmb_active, 1)

        self.btn_set_active = QPushButton(self.i18n.t("profiles.set_active"))
        self.btn_set_active.clicked.connect(self.on_set_active)
        top.addWidget(self.btn_set_active)
        lay.addLayout(top)

        self.list_profiles = QListWidget()
        lay.addWidget(self.list_profiles, 1)

        btns = QHBoxLayout()
        self.btn_add_prof = QPushButton(self.i18n.t("profiles.add"))
        self.btn_copy_prof = QPushButton(self.i18n.t("profiles.copy"))
        self.btn_ren_prof = QPushButton(self.i18n.t("profiles.rename"))
        self.btn_del_prof = QPushButton(self.i18n.t("profiles.delete"))

        self.btn_add_prof.clicked.connect(self.on_add_profile)
        self.btn_copy_prof.clicked.connect(self.on_copy_profile)
        self.btn_ren_prof.clicked.connect(self.on_rename_profile)
        self.btn_del_prof.clicked.connect(self.on_delete_profile)

        btns.addWidget(self.btn_add_prof)
        btns.addWidget(self.btn_copy_prof)
        btns.addWidget(self.btn_ren_prof)
        btns.addWidget(self.btn_del_prof)
        btns.addStretch(1)
        lay.addLayout(btns)

    def _reload_profiles_ui(self):
        self.cmb_active.clear()
        self.list_profiles.clear()
        for p in self.cfg.profiles:
            self.cmb_active.addItem(p.name, p.id)
            it = QListWidgetItem(f"{p.name}  ({p.id[:8]})")
            it.setData(Qt.ItemDataRole.UserRole, p.id)
            if p.id == self.cfg.active_profile_id:
                it.setText(it.text() + "  *")
            self.list_profiles.addItem(it)

        idx = self.cmb_active.findData(self.cfg.active_profile_id)
        if idx >= 0:
            self.cmb_active.setCurrentIndex(idx)

    def on_set_active(self):
        pid = self.cmb_active.currentData()
        if pid:
            self.cfg.active_profile_id = str(pid)
            self._reload_profiles_ui()
            self._reload_rules_table()

    def _selected_profile_id(self) -> str:
        it = self.list_profiles.currentItem()
        if not it:
            return ""
        return str(it.data(Qt.ItemDataRole.UserRole) or "")

    def on_add_profile(self):
        p = Profile(name=self.i18n.t("profiles.new_profile"))
        self.cfg.profiles.append(p)
        self.cfg.active_profile_id = p.id
        self._reload_profiles_ui()
        self._reload_rules_table()

    def on_copy_profile(self):
        pid = self._selected_profile_id() or self.cfg.active_profile_id
        src = next((x for x in self.cfg.profiles if x.id == pid), None)
        if not src:
            return
        data = src.to_dict()
        data["id"] = ""
        data["name"] = src.name + self.i18n.t("profiles.copy_suffix")
        p = Profile.from_dict(data)
        self.cfg.profiles.append(p)
        self.cfg.active_profile_id = p.id
        self._reload_profiles_ui()
        self._reload_rules_table()

    def on_rename_profile(self):
        pid = self._selected_profile_id() or self.cfg.active_profile_id
        p = next((x for x in self.cfg.profiles if x.id == pid), None)
        if not p:
            return
        new_name = self.cmb_active.currentText().strip()
        if new_name:
            p.name = new_name
            self._reload_profiles_ui()

    def on_delete_profile(self):
        pid = self._selected_profile_id()
        if not pid:
            return
        if len(self.cfg.profiles) <= 1:
            QMessageBox.warning(self, self.i18n.t("ui.info_title"), self.i18n.t("msg.cannot_delete_last_profile"))
            return
        self.cfg.profiles = [p for p in self.cfg.profiles if p.id != pid]
        if self.cfg.active_profile_id == pid:
            self.cfg.active_profile_id = self.cfg.profiles[0].id
        self._reload_profiles_ui()
        self._reload_rules_table()

    def _load_from_cfg(self):
        idx = self.cmb_lang.findData(self.cfg.language)
        if idx >= 0:
            self.cmb_lang.setCurrentIndex(idx)

        self.cmb_mode.clear()
        for k, label in _mode_items(self.i18n):
            self.cmb_mode.addItem(label, k)

        self.cmb_conflict.clear()
        for k, label in _conflict_items(self.i18n):
            self.cmb_conflict.addItem(label, k)

        self.cmb_symlinks.clear()
        for k, label in _symlink_items(self.i18n):
            self.cmb_symlinks.addItem(label, k)

        self.cmb_mirror_scope.clear()
        for k, label in _mirror_scope_items(self.i18n):
            self.cmb_mirror_scope.addItem(label, k)

        prof = self.active_profile()

        self.cmb_mode.setCurrentIndex(max(0, self.cmb_mode.findData(prof.mode)))
        self.cmb_conflict.setCurrentIndex(max(0, self.cmb_conflict.findData(prof.conflict)))
        self.cmb_symlinks.setCurrentIndex(max(0, self.cmb_symlinks.findData(prof.symlinks)))

        self.cmb_mirror_scope.setCurrentIndex(max(0, self.cmb_mirror_scope.findData(prof.mirror_delete_scope)))
        self.ed_mirror_subdir.setText(prof.mirror_scope_subdir or "mirror")
        self.ed_mirror_whitelist.setText(", ".join(prof.mirror_delete_ext_whitelist or []))

        self.chk_meta.setChecked(bool(prof.preserve_metadata))
        self.chk_open.setChecked(bool(prof.auto_open_target))

        self.sp_hash.setValue(int(prof.perf.hash_threads))
        self.sp_copy.setValue(int(prof.perf.copy_threads))
        self.sp_chunk.setValue(int(prof.perf.hash_chunk_mb))

        self._reload_profiles_ui()
        self._reload_rules_table()

    def on_save(self):
        self.cfg.language = str(self.cmb_lang.currentData() or "en")

        prof = self.active_profile()
        prof.mode = str(self.cmb_mode.currentData() or prof.mode)
        prof.conflict = str(self.cmb_conflict.currentData() or prof.conflict)
        prof.symlinks = str(self.cmb_symlinks.currentData() or prof.symlinks)
        prof.preserve_metadata = bool(self.chk_meta.isChecked())
        prof.auto_open_target = bool(self.chk_open.isChecked())

        prof.mirror_delete_scope = str(self.cmb_mirror_scope.currentData() or prof.mirror_delete_scope)
        sub = (self.ed_mirror_subdir.text() or "mirror").strip() or "mirror"
        prof.mirror_scope_subdir = sub

        wl = [x.lower().lstrip(".") for x in _split_csv(self.ed_mirror_whitelist.text())]
        prof.mirror_delete_ext_whitelist = wl

        if prof.mirror_delete_scope == MirrorDeleteScope.SUBFOLDER and not prof.mirror_scope_subdir:
            QMessageBox.warning(self, self.i18n.t("ui.info_title"), self.i18n.t("msg.mirror_subdir_empty"))
            return

        prof.perf.hash_threads = int(self.sp_hash.value())
        prof.perf.copy_threads = int(self.sp_copy.value())
        prof.perf.hash_chunk_mb = int(self.sp_chunk.value())

        save_config(self.cfg)
        self.accept()

