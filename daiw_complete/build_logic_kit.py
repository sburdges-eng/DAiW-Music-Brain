#!/usr/bin/env python3
"""
Build a simple Logic-compatible kit mapping text file.

This does NOT automate Logic, it just creates a mapping guide:
    audio_vault/kits/<KIT_NAME>_GUIDE.txt
"""

from pathlib import Path
import os

GM_MAP = {
    "kick": 36,   # C1
    "snare": 38,  # D1
    "hat": 42,    # F#1 (closed)
    "tom": 45,    # A1
    "click": 39,  # D#1 / rim
    "clap": 39,
    "rim": 37,
    "crash": 49,
    "ride": 51,
}


def create_logic_kit_mapping(samples_dir: str, kit_name: str) -> str:
    samples_path = Path(samples_dir)
    if not samples_path.exists():
        raise FileNotFoundError(samples_dir)

    kits_dir = Path("audio_vault/kits")
    kits_dir.mkdir(parents=True, exist_ok=True)

    guide_path = kits_dir / f"{kit_name}_GUIDE.txt"

    lines = [
        f"Kit: {kit_name}",
        f"Source folder: {samples_dir}",
        "",
        "Suggested MIDI note mapping (General MIDI-ish):",
    ]

    for fname in sorted(os.listdir(samples_dir)):
        lower = fname.lower()
        note = None
        for key, gm_note in GM_MAP.items():
            if key in lower:
                note = gm_note
                break
        if note is None:
            note = 48  # default C2
        lines.append(f"{fname} -> MIDI {note}")

    guide_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Kit guide written: {guide_path}")
    return str(guide_path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        create_logic_kit_mapping(sys.argv[1], sys.argv[2])
    else:
        # Default: process demo kit
        try:
            create_logic_kit_mapping("audio_vault/raw/Demo_Kit", "Demo_Kit")
        except FileNotFoundError:
            print("Run generate_demo_samples.py first to create the demo kit.")
