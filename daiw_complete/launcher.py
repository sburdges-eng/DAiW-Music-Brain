"""
DAiW Desktop Launcher
=====================
Wraps Streamlit in a native window via pywebview.
"""

import os
import sys
import time
import socket
import subprocess
import urllib.request
from contextlib import closing

try:
    import webview
    HAS_WEBVIEW = True
except ImportError:
    HAS_WEBVIEW = False

APP_TITLE = "DAiW - Digital Audio Intimate Workstation"
STREAMLIT_SCRIPT = "app.py"


def find_free_port() -> int:
    """Find a free localhost port."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return int(s.getsockname()[1])


def run_streamlit(port: int) -> subprocess.Popen:
    """Runs Streamlit as a subprocess."""
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
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
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url):
                return True
        except Exception:
            time.sleep(0.3)
    return False


def start_webview(url: str) -> None:
    webview.create_window(APP_TITLE, url, width=1000, height=800, resizable=True)
    webview.start()


def main() -> None:
    if not HAS_WEBVIEW:
        print("pywebview not installed. Running Streamlit directly.")
        print("Install with: pip install pywebview")
        port = find_free_port()
        process = run_streamlit(port)
        print(f"Streamlit running at http://localhost:{port}")
        try:
            process.wait()
        except KeyboardInterrupt:
            process.terminate()
        return

    port = find_free_port()
    url = f"http://localhost:{port}"

    process = run_streamlit(port)

    if not wait_for_server(url):
        process.terminate()
        raise RuntimeError(f"Streamlit server failed to start at {url}")

    try:
        start_webview(url)
    finally:
        process.terminate()
        process.wait()


if __name__ == "__main__":
    main()
