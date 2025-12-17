# Volume Backup Sorter

A cross-platform backup tool (Linux/macOS/Windows) with:
- drag & drop sources
- rules engine (folder mapping)
- profiles
- modes: Archive (rules), Incremental (rules), Mirror (tree)
- dedup by SHA256 with SQLite cache
- safe copy (temp + atomic replace)
- preview/dry-run
- multi-language UI (EN/DE/ES)

## Run (venv)
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

pip install -e .
volume-backup-sorter

## CLI
volume-backup-sorter --help

