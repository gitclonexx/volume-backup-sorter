from __future__ import annotations

import logging
from pathlib import Path
from datetime import datetime

from .paths import app_logs_dir


def build_logger(name: str = "vbs") -> logging.Logger:
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)
    if log.handlers:
        return log

    app_logs_dir().mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = app_logs_dir() / f"run_{ts}.log"

    fh = logging.FileHandler(str(logfile), encoding="utf-8")
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    fh.setFormatter(fmt)
    log.addHandler(fh)

    return log

