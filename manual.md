# Volume Backup Sorter – Bedienungsanleitung / User Manual

**Stand / Last updated:** 2025-12-19  
**Gilt für:** UI mit Hauptfenster (Active Profile, Target, Sources, Preview/Start/Cancel, Log) und Settings mit Tabs **General / Rules / Performance / Profiles**.

---

## Inhaltsverzeichnis / Table of Contents

- **Deutsch**
  - 1. Zweck
  - 2. Grundbegriffe
  - 3. Quickstart
  - 4. Hauptfenster
  - 5. Einstellungen (Zahnrad)
  - 6. General (Sprache, Modus, Konflikte, Symlinks, Mirror, Metadaten, Open-after-run)
  - 7. Modi (Archive, Incremental, Mirror)
  - 8. Name conflicts (Konfliktstrategien)
  - 9. Symlinks (Symlink-Strategien)
  - 10. Rules (Regeln) – komplett (inkl. Regex)
  - 11. Performance (Threads, Chunk)
  - 12. Profiles (Profile)
  - 13. Praxis-Beispiele (3 Rezepte)
  - 14. Troubleshooting
  - 15. Sicherheits-Checkliste
  - 16. Glossar
- **English**
  - (same structure)

---

# DEUTSCH

## 1. Zweck

Du gibst **Quellen** (Dateien/Ordner) + ein **Ziel** an. Die App erstellt einen **Plan (Preview)** und führt ihn aus: Dateien werden nach **Regeln** in eine **Zielstruktur kopiert**, **Duplikate** werden erkannt, und im **Mirror-Modus** können im Ziel **kontrolliert** Dateien entfernt werden.

---

## 2. Grundbegriffe (damit alles eindeutig ist)

- **Quelle (Source):** Was du importierst (Dateien/Ordner).  
- **Ziel (Target):** Wo das Backup landet (Ordner/Volume/NAS-Pfad).  
- **Plan / Preview:** „Trockenlauf“: die App berechnet, **was passieren würde** (kopieren/überspringen/löschen) + Mengen/Bytes.  
- **Regeln (Rules):** Entscheiden **wohin** eine Datei im Ziel kommt (z. B. `photos/`, `videos/`, …) – mit Filtern wie Extension, MIME, Regex, Pfad-Contains, Größe.  
- **Profil (Profile):** Gespeicherter Satz an Einstellungen (Modus, Regeln, Safety, Performance, Sprache …).  
- **Index/DB (intern):** Viele Backup-Tools halten eine Datenbank/Index (oft SQLite), um vorhandene Dateien schneller wiederzuerkennen. Ob und wie das hier passiert, siehst du indirekt über „Skip/Duplicate“ im Preview/Log.

---

## 3. Quickstart (60 Sekunden)

1) **App öffnen** → oben siehst du das **Active Profile**.  
2) **Target Folder** wählen:  
   - **Choose** = Zielpfad auswählen  
   - **Open** = Zielordner im Dateimanager öffnen  
3) Quellen hinzufügen:  
   - Drag & Drop in **Sources (drag and drop)**  
   - oder **Add files…** / **Add folder…**  
4) Optional: in der Quellenliste aufräumen:  
   - **Remove selected** = markierte Quelle entfernen  
   - **Clear all** = alle Quellen löschen  
5) **Preview** klicken → Plan prüfen (Copy/Skip/Delete + Bytes).  
6) **Start** klicken → Ausführung.  
7) Während des Runs: **Progress bar** + Status (**Ready** wenn fertig) + **Log** prüfen.  
8) Optional: **Cancel** (bricht sauber ab, macht nichts rückgängig).  
9) Nachher: Ergebnis im **Log** prüfen, ggf. **Clear Log**.

Minimalregel: **Mirror nie ohne Preview.** (Siehe Sicherheitscheckliste.)

---

## 4. Hauptfenster – alle Elemente erklärt

### 4.1 Active Profile
Zeigt das aktuell aktive Profil. Das Profil bestimmt:
- Modus (Archive / Incremental / Mirror)
- Konfliktverhalten (Name conflicts)
- Symlink-Verhalten
- Mirror-Subfolder + Delete-Whitelist
- Regelset
- Performance-Parameter (Threads/Chunk)
- optional UI-Sprache

**Wichtig:** Änderungen in Settings wirken i. d. R. auf das **aktive Profil** (oder werden beim Save dort gespeichert).

### 4.2 Target Folder: Choose / Open
- **Choose:** Zielordner auswählen.  
- **Open:** Zielordner im Dateimanager öffnen.

**Praxis-Regel:** Nutze für Mirror **immer** einen klaren Unterordner (Mirror subfolder), damit nicht aus Versehen „das ganze Target“ als Spiegelbereich gilt.

### 4.3 Sources (Drag & Drop + Buttons)
Hier sammelst du deine Eingaben.

- **Drag & Drop:** Dateien/Ordner hineinziehen.  
- **Add files…:** Einzelne oder mehrere Dateien auswählen.  
- **Add folder…:** Einen Ordner hinzufügen (rekursiv).  
- **Remove selected:** Entfernt nur die markierten Einträge aus der Quellenliste.  
- **Clear all:** Leert die Quellenliste vollständig.

**Hinweise:**
- Doppelte Quellen (z. B. einmal Ordner + einmal Unterordner) führen oft zu mehr Arbeit/mehr Logs. Räum das vor dem Start auf.
- Sehr große Quellen (Millionen Files) → erst Rules sauber machen, dann Preview.

### 4.4 Preview
**Preview ist der wichtigste Sicherheits-Schritt.**  
Die App berechnet einen Plan und zeigt typischerweise:
- **Copy:** wie viele Dateien/Bytes kopiert werden
- **Skip:** wie viele übersprungen werden (z. B. Duplikat schon im Ziel)
- **Delete (nur Mirror):** welche Dateien im Ziel entfernt würden (wenn erlaubt)

**Was du hier prüfst:**
- Ist das **Target** korrekt?
- Sind die Regeln korrekt (landet z. B. `IMG_*.JPG` wirklich unter `photos/`)?
- Kommt irgendwo **Delete** vor? Wenn ja: ist das genau der Bereich, den du spiegeln willst?

### 4.5 Start
Führt den Plan aus:
- Dateien werden verarbeitet (Hash/Check → Regel → Zielpfad → Copy/Skip/Delete)
- Fortschritt über **Progress bar**
- Aktionen im **Log**

### 4.6 Cancel
Bricht den aktuellen Lauf ab.  
**Wichtig:** Abbruch = „so schnell wie möglich sauber stoppen“.  
Bereits kopierte Dateien bleiben kopiert. Bereits gelöschte Dateien bleiben gelöscht. Kein Undo.

### 4.7 Clear Log
Löscht/cleart die Loganzeige im UI.  
Das verändert keine Dateien, nur die Anzeige.

### 4.8 Log-Anzeige
Protokolliert, was passiert:
- Copy / Skip / Delete (Mirror)
- Konfliktlösungen (Rename/Overwrite/Skip)
- Fehler (Permissions, IO, Regex-Fehler, locked files, …)
- Safety-Blocker (z. B. Delete durch Whitelist blockiert)

### 4.9 Progress bar & Status („Ready“)
- Progress zeigt Bearbeitungsfortschritt.
- Status **Ready** bedeutet: kein Lauf aktiv (oder Lauf fertig).

### 4.10 Zahnrad (Settings)
Öffnet die Einstellungen (Tabs).  
Jeder Tab hat **Save** und **Close**:
- **Save:** Änderungen übernehmen/speichern (typisch: ins aktive Profil).
- **Close:** Dialog schließen (ohne weitere Änderungen, je nach App: ungespeicherte Änderungen verwerfen).

---

## 5. Einstellungen – Überblick (Zahnrad)

Es gibt vier Bereiche:
1) **General** – Sprache, Modus, Konflikte, Symlinks, Mirror, Metadaten, Open-after-run  
2) **Rules** – Rule-Liste + Add/Edit/Delete  
3) **Performance** – Hash threads / Copy threads / Hash chunk  
4) **Profiles** – aktives Profil + ADD / Copy / Rename / Delete

---

## 6. Settings: General – alles erklärt

### 6.1 Language (English / Deutsch / Spanish)
Stellt die UI-Sprache um.

**Hinweis:** Wenn nach einem Sprachwechsel einzelne Felder nicht übersetzt sind, ist das i18n-typisch (Strings nicht in Übersetzungsfunktion oder UI nicht „retranslated“). Das ist ein App-Problem, nicht dein Fehler.

### 6.2 Mode (Archive / Incremental / Mirror)
Siehe Kapitel 7 „Modi“.

### 6.3 Name conflicts (Konflikte)
Wenn im Ziel bereits **ein Dateiname existiert**, aber die App dennoch „eine Datei dahin schreiben“ will, braucht sie eine Strategie.

Optionen:
- **rename _1**
- **overwrite**
- **skip**
- **rename with hash**
- **rename with timestamp**

Details & Beispiele siehe Kapitel 8.

### 6.4 Symlinks
Wenn Quellen Symlinks enthalten (Linux/macOS, auch unter Windows möglich), entscheidet die App, was sie damit macht:
- **skip**
- **copy as symlink**
- **follow**

Details siehe Kapitel 9.

### 6.5 Mirror subfolder (Textinput)
Definiert den Unterordner im Target, in dem Mirror arbeitet.

- Target: `/mnt/nas/backups`
- Mirror subfolder: `PC1_SYNC`
- Effektives Mirror-Root: `/mnt/nas/backups/PC1_SYNC`

**Bedeutung:** Mirror-Deletes (und Mirror-Copies) sollen nur in diesem Bereich stattfinden.

**Safety:** Mirror subfolder ist dein „Airbag“. Ohne ihn wäre Mirror potenziell gefährlich, weil „Target Root“ zu groß ist.

### 6.6 Delete whitelist (extensions) (Textinput)
Kommagetrennte Liste von Extensions, die Mirror löschen darf.

Beispiel:
`jpg,jpeg,png,heic,mp4,mov,pdf,txt`

**Wirkung (Mirror):**
- Mirror will `old.jpg` löschen → erlaubt nur, wenn `jpg` in der Whitelist steht.
- Steht `jpg` nicht drin → Delete wird blockiert und geloggt.

**Praxis:**  
Start: konservativ (z. B. nur `tmp,log`).  
Später: erweitern, bis echtes Spiegeln möglich ist.

### 6.7 Preserve metadata
Wenn aktiv, versucht die App Metadaten zu erhalten:
- Timestamp (mtime/atime/ctime je nach OS und Copy-Methode)
- ggf. Permissions

**Wichtige Realität:**
- macOS, Linux, Windows und SMB/NAS verhalten sich unterschiedlich.
- Nicht alles lässt sich 1:1 übernehmen (Owner/ACL, resource forks, …).

### 6.8 Open target after run
Wenn aktiv, öffnet die App nach einem erfolgreichen Run den Target-Ordner im Dateimanager.

---

## 7. Modi – exakt und ohne Schönreden

### 7.1 Archive (append-only)
- Kopiert neue Dateien nach Rules ins Ziel.
- Erkanntes Duplikat → **Skip**.
- Löscht im Ziel **niemals**.

**Ideal für:** „Ich will nichts riskieren.“

### 7.2 Incremental (nur Neues/Geändertes)
- Kopiert nur Dateien, die **neu** sind oder sich **geändert** haben.
- Normalerweise keine Deletes (das ist kein Mirror).
- „Geändert“ kann je nach Implementierung über size/mtime und/oder Hash erkannt werden.

**Ideal für:** regelmäßige Backups derselben Quelle(n), ohne alles neu zu kopieren.

### 7.3 Mirror (spiegeln, inklusive Deletes)
- Ziel soll im Mirror-Root wie die Quelle(n) aussehen.
- Kopiert neue/geänderte Dateien.
- Löscht Dateien im Ziel, die es in den Quellen nicht mehr gibt – **aber nur**, wenn:
  - sie im Mirror-Bereich liegen (praktisch: innerhalb des **Mirror subfolder**), und
  - ihre Extension in der **Delete whitelist** erlaubt ist.

**Ideal für:** Sync-Ordner auf NAS, „Target soll sauber sein“.  
**Risiko:** Mirror kann Daten löschen → Preview + Whitelist + Subfolder sind Pflicht.

---

## 8. Name conflicts – Konfliktstrategien (mit Beispielen)

**Situation:** Zielpfad soll `photos/IMG_0001.jpg` sein, aber diese Datei existiert bereits im Ziel.

### 8.1 skip
Die App schreibt nicht drüber.
- Wenn die existierende Datei identisch ist → perfekt.
- Wenn sie anders ist → du verlierst die neue Version (wird im Log sichtbar).

**Gut für:** „Nichts überschreiben, Sicherheit first.“

### 8.2 overwrite
Die App ersetzt die Ziel-Datei.

**Risiko:** Du überschreibst ggf. etwas Wichtiges.  
**Nur sinnvoll**, wenn du genau weißt, dass Ziel „der Wahrheitsspiegel“ sein soll (z. B. Mirror + du vertraust der Quelle).

### 8.3 rename _1
Die App benennt um:
- `IMG_0001.jpg` existiert → neue Datei wird `IMG_0001_1.jpg`
- nächste Kollision: `_2`, `_3`, …

**Gut für:** Archive-Imports, wo Name-Kollisionen häufig sind (z. B. Kameras/WhatsApp).

### 8.4 rename with hash
Die App hängt einen Hash an, z. B.:
- `IMG_0001__a1b2c3d4.jpg`

**Vorteil:** Konfliktlösung ist stabil und deterministisch (gleicher Inhalt → gleicher Hash).  
**Nachteil:** Dateinamen werden länger/„hässlicher“, aber dafür eindeutig.

### 8.5 rename with timestamp
Die App hängt einen Zeitstempel an, z. B.:
- `IMG_0001__2025-12-19_092233.jpg`

**Gut für:** Logs/Exports, bei denen „wann importiert“ wichtiger ist als Content-Identität.  
**Nachteil:** Bei wiederholten Runs kann derselbe Inhalt mehrfach auftauchen, wenn Dedup nicht greift.

---

## 9. Symlinks – was passiert wirklich?

Symlinks sind Verweise, keine echten Dateien. Das ist in Backups ein Minenfeld.

### 9.1 skip
Symlinks werden ignoriert.

**Gut für:** sichere Backups, wenn du keine Symlink-Struktur brauchst.  
**Nachteil:** du verlierst ggf. „Verknüpfungslogik“.

### 9.2 copy as symlink
Symlink wird im Ziel als Symlink erstellt.

**Gut für:** wenn du Strukturen exakt replizieren willst (z. B. Dev-Workspaces).  
**Achtung:** Zielsystem muss Symlinks unterstützen (Windows je nach Setting/Permissions).

### 9.3 follow
Die App folgt dem Link und kopiert die **Zieldatei/den Zielordner**.

**Risiken:**
- Du kopierst plötzlich viel mehr (Symlink zeigt auf große Ordner).
- Zyklische Links → theoretisch Endlosschleifen (gute Tools verhindern das, aber nicht blind vertrauen).

**Empfehlung:** Follow nur, wenn du weißt, dass deine Quellen sauber sind.

---

## 10. Rules – vollständige Erklärung (inkl. Regex ultra genau)

### 10.1 Was Rules machen
Für jede Datei wird entschieden:
1) **Matcht eine Regel?**  
2) Wenn ja: **in welchen Zielordner** (Target folder) wird kopiert?  
3) Wenn mehrere matchen: **welche gewinnt?** (typisch: „erste passende Regel gewinnt“)  
4) Wenn keine matcht: **Fallback** (empfohlen: Catch-all-Regel am Ende, z. B. `other/`)

### 10.2 Die Rules-Liste (Tab „Rules“)
- Die Regeln werden angezeigt (meist mit Reihenfolge).
- Aktionen:
  - **Add** (öffnet Rule-Dialog)
  - **Edit**
  - **Delete**

**Wichtig zur Reihenfolge:**  
Falls die UI „Drag to reorder“ oder „Priorität“ hat: nutze das.  
Wenn nicht: plane deine Regeln so, dass spezifische Regeln vor generischen kommen.

Beispiel Reihenfolge:
1) Screenshots (Regex/Pfad) → `photos/screenshots/`
2) Bilder (Extensions) → `photos/`
3) Videos → `videos/`
4) Catch-all → `other/`

### 10.3 Rule-Dialog: Felder und Logik

Beim **Add** oder **Edit** siehst du folgende Felder:

#### 10.3.1 enabled
- **On:** Regel wird angewendet.
- **Off:** Regel bleibt gespeichert, wird aber ignoriert.

#### 10.3.2 name
Freier Name zur Orientierung (z. B. „Bilder“, „WhatsApp“, „Screenshots“).

#### 10.3.3 target folder
Zielunterordner **relativ zum effektiven Target-Root**.

- Archive/Incremental: relativ zu `Target`
- Mirror: relativ zu `Target/<Mirror subfolder>` (praktisch)

Beispiele:
- `photos/`
- `videos/`
- `docs/pdf/`
- `other/`

**Best Practice:** Immer mit `/` enden (rein kosmetisch, aber klar).

#### 10.3.4 extensions (comma)
Kommagetrennte Liste ohne Punkt:

- `jpg,jpeg,png,heic`
- `mp4,mov,mkv`

**Typisches Verhalten:** case-insensitiv.  
**Achtung:** Manche Dateien haben keine Extension → dafür entweder MIME/Regex oder eine Catch-all-Regel.

#### 10.3.5 MIME prefixes (comma)
Filtert nach MIME-Typ-Präfixen (z. B. aus `mimetypes`):
- `image/`
- `video/`
- `audio/`
- `text/`
- `application/`

Beispiele:
- Bilder: `image/`
- Videos: `video/`
- PDFs: `application/pdf` (hier ist es kein Präfix, sondern ein konkreter Typ – je nach Implementierung geht beides; sicherer ist `application/` + Extension `pdf`)

**Warum nützlich?**
- Dateien ohne Extension
- „falsche“ Extensions

#### 10.3.6 name regex
Regex gegen den **Dateinamen** (typisch: basename, ohne Pfad).

Beispiele:
- Nur `IMG_`-Dateien: `^IMG_`
- Nur `Screenshot`-Dateien: `(?i)^screenshot`
- Nur `DSC_####`: `^DSC_\d{4}\.`

Regex ist mächtig und kann langsam sein – siehe ReDoS (unten).

#### 10.3.7 path contains
Ein einfacher Substring-Filter gegen den **relativen Pfad**.

Beispiele:
- `DCIM/Camera`
- `WhatsApp Images`
- `Screenshots`

**Hinweis:** „contains“ heißt normalerweise: muss irgendwo im Pfad vorkommen. Groß-/Kleinschreibung hängt von Implementierung ab. Wenn du sicher sein willst: nutze Regex.

#### 10.3.8 min size (MB) / max size (MB)
Dateigröße als Filter.

Beispiele:
- Min size: `10` → nur Dateien >= 10 MB (typisch Videos)
- Max size: `1` → nur Dateien <= 1 MB (z. B. Thumbnails/Icons)

**Sinnvoll für:**
- Videos vs Fotos trennen
- „riesige“ Dateien separat behandeln (z. B. `large/`)

### 10.4 Matching-Logik einer Regel (so solltest du es verstehen)
Eine Regel matcht, wenn **alle gesetzten Felder** passen:

- enabled = an  
- UND (extensions matcht ODER extensions leer)  
- UND (MIME matcht ODER MIME leer)  
- UND (name regex matcht ODER regex leer)  
- UND (path contains passt ODER leer)  
- UND (min/max size passt ODER leer)

**Wenn du mehrere Filter setzt, wird die Regel enger.**  
Das ist gut – aber du kannst dich auch aus Versehen „0 Treffer“ bauen. Preview zeigt’s.

### 10.5 Regex – ultra genau (Python-Style)

> Annahme: Regex-Engine ist Python `re` (sehr üblich). Wenn dein Tool anders ist, merkst du das an Syntax/Fehlermeldungen.

#### 10.5.1 Basics
- `^` Start der Zeichenkette  
- `$` Ende  
- `.` beliebiges Zeichen  
- `.*` beliebig viele (greedy)  
- `.*?` beliebig viele (lazy)  
- `\d` Ziffer  
- `\w` Wortzeichen (A–Z, a–z, 0–9, _)  
- `[...]` Zeichenklasse  
- `( … )` Gruppe  
- `(?: … )` nicht-capturing Gruppe  
- `(?P<name> … )` Named group (wenn Zielpfade Gruppen verwenden – falls nicht: trotzdem gut lesbar)

#### 10.5.2 Anchoring (häufigster Fehler)
Ohne `^`/`$` matcht Regex irgendwo im String.

- Zu offen: `jpg`  
  Matcht auch `notjpg.txt` (wenn Pfad/Name so aussieht)
- Besser: `(?i)\.jpe?g$`  
  Matcht nur `.jpg` oder `.jpeg` am Ende (case-insensitiv)

#### 10.5.3 Case-insensitive
- Inline: `(?i)` am Anfang oder in Gruppe  
  Beispiel: `(?i)^screenshot`
- Oder Flag in Code (nicht im UI)

#### 10.5.4 Escaping
Backslash ist in Regex ein Escape. Für „Punkt“ brauchst du `\.`.

Beispiele:
- Endet auf `.png`: `(?i)\.png$`
- „(“ im Text matchen: `\(`

#### 10.5.5 Beispiele (Name-Regex)
- WhatsApp Bilder oft so: `IMG-2025...`  
  Regex: `^IMG-\d{8}-WA\d+`
- iPhone Live Photos (manchmal `IMG_1234.MOV` + `.HEIC`):  
  Name-Regex: `^IMG_\d{4}\.(?i:mov|heic)$`

#### 10.5.6 ReDoS / Performance-Fallen
Manche Regex sind extrem langsam (catastrophic backtracking), z. B.:
- `(.*)+`
- `(.+)+`
- `(.+)*`
- verschachtelte Quantifier

**Regel:** Wenn du `.*` nutzt, halte es kurz und anchor sauber.

### 10.6 Empfohlenes Rule-Set (praktisches Default)
1) Bilder → `photos/`  
   - extensions: `jpg,jpeg,png,heic,webp`  
   - MIME prefixes: `image/` (optional)
2) Videos → `videos/`  
   - extensions: `mp4,mov,mkv`  
   - min size: `10` (optional)
3) Dokumente → `docs/`  
   - extensions: `pdf,docx,xlsx,pptx,txt`
4) Archive → `archives/`  
   - extensions: `zip,7z,rar,tar,gz`
5) Catch-all → `other/`  
   - (keine Filter, enabled an)

---

## 11. Performance – Threads & Chunk

### 11.1 Hash threads (Default: 4)
Wie viele Worker parallel Hashes berechnen.

- Mehr Threads helfen, wenn CPU der Flaschenhals ist.
- Auf HDD/NAS ist oft I/O der Flaschenhals → zu viele Threads bringen dann wenig.

**Empfehlung:**
- Desktop CPU + SSD: 4–8
- NAS über SMB + HDD: 2–4

### 11.2 Copy threads (Default: 2)
Wie viele Kopiervorgänge parallel laufen.

- Zu viele parallele Copies können HDD/NAS zerstückeln (Seek, Overhead).
- Für viele kleine Dateien ist parallel manchmal gut, manchmal schlecht – testen.

**Empfehlung:**
- Lokale SSD: 2–4
- Einzelne HDD: 1–2
- NAS: 1–2 (oft stabiler)

### 11.3 Hash chunk (MB) (Default: 4)
Blockgröße fürs Hashing (wie viel pro Read).

- Größer = weniger Syscalls, oft schneller auf großen Dateien.
- Zu groß = mehr RAM/Cache-Pressure, manchmal schlechter bei vielen kleinen Dateien.

**Empfehlung:**
- Default 4 MB ist ein guter Sweet Spot.
- Große Video-Backups: 8–16 MB testen.

---

## 12. Profiles – aktiv, anlegen, kopieren, umbenennen, löschen

### 12.1 Active profile
Zeigt, welches Profil gerade aktiv ist. Alle Settings + Rules beziehen sich auf dieses Profil.

### 12.2 ADD
Erstellt ein neues Profil.
Typisch: du gibst einen Namen, und es wird mit aktuellen Settings initialisiert.

### 12.3 Copy
Dupliziert das aktuelle Profil (perfekt, um Varianten zu bauen: „Phone Archive“ vs „Phone Mirror“).

### 12.4 Rename
Benennt das Profil um.

### 12.5 Delete
Löscht ein Profil.

**Safety-Hinweis:** Lösch nie dein einzig funktionierendes Profil ohne Backup. Profile sind deine Wiederholbarkeit.

---

## 13. Praxis-Beispiele (konkret)

### Beispiel A: „Phone Import (Archive, sicher)“
Ziel: Alles vom Handy importieren, nichts löschen, Duplikate skippen.

- General:
  - Mode: **Archive**
  - Name conflicts: **rename with hash** (robust)
  - Symlinks: **skip**
  - Preserve metadata: **on**
  - Open target after run: **on**
- Rules:
  1) Bilder → `photos/` (jpg,jpeg,png,heic,webp)
  2) Videos → `videos/` (mp4,mov)
  3) Catch-all → `other/`

Workflow:
1) Target wählen: `~/Backups/PhoneArchive`
2) Ordner `DCIM/` droppen
3) Preview prüfen → Start

### Beispiel B: „Projektbackup (Incremental, schnell)“
Ziel: Dev-Projekt regelmäßig sichern, ohne jedes Mal alles zu kopieren.

- General:
  - Mode: **Incremental**
  - Name conflicts: **overwrite** (wenn du Ziel als „aktueller Stand“ willst) oder **skip** (wenn du konservativ bist)
  - Symlinks: **copy as symlink** (für Node/Python venv eher skip, je nach Setup)
  - Preserve metadata: optional
- Rules:
  - Source ist ohnehin sortiert → oft reicht Catch-all in `project/`
  - Optional: `node_modules` via path contains filtern (wenn du dafür eine „exclude“-Möglichkeit hast; falls nicht: am besten Source ohne node_modules wählen)

Workflow:
1) Target: `/mnt/nas/projects_backup/`
2) Source: Projektordner
3) Preview → Start

### Beispiel C: „NAS Sync (Mirror, danger-controlled)“
Ziel: NAS-Ordner soll exakt Spiegel sein (inkl. Deletes), aber nur im Unterordner.

- General:
  - Mode: **Mirror**
  - Mirror subfolder: `PC1_SYNC`
  - Delete whitelist: `jpg,jpeg,png,heic,mp4,mov,pdf,txt,docx,xlsx` (anfangs kleiner!)
  - Name conflicts: **overwrite** (klassisch Mirror) oder **rename with hash** (sicherer, aber weniger „Mirror-Feeling“)
  - Preserve metadata: on
- Rules:
  - Zielordner relativ im Mirror: `photos/`, `docs/` etc.

Workflow (wichtig):
1) Target: `/mnt/nas/backups/`
2) Mirror subfolder: `PC1_SYNC`
3) Preview: Prüfe, ob Deletes nur innerhalb `/mnt/nas/backups/PC1_SYNC` passieren.
4) Erst dann Start.

---

## 14. Troubleshooting (realistische Fälle)

### 14.1 Permission denied / Zugriff verweigert
- Quelle/Ziel nicht lesbar/schreibbar.
- Linux: Mount-Optionen, Eigentümer, ACL.
- NAS: SMB-Rechte, „noexec“/„nosuid“ ist egal, aber „ro“ nicht.
- macOS: „Dateien & Ordner“-Berechtigungen (TCC).

### 14.2 Mirror löscht zu wenig
- Extension nicht in Delete whitelist → Delete wird blockiert (Log!)
- Du bist nicht im Mirror subfolder (falscher Subfolder oder leerer Subfolder) → App löscht nicht, weil Scope nicht passt.

### 14.3 Mirror will „zu viel“ löschen
- Falsches Target oder falscher Mirror subfolder.
- Du hast Quellen gewechselt (z. B. nur Teilordner gedroppt) → Mirror denkt „alles andere ist weg“.

**Fix:** Cancel, Settings prüfen, Sources korrekt auswählen, Preview neu.

### 14.4 Regex-Fehler
- Ungültige Regex → Regel matcht nie oder Save wird blockiert.
- Fix: Regex vereinfachen, anchor nutzen, Sonderzeichen escapen.

### 14.5 Performance ist schlecht
- Viele kleine Dateien → I/O-Overhead.  
  Lösung: Rules/Filter schärfen, Copy threads nicht zu hoch.
- NAS über WLAN → Flaschenhals.  
  Lösung: Kabel.

---

## 15. Sicherheits-Checkliste (kurz, aber ernst)

- Mirror nur mit **Mirror subfolder** verwenden.
- Mirror nur mit **Preview** starten.
- Delete whitelist anfangs klein, dann kontrolliert erweitern.
- Bei „overwrite“ doppelt hinschauen.
- Symlinks „follow“ nur, wenn du das Ergebnis wirklich willst.
- Backups sind erst Backups, wenn du einen Restore testest.

---

## 16. Glossar (kurz)
- **Copy:** Datei wird geschrieben/kopiert.
- **Skip:** Datei wird bewusst nicht kopiert (z. B. Duplikat oder Konfliktstrategie).
- **Delete:** Datei wird entfernt (nur Mirror, nur wenn erlaubt).
- **Rule:** Filter + Zielordnerzuweisung.
- **Profile:** gespeicherte Job-Konfiguration.

---

# ENGLISH

## 1. Purpose

You provide **sources** (files/folders) and a **target**. The app creates a **plan (Preview)** and then executes it: files are **copied into an organized structure** based on **rules**, **duplicates** are detected, and in **Mirror mode** the app may **delete** certain target files in a controlled way.

---

## 2. Core concepts

- **Source:** what you add (files/folders).  
- **Target:** where output is written (backup folder, NAS path).  
- **Preview / Plan:** dry run: what would be copied/skipped/deleted + counts/bytes.  
- **Rules:** decide where a file goes (target subfolder) based on filters (extension, MIME, regex, path contains, size).  
- **Profile:** saved set of settings (mode, rules, safety, performance, language…).  
- **Index/DB (internal):** many backup tools keep an internal index (often SQLite) to speed up duplicate detection; you’ll see the effect as “Skip/Duplicate” in Preview/Log.

---

## 3. Quickstart

1) Open the app → check **Active Profile**.  
2) Choose your **Target Folder**:
   - **Choose** selects the target path
   - **Open** opens it in your file manager  
3) Add sources:
   - drag & drop into **Sources**
   - or **Add files…** / **Add folder…**  
4) Clean up the list:
   - **Remove selected**
   - **Clear all**  
5) Click **Preview** and verify the plan.  
6) Click **Start** to run.  
7) Watch **Progress bar** + **Log**.  
8) **Cancel** stops as soon as possible (no undo).  
9) **Clear Log** clears only the UI log view.

Rule of sanity: **Never run Mirror without Preview.**

---

## 4. Main window – every element

### 4.1 Active Profile
Shows which profile is active. The profile defines:
- Mode (Archive / Incremental / Mirror)
- Name conflict behavior
- Symlink behavior
- Mirror subfolder + delete whitelist
- Rule set
- Performance parameters (threads/chunk)
- optional UI language

### 4.2 Target Folder: Choose / Open
- **Choose:** pick the target directory.
- **Open:** open the target in your file manager.

Mirror safety: always use a dedicated **Mirror subfolder** so Mirror does not “see” your entire target root.

### 4.3 Sources
- Drag & drop area
- **Add files…** / **Add folder…**
- **Remove selected**
- **Clear all**

Avoid adding overlapping sources (same folder twice) unless you intentionally want that.

### 4.4 Preview
The most important safety step. Typically shows:
- Copy count/bytes
- Skip count/bytes (duplicates already present)
- Delete count/bytes (Mirror only, if allowed)

Verify target + rules + any deletes before you run.

### 4.5 Start
Executes the plan. Progress shows work done; log records actions/errors.

### 4.6 Cancel
Stops the run as soon as possible. Already completed actions stay completed.

### 4.7 Clear Log
Clears the log view only.

### 4.8 Log
Records:
- copy/skip/delete
- conflict resolution (rename/overwrite/skip)
- errors (permissions, I/O, regex)
- safety blocks (delete blocked by whitelist)

### 4.9 Settings (gear)
Opens settings tabs. Each tab has **Save** and **Close**:
- **Save:** apply/store changes (typically into the active profile)
- **Close:** close the dialog (unsaved changes may be discarded)

---

## 5. Settings – overview

Tabs:
1) **General**
2) **Rules**
3) **Performance**
4) **Profiles**

---

## 6. Settings: General

### 6.1 Language
English / German / Spanish.

If some texts don’t change after switching, that’s an app i18n issue (missing translation keys / missing UI retranslate).

### 6.2 Mode
Archive / Incremental / Mirror (see section 7).

### 6.3 Name conflicts
Strategies when the destination filename already exists:
- rename _1
- overwrite
- skip
- rename with hash
- rename with timestamp

See section 8 for detailed behavior and examples.

### 6.4 Symlinks
How to handle symlinks found in sources:
- skip
- copy as symlink
- follow

See section 9.

### 6.5 Mirror subfolder
Text input that defines where Mirror operates inside the target.

Example:
- Target: `/mnt/nas/backups`
- Mirror subfolder: `PC1_SYNC`
- Effective mirror root: `/mnt/nas/backups/PC1_SYNC`

This is your primary safety boundary for Mirror operations.

### 6.6 Delete whitelist (extensions)
Comma-separated extensions that Mirror is allowed to delete.

Example:
`jpg,jpeg,png,heic,mp4,mov,pdf,txt`

If Mirror wants to delete `old.jpg` but `jpg` is not in the whitelist, deletion is blocked and logged.

Start conservative, expand only after Preview confirms everything.

### 6.7 Preserve metadata
If enabled, the app attempts to preserve timestamps and possibly permissions.

Behavior differs across platforms and SMB/NAS filesystems. Don’t assume perfect 1:1 preservation.

### 6.8 Open target after run
Automatically opens the target folder after a successful run.

---

## 7. Modes

### 7.1 Archive (append-only)
- Copies new files according to rules.
- Duplicates → skip.
- No deletes, ever.

Best for: safest “import and keep” backups.

### 7.2 Incremental
- Copies only new/changed files.
- Typically no deletes.
- “Changed” may be detected via size/mtime and/or hashing depending on implementation.

Best for: frequent backups of the same sources without recopying everything.

### 7.3 Mirror
- Target should match sources within the mirror root.
- Copies new/changed files.
- Deletes target files that no longer exist in sources, but only:
  - inside the mirror root (effectively controlled by **Mirror subfolder**), and
  - with extensions allowed by **Delete whitelist**.

Best for: NAS sync folders.  
Risk: deletes are real → always Preview.

---

## 8. Name conflicts (detailed)

Scenario: Destination wants `photos/IMG_0001.jpg`, but it already exists.

### 8.1 skip
Does not write. Safe, but you may miss updates if the existing file differs.

### 8.2 overwrite
Replaces the target file. Risky unless your workflow demands it (often Mirror).

### 8.3 rename _1
Creates `IMG_0001_1.jpg`, then `_2`, etc. Great for camera/phone imports.

### 8.4 rename with hash
Appends a hash suffix to guarantee uniqueness and stability.

### 8.5 rename with timestamp
Appends a timestamp. Useful for “import time” tracking, but can create multiple copies if dedupe doesn’t prevent it.

---

## 9. Symlinks (detailed)

### 9.1 skip
Ignore symlinks.

### 9.2 copy as symlink
Recreate the symlink in the target. Requires symlink support on the target system.

### 9.3 follow
Copy the link target’s content. Can explode backup size and may create cycles if your sources contain weird links.

Recommendation: follow only if you fully understand your source tree.

---

## 10. Rules (complete, incl. regex)

### 10.1 What rules do
For each file:
1) determine which rule matches
2) route into a target subfolder
3) resolve conflicts (name conflicts setting)

Most systems use “first matching rule wins”. Keep specific rules above generic rules.

### 10.2 Rules list
- Shows all rules
- **Add / Edit / Delete**

### 10.3 Rule dialog fields

- **enabled:** on/off
- **name:** descriptive label
- **target folder:** relative path inside the effective target root
- **extensions (comma):** `jpg,jpeg,png`
- **MIME prefixes (comma):** `image/`, `video/`, …
- **name regex:** regex for filename (basename)
- **path contains:** substring filter on relative path
- **min size (MB)** / **max size (MB)**

### 10.4 Rule matching logic
A rule matches if all specified filters match (empty filter = “don’t care”). Tight rules are good—until you accidentally build a rule that matches nothing. Preview reveals that.

### 10.5 Regex deep dive (Python-style)
Assuming Python `re`:

- `^` start, `$` end
- `.` any char
- `.*` greedy, `.*?` lazy
- `\d`, `\w`, `[...]`, groups `( )`
- Case-insensitive: `(?i)`

Anchoring is the most common mistake:
- too broad: `jpg`
- good: `(?i)\.jpe?g$`

Avoid catastrophic backtracking patterns like `(.*)+` or `(.+)*` on large datasets.

### 10.6 Suggested default rule set
1) Photos → `photos/` (extensions: `jpg,jpeg,png,heic,webp`, MIME: `image/` optional)
2) Videos → `videos/` (extensions: `mp4,mov,mkv`, min size optional)
3) Docs → `docs/` (extensions: `pdf,docx,xlsx,pptx,txt`)
4) Archives → `archives/` (extensions: `zip,7z,rar,tar,gz`)
5) Catch-all → `other/` (no filters)

---

## 11. Performance

### 11.1 Hash threads (default 4)
Parallel hashing workers. Useful when CPU-bound; less useful when I/O-bound.

### 11.2 Copy threads (default 2)
Parallel copy workers. Too many can hurt HDD/NAS performance.

### 11.3 Hash chunk (MB) (default 4)
Read block size for hashing. Larger can speed up large files; default is usually a good compromise.

---

## 12. Profiles

- **Active profile:** current selection
- **ADD:** create a new profile (often starting from current settings)
- **Copy:** duplicate current profile
- **Rename:** rename current profile
- **Delete:** remove a profile

Profiles are what make your backups repeatable and safe. Treat them like “job definitions”.

---

## 13. Practical recipes

### A) Phone import (Archive)
Archive mode, rename with hash, photos/videos rules, Preview then Start.

### B) Project backup (Incremental)
Incremental mode, conservative conflict strategy, symlink strategy depending on project, optional rules.

### C) NAS sync (Mirror, controlled)
Mirror mode, mirror subfolder set, delete whitelist set, Preview must show deletes only inside mirror root.

---

## 14. Troubleshooting

- Permission denied: fix filesystem permissions/mounts/macOS privacy access.
- Mirror deletes too little: whitelist blocks extensions; mirror subfolder mismatch.
- Mirror wants to delete too much: wrong target/subfolder, or incomplete sources selected.
- Regex errors: simplify, anchor, escape.
- Slow runs: too many small files, slow network, too many threads.

---

## 15. Safety checklist

- Mirror only with a dedicated **mirror subfolder**.
- Always **Preview** before Mirror.
- Start with a small **delete whitelist**, expand carefully.
- Be careful with **overwrite**.
- Use **follow symlinks** only if you know what that implies.
- A backup is only real after a restore test.

