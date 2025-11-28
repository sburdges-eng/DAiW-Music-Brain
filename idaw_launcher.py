#!/usr/bin/env python3
"""
iDAW Native macOS Launcher
==========================
Version: 1.0.00

This creates a native macOS app experience using PyObjC.
Double-click to launch - no terminal required.

Requirements (run once):
    pip install pyobjc streamlit music21 mido numpy pydub
"""

import os
import sys
import subprocess
import threading
import webbrowser
import time
from pathlib import Path

# Get the app bundle path
if getattr(sys, 'frozen', False):
    # Running as compiled
    APP_PATH = Path(sys.executable).parent.parent / "Resources"
else:
    # Running as script
    APP_PATH = Path(__file__).parent

def check_dependencies():
    """Check if required packages are installed."""
    required = ['streamlit', 'music21', 'mido', 'numpy']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    return missing

def install_dependencies(missing):
    """Prompt to install missing dependencies."""
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        
        result = messagebox.askyesno(
            "iDAW - Install Dependencies",
            f"The following packages need to be installed:\n\n{', '.join(missing)}\n\nInstall now?"
        )
        
        if result:
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing, check=True)
            messagebox.showinfo("iDAW", "Dependencies installed! Please restart the app.")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def start_streamlit():
    """Start the Streamlit server."""
    ui_path = APP_PATH / "idaw_ableton_ui.py"
    
    if not ui_path.exists():
        # Try current directory
        ui_path = Path("idaw_ableton_ui.py")
    
    if not ui_path.exists():
        print(f"Error: Could not find idaw_ableton_ui.py")
        print(f"Looked in: {APP_PATH}")
        return None
    
    # Start Streamlit
    process = subprocess.Popen([
        sys.executable, '-m', 'streamlit', 'run',
        str(ui_path),
        '--server.headless=true',
        '--server.port=8501',
        '--browser.gatherUsageStats=false',
        '--theme.base=dark',
        '--theme.primaryColor=#ff9500',
        '--theme.backgroundColor=#1e1e1e',
        '--theme.secondaryBackgroundColor=#2d2d2d',
        '--theme.textColor=#cccccc',
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    return process

def main():
    """Main entry point."""
    print("=" * 50)
    print("iDAW - intelligent Digital Audio Workspace")
    print("Version 1.0.00")
    print("=" * 50)
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"Missing packages: {missing}")
        if not install_dependencies(missing):
            print("Cannot run without required packages.")
            sys.exit(1)
        sys.exit(0)  # Restart after install
    
    # Start Streamlit server
    print("Starting iDAW server...")
    process = start_streamlit()
    
    if process is None:
        print("Failed to start server.")
        sys.exit(1)
    
    # Wait for server to be ready
    time.sleep(3)
    
    # Open browser
    print("Opening iDAW in browser...")
    webbrowser.open("http://localhost:8501")
    
    print("\niDAW is running at http://localhost:8501")
    print("Press Ctrl+C to quit.\n")
    
    # Keep running
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\nShutting down iDAW...")
        process.terminate()
        process.wait()
        print("Goodbye!")

if __name__ == "__main__":
    main()
