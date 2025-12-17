from __future__ import annotations

import os
import threading
from dataclasses import dataclass
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, Future

from PyQt6.QtCore import QThread, pyqtSignal

from .models import (
    Profile, BackupMode, ConflictStrategy, SymlinkMode,
    MirrorDeleteScope, now_utc
)
from .hashing import sha256_file
from .fsops import (
    unique_dest_path,
    safe_copy_file,
    copy_symlink,
    should_follow_symlink,
)
from .index_db import IndexDB
from .planner import iter_files, dest_for_rules, dest_for_mirror, infer_source_roots
from .loggers import build_logger


@dataclass
class RunResult:
    total_sources: int = 0
    copied: int = 0
    skipped_duplicates: int = 0
    skipped_missing_sources: int = 0
    deleted_mirror: int = 0
    bytes_copied: int = 0


class BackupWorker(QThread):
    message = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal(object)  # RunResult
    progress = pyqtSignal(int, int)  # current, total
    phase = pyqtSignal(str)

    def __init__(self, profile: Profile, target_dir: str, sources: list[str], dry_run: bool, parent=None):
        super().__init__(parent)
        self.profile = profile
        self.target_root = Path(target_dir).expanduser().resolve()
        self.sources = sources[:]
        self.dry_run = dry_run

        self._stop = threading.Event()
        self._log = build_logger()

        self._db_path = self.target_root / ".vbs_index.sqlite"
        self._db: IndexDB | None = None

        self._total = 0
        self._done = 0

        self._known_hashes: dict[str, Path] = {}
        self._reserved_hashes: set[str] = set()
        self._reserved_paths: set[Path] = set()
        self._lock = threading.Lock()

        self._mirror_keep: set[Path] = set()

    def stop(self) -> None:
        self._stop.set()

    def _stopped(self) -> bool:
        return self._stop.is_set()

    def _emit(self, s: str) -> None:
        self.message.emit(s)
        try:
            self._log.info(s)
        except Exception:
            pass

    def _open_db(self) -> None:
        self._db = IndexDB(self._db_path)
        self._db.open()

    def _close_db(self) -> None:
        if self._db:
            self._db.close()
            self._db = None

    def _index_target(self) -> None:
        assert self._db is not None
        self.phase.emit("index")

        existing: set[Path] = set()
        self._emit("Indexing target (DB cache)…")

        for root, _, files in os.walk(self.target_root):
            if self._stopped():
                return
            for name in files:
                p = (Path(root) / name).resolve()
                if p.name.startswith(self._db_path.name):
                    continue

                existing.add(p)
                try:
                    st = p.stat()
                    rec = self._db.get(p)
                    if rec and rec.size == st.st_size and rec.mtime == st.st_mtime and rec.sha256:
                        h = rec.sha256
                    else:
                        h = sha256_file(p, chunk_size=self.profile.perf.hash_chunk_mb * 1024 * 1024)
                        self._db.set(p, st.st_size, st.st_mtime, h)
                    self._known_hashes.setdefault(h, p)
                except Exception:
                    continue

        try:
            removed = self._db.cleanup_missing(existing)
            if removed:
                self._emit(f"DB cleanup removed {removed} stale rows.")
        except Exception:
            pass

        self._emit(f"Target index ready. Unique files: {len(self._known_hashes)}")

    def _count_sources(self) -> tuple[int, int]:
        missing = 0
        total = 0
        for raw in self.sources:
            p = Path(raw).expanduser()
            if not p.exists():
                missing += 1
                continue
            if p.is_file():
                total += 1
            elif p.is_dir():
                for _, _, files in os.walk(p):
                    total += len(files)
        return total, missing

    def _hash_source(self, src: Path) -> str:
        return sha256_file(src, chunk_size=self.profile.perf.hash_chunk_mb * 1024 * 1024)

    def _reserve_hash(self, h: str) -> bool:
        with self._lock:
            if h in self._known_hashes or h in self._reserved_hashes:
                return False
            self._reserved_hashes.add(h)
            return True

    def _reserve_path(self, p: Path) -> None:
        with self._lock:
            self._reserved_paths.add(p)

    def _path_reserved(self, p: Path) -> bool:
        with self._lock:
            return p in self._reserved_paths

    def _mirror_base_root(self) -> Path:
        if self.profile.mirror_delete_scope == MirrorDeleteScope.SUBFOLDER:
            sub = (self.profile.mirror_scope_subdir or "mirror").strip() or "mirror"
            base = (self.target_root / sub).resolve()
        else:
            base = self.target_root.resolve()

        try:
            base.relative_to(self.target_root.resolve())
        except Exception:
            base = self.target_root.resolve()
        return base

    def _delete_allowed(self, p: Path) -> bool:
        wl = {x.lower().lstrip(".") for x in (self.profile.mirror_delete_ext_whitelist or []) if str(x).strip()}
        if not wl:
            return True
        ext = p.suffix.lower().lstrip(".")
        return ext in wl

    def run(self) -> None:
        res = RunResult()
        try:
            if not self.target_root.is_dir():
                self.error.emit("Target folder does not exist or is not a folder.")
                self.finished.emit(res)
                return

            self._total, missing = self._count_sources()
            res.total_sources = self._total
            res.skipped_missing_sources = missing
            self._done = 0
            self.progress.emit(self._done, max(1, self._total))

            self._open_db()
            if self.profile.mode in (BackupMode.ARCHIVE_RULES, BackupMode.INCREMENTAL_RULES):
                self._index_target()

            roots = infer_source_roots(self.sources)
            mirror_base = self._mirror_base_root()

            hash_workers = self.profile.perf.hash_threads
            copy_workers = self.profile.perf.copy_threads

            self.phase.emit("run")

            with ThreadPoolExecutor(max_workers=hash_workers) as hash_pool, ThreadPoolExecutor(max_workers=copy_workers) as copy_pool:
                in_flight: set[Future] = set()

                def submit_hash(p: Path):
                    fut = hash_pool.submit(self._hash_source, p)
                    fut._src_path = p  # type: ignore[attr-defined]
                    return fut

                def handle_one(src_path: Path, src_hash: str):
                    nonlocal res
                    if self._stopped():
                        return

                    if self.profile.mode == BackupMode.INCREMENTAL_RULES and self.profile.last_run_utc:
                        try:
                            if src_path.stat().st_mtime <= self.profile.last_run_utc:
                                self._emit(f"[Skip incremental] {src_path}")
                                return
                        except Exception:
                            pass

                    if self.profile.mode in (BackupMode.ARCHIVE_RULES, BackupMode.INCREMENTAL_RULES):
                        if not self._reserve_hash(src_hash):
                            res.skipped_duplicates += 1
                            self._emit(f"[Skip duplicate] {src_path}")
                            return
                        try:
                            size = src_path.stat().st_size
                        except Exception:
                            size = 0
                        dest = dest_for_rules(self.profile, self.target_root, src_path, size)
                    else:
                        root = None
                        for r in roots:
                            try:
                                src_path.resolve().relative_to(r.resolve())
                                root = r
                                break
                            except Exception:
                                continue
                        if root is None:
                            root = roots[0] if roots else src_path.parent

                        dest = dest_for_mirror(mirror_base, root, src_path)
                        self._mirror_keep.add(dest)

                    dest_final = unique_dest_path(dest, self.profile.conflict, src_hash)

                    if self._path_reserved(dest_final):
                        dest_final = unique_dest_path(dest_final, ConflictStrategy.RENAME_COUNTER, src_hash)
                    self._reserve_path(dest_final)

                    if dest.exists() and self.profile.conflict == ConflictStrategy.SKIP:
                        self._emit(f"[Skip exists] {src_path} -> {dest_final}")
                        return

                    if self.dry_run:
                        try:
                            res.bytes_copied += src_path.stat().st_size
                        except Exception:
                            pass
                        res.copied += 1
                        self._emit(f"[Would copy] {src_path} -> {dest_final}")
                        return

                    def do_copy():
                        nonlocal res
                        if self._stopped():
                            return

                        if src_path.is_symlink():
                            if self.profile.symlinks == SymlinkMode.SKIP:
                                return
                            if self.profile.symlinks == SymlinkMode.LINK:
                                copy_symlink(src_path, dest_final)
                            else:
                                safe_copy_file(src_path, dest_final, self.profile.preserve_metadata)
                        else:
                            safe_copy_file(src_path, dest_final, self.profile.preserve_metadata)

                        try:
                            res.bytes_copied += src_path.stat().st_size
                        except Exception:
                            pass
                        res.copied += 1

                        if self.profile.mode in (BackupMode.ARCHIVE_RULES, BackupMode.INCREMENTAL_RULES):
                            assert self._db is not None
                            try:
                                st = dest_final.stat()
                                self._db.set(dest_final, st.st_size, st.st_mtime, src_hash)
                            except Exception:
                                pass

                        with self._lock:
                            self._known_hashes[src_hash] = dest_final

                        self._emit(f"[Copied] {src_path} -> {dest_final}")

                    copy_pool.submit(do_copy)

                follow = should_follow_symlink(self.profile.symlinks)
                for src in iter_files(self.sources, follow_symlinks=follow):
                    if self._stopped():
                        break
                    try:
                        if not src.exists():
                            continue
                        if not src.is_file() and not src.is_symlink():
                            continue
                    except Exception:
                        continue

                    fut = submit_hash(src)
                    in_flight.add(fut)

                    while len(in_flight) >= max(4, hash_workers * 3):
                        if self._stopped():
                            break
                        fut2 = next(iter(in_flight))
                        in_flight.remove(fut2)
                        sp = getattr(fut2, "_src_path", None)
                        try:
                            h = fut2.result()
                        except Exception:
                            h = ""
                        if sp and h:
                            handle_one(sp, h)

                        self._done += 1
                        self.progress.emit(self._done, max(1, self._total))

                for fut2 in list(in_flight):
                    if self._stopped():
                        break
                    sp = getattr(fut2, "_src_path", None)
                    try:
                        h = fut2.result()
                    except Exception:
                        h = ""
                    if sp and h:
                        handle_one(sp, h)
                    self._done += 1
                    self.progress.emit(self._done, max(1, self._total))

            if self.profile.mode == BackupMode.MIRROR_TREE and not self._stopped():
                if self.profile.mirror_delete_scope == MirrorDeleteScope.NO_DELETE:
                    res.deleted_mirror = 0
                else:
                    if self.dry_run:
                        res.deleted_mirror = self._mirror_count_deletions(mirror_base, self._mirror_keep)
                        self._emit(f"[Would delete] {res.deleted_mirror} files (mirror)")
                    else:
                        res.deleted_mirror = self._mirror_delete(mirror_base, self._mirror_keep)
                        if res.deleted_mirror:
                            self._emit(f"Deleted {res.deleted_mirror} files (mirror).")

            if not self.dry_run and not self._stopped():
                self.profile.last_run_utc = now_utc()

            self.phase.emit("done")
            self._emit("Done.")

        except Exception as e:
            self.error.emit(f"Unexpected error: {e}")
        finally:
            try:
                self._close_db()
            finally:
                self.finished.emit(res)

    def _mirror_count_deletions(self, base: Path, keep: set[Path]) -> int:
        if not base.exists():
            return 0
        cnt = 0
        for root, _, files in os.walk(base):
            if self._stopped():
                break
            for name in files:
                p = (Path(root) / name).resolve()
                if p.name.startswith(self._db_path.name):
                    continue
                if p not in keep and self._delete_allowed(p):
                    cnt += 1
        return cnt

    def _mirror_delete(self, base: Path, keep: set[Path]) -> int:
        if not base.exists():
            return 0
        deleted = 0
        for root, _, files in os.walk(base):
            if self._stopped():
                break
            for name in files:
                p = (Path(root) / name).resolve()
                if p.name.startswith(self._db_path.name):
                    continue
                if p not in keep and self._delete_allowed(p):
                    try:
                        p.unlink()
                        deleted += 1
                    except Exception:
                        pass
        return deleted

