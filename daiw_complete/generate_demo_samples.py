#!/usr/bin/env python3
"""
Generate a tiny synthetic demo kit for AudioVault.

Creates:
    audio_vault/raw/Demo_Kit/*.wav
"""

from pathlib import Path

import numpy as np

try:
    import soundfile as sf
    HAS_SF = True
except ImportError:
    HAS_SF = False

SAMPLE_RATE = 44100
OUT_DIR = Path("audio_vault/raw/Demo_Kit")


def _sine(freq: float, length_sec: float, decay: float = 4.0) -> np.ndarray:
    t = np.linspace(0, length_sec, int(SAMPLE_RATE * length_sec), endpoint=False)
    sig = np.sin(2 * np.pi * freq * t)
    env = np.exp(-decay * t)
    return sig * env


def _noise(length_sec: float, decay: float = 4.0) -> np.ndarray:
    t = np.linspace(0, length_sec, int(SAMPLE_RATE * length_sec), endpoint=False)
    sig = np.random.randn(len(t))
    env = np.exp(-decay * t)
    return sig * env


def generate_kit():
    if not HAS_SF:
        print("❌ soundfile not installed. Run: pip install soundfile")
        return
        
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Kick
    kick = _sine(60, 0.5, decay=6.0)
    sf.write(OUT_DIR / "kick_demo.wav", kick, SAMPLE_RATE)

    # Snare
    snare = _noise(0.4, decay=8.0)
    sf.write(OUT_DIR / "snare_demo.wav", snare, SAMPLE_RATE)

    # Hat
    hat = _noise(0.2, decay=15.0)
    sf.write(OUT_DIR / "hat_demo.wav", hat * 0.4, SAMPLE_RATE)

    # Tom
    tom = _sine(120, 0.6, decay=5.0)
    sf.write(OUT_DIR / "tom_demo.wav", tom, SAMPLE_RATE)

    # Perc / click
    click = _sine(800, 0.1, decay=20.0)
    sf.write(OUT_DIR / "click_demo.wav", click * 0.5, SAMPLE_RATE)

    print(f"✅ Demo kit written to {OUT_DIR}")


if __name__ == "__main__":
    generate_kit()
