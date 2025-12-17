# Volume Backup Sorter

Volume Backup Sorter is a cross-platform desktop application for safe, transparent, and reproducible backups.
It is designed to copy and organize large volumes of files without duplicates while keeping full user control.

The focus of this project is correctness, safety, and clarity.
Nothing is deleted silently, nothing is hidden, and every action can be previewed before execution.

---

## About

This tool started as a personal solution for backing up disks, phones, SD cards, and NAS volumes
without trusting opaque “one-click” backup software.

Volume Backup Sorter uses cryptographic hashing, a persistent file index, and configurable rules
to ensure that files are copied exactly once and placed into predictable folder structures.

It is intended for power users who want to understand what happens to their data.

---

## Features

- Drag & drop files and folders
- SHA256-based duplicate detection
- Persistent SQLite index for fast re-runs
- Rule-based file sorting (extensions, regex, size)
- Backup modes:
  - Archive (append-only, default)
  - Mirror (optional scoped deletion)
- Safe preview (dry-run) with file count and byte size
- Resume-safe backups
- Profiles for different backup scenarios
- Multi-language UI (English, German, additional languages)
- Cross-platform: Linux, macOS, Windows

---

## Requirements (from source)

- Python 3.10 or newer
- PyQt6

---

## Running from source

```bash
python3 -m venv venv
source venv/bin/activate

pip install -U pip
pip install -e .

python -m volume_backup_sorter

---

## Building standalone executables

Standalone binaries are built using PyInstaller.
Each platform must be built on its own operating system.

Build artifacts (dist/, build/) are intentionally not committed to the repository.

---

## Linux (onefile,GUI)

python3 -m venv venv
source venv/bin/activate

pip install -U pip
pip install -e .
pip install pyinstaller

rm -rf build dist *.spec

pyinstaller \
  --onefile \
  --windowed \
  --name volume-backup-sorter \
  --collect-all PyQt6 \
  volume_backup_sorter/__main__.py


Result:
dist/volume-backup-sorter

---

## macOS (onefile,GUI)

python3 -m venv venv
source venv/bin/activate

pip install -U pip
pip install -e .
pip install pyinstaller

rm -rf build dist *.spec

pyinstaller \
  --onefile \
  --windowed \
  --name volume-backup-sorter \
  --collect-all PyQt6 \
  volume_backup_sorter/__main__.py


First run (Gatekeeper):
xattr -dr com.apple.quarantine dist/volume-backup-sorter

---

## Windows (onefile,GUI)

py -m venv venv
.\venv\Scripts\activate

python -m pip install -U pip
pip install -e .
pip install pyinstaller

rmdir /s /q build,dist 2>$null
del *.spec 2>$null

pyinstaller `
  --onefile `
  --noconsole `
  --name volume-backup-sorter `
  --collect-all PyQt6 `
  volume_backup_sorter\__main__.py


Result:
dist\volume-backup-sorter.exe

---

## Project structure

volume_backup_sorter/
    - app.py
    - cli.py
    - config_store.py
    - fsops.py
    - hashing.py
    - i18n.py
    - index_db.py
    - loggers.py
    - models.py
    - paths.py
    - planner.py
    - worker.py
    - ui/
        - main_window.py
        - preview_dialog.py
        - rule_editor.py
        - settings_dialog.py
        - widgets.py

--- 

## Publishing

- GitHub repository contains only source code.
- GitHub Releases coming soon.
- PyPI coming soon.

--- 

## License

This project is licensed under the MIT License.

You are free to use, modify, and distribute this software.
There is no warranty; use it at your own risk.

See the LICENSE file for the full license test.

---

## END
