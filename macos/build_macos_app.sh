#!/bin/bash
# =============================================================================
# iDAW macOS Application Builder
# Version: 1.0.0
# Codename: Dual Engine
# =============================================================================
#
# This script builds the iDAW.app bundle for macOS distribution.
#
# Requirements:
#   - macOS 10.15 or later
#   - Python 3.11
#   - Xcode Command Line Tools
#   - PyInstaller
#
# Usage:
#   ./build_macos_app.sh [--sign] [--notarize]
#
# Options:
#   --sign      Sign the app with your Developer ID
#   --notarize  Notarize the app with Apple (requires --sign)
#
# =============================================================================

set -e

# Configuration
APP_NAME="iDAW"
APP_VERSION="1.0.0"
BUNDLE_ID="com.idaw.app"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_ROOT/build"
DIST_DIR="$PROJECT_ROOT/dist"
APP_BUNDLE="$DIST_DIR/$APP_NAME.app"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║     ██╗██████╗  █████╗ ██╗    ██╗                           ║"
echo "║     ██║██╔══██╗██╔══██╗██║    ██║                           ║"
echo "║     ██║██║  ██║███████║██║ █╗ ██║                           ║"
echo "║     ██║██║  ██║██╔══██║██║███╗██║                           ║"
echo "║     ██║██████╔╝██║  ██║╚███╔███╔╝                           ║"
echo "║     ╚═╝╚═════╝ ╚═╝  ╚═╝ ╚══╝╚══╝                            ║"
echo "║                                                              ║"
echo "║           Intelligent Digital Audio Workstation              ║"
echo "║                   Dual Engine v$APP_VERSION                         ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Parse arguments
SIGN_APP=false
NOTARIZE_APP=false
for arg in "$@"; do
    case $arg in
        --sign)
            SIGN_APP=true
            ;;
        --notarize)
            NOTARIZE_APP=true
            ;;
    esac
done

# Check for required tools
echo -e "${YELLOW}[1/8] Checking requirements...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "  ✓ Python $PYTHON_VERSION found"

if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is not installed${NC}"
    exit 1
fi
echo "  ✓ pip3 found"

# Install dependencies
echo -e "${YELLOW}[2/8] Installing dependencies...${NC}"
pip3 install --quiet pyinstaller py2app

# Clean previous builds
echo -e "${YELLOW}[3/8] Cleaning previous builds...${NC}"
rm -rf "$BUILD_DIR" "$DIST_DIR"
mkdir -p "$BUILD_DIR" "$DIST_DIR"

# Install the package
echo -e "${YELLOW}[4/8] Installing iDAW package...${NC}"
cd "$PROJECT_ROOT"
pip3 install --quiet -e .

# Build the application using PyInstaller
echo -e "${YELLOW}[5/8] Building application bundle...${NC}"

cat > "$BUILD_DIR/idaw_spec.spec" << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Get project root
project_root = os.path.dirname(os.path.dirname(SPECPATH))

# Collect all data files
datas = [
    (os.path.join(project_root, 'music_brain', 'data'), 'music_brain/data'),
    (os.path.join(project_root, 'iDAW_Core', 'data'), 'iDAW_Core/data'),
    (os.path.join(project_root, 'iDAW_Core', 'shaders'), 'iDAW_Core/shaders'),
    (os.path.join(project_root, 'iDAW_Core', 'plugins'), 'iDAW_Core/plugins'),
    (os.path.join(project_root, 'macos', 'Info.plist'), '.'),
]

# Filter existing paths
datas = [(src, dst) for src, dst in datas if os.path.exists(src)]

a = Analysis(
    [os.path.join(project_root, 'launcher.py')],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'music_brain',
        'music_brain.orchestrator',
        'music_brain.orchestrator.bridge_api',
        'music_brain.groove',
        'music_brain.structure',
        'music_brain.audio',
        'mido',
        'numpy',
        'streamlit',
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
    name='iDAW',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=os.path.join(project_root, 'macos', 'iDAW.entitlements'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='iDAW',
)

app = BUNDLE(
    coll,
    name='iDAW.app',
    icon=os.path.join(project_root, 'macos', 'iDAW.icns') if os.path.exists(os.path.join(project_root, 'macos', 'iDAW.icns')) else None,
    bundle_identifier='com.idaw.app',
    info_plist={
        'CFBundleName': 'iDAW',
        'CFBundleDisplayName': 'iDAW - Intelligent Digital Audio Workstation',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15',
        'NSMicrophoneUsageDescription': 'iDAW needs microphone access for The Parrot plugin.',
        'LSApplicationCategoryType': 'public.app-category.music',
        'NSHumanReadableCopyright': 'Copyright © 2025 Sean Burdges. All rights reserved.',
    },
)
EOF

pyinstaller --clean --noconfirm "$BUILD_DIR/idaw_spec.spec"

# Copy additional resources
echo -e "${YELLOW}[6/8] Copying resources...${NC}"
if [ -d "$APP_BUNDLE" ]; then
    # Copy entitlements
    cp "$SCRIPT_DIR/iDAW.entitlements" "$APP_BUNDLE/Contents/"
    
    # Copy shaders if not already present
    if [ -d "$PROJECT_ROOT/iDAW_Core/shaders" ]; then
        mkdir -p "$APP_BUNDLE/Contents/Resources/shaders"
        cp -r "$PROJECT_ROOT/iDAW_Core/shaders/"* "$APP_BUNDLE/Contents/Resources/shaders/" 2>/dev/null || true
    fi
    
    # Copy plugin shaders
    if [ -d "$PROJECT_ROOT/iDAW_Core/plugins" ]; then
        mkdir -p "$APP_BUNDLE/Contents/Resources/plugins"
        cp -r "$PROJECT_ROOT/iDAW_Core/plugins/"* "$APP_BUNDLE/Contents/Resources/plugins/" 2>/dev/null || true
    fi
    
    echo "  ✓ Resources copied"
else
    echo -e "${RED}Error: App bundle not found${NC}"
    exit 1
fi

# Code signing (optional)
echo -e "${YELLOW}[7/8] Code signing...${NC}"
if [ "$SIGN_APP" = true ]; then
    if [ -n "$DEVELOPER_ID" ]; then
        codesign --force --deep --options runtime \
            --entitlements "$SCRIPT_DIR/iDAW.entitlements" \
            --sign "$DEVELOPER_ID" \
            "$APP_BUNDLE"
        echo "  ✓ App signed with $DEVELOPER_ID"
    else
        echo -e "${YELLOW}  ⚠ DEVELOPER_ID not set, skipping signing${NC}"
    fi
else
    echo "  ⏭ Skipping (use --sign to enable)"
fi

# Notarization (optional)
echo -e "${YELLOW}[8/8] Notarization...${NC}"
if [ "$NOTARIZE_APP" = true ] && [ "$SIGN_APP" = true ]; then
    if [ -n "$APPLE_ID" ] && [ -n "$APPLE_TEAM_ID" ]; then
        # Create ZIP for notarization
        ditto -c -k --keepParent "$APP_BUNDLE" "$DIST_DIR/iDAW.zip"
        
        xcrun notarytool submit "$DIST_DIR/iDAW.zip" \
            --apple-id "$APPLE_ID" \
            --team-id "$APPLE_TEAM_ID" \
            --wait
        
        # Staple the notarization
        xcrun stapler staple "$APP_BUNDLE"
        echo "  ✓ App notarized"
    else
        echo -e "${YELLOW}  ⚠ APPLE_ID or APPLE_TEAM_ID not set, skipping notarization${NC}"
    fi
else
    echo "  ⏭ Skipping (use --sign --notarize to enable)"
fi

# Summary
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    BUILD COMPLETE!                           ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "  📦 App Bundle: $APP_BUNDLE"
echo "  📊 Version: $APP_VERSION"
echo ""

# List included plugins
echo "  🎛️ Included Plugins:"
echo "     • 001: The Eraser (Spectral Gating)"
echo "     • 002: The Pencil (Tube Saturation)"
echo "     • 003: The Press (VCA Compressor)"
echo "     • 004: The Smudge (Convolution Reverb)"
echo "     • 005: The Trace (Delay)"
echo "     • 006: The Palette (Wavetable Synth)"
echo "     • 007: The Parrot (Vocal/Instrument Companion)"
echo ""
echo "  🚀 To run: open $APP_BUNDLE"
echo ""

# Create DMG (optional)
if command -v create-dmg &> /dev/null; then
    echo -e "${YELLOW}Creating DMG installer...${NC}"
    create-dmg \
        --volname "iDAW $APP_VERSION" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "iDAW.app" 175 190 \
        --hide-extension "iDAW.app" \
        --app-drop-link 425 190 \
        "$DIST_DIR/iDAW-$APP_VERSION.dmg" \
        "$APP_BUNDLE"
    echo "  ✓ DMG created: $DIST_DIR/iDAW-$APP_VERSION.dmg"
fi
