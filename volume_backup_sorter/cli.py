from __future__ import annotations

import argparse

from .app import run_gui


def main() -> int:
    # Keep CLI simple: GUI by default
    parser = argparse.ArgumentParser(prog="volume-backup-sorter")
    parser.add_argument("--gui", action="store_true", help="Start GUI (default)")
    args = parser.parse_args()
    return run_gui()

