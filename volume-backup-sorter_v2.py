import sys
import os
import shutil
import hashlib
import json
import sqlite3
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QTextEdit,
    QProgressBar,
    QFrame,
    QComboBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# conf 

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".nas_backup_sorter")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


#functions helping 

def hash_file(path, chunk_size=1024 * 1024):
    """Return SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


# worker



class BackupWorker(QThread):
    message = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(int, int)  # current, total

    def __init__(self, target_dir, source_paths, parent=None):
        super().__init__(parent)
        self.target_dir = os.path.abspath(target_dir)
        self.source_paths = source_paths
        self._stop = False

        # progress
        self.total_files = 0
        self.processed_files = 0

        # statistic
        self.copied = 0
        self.skipped_duplicates = 0
        self.skipped_missing = 0

        # DB
        self.db_path = os.path.join(self.target_dir, ".nas_backup_index.sqlite")
        self.db_conn = None
        self._db_pending_writes = 0

    # db 

    def _open_db(self):
        self.db_conn = sqlite3.connect(self.db_path)
        cur = self.db_conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
                path   TEXT PRIMARY KEY,
                size   INTEGER,
                mtime  REAL,
                sha256 TEXT
            )
            """
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_files_sha256 ON files(sha256)"
        )
        self.db_conn.commit()

    def _close_db(self):
        if self.db_conn is not None:
            try:
                self.db_conn.commit()
            except Exception:
                pass
            self.db_conn.close()
            self.db_conn = None

    def _get_file_record(self, path):
        cur = self.db_conn.cursor()
        cur.execute(
            "SELECT size, mtime, sha256 FROM files WHERE path = ?",
            (path,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {"size": row[0], "mtime": row[1], "sha256": row[2]}

    def _set_file_record(self, path, size, mtime, sha256):
        cur = self.db_conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO files (path, size, mtime, sha256) "
            "VALUES (?, ?, ?, ?)",
            (path, size, mtime, sha256),
        )
        self._db_pending_writes += 1
        if self._db_pending_writes >= 100:
            self.db_conn.commit()
            self._db_pending_writes = 0

    def _cleanup_db(self, valid_paths):
        """Entfernt Einträge für Dateien, die es nicht mehr gibt."""
        cur = self.db_conn.cursor()
        cur.execute("SELECT path FROM files")
        rows = cur.fetchall()
        to_delete = [row[0] for row in rows if row[0] not in valid_paths]
        if to_delete:
            cur.executemany("DELETE FROM files WHERE path = ?", ((p,) for p in to_delete))
            self.db_conn.commit()

    def _get_or_compute_hash_for_target(self, path, known_hashes):
        """
        Holt Hash aus DB, falls Größe+mtime noch passen,
        sonst neu hashen und DB aktualisieren.
        """
        st = os.stat(path)
        size = st.st_size
        mtime = st.st_mtime

        rec = self._get_file_record(path)
        if rec and rec["size"] == size and rec["mtime"] == mtime and rec["sha256"]:
            file_hash = rec["sha256"]
        else:
            file_hash = hash_file(path)
            self._set_file_record(path, size, mtime, file_hash)

        if file_hash not in known_hashes:
            known_hashes[file_hash] = path

        return file_hash

    # threading

    def stop(self):
        self._stop = True

    def _count_source_files(self):
        count = 0
        for src in self.source_paths:
            if os.path.isfile(src):
                count += 1
            elif os.path.isdir(src):
                for _, _, files in os.walk(src):
                    count += len(files)
        return count

    def run(self):
        try:
            if not os.path.isdir(self.target_dir):
                self.error.emit("Zielordner existiert nicht oder ist kein Ordner.")
                return

            # DB open
            self._open_db()

            # count files
            self.total_files = self._count_source_files()
            self.processed_files = 0
            self.progress.emit(self.processed_files, self.total_files)

            # index
            self.message.emit(
                "Indexiere bestehende Dateien im Ziel (nutzt lokale Datenbank, kann dauern)..."
            )
            known_hashes = {}  # hash
            paths_in_target = set()

            for root, dirs, files in os.walk(self.target_dir):
                if self._stop:
                    return
                for name in files:
                    dest_path = os.path.join(root, name)
                    # db file pass
                    if os.path.abspath(dest_path) == os.path.abspath(self.db_path):
                        continue
                    paths_in_target.add(dest_path)
                    try:
                        self._get_or_compute_hash_for_target(dest_path, known_hashes)
                    except Exception as e:
                        self.message.emit(
                            f"[Fehler beim Hashen im Ziel] {dest_path}: {e}"
                        )

            # DB cleanup
            self._cleanup_db(paths_in_target)

            self.message.emit(
                f"Index fertig. {len(known_hashes)} eindeutige Dateien im Ziel."
            )

            # sources 
            for src in self.source_paths:
                if self._stop:
                    return

                if not os.path.exists(src):
                    self.skipped_missing += 1
                    self.message.emit(f"[Übersprungen] Quelle existiert nicht: {src}")
                    continue

                if os.path.isfile(src):
                    self._process_file(src, known_hashes)
                else:
                    self.message.emit(f"Verarbeite Ordner: {src}")
                    for root, dirs, files in os.walk(src):
                        if self._stop:
                            return
                        for name in files:
                            src_path = os.path.join(root, name)
                            self._process_file(src_path, known_hashes)

            self.message.emit(
                f"Fertig. Kopiert: {self.copied}, "
                f"Dubletten übersprungen: {self.skipped_duplicates}, "
                f"Fehlende Quellen: {self.skipped_missing}"
            )
        except Exception as e:
            self.error.emit(f"Unerwarteter Fehler: {e}")
        finally:
            # DB ordentlich schließen
            self._close_db()
            self.finished.emit()

    def _process_file(self, src_path, known_hashes):
        if self._stop:
            return

        if not os.path.isfile(src_path):
            return

        # progressbar
        self.processed_files += 1
        self.progress.emit(self.processed_files, self.total_files)

        try:
            file_hash = hash_file(src_path)
        except Exception as e:
            self.message.emit(f"[Fehler beim Hashen] {src_path}: {e}")
            return

        if file_hash in known_hashes:
            self.skipped_duplicates += 1
            self.message.emit(f"[Duplikat übersprungen] {src_path}")
            return

        # get fileinfo
        _, ext = os.path.splitext(src_path)
        ext = ext.lower().lstrip(".")
        if not ext:
            ext = "no_extension"

        dest_subdir = os.path.join(self.target_dir, ext)
        os.makedirs(dest_subdir, exist_ok=True)

        base_name = os.path.basename(src_path)
        dest_path = os.path.join(dest_subdir, base_name)

        # change name
        dest_path = self._unique_path(dest_path)

        try:
            shutil.copy2(src_path, dest_path)
            self.copied += 1

            # Into db
            st = os.stat(dest_path)
            self._set_file_record(
                dest_path, st.st_size, st.st_mtime, file_hash
            )

            known_hashes[file_hash] = dest_path
            self.message.emit(f"[Kopiert] {src_path} -> {dest_path}")
        except Exception as e:
            self.message.emit(
                f"[Fehler beim Kopieren] {src_path} -> {dest_path}: {e}"
            )

    def _unique_path(self, path):
        """Wenn path existiert, hänge _1, _2, ... an."""
        if not os.path.exists(path):
            return path

        directory, name = os.path.split(path)
        base, ext = os.path.splitext(name)

        counter = 1
        while True:
            candidate = os.path.join(directory, f"{base}_{counter}{ext}")
            if not os.path.exists(candidate):
                return candidate
            counter += 1


# drop area


class DropArea(QFrame):
    pathsDropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        self.setAcceptDrops(True)
        self.label = QLabel("Ordner/Dateien hierher ziehen", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
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


#gui


class BackupGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None

        self.setWindowTitle("Volume Backup Sorter")
        self.resize(700, 500)

        self.config = load_config()
        self.recent_targets = self.config.get("recent_targets", [])

        main_layout = QVBoxLayout(self)

        # target choose
        path_layout = QHBoxLayout()
        self.target_combo = QComboBox()
        self.target_combo.setEditable(True)
        # old targets
        for p in self.recent_targets:
            self.target_combo.addItem(p)

        self.browse_button = QPushButton("Ziel wählen...")
        self.browse_button.clicked.connect(self.choose_target)

        path_layout.addWidget(QLabel("Zielordner:"))
        path_layout.addWidget(self.target_combo)
        path_layout.addWidget(self.browse_button)

        main_layout.addLayout(path_layout)

        # Droparea
        self.drop_area = DropArea()
        self.drop_area.pathsDropped.connect(self.handle_drop)
        main_layout.addWidget(self.drop_area)

        # Progress
        self.progress = QProgressBar()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        main_layout.addWidget(self.progress)

        # Log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        main_layout.addWidget(self.log)

        # Buttons: Stop + Log clena
        self.stop_button = QPushButton("Abbrechen")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_worker)

        self.clear_log_button = QPushButton("Log leeren")
        self.clear_log_button.clicked.connect(self.log.clear)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.clear_log_button)
        button_layout.addStretch(1)

        main_layout.addLayout(button_layout)

    # target handling

    def _set_target(self, directory: str):
        directory = os.path.abspath(directory)
        idx = self.target_combo.findText(directory)
        if idx >= 0:
            self.target_combo.removeItem(idx)
        self.target_combo.insertItem(0, directory)
        self.target_combo.setCurrentIndex(0)
        self.log.append(f"Ziel gesetzt: {directory}")

    def choose_target(self):
        start_dir = self.target_combo.currentText().strip()
        if not start_dir:
            start_dir = os.path.expanduser("~")

        directory = QFileDialog.getExistingDirectory(
            self, "Zielordner wählen", start_dir
        )
        if directory:
            self._set_target(directory)

    def _current_target(self) -> str:
        return self.target_combo.currentText().strip()

    # drag and dorp

    def handle_drop(self, paths):
        target = self._current_target()
        if not target:
            self.log.append("Bitte zuerst einen Zielordner wählen.")
            return

        self.log.append("Quellen hinzugefügt:")
        for p in paths:
            self.log.append(f"  {p}")

        # Worker starten
        if self.worker is not None and self.worker.isRunning():
            self.log.append("Es läuft bereits ein Backup-Vorgang.")
            return

        self.worker = BackupWorker(target, paths)
        self.worker.message.connect(self.on_message)
        self.worker.error.connect(self.on_error)
        self.worker.finished.connect(self.on_finished)
        self.worker.progress.connect(self.on_progress)

        # reset progress
        self.progress.setRange(0, 1)
        self.progress.setValue(0)

        self.stop_button.setEnabled(True)
        self.drop_area.setEnabled(False)
        self.browse_button.setEnabled(False)

        self.worker.start()

    # callback worker

    def stop_worker(self):
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()
            self.log.append("Abbruch angefordert...")

    def on_message(self, msg):
        self.log.append(msg)

    def on_error(self, msg):
        self.log.append(f"[ERROR] {msg}")

    def on_progress(self, current, total):
        if total <= 0:
            self.progress.setRange(0, 1)
            self.progress.setValue(0)
            return
        if self.progress.maximum() != total:
            self.progress.setRange(0, total)
        # hartcap
        current = max(0, min(current, total))
        self.progress.setValue(current)

    def on_finished(self):
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.stop_button.setEnabled(False)
        self.drop_area.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.log.append("--- Vorgang beendet ---")

    # end config

    def closeEvent(self, event):
        # stop
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(2000)

        # recent targets
        items = []
        for i in range(self.target_combo.count()):
            text = self.target_combo.itemText(i).strip()
            if text and text not in items:
                items.append(text)
        # 10 recents max
        items = items[:10]
        self.config["recent_targets"] = items
        save_config(self.config)

        event.accept()



# main




def main():
    app = QApplication(sys.argv)
    gui = BackupGUI()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
