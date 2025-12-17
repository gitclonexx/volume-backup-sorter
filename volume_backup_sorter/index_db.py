from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DbRecord:
    size: int
    mtime: float
    sha256: str


class IndexDB:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn: sqlite3.Connection | None = None
        self._pending = 0

    def open(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        cur = self.conn.cursor()

        # Speed-friendly defaults for local cache
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
                path   TEXT PRIMARY KEY,
                size   INTEGER NOT NULL,
                mtime  REAL NOT NULL,
                sha256 TEXT NOT NULL
            )
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_files_sha256 ON files(sha256)")
        self.conn.commit()

    def close(self) -> None:
        if not self.conn:
            return
        try:
            self.conn.commit()
        except Exception:
            pass
        self.conn.close()
        self.conn = None

    def get(self, path: Path) -> DbRecord | None:
        assert self.conn is not None
        cur = self.conn.cursor()
        cur.execute("SELECT size, mtime, sha256 FROM files WHERE path = ?", (str(path),))
        row = cur.fetchone()
        if not row:
            return None
        return DbRecord(int(row[0]), float(row[1]), str(row[2]))

    def set(self, path: Path, size: int, mtime: float, sha256: str) -> None:
        assert self.conn is not None
        cur = self.conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO files(path, size, mtime, sha256) VALUES (?, ?, ?, ?)",
            (str(path), int(size), float(mtime), str(sha256)),
        )
        self._pending += 1
        if self._pending >= 200:
            self.conn.commit()
            self._pending = 0

    def cleanup_missing(self, existing_paths: set[Path]) -> int:
        # Remove rows for files that do not exist anymore
        assert self.conn is not None
        cur = self.conn.cursor()
        cur.execute("SELECT path FROM files")
        rows = cur.fetchall()
        keep = {str(p) for p in existing_paths}
        to_delete = [r[0] for r in rows if r[0] not in keep]
        if not to_delete:
            return 0
        cur.executemany("DELETE FROM files WHERE path = ?", ((p,) for p in to_delete))
        self.conn.commit()
        return len(to_delete)

