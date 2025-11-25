#!/usr/bin/env python3
# audio_vault/build_logic_kit.py
"""
Build a Logic Pro compatible sample kit from audio files.

Organizes samples into the correct folder structure for Logic Pro's
Sampler instrument and generates metadata.

Usage:
    python -m audio_vault.build_logic_kit --input ./samples --output ./kits/my_kit
    python -m audio_vault.build_logic_kit --input ./samples --name "Therapy Kit"
"""

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_INPUT = Path(__file__).parent / "samples"
DEFAULT_OUTPUT = Path(__file__).parent / "kits"


# MIDI note mapping for drum kits (General MIDI standard)
DRUM_MAP = {
    "kick": 36,      # C1
    "snare": 38,     # D1
    "hihat": 42,     # F#1
    "clap": 39,      # D#1
    "tom_low": 41,   # F1
    "tom_mid": 45,   # A1
    "tom_high": 48,  # C2
    "crash": 49,     # C#2
    "ride": 51,      # D#2
}


def detect_sample_type(filename: str) -> Optional[str]:
    """Detect sample type from filename."""
    name = filename.lower()

    for drum_type in DRUM_MAP:
        if drum_type in name:
            return drum_type

    # Check for note names (C4, D#5, etc.)
    import re
    note_match = re.search(r'([A-Ga-g][#b]?\d)', name)
    if note_match:
        return "melodic"

    return "unknown"


def note_name_to_midi(note: str) -> int:
    """Convert note name to MIDI number."""
    note_map = {
        'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11
    }

    name = note.upper()
    base = note_map.get(name[0], 0)

    offset = 0
    idx = 1
    if len(name) > 1 and name[1] == '#':
        offset = 1
        idx = 2
    elif len(name) > 1 and name[1] == 'B':
        offset = -1
        idx = 2

    octave = int(name[idx:]) if idx < len(name) else 4

    return base + offset + (octave + 1) * 12


def build_kit(
    input_dir: Path,
    output_dir: Path,
    kit_name: str = "DAiW Kit",
) -> Dict:
    """Build a Logic Pro kit from samples."""

    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all audio files
    audio_extensions = {'.wav', '.aif', '.aiff', '.mp3', '.m4a', '.flac'}
    samples = []

    for ext in audio_extensions:
        samples.extend(input_dir.glob(f"*{ext}"))
        samples.extend(input_dir.glob(f"*{ext.upper()}"))

    if not samples:
        print(f"No audio files found in {input_dir}")
        return {}

    # Organize samples
    kit_info = {
        "name": kit_name,
        "samples": [],
        "mappings": {},
    }

    samples_dir = output_dir / "Samples"
    samples_dir.mkdir(exist_ok=True)

    for sample_path in sorted(samples):
        sample_type = detect_sample_type(sample_path.name)

        # Copy sample to kit
        dest_path = samples_dir / sample_path.name
        shutil.copy2(sample_path, dest_path)

        # Determine MIDI mapping
        if sample_type in DRUM_MAP:
            midi_note = DRUM_MAP[sample_type]
        elif sample_type == "melodic":
            # Extract note from filename
            import re
            match = re.search(r'([A-Ga-g][#b]?\d)', sample_path.name)
            if match:
                midi_note = note_name_to_midi(match.group(1))
            else:
                midi_note = 60  # Default to C4
        else:
            midi_note = 60

        sample_info = {
            "file": sample_path.name,
            "type": sample_type,
            "midi_note": midi_note,
            "root_note": midi_note,
        }

        kit_info["samples"].append(sample_info)
        kit_info["mappings"][sample_path.name] = midi_note

        print(f"  {sample_path.name} → MIDI {midi_note}")

    # Write kit metadata
    metadata_path = output_dir / "kit_info.json"
    with open(metadata_path, 'w') as f:
        json.dump(kit_info, f, indent=2)

    print(f"\nKit metadata written to {metadata_path}")

    return kit_info


def main():
    parser = argparse.ArgumentParser(
        description="Build Logic Pro compatible sample kit"
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        default=DEFAULT_INPUT,
        help="Input directory containing samples"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output directory for kit"
    )
    parser.add_argument(
        "--name", "-n",
        default="DAiW Kit",
        help="Name for the kit"
    )
    args = parser.parse_args()

    output_dir = args.output
    if output_dir is None:
        # Create kit name from input
        safe_name = args.name.replace(" ", "_").lower()
        output_dir = DEFAULT_OUTPUT / safe_name

    print(f"Building kit: {args.name}")
    print(f"Input: {args.input}")
    print(f"Output: {output_dir}")
    print()

    kit_info = build_kit(args.input, output_dir, args.name)

    if kit_info:
        print(f"\nKit '{args.name}' created with {len(kit_info['samples'])} samples")


if __name__ == "__main__":
    main()
