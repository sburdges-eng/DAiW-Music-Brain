# launcher.py
"""
iDAW Native Desktop Launcher

pywebview wrapper that makes the Streamlit app feel like a real desktop application.
Handles server lifecycle and provides a native window without browser chrome.

Version: 1.0.0
Codename: Dual Engine
"""
import os
import sys
import time
import socket
import subprocess
import urllib.request
from contextlib import closing

APP_TITLE = "iDAW - Intelligent Digital Audio Workstation"
APP_VERSION = "1.0.0"
STREAMLIT_SCRIPT = "app.py"


def find_free_port() -> int:
    """Finds an available port on localhost."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def run_streamlit(port: int) -> subprocess.Popen:
    """Runs Streamlit as a subprocess."""
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    script_path = os.path.join(base_path, STREAMLIT_SCRIPT)

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        script_path,
        "--server.port",
        str(port),
        "--server.headless",
        "true",
        "--global.developmentMode",
        "false",
        "--theme.base",
        "dark",
    ]

    return subprocess.Popen(
        cmd,
        cwd=base_path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
    )


def wait_for_server(url: str, timeout: int = 15) -> bool:
    """Polls the server until it responds or times out."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url):
                return True
        except Exception:
            time.sleep(0.3)
    return False


def start_webview(url: str) -> None:
    """Starts the native window."""
    try:
        import webview
    except ImportError:
        print("pywebview not installed. Install with: pip install pywebview")
        print(f"Falling back to browser. Open: {url}")
        import webbrowser
        webbrowser.open(url)
        input("Press Enter to stop the server...")
        return

    webview.create_window(APP_TITLE, url, width=1000, height=800, resizable=True)
    webview.start()


def main() -> None:
    """
    Main entry point for the iDAW desktop application.
    
    Launches the Streamlit backend server and opens a native window
    using pywebview (falls back to browser if not available).
    """
    print(f"\n{'='*60}")
    print(f"  iDAW - Intelligent Digital Audio Workstation")
    print(f"  Version {APP_VERSION} (Dual Engine)")
    print(f"{'='*60}\n")
    
    port = find_free_port()
    url = f"http://localhost:{port}"
    
    print(f"[iDAW] Starting Streamlit server on port {port}...")
    process = run_streamlit(port)

    print(f"[iDAW] Waiting for server to be ready...")
    if not wait_for_server(url):
        process.terminate()
        raise RuntimeError(f"Streamlit server failed to start at {url}")

    print(f"[iDAW] Server ready at {url}")
    print(f"[iDAW] Opening native window...")
    
    try:
        start_webview(url)
    finally:
        print(f"[iDAW] Shutting down server...")
        process.terminate()
        process.wait()
        print(f"[iDAW] Goodbye!")


if __name__ == "__main__":
    main()
