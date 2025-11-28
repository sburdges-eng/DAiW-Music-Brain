# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

block_cipher = None

datas = [
    ("app.py", "."),
    ("music_brain", "music_brain"),
]
datas += collect_data_files("streamlit")
datas += copy_metadata("streamlit")

a = Analysis(
    ["launcher.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "streamlit",
        "pywebview",
        "music_brain",
        "music_brain.structure.comprehensive_engine",
        "music_brain.groove.engine",
        "music_brain.structure.tension",
        "music_brain.lyrics.engine",
        "music_brain.daw.logic",
        "mido",
        "numpy",
        "markovify",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DAiW",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # set to True if you want a debug console
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="DAiW",
)

# macOS app bundle
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="DAiW.app",
        icon=None,
        bundle_identifier="com.daiw.companion",
    )
