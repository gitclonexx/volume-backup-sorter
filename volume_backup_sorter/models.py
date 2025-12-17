from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any
import uuid
import time


class BackupMode:
    ARCHIVE_RULES = "archive_rules"
    INCREMENTAL_RULES = "incremental_rules"
    MIRROR_TREE = "mirror_tree"


class ConflictStrategy:
    RENAME_COUNTER = "rename_counter"
    OVERWRITE = "overwrite"
    SKIP = "skip"
    RENAME_HASH = "rename_hash"
    RENAME_TIME = "rename_time"


class SymlinkMode:
    SKIP = "skip"
    FOLLOW = "follow"
    LINK = "link"


class MirrorDeleteScope:
    SUBFOLDER = "subfolder"
    WHOLE_TARGET = "whole_target"
    NO_DELETE = "no_delete"


@dataclass
class Rule:
    enabled: bool = True
    name: str = "Rule"
    target_folder: str = "misc"

    extensions: list[str] = field(default_factory=list)
    mime_prefixes: list[str] = field(default_factory=list)
    name_regex: str = ""
    path_contains: str = ""
    size_min_mb: int = 0
    size_max_mb: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "Rule":
        r = Rule()
        for k, v in d.items():
            if hasattr(r, k):
                setattr(r, k, v)

        r.extensions = [str(x).lower().lstrip(".") for x in (r.extensions or []) if str(x).strip()]
        r.mime_prefixes = [str(x).lower() for x in (r.mime_prefixes or []) if str(x).strip()]
        r.target_folder = (r.target_folder or "misc").strip() or "misc"
        r.name = (r.name or "Rule").strip() or "Rule"
        r.name_regex = (r.name_regex or "").strip()
        r.path_contains = (r.path_contains or "").strip()
        r.size_min_mb = int(r.size_min_mb or 0)
        r.size_max_mb = int(r.size_max_mb or 0)
        return r


@dataclass
class PerformanceOptions:
    hash_threads: int = 4
    copy_threads: int = 2
    hash_chunk_mb: int = 4

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "PerformanceOptions":
        p = PerformanceOptions()
        for k, v in d.items():
            if hasattr(p, k):
                setattr(p, k, int(v))
        p.hash_threads = max(1, min(p.hash_threads, 64))
        p.copy_threads = max(1, min(p.copy_threads, 16))
        p.hash_chunk_mb = max(1, min(p.hash_chunk_mb, 64))
        return p


@dataclass
class Profile:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    name: str = "Default"
    mode: str = BackupMode.ARCHIVE_RULES

    conflict: str = ConflictStrategy.RENAME_COUNTER
    symlinks: str = SymlinkMode.SKIP
    preserve_metadata: bool = True
    auto_open_target: bool = False

    mirror_delete_scope: str = MirrorDeleteScope.SUBFOLDER
    mirror_scope_subdir: str = "mirror"

    # If not empty, mirror delete only affects these extensions
    mirror_delete_ext_whitelist: list[str] = field(default_factory=list)

    rules: list[Rule] = field(default_factory=list)
    perf: PerformanceOptions = field(default_factory=PerformanceOptions)

    last_run_utc: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "mode": self.mode,
            "conflict": self.conflict,
            "symlinks": self.symlinks,
            "preserve_metadata": bool(self.preserve_metadata),
            "auto_open_target": bool(self.auto_open_target),
            "mirror_delete_scope": str(self.mirror_delete_scope),
            "mirror_scope_subdir": str(self.mirror_scope_subdir),
            "mirror_delete_ext_whitelist": list(self.mirror_delete_ext_whitelist or []),
            "rules": [r.to_dict() for r in self.rules],
            "perf": self.perf.to_dict(),
            "last_run_utc": float(self.last_run_utc),
        }

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "Profile":
        p = Profile()
        p.id = str(d.get("id") or p.id)
        p.name = str(d.get("name") or p.name)
        p.mode = str(d.get("mode") or p.mode)
        p.conflict = str(d.get("conflict") or p.conflict)
        p.symlinks = str(d.get("symlinks") or p.symlinks)
        p.preserve_metadata = bool(d.get("preserve_metadata", True))
        p.auto_open_target = bool(d.get("auto_open_target", False))

        p.mirror_delete_scope = str(d.get("mirror_delete_scope") or MirrorDeleteScope.SUBFOLDER)
        p.mirror_scope_subdir = str(d.get("mirror_scope_subdir") or "mirror").strip() or "mirror"

        wl = d.get("mirror_delete_ext_whitelist") or []
        if isinstance(wl, str):
            wl = [x.strip() for x in wl.split(",")]
        p.mirror_delete_ext_whitelist = [str(x).lower().lstrip(".") for x in wl if str(x).strip()]

        p.rules = [Rule.from_dict(x) for x in (d.get("rules") or [])]
        p.perf = PerformanceOptions.from_dict(d.get("perf") or {})
        p.last_run_utc = float(d.get("last_run_utc") or 0.0)

        if p.mirror_delete_scope not in (
            MirrorDeleteScope.SUBFOLDER,
            MirrorDeleteScope.WHOLE_TARGET,
            MirrorDeleteScope.NO_DELETE,
        ):
            p.mirror_delete_scope = MirrorDeleteScope.SUBFOLDER

        if not p.rules:
            p.rules = default_rules()

        return p


@dataclass
class AppConfig:
    version: int = 1
    language: str = "en"
    active_profile_id: str = ""
    profiles: list[Profile] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": int(self.version),
            "language": str(self.language),
            "active_profile_id": str(self.active_profile_id),
            "profiles": [p.to_dict() for p in self.profiles],
        }

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "AppConfig":
        cfg = AppConfig()
        cfg.version = int(d.get("version") or 1)
        cfg.language = str(d.get("language") or "en")
        cfg.active_profile_id = str(d.get("active_profile_id") or "")
        cfg.profiles = [Profile.from_dict(x) for x in (d.get("profiles") or [])]

        if not cfg.profiles:
            cfg.profiles = [Profile(name="Default", rules=default_rules())]
            cfg.active_profile_id = cfg.profiles[0].id

        if not cfg.active_profile_id or cfg.active_profile_id not in {p.id for p in cfg.profiles}:
            cfg.active_profile_id = cfg.profiles[0].id

        if cfg.language not in ("en", "de", "es"):
            cfg.language = "en"

        return cfg


def default_rules() -> list[Rule]:
    return [
        Rule(True, "Images", "images", extensions=["jpg", "jpeg", "png", "gif", "webp", "heic", "tiff"], mime_prefixes=["image/"]),
        Rule(True, "Videos", "videos", extensions=["mp4", "mov", "mkv", "avi", "webm"], mime_prefixes=["video/"]),
        Rule(True, "Audio", "audio", extensions=["mp3", "wav", "flac", "m4a", "aac", "ogg"], mime_prefixes=["audio/"]),
        Rule(True, "Documents", "documents", extensions=["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "md"]),
        Rule(True, "Archives", "archives", extensions=["zip", "7z", "rar", "tar", "gz", "bz2", "xz"]),
        Rule(True, "Code", "code", extensions=["py", "js", "ts", "json", "yaml", "yml", "toml", "ini", "sh", "bat"]),
        Rule(True, "Everything else", "misc"),
    ]


def now_utc() -> float:
    return time.time()

