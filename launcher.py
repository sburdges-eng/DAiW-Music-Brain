"""
DAiW Native Desktop Launcher

Wraps the Streamlit app in a native webview window using pywebview.
This provides a dedicated desktop application experience without browser chrome.

Usage:
    python launcher.py           # Development mode
    ./DAiW.app                   # After PyInstaller build (macOS)
    ./DAiW.exe                   # After PyInstaller build (Windows)
"""

import os
import sys
import time
import socket
import subprocess
import urllib.request
from contextlib import closing


# =============================================================================
# CONFIGURATION
# =============================================================================

APP_TITLE = "DAiW - Digital Audio Intimate Workstation"
STREAMLIT_SCRIPT = "app.py"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
SERVER_TIMEOUT = 20  # seconds to wait for Streamlit to start


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def find_free_port() -> int:
    """
    Find an available port on localhost.

    Returns:
        Available port number
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def get_base_path() -> str:
    """
    Get the base path for resources.

    Handles both development mode and frozen (PyInstaller) mode.

    Returns:
        Base path string
    """
    if getattr(sys, "frozen", False):
        # Running as compiled executable
        return sys._MEIPASS
    else:
        # Running in development
        return os.path.dirname(os.path.abspath(__file__))


def run_streamlit(port: int) -> subprocess.Popen:
    """
    Run Streamlit as a background subprocess.

    Args:
        port: Port number to run the server on

    Returns:
        Popen object for the subprocess
    """
    base_path = get_base_path()
    script_path = os.path.join(base_path, STREAMLIT_SCRIPT)

    # Verify the script exists
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Streamlit script not found: {script_path}")

    # Build the command
    cmd = [
        sys.executable, "-m", "streamlit", "run", script_path,
        "--server.port", str(port),
        "--server.headless", "true",
        "--server.address", "localhost",
        "--global.developmentMode", "false",
        "--theme.base", "dark",
        "--browser.gatherUsageStats", "false",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
    ]

    # Launch subprocess with output suppressed to prevent pipe deadlocks
    return subprocess.Popen(
        cmd,
        cwd=base_path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
    )


def wait_for_server(url: str, timeout: int = SERVER_TIMEOUT) -> bool:
    """
    Poll the server until it responds or times out.

    Args:
        url: URL to check
        timeout: Maximum seconds to wait

    Returns:
        True if server is ready, False if timeout
    """
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1):
                return True
        except Exception:
            time.sleep(0.3)
    return False


def start_webview(url: str):
    """
    Start the native webview window.

    This function blocks until the window is closed.

    Args:
        url: URL to load in the window
    """
    try:
        import webview
    except ImportError:
        print("ERROR: pywebview not installed. Install with: pip install pywebview")
        print(f"Falling back to browser mode: {url}")
        import webbrowser
        webbrowser.open(url)
        input("Press Enter to stop the server...")
        return

    # Create the window
    window = webview.create_window(
        APP_TITLE,
        url,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        resizable=True,
        min_size=(800, 600),
    )

    # Start the webview (blocks until window is closed)
    webview.start()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """
    Main entry point for the DAiW desktop application.

    Orchestrates:
    1. Finding a free port
    2. Starting the Streamlit server
    3. Waiting for the server to be ready
    4. Opening the native window
    5. Cleaning up when the window closes
    """
    print(f"Starting {APP_TITLE}...")

    # Find available port
    port = find_free_port()
    url = f"http://localhost:{port}"
    print(f"Using port {port}")

    # Start Streamlit server
    print("Starting Streamlit server...")
    try:
        process = run_streamlit(port)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # Wait for server to be ready
    print("Waiting for server to initialize...")
    if not wait_for_server(url):
        print(f"ERROR: Streamlit server failed to start at {url}")
        process.terminate()
        process.wait()
        sys.exit(1)

    print("Server ready. Opening window...")

    # Open native window (blocks until closed)
    try:
        start_webview(url)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        # Cleanup: terminate the Streamlit server
        print("Shutting down server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        print("Goodbye!")


if __name__ == '__main__':
    main()
