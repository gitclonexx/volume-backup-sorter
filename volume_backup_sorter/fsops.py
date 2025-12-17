from __future__ import annotations

import os
import re
import shutil
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .models import ConflictStrategy, SymlinkMode


@dataclass(frozen=True)
class FileInfo:
    path: Path
    size: int
    mtime: float
    name: str


def file_info(p: Path, follow_symlinks: bool) -> Optional[FileInfo]:
    try:
        st = p.stat() if follow_symlinks else p.lstat()
        if not p.is_file() and not (follow_symlinks and p.is_symlink()):
            return None
        return FileInfo(path=p, size=int(st.st_size), mtime=float(st.st_mtime), name=p.name)
    except Exception:
        return None


def guess_mime(path: Path) -> str:
    # This is extension-based (stdlib). It is fast and cross-platform.
    mt, _ = mimetypes.guess_type(str(path))
    return (mt or "").lower()


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def sanitize_folder_name(name: str) -> str:
    name = (name or "").strip()
    if not name:
        return "misc"
    # Remove path separators
    name = name.replace("/", "_").replace("\\", "_")
    return name


def unique_dest_path(dest: Path, strategy: str, content_hash: str) -> Path:
    if strategy == ConflictStrategy.OVERWRITE:
        return dest
    if strategy == ConflictStrategy.SKIP:
        return dest
    if not dest.exists():
        return dest

    parent = dest.parent
    stem = dest.stem
    suf = dest.suffix

    if strategy == ConflictStrategy.RENAME_HASH:
        cand = parent / f"{stem}_{content_hash[:12]}{suf}"
        if not cand.exists():
            return cand

    if strategy == ConflictStrategy.RENAME_TIME:
        import time
        ts = time.strftime("%Y%m%d_%H%M%S")
        cand = parent / f"{stem}_{ts}{suf}"
        if not cand.exists():
            return cand

    # Default: counter
    i = 1
    while True:
        cand = parent / f"{stem}_{i}{suf}"
        if not cand.exists():
            return cand
        i += 1


def safe_copy_file(src: Path, dst: Path, preserve_metadata: bool) -> None:
    # Copy via temp file and atomic replace to be crash-safe
    ensure_dir(dst.parent)
    tmp = dst.with_name(dst.name + ".partial")

    if tmp.exists():
        try:
            tmp.unlink()
        except Exception:
            pass

    with src.open("rb") as fsrc, tmp.open("wb") as fdst:
        shutil.copyfileobj(fsrc, fdst, length=1024 * 1024)

    if preserve_metadata:
        try:
            shutil.copystat(src, tmp, follow_symlinks=True)
        except Exception:
            pass

    os.replace(tmp, dst)


def copy_symlink(src: Path, dst: Path) -> None:
    # Recreate symlink if allowed
    ensure_dir(dst.parent)
    if dst.exists():
        dst.unlink()
    target = os.readlink(src)
    os.symlink(target, dst)


def compile_regex(pattern: str):
    if not pattern:
        return None
    try:
        return re.compile(pattern)
    except Exception:
        return None


def should_follow_symlink(mode: str) -> bool:
    return mode == SymlinkMode.FOLLOW

