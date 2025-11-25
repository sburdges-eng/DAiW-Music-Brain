# launcher.py
import os
import sys
import time
import socket
import subprocess
import urllib.request
from contextlib import closing

import webview

APP_TITLE = "DAiW - Digital Audio Intimate Workstation"
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
    webview.create_window(APP_TITLE, url, width=1000, height=800, resizable=True)
    webview.start()


def main():
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
