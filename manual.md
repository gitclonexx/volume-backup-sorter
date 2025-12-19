# Volume Backup Sorter – Manual (DE/EN)

**Datum / Date:** 2025-12-19  

---

# 1. Zweck / Purpose

## DE:
Du wählst einen **Zielordner** und fügst **Quellen** (Dateien/Ordner) hinzu. Die App erstellt mit **Preview** einen Plan und führt ihn mit **Start** aus: Dateien werden nach **Regeln** in eine Zielstruktur kopiert, Duplikate werden übersprungen und im **Mirror-Modus** können Dateien im Ziel **kontrolliert** gelöscht werden (nur innerhalb des Mirror-Bereichs + nur mit Whitelist).

## EN:
You choose a **target folder** and add **sources** (files/folders). The app builds a plan via **Preview** and executes it via **Start**: files are copied into a target structure using **rules**, duplicates are skipped, and in **Mirror mode** the app may **delete** target files in a controlled way (only inside the mirror scope + only if allowed by the delete whitelist).

---

# 2. Grundbegriffe / Core Terms

## DE:
- **Active Profile:** Das aktuell aktive Profil. Bestimmt Modus, Regeln, Safety, Performance, Sprache.
- **Target Folder:** Der Ordner, in den geschrieben wird.
- **Sources:** Liste deiner Eingaben (Dateien/Ordner), die verarbeitet werden.
- **Preview (Plan):** Trockenlauf: Copy/Skip/Delete + Mengen/Bytes, bevor etwas geändert wird.
- **Rule (Regel):** Filter + Zielordner. Sagt: „Wenn Datei X passt → kopiere nach Y“.
- **Name conflicts:** Was passiert, wenn der Ziel-Dateiname schon existiert (rename/overwrite/skip/…).
- **Symlinks:** Umgang mit symbolischen Links (skip/copy as symlink/follow).
- **Mirror subfolder:** Unterordner im Target, der als Mirror-Root dient (Safety-Airbag).
- **Delete whitelist:** Extensions, die Mirror überhaupt löschen darf.
- **Preserve metadata:** Timestamps/Attribute möglichst übernehmen.
- **Threads / Chunk:** Performance-Parameter (Parallelität + Blockgröße fürs Hashing).

## EN:
- **Active Profile:** The currently active profile. Defines mode, rules, safety, performance, language.
- **Target Folder:** Where output is written.
- **Sources:** Your input list (files/folders) to process.
- **Preview (Plan):** Dry run: Copy/Skip/Delete + counts/bytes before anything changes.
- **Rule:** Filter + destination folder. “If file matches → copy to …”
- **Name conflicts:** What to do when the destination filename already exists (rename/overwrite/skip/…).
- **Symlinks:** How to handle symbolic links (skip/copy as symlink/follow).
- **Mirror subfolder:** Target subfolder used as mirror root (your safety airbag).
- **Delete whitelist:** Extensions Mirror is allowed to delete.
- **Preserve metadata:** Try to preserve timestamps/attributes.
- **Threads / Chunk:** Performance knobs (parallelism + hashing block size).

---

# 3. Quickstart / Schnellstart

## DE (60 Sekunden):
1. App öffnen → **Zahnrad** öffnen.
2. **General -> Language** 
3. **Save** (die App schließt sich; anschließend neu starten)
4. Zielordner auswählen:
   - Drag & Drop in **Drop-Zone**, oder
   - **Dateien hinzufügen…** / **Ordner hinzufügen…**
5. Optional aufräumen: **Auswahl entfernen** / **Alle löschen**
6. **Vorschau** klicken → überprüfen (besonders bei Mirror!).
7. **Start** klicken → ausführen.
8. Status/Progress/Log beobachten

## EN (60 seconds):
1. Open the app
2. Click **Target Folder → Choose**, select a target.
3. Add sources:
   - drag & drop into **Drop-Zone**, or
   - **Add files…** / **Add folder…**
4. Optional cleanup: **Remove selected** / **Clear all**
5. Click **Preview** → verify the plan (especially in Mirror!).
6. Click **Start** → execute.
7. Watch status/progress/log

---

# 4. Settings / Einstellungen

## 4.1 Active Profile / Aktives Profil

### DE:
Oben siehst du **Profile**. Wähle dein aktives Profil oder füge eines hinzu. Alles, was die App tut, wird dadurch gesteuert:
- Alle Einstellungen werden pro Profil gespeichert.

**Praxis:** Für unterschiedliche Jobs (Handy-Import, NAS-Sync, Projektbackup) nutze separate Profile.

### EN:
At the top you see the **Profiles**. Choose your active Profile or add one. It controls everything:
- All settings will be saved in each profile.

**Practice:** Use separate profiles for different jobs (phone import, NAS sync, project backup).

---

## 4.2 General / Allgemein

### Language / Sprache

DE:
UI-Sprache: **English / Deutsch / Spanish**.

EN:
UI language: **English / German / Spanish**.


### Mode (Archive / Incremental / Mirror)

DE:
- **Archive:** nur hinzufügen, niemals löschen.
- **Incremental:** nur neue/geänderte kopieren, normalerweise keine Deletes.
- **Mirror:** Spiegeln, inkl. kontrollierter Deletes.


EN:
- **Archive:** append-only, never deletes.
- **Incremental:** copy new/changed only, typically no deletes.
- **Mirror:** syncing, including controlled deletes.


### Name conflicts / Namenskonflikte 

DE:
Wenn Ziel-Dateiname existiert: Strategie wählen.  
Optionen: **rename _1**, **overwrite**, **skip**, **rename with hash**, **rename with timestamp**.  

EN:
When destination filename exists: choose a strategy.  
Options: **rename _1**, **overwrite**, **skip**, **rename with hash**, **rename with timestamp**.  


### Symlinks

DE:
Optionen: **skip**, **copy as symlink**, **follow**.  
Details siehe Kapitel 9.

EN:
Options: **skip**, **copy as symlink**, **follow**.  
Details in section 9.


### Mirror subfolder / Mirror Unterordner

DE:
Textfeld. Definiert den Unterordner im Target, in dem Mirror arbeitet.

Beispiel:
- Target: `/mnt/nas/backups`
- Mirror subfolder: `PC1_SYNC`
- Effektiv: `/mnt/nas/backups/PC1_SYNC`

**Warum Pflicht:** Damit Mirror-Deletes niemals „aus Versehen“ außerhalb deines Sync-Bereichs passieren.

EN:
Text field. Defines the target subfolder used as Mirror root.

Example:
- Target: `/mnt/nas/backups`
- Mirror subfolder: `PC1_SYNC`
- Effective: `/mnt/nas/backups/PC1_SYNC`

**Why it matters:** Prevents Mirror deletes from touching anything outside your sync area.


### Delete whitelist (extensions)

DE:
Kommagetrennte Extensions (ohne Punkt). Beispiel:
`jpg,jpeg,png,heic,mp4,mov,pdf,txt`

EN:
Comma-separated extensions (no dot). Example:
`jpg,jpeg,png,heic,mp4,mov,pdf,txt`


### Preserve metadata / Metadaten erhalten

DE:
Versucht Timestamps/Attribute zu erhalten. Das klappt je nach OS/Filesystem unterschiedlich (SMB/NAS kann abweichen).

EN:
Tries to preserve timestamps/attributes. Behavior differs across OS/filesystems (SMB/NAS may differ).


### Open target after run / Ziel nach Lauf öffnen

DE:
Öffnet nach dem Run den Zielordner im Dateimanager.

EN:
Opens the target folder in your file manager after the run.

---

## 4.3 Rules / Regeln

DE:
Du siehst eine Liste deiner Regeln. Aktionen:
- **Add**: neue Regel
- **Edit**: bearbeiten
- **Delete**: löschen

EN:
You see a list of rules. Actions:
- **Add**
- **Edit**
- **Delete**


### Rule-Felder / Rule fields (Add/Edit Dialog)

Jede Regel hat / each rule has the following attributes:

- **enabled**
- **name**
- **target folder**
- **extensions (comma)**
- **MIME prefixes (comma)**
- **name regex**
- **path contains**
- **min size (MB)**
- **max size (MB)**
- **OK / Cancel**

---

## 4.4 Performance / Performance

### Hash threads (Default: 4)

DE:
Parallelität beim Hashen. Mehr hilft bei CPU-Limit, weniger bei I/O-Limit (HDD/NAS).

EN:
Parallel hashing. Helps when CPU-bound, less when I/O-bound (HDD/NAS).


### Copy threads (Default: 2)

DE:
Parallelität beim Kopieren. Zu hoch kann HDD/NAS verschlechtern (Seek/Overhead).

EN:
Parallel copying. Too high can hurt HDD/NAS (seek/overhead).


### Hash chunk (MB) (Default: 4)

DE:
Blockgröße fürs Lesen beim Hashing. Größer kann große Dateien beschleunigen, Default ist meist ok.

EN:
Read block size for hashing. Larger can speed up large files; default is usually fine.

---

# 5. Modi / Modes 

## 5.1 Archive

DE:
- Kopiert neue Dateien nach Rules.
- Skip bei Duplikaten.
- **Keine Deletes**.

**Für:** „sicherer Import“.

EN:
- Copies new files per rules.
- Skips duplicates.
- **No deletes**.

**For:** safe imports.


## 5.2 Incremental

DE:
- Kopiert nur neue/geänderte Dateien.

**Für:** regelmäßige Backups ohne alles neu zu kopieren.

EN:
- Copies new/changed files only.

**For:** recurring backups without recopying everything.


## 5.3 Mirror

DE:
- Ziel im Mirror-Root soll dem Quellen-Stand entsprechen.
- Kopiert neue/geänderte Dateien.
- Löscht Dateien im Ziel, die in Quellen nicht mehr existieren – aber nur:
  - innerhalb des Mirror subfolder

**Für:** NAS-Sync / „Target sauber halten“.

EN:
- Target within mirror root should match the sources.
- Copies new/changed files.
- Deletes target files missing in sources, but only:
  - within the mirror subfolder

**For:** NAS sync / keeping target clean.

---



