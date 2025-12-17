# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files

block_cipher = None

pyqt6_datas = collect_data_files("PyQt6", include_py_files=False)
pyqt6_bins  = collect_dynamic_libs("PyQt6")

excludes = [
    
    "PyQt6.QtQml",
    "PyQt6.QtQuick",
    "PyQt6.QtQuickWidgets",
    "PyQt6.QtWebEngineCore",
    "PyQt6.QtWebEngineWidgets",
    "PyQt6.QtWebEngineQuick",
    "PyQt6.QtWebChannel",

   
    "PyQt6.QtBluetooth",
    "PyQt6.QtNfc",
    "PyQt6.QtPositioning",
    "PyQt6.QtSensors",
    "PyQt6.QtSerialPort",
    "PyQt6.QtSql",
    "PyQt6.QtTest",
    "PyQt6.QtRemoteObjects",
]

a = Analysis(
    ["volume_backup_sorter/__main__.py"],
    pathex=["."],
    binaries=pyqt6_bins,
    datas=pyqt6_datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=excludes,
    noarchive=True,   # schnellere Starts (mehr Files, aber flotter)
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="volume-backup-sorter",
    debug=False,
    strip=True,
    upx=False,        
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=True,
    upx=False,
    name="volume-backup-sorter"
)

app = BUNDLE(
    coll,
    name="Volume Backup Sorter.app",
    bundle_identifier="com.janluca.volume-backup-sorter",
    info_plist={
        "CFBundleName": "Volume Backup Sorter",
        "CFBundleDisplayName": "Volume Backup Sorter",
        "CFBundleShortVersionString": "0.3.0",
        "CFBundleVersion": "0.3.0",
        "NSHighResolutionCapable": True,
        # Optional
        # "NSDocumentsFolderUsageDescription": "Zugriff auf Dokumente für Backups.",
        # "NSDownloadsFolderUsageDescription": "Zugriff auf Downloads für Backups.",
    },
    # icon="assets/app.icns",  # 
)

