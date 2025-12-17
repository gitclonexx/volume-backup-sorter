from __future__ import annotations

import json
from pathlib import Path

from .paths import app_config_dir
from .models import AppConfig


CONFIG_FILE = "config.json"


def config_path() -> Path:
    return app_config_dir() / CONFIG_FILE


def load_config() -> AppConfig:
    p = config_path()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return AppConfig.from_dict(data)
    except Exception:
        cfg = AppConfig.from_dict({})
        save_config(cfg)
        return cfg


def save_config(cfg: AppConfig) -> None:
    d = app_config_dir()
    d.mkdir(parents=True, exist_ok=True)
    p = config_path()
    p.write_text(json.dumps(cfg.to_dict(), indent=2), encoding="utf-8")

