from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileRecord:
    size: int
    mtime: float
    sha256: str


class FileIndexDB:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn: sqlite3.Connection | None = None
        self._pending_writes = 0

    def open(self) -> None:
        self.conn = sqlite3.connect(str(self.db_path))
        cur = self.conn.cursor()
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
        cur.execute("CREATE INDEX IF NOT EXISTS idx_files_sha256 ON files(sha256)")
        self.conn.commit()

    def close(self) -> None:
        if self.conn is None:
            return
        try:
            self.conn.commit()
        except Exception:
            pass
        self.conn.close()
        self.conn = None

    def get(self, path: Path) -> FileRecord | None:
        assert self.conn is not None
        cur = self.conn.cursor()
        cur.execute(
            "SELECT size, mtime, sha256 FROM files WHERE path = ?",
            (str(path),),
        )
        row = cur.fetchone()
        if not row:
            return None
        return FileRecord(size=row[0], mtime=row[1], sha256=row[2] or "")

    def set(self, path: Path, size: int, mtime: float, sha256: str) -> None:
        assert self.conn is not None
        cur = self.conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO files (path, size, mtime, sha256) VALUES (?, ?, ?, ?)",
            (str(path), size, mtime, sha256),
        )
        self._pending_writes += 1
        if self._pending_writes >= 100:
            self.conn.commit()
            self._pending_writes = 0

    def cleanup(self, valid_paths: set[Path]) -> None:
        """Entfernt DB-Einträge für Dateien, die im Ziel nicht mehr existieren."""
        assert self.conn is not None
        valid = {str(p) for p in valid_paths}

        cur = self.conn.cursor()
        cur.execute("SELECT path FROM files")
        rows = cur.fetchall()

        to_delete = [row[0] for row in rows if row[0] not in valid]
        if not to_delete:
            return

        cur.executemany("DELETE FROM files WHERE path = ?", ((p,) for p in to_delete))
        self.conn.commit()
