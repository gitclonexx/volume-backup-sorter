from __future__ import annotations

import os
import shutil
import threading
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from .db import FileIndexDB
from .hashing import hash_file


class BackupWorker(QThread):
    message = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(int, int)  # current, total

    def __init__(self, target_dir: str, source_paths: list[str], parent=None):
        super().__init__(parent)
        self.target_dir = Path(target_dir).expanduser().resolve()
        self.source_paths = [str(Path(p).expanduser()) for p in source_paths]
        self._stop_event = threading.Event()

        self.total_files = 0
        self.processed_files = 0

        self.copied = 0
        self.skipped_duplicates = 0
        self.skipped_missing = 0

        self.db_path = self.target_dir / ".nas_backup_index.sqlite"
        self.db: FileIndexDB | None = None

    def stop(self) -> None:
        self._stop_event.set()

    def _stopped(self) -> bool:
        return self._stop_event.is_set()

    def _count_source_files(self) -> int:
        count = 0
        for src in self.source_paths:
            p = Path(src)
            try:
                if p.is_file():
                    count += 1
                elif p.is_dir():
                    for _, _, files in os.walk(p):
                        count += len(files)
            except Exception:
                # zählt dann halt nicht sauber, ist ok
                pass
        return count

    def _iter_source_files(self):
        for src in self.source_paths:
            if self._stopped():
                return
            p = Path(src)
            if not p.exists():
                self.skipped_missing += 1
                self.message.emit(f"[Übersprungen] Quelle existiert nicht: {p}")
                continue

            if p.is_file():
                yield p
            elif p.is_dir():
                self.message.emit(f"Verarbeite Ordner: {p}")
                for root, _, files in os.walk(p):
                    if self._stopped():
                        return
                    for name in files:
                        yield Path(root) / name

    def _unique_path(self, path: Path) -> Path:
        if not path.exists():
            return path

        directory = path.parent
        base = path.stem
        ext = path.suffix

        counter = 1
        while True:
            candidate = directory / f"{base}_{counter}{ext}"
            if not candidate.exists():
                return candidate
            counter += 1

    def _get_or_compute_hash_for_target(self, path: Path, known_hashes: dict[str, Path]) -> str:
        assert self.db is not None
        st = path.stat()
        rec = self.db.get(path)

        if rec and rec.size == st.st_size and rec.mtime == st.st_mtime and rec.sha256:
            file_hash = rec.sha256
        else:
            file_hash = hash_file(path)
            self.db.set(path, st.st_size, st.st_mtime, file_hash)

        known_hashes.setdefault(file_hash, path)
        return file_hash

    def run(self) -> None:
        try:
            if not self.target_dir.is_dir():
                self.error.emit("Zielordner existiert nicht oder ist kein Ordner.")
                return

            self.db = FileIndexDB(self.db_path)
            self.db.open()

            self.total_files = self._count_source_files()
            self.processed_files = 0
            self.progress.emit(self.processed_files, self.total_files)

            # Ziel indexieren
            self.message.emit("Indexiere bestehende Dateien im Ziel (DB-Cache, kann dauern)...")
            known_hashes: dict[str, Path] = {}
            paths_in_target: set[Path] = set()

            for root, _, files in os.walk(self.target_dir):
                if self._stopped():
                    return
                for name in files:
                    dest_path = (Path(root) / name).resolve()

                    # DB-Datei überspringen (inkl. Journal/WAL)
                    if dest_path == self.db_path:
                        continue
                    if dest_path.name.startswith(self.db_path.name):
                        # .sqlite-journal/.sqlite-wal/.sqlite-shm etc.
                        continue

                    paths_in_target.add(dest_path)
                    try:
                        self._get_or_compute_hash_for_target(dest_path, known_hashes)
                    except Exception as e:
                        self.message.emit(f"[Fehler beim Hashen im Ziel] {dest_path}: {e}")

            self.db.cleanup(paths_in_target)
            self.message.emit(f"Index fertig. {len(known_hashes)} eindeutige Dateien im Ziel.")

            # Quellen verarbeiten
            for src_path in self._iter_source_files():
                if self._stopped():
                    return
                self._process_file(src_path, known_hashes)

            self.message.emit(
                f"Fertig. Kopiert: {self.copied}, "
                f"Dubletten übersprungen: {self.skipped_duplicates}, "
                f"Fehlende Quellen: {self.skipped_missing}"
            )

        except Exception as e:
            self.error.emit(f"Unerwarteter Fehler: {e}")
        finally:
            try:
                if self.db is not None:
                    self.db.close()
            finally:
                self.finished.emit()

    def _process_file(self, src_path: Path, known_hashes: dict[str, Path]) -> None:
        if self._stopped():
            return
        if not src_path.is_file():
            return

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

        ext = src_path.suffix.lower().lstrip(".") or "no_extension"
        dest_subdir = self.target_dir / ext
        dest_subdir.mkdir(parents=True, exist_ok=True)

        dest_path = dest_subdir / src_path.name
        dest_path = self._unique_path(dest_path)

        try:
            shutil.copy2(src_path, dest_path)
            self.copied += 1

            # In DB schreiben (mit Hash vom Source, passt weil copy2 identisch)
            assert self.db is not None
            st = dest_path.stat()
            self.db.set(dest_path, st.st_size, st.st_mtime, file_hash)

            known_hashes[file_hash] = dest_path
            self.message.emit(f"[Kopiert] {src_path} -> {dest_path}")
        except Exception as e:
            self.message.emit(f"[Fehler beim Kopieren] {src_path} -> {dest_path}: {e}")

