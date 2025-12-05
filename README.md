# volume-backup-sorter
Minimalistic Drag &amp; Drop Backup Tool  with de-duplication, per-target SQLite index and extension-based sorting (PyQt6)

# NAS Backup Sorter

Ein kleines, plattformunabhängiges Backup-Tool mit Drag & Drop GUI (PyQt6).  
Dateien werden nach Dateiendung in Unterordner sortiert, per SHA256 gehasht und in einer lokalen SQLite-Datenbank erfasst.  
Bereits bekannte Dateien werden übersprungen (Duplikate werden nicht erneut kopiert).

## Features

- ✅ Drag & Drop von Dateien und Ordnern
- ✅ Zielordner-History („Zuletzt verwendete Ziele“)
- ✅ Erkennung von Duplikaten via SHA256-Hash
- ✅ Lokale SQLite-Datenbank pro Zielordner (`.nas_backup_index.sqlite`)
- ✅ Automatische Ordnerstruktur nach Dateiendung (`jpg/`, `pdf/`, `no_extension/`, …)
- ✅ Automatisches Umbenennen bei Namenskollision (`_1`, `_2`, …)
- ✅ Fortschrittsbalken + Log-Ausgabe
- ✅ Lokale Config/History unter `~/.nas_backup_sorter/config.json`

Das Tool ist gedacht, um Fotos, Downloads oder alte Datenträger schnell in ein NAS / Backup-Verzeichnis zu schaufeln, ohne 100x dieselben Dateien zu kopieren.
