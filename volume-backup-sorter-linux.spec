# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.building.datastruct import TOC
from PyInstaller.compat import is_win

block_cipher = None

APP_NAME = "volume-backup-sorter"
ENTRY = "volume_backup_sorter/__main__.py"

KEEP_QT_LANGS = ("de", "en", "es")

EXCLUDES = [
    # Drop QML/Quick/WebEngine
    "PyQt6.QtQml",
    "PyQt6.QtQuick",
    "PyQt6.QtQuickWidgets",
    "PyQt6.QtWebEngineCore",
    "PyQt6.QtWebEngineWidgets",
    "PyQt6.QtWebEngineQuick",
    "PyQt6.QtWebChannel",

    # Usually not needed
    "PyQt6.QtBluetooth",
    "PyQt6.QtNfc",
    "PyQt6.QtPositioning",
    "PyQt6.QtSensors",
    "PyQt6.QtSerialPort",
    "PyQt6.QtTest",
    "PyQt6.QtRemoteObjects",
]

def _norm(p: str) -> str:
    return p.replace("\\", "/")

def drop_by_dest_prefix(toc, prefix: str):
    prefix = _norm(prefix)
    out = [(d, s, t) for (d, s, t) in toc if not _norm(d).startswith(prefix)]
    return TOC(out)

def keep_qt_translations_only(toc, keep_langs):
    prefix = "PyQt6/Qt6/translations/"
    out = []
    for (dest, src, typ) in toc:
        d = _norm(dest)
        if d.startswith(prefix) and str(src).lower().endswith(".qm"):
            base = Path(src).name.lower()
            if any(f"_{lang}" in base for lang in keep_langs):
                out.append((dest, src, typ))
            continue
        out.append((dest, src, typ))
    return TOC(out)

a = Analysis(
    [ENTRY],
    pathex=["."],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=EXCLUDES,
    noarchive=True,   # onedir: faster startup
)

# QML
a.datas = drop_by_dest_prefix(a.datas, "PyQt6/Qt6/qml/")
a.binaries = drop_by_dest_prefix(a.binaries, "PyQt6/Qt6/qml/")

# langs
a.datas = keep_qt_translations_only(a.datas, KEEP_QT_LANGS)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    console=False,
    strip=True,
    upx=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,
    upx=False,
    name=APP_NAME,
)

