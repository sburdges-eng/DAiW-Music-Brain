#!/usr/bin/env python3
"""
Build Logic Kit - Create Logic Pro X compatible sample kit from AudioVault.

This script scans AudioVault and creates a kit mapping file that can be
used with Logic Pro X's Sampler or Drum Machine Designer.

Usage:
    python scripts/build_logic_kit.py [kit_name] [--mood MOOD] [--genre GENRE]

Examples:
    python scripts/build_logic_kit.py "My Grief Kit" --mood grief
    python scripts/build_logic_kit.py "Punk Drums" --mood rage --genre punk

Output:
    Creates a JSON mapping file that describes the kit configuration.
    This can be used with DAW integration modules.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from music_brain.audio_refinery import (
    scan_audio_vault,
    build_kit_from_samples,
    suggest_samples_for_mood,
    save_kit,
)
from music_brain.config import get_audio_vault_path


# General MIDI drum mapping (for reference)
GM_DRUM_MAP = {
    "kick": 36,      # C1 - Bass Drum 1
    "snare": 38,     # D1 - Acoustic Snare
    "hihat": 42,     # F#1 - Closed Hi-Hat
    "hihat_open": 46,  # A#1 - Open Hi-Hat
    "tom": 45,       # A1 - Low Tom
    "crash": 49,     # C#2 - Crash Cymbal 1
    "ride": 51,      # D#2 - Ride Cymbal 1
    "perc": 39,      # D#1 - Hand Clap
}


def build_logic_kit(
    name: str,
    vault_path: Optional[Path] = None,
    mood: Optional[str] = None,
    genre: Optional[str] = None,
    output_path: Optional[Path] = None,
) -> dict:
    """
    Build a Logic Pro compatible kit definition.

    Args:
        name: Kit name
        vault_path: AudioVault path
        mood: Mood for sample selection
        genre: Genre tag
        output_path: Where to save the kit JSON

    Returns:
        Kit configuration dictionary
    """
    if vault_path is None:
        vault_path = get_audio_vault_path()

    print(f"Scanning AudioVault: {vault_path}")

    # Get samples based on mood or scan all
    if mood:
        print(f"Selecting samples for mood: {mood}")
        samples = suggest_samples_for_mood(mood, vault_path, max_samples=20)
    else:
        samples = scan_audio_vault(vault_path)

    print(f"Found {len(samples)} samples")

    if not samples:
        print("No samples found. Run generate_demo_samples.py first or add samples to AudioVault.")
        return {}

    # Build kit
    kit = build_kit_from_samples(
        name=name,
        samples=samples[:16],  # Limit to 16 for typical drum pad
        mood=mood,
        genre=genre,
        description=f"Auto-generated kit for {mood or 'general'} mood",
    )

    # Create Logic-specific mapping
    logic_config = {
        "kit_name": kit.name,
        "mood": kit.mood,
        "genre": kit.genre,
        "description": kit.description,
        "samples": [],
        "midi_mapping": [],
    }

    # Map samples to MIDI notes
    for i, sample in enumerate(kit.samples):
        # Determine MIDI note based on category
        category = sample.category
        midi_note = GM_DRUM_MAP.get(category, 60 + i)  # Default to middle C + offset

        sample_config = {
            "name": sample.name,
            "path": str(sample.path),
            "category": category,
            "midi_note": midi_note,
            "bpm": sample.bpm,
            "key": sample.key,
        }
        logic_config["samples"].append(sample_config)

        logic_config["midi_mapping"].append({
            "note": midi_note,
            "sample": sample.name,
            "category": category,
        })

    # Save to file
    if output_path is None:
        output_path = vault_path / "kits" / f"{name.lower().replace(' ', '_')}.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(logic_config, f, indent=2)

    print(f"\nKit saved to: {output_path}")

    # Print summary
    print(f"\n{kit.name}")
    print("=" * len(kit.name))
    print(f"Mood: {kit.mood or 'N/A'}")
    print(f"Genre: {kit.genre or 'N/A'}")
    print(f"Samples: {len(kit.samples)}")
    print("\nMIDI Mapping:")
    for mapping in logic_config["midi_mapping"]:
        print(f"  Note {mapping['note']:3d}: {mapping['sample']} ({mapping['category']})")

    return logic_config


def main():
    parser = argparse.ArgumentParser(
        description="Build Logic Pro X compatible sample kit from AudioVault"
    )
    parser.add_argument(
        "name",
        nargs="?",
        default="DAiW Kit",
        help="Kit name (default: 'DAiW Kit')"
    )
    parser.add_argument(
        "--mood",
        choices=["grief", "rage", "nostalgia", "defiance", "hope", "anxiety", "peace"],
        help="Mood for sample selection"
    )
    parser.add_argument(
        "--genre",
        help="Genre tag for the kit"
    )
    parser.add_argument(
        "--vault",
        type=Path,
        help="AudioVault path (default: from config)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path"
    )

    args = parser.parse_args()

    build_logic_kit(
        name=args.name,
        vault_path=args.vault,
        mood=args.mood,
        genre=args.genre,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
