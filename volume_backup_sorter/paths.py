from __future__ import annotations

import os
import platform
from pathlib import Path


APP_NAME = "VolumeBackupSorter"
APP_AUTHOR = "VolumeBackupSorter"


def _windows_appdata() -> Path:
    base = os.environ.get("APPDATA") or os.environ.get("LOCALAPPDATA")
    if not base:
        base = str(Path.home() / "AppData" / "Roaming")
    return Path(base)


def _mac_appsupport() -> Path:
    return Path.home() / "Library" / "Application Support"


def _linux_xdg_config() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME")
    return Path(base) if base else Path.home() / ".config"


def _linux_xdg_state() -> Path:
    base = os.environ.get("XDG_STATE_HOME")
    return Path(base) if base else Path.home() / ".local" / "state"


def app_config_dir() -> Path:
    sys = platform.system().lower()
    if "windows" in sys:
        return _windows_appdata() / APP_NAME
    if "darwin" in sys:
        return _mac_appsupport() / APP_NAME
    return _linux_xdg_config() / APP_NAME


def app_state_dir() -> Path:
    sys = platform.system().lower()
    if "windows" in sys:
        return _windows_appdata() / APP_NAME / "state"
    if "darwin" in sys:
        return _mac_appsupport() / APP_NAME / "state"
    return _linux_xdg_state() / APP_NAME


def app_logs_dir() -> Path:
    return app_state_dir() / "logs"

