#!/usr/bin/env python3
"""
DAiW Kit Builder: Industrial / Rage
Uses the refinery to crush samples into an aggressive kit.
"""

import os
from pathlib import Path

try:
    from music_brain.audio_refinery import pipe_industrial, process_file
    HAS_REFINERY = True
except ImportError:
    HAS_REFINERY = False

from build_logic_kit import create_logic_kit_mapping

KIT_NAME = "Industrial_Glitch_Kit"
RAW_DIR = Path("./audio_vault/raw") / KIT_NAME
REFINED_DIR = Path("./audio_vault/refined") / KIT_NAME


def refine_folder(input_dir: Path, output_dir: Path):
    if not HAS_REFINERY:
        print("❌ Audio refinery not available (missing dependencies)")
        return
        
    if not input_dir.exists():
        print(f"❌ Raw directory missing: {input_dir}")
        print("   Drop your glitch/industrial samples there first.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    for root, _, files in os.walk(input_dir):
        for filename in files:
            if not filename.lower().endswith((".wav", ".aiff", ".flac", ".mp3")):
                continue
            input_path = Path(root) / filename
            rel = input_path.relative_to(input_dir)
            out_path = output_dir / rel
            out_path = out_path.with_suffix(".wav")
            process_file(str(input_path), str(out_path), pipe_industrial)


def build_kit():
    print(f"🔨 Forging {KIT_NAME}...")
    
    if not RAW_DIR.exists():
        print(f"❌ Create {RAW_DIR} and add your source samples first.")
        return
    
    REFINED_DIR.mkdir(parents=True, exist_ok=True)
    refine_folder(RAW_DIR, REFINED_DIR)

    if not any(REFINED_DIR.iterdir()):
        print("❌ Refinement failed or nothing to refine.")
        return

    kit_file = create_logic_kit_mapping(str(REFINED_DIR), KIT_NAME)

    print("\n" + "=" * 40)
    print(f"🔥 KIT READY: {KIT_NAME}")
    print(f"📍 Location: {kit_file}")
    print("=" * 40)


if __name__ == "__main__":
    build_kit()
