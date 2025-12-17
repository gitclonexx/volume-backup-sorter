from __future__ import annotations

from dataclasses import dataclass


LANGUAGES = {
    "en": "English",
    "de": "Deutsch",
    "es": "Español",
}


@dataclass(frozen=True)
class I18N:
    lang: str

    def t(self, key: str) -> str:
        lang = self.lang if self.lang in _STRINGS else "en"
        return _STRINGS[lang].get(key, _STRINGS["en"].get(key, key))


_STRINGS = {
    "en": {
        "app.title": "Volume Backup Sorter",

        "ui.info_title": "Info",
        "ui.error_title": "Error",

        "menu.file": "File",
        "menu.quit": "Quit",

        "ui.target": "Target",
        "ui.target_folder": "Target folder:",
        "ui.choose": "Choose…",
        "ui.open": "Open",
        "ui.sources": "Sources",
        "ui.drop.title": "Drop Zone",
        "ui.drop.hint": "Drag files/folders here\nor click to add files",
        "ui.add_files": "Add files…",
        "ui.add_folder": "Add folder…",
        "ui.remove_selected": "Remove selected",
        "ui.clear_all": "Clear all",
        "ui.progress": "Progress",
        "ui.ready": "Ready.",
        "ui.log": "Log",
        "ui.start": "Start",
        "ui.preview": "Preview",
        "ui.cancel": "Cancel",
        "ui.clear_log": "Clear log",
        "ui.settings": "Settings",

        "msg.missing_target": "Please select a target folder.",
        "msg.missing_sources": "Please add at least one source.",
        "msg.running": "A job is already running.",
        "msg.preview_start": "Preview start…",
        "msg.run_start": "Run start…",
        "msg.cancel_requested": "Cancel requested…",
        "msg.done": "Done.",

        "msg.cannot_delete_last_profile": "Cannot delete the last profile.",
        "msg.mirror_subdir_empty": "Mirror subfolder cannot be empty.",

        "settings.title": "Settings",
        "settings.general": "General",
        "settings.rules": "Rules",
        "settings.performance": "Performance",
        "settings.profiles": "Profiles",
        "settings.language": "Language:",
        "settings.mode": "Mode:",
        "settings.conflict": "Name conflicts:",
        "settings.symlink": "Symlinks:",
        "settings.metadata": "Preserve metadata",
        "settings.auto_open": "Open target after run",

        "settings.mirror_scope": "Mirror delete scope:",
        "settings.mirror_subdir": "Mirror subfolder:",
        "settings.mirror_whitelist": "Delete whitelist (extensions):",

        "mirror.scope.subfolder": "Only inside a subfolder (safe)",
        "mirror.scope.whole": "Whole target (dangerous)",
        "mirror.scope.none": "No delete (copy only)",

        "mirror.confirm.title": "Danger confirmation",
        "mirror.confirm.text": "Whole-target delete is enabled.\nType DELETE to continue:",
        "mirror.confirm_wrong": "Confirmation failed. Run canceled.",

        "settings.save": "Save",
        "settings.close": "Close",

        "profiles.active": "Active profile:",
        "profiles.add": "Add",
        "profiles.copy": "Copy",
        "profiles.rename": "Rename",
        "profiles.delete": "Delete",
        "profiles.set_active": "Set active",
        "profiles.new_profile": "New Profile",
        "profiles.copy_suffix": " Copy",

        "rules.add": "Add",
        "rules.edit": "Edit",
        "rules.delete": "Delete",
        "rules.up": "Up",
        "rules.down": "Down",
        "rules.enabled": "Enabled",
        "rules.name": "Name",
        "rules.target": "Folder",
        "rules.match": "Match",

        "rule_editor.title_add": "Add rule",
        "rule_editor.title_edit": "Edit rule",
        "rule_editor.ok": "OK",
        "rule_editor.cancel": "Cancel",
        "rule_editor.invalid_regex": "Invalid regex pattern.",
        "rule_editor.invalid_size": "Min size must be <= max size (or max = 0).",

        "mode.archive": "Archive (rules + dedup)",
        "mode.incremental": "Incremental (rules + since last run)",
        "mode.mirror": "Mirror (tree + delete missing)",

        "conflict.rename_counter": "Rename (_1, _2, …)",
        "conflict.overwrite": "Overwrite",
        "conflict.skip": "Skip",
        "conflict.rename_hash": "Rename with hash",
        "conflict.rename_time": "Rename with timestamp",

        "symlink.skip": "Skip",
        "symlink.follow": "Follow (copy target file)",
        "symlink.link": "Copy as symlink",

        "perf.hash_threads": "Hash threads:",
        "perf.copy_threads": "Copy threads:",
        "perf.chunk_mb": "Hash chunk (MB):",

        "preview.dialog.title": "Preview summary",
        "preview.files_total": "Total source files:",
        "preview.copy": "Would copy:",
        "preview.skip_dup": "Would skip duplicates:",
        "preview.skip_missing": "Missing sources:",
        "preview.delete_mirror": "Would delete (mirror):",
        "preview.bytes": "Estimated bytes to copy:",
        "preview.close": "Close",
    },
    "de": {
        "app.title": "Volume Backup Sorter",

        "ui.info_title": "Info",
        "ui.error_title": "Fehler",

        "menu.file": "Datei",
        "menu.quit": "Beenden",

        "ui.target": "Ziel",
        "ui.target_folder": "Zielordner:",
        "ui.choose": "Wählen…",
        "ui.open": "Öffnen",
        "ui.sources": "Quellen",
        "ui.drop.title": "Drop-Zone",
        "ui.drop.hint": "Dateien/Ordner hierher ziehen\noder klicken, um Dateien hinzuzufügen",
        "ui.add_files": "Dateien hinzufügen…",
        "ui.add_folder": "Ordner hinzufügen…",
        "ui.remove_selected": "Auswahl entfernen",
        "ui.clear_all": "Alle löschen",
        "ui.progress": "Fortschritt",
        "ui.ready": "Bereit.",
        "ui.log": "Log",
        "ui.start": "Start",
        "ui.preview": "Vorschau",
        "ui.cancel": "Abbrechen",
        "ui.clear_log": "Log leeren",
        "ui.settings": "Einstellungen",

        "msg.missing_target": "Bitte einen Zielordner auswählen.",
        "msg.missing_sources": "Bitte mindestens eine Quelle hinzufügen.",
        "msg.running": "Es läuft bereits ein Vorgang.",
        "msg.preview_start": "Vorschau startet…",
        "msg.run_start": "Vorgang startet…",
        "msg.cancel_requested": "Abbruch angefordert…",
        "msg.done": "Fertig.",

        "msg.cannot_delete_last_profile": "Das letzte Profil kann nicht gelöscht werden.",
        "msg.mirror_subdir_empty": "Mirror-Unterordner darf nicht leer sein.",

        "settings.title": "Einstellungen",
        "settings.general": "Allgemein",
        "settings.rules": "Regeln",
        "settings.performance": "Performance",
        "settings.profiles": "Profile",
        "settings.language": "Sprache:",
        "settings.mode": "Modus:",
        "settings.conflict": "Namenskonflikte:",
        "settings.symlink": "Symlinks:",
        "settings.metadata": "Metadaten erhalten",
        "settings.auto_open": "Ziel nach Lauf öffnen",

        "settings.mirror_scope": "Mirror-Löschbereich:",
        "settings.mirror_subdir": "Mirror-Unterordner:",
        "settings.mirror_whitelist": "Delete-Whitelist (Extensions):",

        "mirror.scope.subfolder": "Nur in Unterordner (sicher)",
        "mirror.scope.whole": "Ganzes Ziel (gefährlich)",
        "mirror.scope.none": "Kein Löschen (nur kopieren)",

        "mirror.confirm.title": "Gefahr bestätigen",
        "mirror.confirm.text": "Ganzes Ziel löschen ist aktiv.\nTippe DELETE um fortzufahren:",
        "mirror.confirm_wrong": "Bestätigung fehlgeschlagen. Vorgang abgebrochen.",

        "settings.save": "Speichern",
        "settings.close": "Schließen",

        "profiles.active": "Aktives Profil:",
        "profiles.add": "Neu",
        "profiles.copy": "Kopieren",
        "profiles.rename": "Umbenennen",
        "profiles.delete": "Löschen",
        "profiles.set_active": "Aktiv setzen",
        "profiles.new_profile": "Neues Profil",
        "profiles.copy_suffix": " Kopie",

        "rules.add": "Neu",
        "rules.edit": "Bearbeiten",
        "rules.delete": "Löschen",
        "rules.up": "Hoch",
        "rules.down": "Runter",
        "rules.enabled": "Aktiv",
        "rules.name": "Name",
        "rules.target": "Ordner",
        "rules.match": "Match",

        "rule_editor.title_add": "Regel hinzufügen",
        "rule_editor.title_edit": "Regel bearbeiten",
        "rule_editor.ok": "OK",
        "rule_editor.cancel": "Abbrechen",
        "rule_editor.invalid_regex": "Ungültiges Regex-Muster.",
        "rule_editor.invalid_size": "Min. Größe muss <= Max. Größe sein (oder Max = 0).",

        "mode.archive": "Archiv (Regeln + Dedup)",
        "mode.incremental": "Inkrementell (Regeln + seit letztem Lauf)",
        "mode.mirror": "Mirror (Baum + Löschen)",

        "conflict.rename_counter": "Umbenennen (_1, _2, …)",
        "conflict.overwrite": "Überschreiben",
        "conflict.skip": "Überspringen",
        "conflict.rename_hash": "Umbenennen mit Hash",
        "conflict.rename_time": "Umbenennen mit Zeitstempel",

        "symlink.skip": "Überspringen",
        "symlink.follow": "Folgen (Zieldatei kopieren)",
        "symlink.link": "Als Symlink kopieren",

        "perf.hash_threads": "Hash-Threads:",
        "perf.copy_threads": "Copy-Threads:",
        "perf.chunk_mb": "Hash-Chunk (MB):",

        "preview.dialog.title": "Vorschau",
        "preview.files_total": "Quellen-Dateien gesamt:",
        "preview.copy": "Würde kopieren:",
        "preview.skip_dup": "Würde Dubletten skippen:",
        "preview.skip_missing": "Fehlende Quellen:",
        "preview.delete_mirror": "Würde löschen (Mirror):",
        "preview.bytes": "Geschätzte Bytes zum Kopieren:",
        "preview.close": "Schließen",
    },
    "es": {
        "app.title": "Volume Backup Sorter",

        "ui.info_title": "Info",
        "ui.error_title": "Error",

        "menu.file": "Archivo",
        "menu.quit": "Salir",

        "ui.target": "Destino",
        "ui.target_folder": "Carpeta destino:",
        "ui.choose": "Elegir…",
        "ui.open": "Abrir",
        "ui.sources": "Fuentes",
        "ui.drop.title": "Zona de drop",
        "ui.drop.hint": "Arrastra archivos/carpetas aquí\no haz clic para añadir archivos",
        "ui.add_files": "Añadir archivos…",
        "ui.add_folder": "Añadir carpeta…",
        "ui.remove_selected": "Quitar selección",
        "ui.clear_all": "Borrar todo",
        "ui.progress": "Progreso",
        "ui.ready": "Listo.",
        "ui.log": "Log",
        "ui.start": "Iniciar",
        "ui.preview": "Vista previa",
        "ui.cancel": "Cancelar",
        "ui.clear_log": "Limpiar log",
        "ui.settings": "Ajustes",

        "msg.missing_target": "Selecciona una carpeta destino.",
        "msg.missing_sources": "Añade al menos una fuente.",
        "msg.running": "Ya hay un proceso en marcha.",
        "msg.preview_start": "Iniciando vista previa…",
        "msg.run_start": "Iniciando…",
        "msg.cancel_requested": "Cancelación solicitada…",
        "msg.done": "Hecho.",

        "msg.cannot_delete_last_profile": "No se puede eliminar el último perfil.",
        "msg.mirror_subdir_empty": "La subcarpeta mirror no puede estar vacía.",

        "settings.title": "Ajustes",
        "settings.general": "General",
        "settings.rules": "Reglas",
        "settings.performance": "Rendimiento",
        "settings.profiles": "Perfiles",
        "settings.language": "Idioma:",
        "settings.mode": "Modo:",
        "settings.conflict": "Conflictos de nombre:",
        "settings.symlink": "Symlinks:",
        "settings.metadata": "Conservar metadatos",
        "settings.auto_open": "Abrir destino al terminar",

        "settings.mirror_scope": "Alcance de borrado (mirror):",
        "settings.mirror_subdir": "Subcarpeta mirror:",
        "settings.mirror_whitelist": "Whitelist de borrado (extensiones):",

        "mirror.scope.subfolder": "Solo dentro de subcarpeta (seguro)",
        "mirror.scope.whole": "Todo el destino (peligroso)",
        "mirror.scope.none": "Sin borrar (solo copiar)",

        "mirror.confirm.title": "Confirmación de peligro",
        "mirror.confirm.text": "Borrado de todo el destino está activo.\nEscribe DELETE para continuar:",
        "mirror.confirm_wrong": "Confirmación fallida. Proceso cancelado.",

        "settings.save": "Guardar",
        "settings.close": "Cerrar",

        "profiles.active": "Perfil activo:",
        "profiles.add": "Añadir",
        "profiles.copy": "Copiar",
        "profiles.rename": "Renombrar",
        "profiles.delete": "Eliminar",
        "profiles.set_active": "Activar",
        "profiles.new_profile": "Nuevo perfil",
        "profiles.copy_suffix": " Copia",

        "rules.add": "Añadir",
        "rules.edit": "Editar",
        "rules.delete": "Eliminar",
        "rules.up": "Subir",
        "rules.down": "Bajar",
        "rules.enabled": "Activo",
        "rules.name": "Nombre",
        "rules.target": "Carpeta",
        "rules.match": "Match",

        "rule_editor.title_add": "Añadir regla",
        "rule_editor.title_edit": "Editar regla",
        "rule_editor.ok": "OK",
        "rule_editor.cancel": "Cancelar",
        "rule_editor.invalid_regex": "Patrón regex inválido.",
        "rule_editor.invalid_size": "El tamaño mín. debe ser <= máx. (o máx = 0).",

        "mode.archive": "Archivo (reglas + dedup)",
        "mode.incremental": "Incremental (reglas + desde último)",
        "mode.mirror": "Espejo (árbol + borrar)",

        "conflict.rename_counter": "Renombrar (_1, _2, …)",
        "conflict.overwrite": "Sobrescribir",
        "conflict.skip": "Saltar",
        "conflict.rename_hash": "Renombrar con hash",
        "conflict.rename_time": "Renombrar con tiempo",

        "symlink.skip": "Saltar",
        "symlink.follow": "Seguir (copiar archivo real)",
        "symlink.link": "Copiar como symlink",

        "perf.hash_threads": "Hilos hash:",
        "perf.copy_threads": "Hilos copia:",
        "perf.chunk_mb": "Chunk hash (MB):",

        "preview.dialog.title": "Resumen",
        "preview.files_total": "Archivos totales:",
        "preview.copy": "Copiaría:",
        "preview.skip_dup": "Saltar duplicados:",
        "preview.skip_missing": "Fuentes faltantes:",
        "preview.delete_mirror": "Borraría (mirror):",
        "preview.bytes": "Bytes estimados:",
        "preview.close": "Cerrar",
    },
}

