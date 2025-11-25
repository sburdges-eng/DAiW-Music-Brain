# -*- mode: python ; coding: utf-8 -*-
"""
DAiW PyInstaller Spec File

Build the desktop application with:
    pyinstaller daiw.spec --clean --noconfirm

Output:
    dist/DAiW/           - Application folder
    dist/DAiW/DAiW       - Executable (Linux)
    dist/DAiW/DAiW.exe   - Executable (Windows)
    dist/DAiW.app/       - Application bundle (macOS)

Troubleshooting:
    If the app opens and immediately closes:
    1. Change console=False to console=True below
    2. Rebuild with: pyinstaller daiw.spec --clean --noconfirm
    3. Run the executable from terminal to see error messages
    4. Add missing modules to hiddenimports list
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

block_cipher = None

# =============================================================================
# DATA COLLECTION
# =============================================================================

# Collect Streamlit's internal files (config, frontend assets)
datas = []
datas += collect_data_files('streamlit')
datas += copy_metadata('streamlit')

# Include our application files
datas += [
    ('app.py', '.'),                              # Main Streamlit UI
    ('music_brain', 'music_brain'),               # Backend package
]

# Include music_brain data files
if os.path.exists('music_brain/data'):
    datas += [('music_brain/data', 'music_brain/data')]

# =============================================================================
# ANALYSIS
# =============================================================================

a = Analysis(
    ['launcher.py'],              # Entry point is the native launcher
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # Streamlit and web framework
        'streamlit',
        'streamlit.runtime.scriptrunner',
        'streamlit.web.cli',

        # Native window
        'webview',
        'webview.platforms',

        # Music Brain modules
        'music_brain',
        'music_brain.structure',
        'music_brain.structure.comprehensive_engine',
        'music_brain.structure.progression',
        'music_brain.structure.chord',
        'music_brain.structure.sections',
        'music_brain.structure.tension_curve',
        'music_brain.groove',
        'music_brain.groove.templates',
        'music_brain.groove.extractor',
        'music_brain.groove.applicator',
        'music_brain.groove.groove_engine',
        'music_brain.groove_engine',
        'music_brain.session',
        'music_brain.session.intent_schema',
        'music_brain.session.intent_processor',
        'music_brain.session.interrogator',
        'music_brain.session.teaching',
        'music_brain.session.generator',
        'music_brain.audio',
        'music_brain.audio.feel',
        'music_brain.audio.reference_dna',
        'music_brain.text',
        'music_brain.text.lyrical_mirror',
        'music_brain.daw',
        'music_brain.daw.logic',
        'music_brain.daw.markers',
        'music_brain.utils',
        'music_brain.utils.midi_io',
        'music_brain.utils.instruments',
        'music_brain.utils.ppq',

        # Core dependencies
        'mido',
        'numpy',

        # Streamlit internals that may be missed
        'altair',
        'pandas',
        'PIL',
        'PIL._tkinter_finder',
        'pkg_resources',
        'packaging',
        'packaging.version',
        'packaging.specifiers',
        'packaging.requirements',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy optional dependencies not needed for core functionality
        'tensorflow',
        'torch',
        'scipy',
        'matplotlib',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# =============================================================================
# PYZ ARCHIVE
# =============================================================================

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

# =============================================================================
# EXECUTABLE
# =============================================================================

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DAiW',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    # Set to True for debugging if app closes immediately
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Uncomment and set path if you have an icon:
    # icon='assets/icon.ico',  # Windows
)

# =============================================================================
# COLLECT (FOLDER BUILD)
# =============================================================================

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DAiW',
)

# =============================================================================
# macOS APP BUNDLE
# =============================================================================

app = BUNDLE(
    coll,
    name='DAiW.app',
    # Uncomment and set path if you have an icon:
    # icon='assets/icon.icns',
    icon=None,
    bundle_identifier='com.daiw.creative-companion',
    info_plist={
        'CFBundleName': 'DAiW',
        'CFBundleDisplayName': 'DAiW - Creative Companion',
        'CFBundleVersion': '0.3.0',
        'CFBundleShortVersionString': '0.3.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
    },
)
