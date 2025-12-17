from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import re

from .models import Profile, Rule, BackupMode, SymlinkMode
from .fsops import guess_mime, sanitize_folder_name, compile_regex


@dataclass(frozen=True)
class PlanItem:
    src: Path
    dest: Path
    action: str  # "copy" | "skip" | "delete"
    reason: str = ""


@dataclass
class PlanSummary:
    total_sources: int = 0
    would_copy: int = 0
    would_skip_dup: int = 0
    missing_sources: int = 0
    would_delete: int = 0
    bytes_to_copy: int = 0


def iter_files(paths: list[str], follow_symlinks: bool) -> Iterable[Path]:
    for raw in paths:
        p = Path(raw).expanduser()
        if not p.exists():
            yield from ()
            continue

        if p.is_file():
            yield p
            continue

        if p.is_dir():
            # Use os.walk for cross-platform behavior
            for root, _, files in os.walk(p):
                for name in files:
                    fp = Path(root) / name
                    # Skip broken symlinks when not following
                    if fp.is_symlink() and not follow_symlinks:
                        continue
                    yield fp


def rule_matches(rule: Rule, src: Path, mime: str, size: int, regex_cache: dict[str, re.Pattern | None]) -> bool:
    if not rule.enabled:
        return False

    # Extensions
    if rule.extensions:
        ext = src.suffix.lower().lstrip(".")
        if ext not in set(rule.extensions):
            return False

    # MIME
    if rule.mime_prefixes:
        if not mime:
            return False
        ok = False
        ml = mime.lower()
        for pref in rule.mime_prefixes:
            if ml.startswith(pref):
                ok = True
                break
        if not ok:
            return False

    # Name regex
    if rule.name_regex:
        pat = rule.name_regex
        rx = regex_cache.get(pat)
        if rx is None and pat not in regex_cache:
            rx = compile_regex(pat)
            regex_cache[pat] = rx
        if not rx:
            return False
        if not rx.search(src.name):
            return False

    # Path contains
    if rule.path_contains:
        if rule.path_contains.lower() not in str(src).lower():
            return False

    # Size range
    if rule.size_min_mb and size < rule.size_min_mb * 1024 * 1024:
        return False
    if rule.size_max_mb and size > rule.size_max_mb * 1024 * 1024:
        return False

    return True


def dest_for_rules(profile: Profile, target_root: Path, src: Path, size: int) -> Path:
    mime = guess_mime(src)
    regex_cache: dict[str, re.Pattern | None] = {}

    for r in profile.rules:
        if rule_matches(r, src, mime, size, regex_cache):
            folder = sanitize_folder_name(r.target_folder)
            return target_root / folder / src.name

    return target_root / "misc" / src.name


def dest_for_mirror(target_root: Path, source_root: Path, src: Path) -> Path:
    # Mirror keeps relative path from each source root
    rel = src.resolve().relative_to(source_root.resolve())
    return target_root / rel


def infer_source_roots(source_paths: list[str]) -> list[Path]:
    roots = []
    for s in source_paths:
        p = Path(s).expanduser()
        if p.exists():
            roots.append(p)
    return roots

