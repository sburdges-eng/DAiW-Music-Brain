"""
iDAW - Build Script for Native macOS App
=========================================

This uses py2app to create a proper .app bundle that:
- Double-click to launch
- Shows in Dock
- No terminal window
- Proper icon

USAGE:
------
1. Install py2app:
   pip install py2app

2. Build the app:
   python setup_macos.py py2app

3. Find the app in:
   dist/iDAW.app

4. Drag to /Applications

REQUIREMENTS:
-------------
pip install py2app streamlit music21 mido numpy pydub pyobjc
"""

from setuptools import setup
import sys

# App info
APP_NAME = 'iDAW'
APP_VERSION = '1.0.00'
APP_SCRIPT = 'idaw_launcher.py'

# Files to include
DATA_FILES = [
    'idaw_ableton_ui.py',
    'idaw_complete_pipeline.py',
    'vernacular.py',
    'vernacular_database.json',
]

# py2app options
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'AppIcon.icns',  # Create this from the SVG
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleIdentifier': 'com.idaw.intelligentdigitalaudioworkspace',
        'CFBundleVersion': APP_VERSION,
        'CFBundleShortVersionString': APP_VERSION,
        'LSMinimumSystemVersion': '10.15',
        'NSHighResolutionCapable': True,
        'NSHumanReadableCopyright': 'Copyright © 2025 iDAW',
        'LSApplicationCategoryType': 'public.app-category.music',
        'LSBackgroundOnly': False,
    },
    'packages': [
        'streamlit',
        'music21',
        'mido',
        'numpy',
        'pydub',
    ],
    'includes': [
        'streamlit.web.cli',
    ],
    'excludes': [
        'tkinter',  # Save space if not needed
    ],
}

setup(
    name=APP_NAME,
    version=APP_VERSION,
    app=[APP_SCRIPT],
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
