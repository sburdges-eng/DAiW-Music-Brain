#!/usr/bin/env python3
"""
Generate Demo Samples - Create placeholder samples for testing AudioVault.

This script creates a demo AudioVault structure with placeholder audio files
for testing the DAiW sample discovery and kit building features.

Usage:
    python scripts/generate_demo_samples.py [output_dir]

Note: This creates empty .wav files as placeholders. For actual audio,
you would need to generate real samples with a library like pydub or scipy.
"""

import os
import sys
from pathlib import Path


def create_placeholder_wav(path: Path, duration_ms: int = 100) -> None:
    """
    Create a minimal valid WAV file (silence).

    This creates a proper WAV header with no audio data (silence).
    For testing purposes only.
    """
    import struct

    sample_rate = 44100
    num_channels = 1
    bits_per_sample = 16
    num_samples = int(sample_rate * duration_ms / 1000)
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = num_samples * block_align

    # Create directory if needed
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "wb") as f:
        # RIFF header
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + data_size))  # File size - 8
        f.write(b"WAVE")

        # fmt chunk
        f.write(b"fmt ")
        f.write(struct.pack("<I", 16))  # Chunk size
        f.write(struct.pack("<H", 1))   # Audio format (PCM)
        f.write(struct.pack("<H", num_channels))
        f.write(struct.pack("<I", sample_rate))
        f.write(struct.pack("<I", byte_rate))
        f.write(struct.pack("<H", block_align))
        f.write(struct.pack("<H", bits_per_sample))

        # data chunk
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        # Write silence (zeros)
        f.write(b"\x00" * data_size)


def generate_demo_vault(output_dir: Path) -> None:
    """
    Generate a demo AudioVault structure with sample files.
    """
    print(f"Generating demo AudioVault at: {output_dir}")

    # Define sample structure
    samples = {
        "Drums/Kicks": [
            "kick_acoustic_01.wav",
            "kick_electronic_02.wav",
            "kick_808_sub.wav",
            "kick_punchy_120bpm.wav",
        ],
        "Drums/Snares": [
            "snare_tight_01.wav",
            "snare_room_02.wav",
            "snare_clap_layer.wav",
        ],
        "Drums/HiHats": [
            "hihat_closed_01.wav",
            "hihat_open_02.wav",
            "hihat_pedal_03.wav",
        ],
        "Drums/Percussion": [
            "shaker_01.wav",
            "tambourine_02.wav",
            "conga_hit.wav",
        ],
        "Bass": [
            "bass_synth_Am_90bpm.wav",
            "bass_808_Dm_120bpm.wav",
            "bass_acoustic_C.wav",
        ],
        "Synths/Leads": [
            "lead_saw_Am.wav",
            "lead_pluck_Cmaj.wav",
        ],
        "Synths/Pads": [
            "pad_ambient_Dm.wav",
            "pad_warm_F.wav",
            "pad_ethereal_Am.wav",
        ],
        "FX": [
            "riser_8bar.wav",
            "impact_01.wav",
            "sweep_down.wav",
        ],
        "Loops": [
            "drum_loop_120bpm.wav",
            "groove_90bpm_funk.wav",
            "beat_140bpm_dnb.wav",
        ],
        "Vocals": [
            "vocal_chop_01.wav",
            "vocal_atmosphere.wav",
        ],
    }

    total = 0
    for subdir, files in samples.items():
        for filename in files:
            filepath = output_dir / subdir / filename
            create_placeholder_wav(filepath)
            print(f"  Created: {subdir}/{filename}")
            total += 1

    # Create kits directory with sample kit JSON
    kits_dir = output_dir / "kits"
    kits_dir.mkdir(parents=True, exist_ok=True)

    # Sample kit definition
    demo_kit = {
        "name": "Demo Drum Kit",
        "mood": "neutral",
        "genre": "electronic",
        "description": "Auto-generated demo kit for testing",
        "samples": [
            {"path": str(output_dir / "Drums/Kicks/kick_acoustic_01.wav"),
             "name": "kick_acoustic_01", "category": "kick"},
            {"path": str(output_dir / "Drums/Snares/snare_tight_01.wav"),
             "name": "snare_tight_01", "category": "snare"},
            {"path": str(output_dir / "Drums/HiHats/hihat_closed_01.wav"),
             "name": "hihat_closed_01", "category": "hihat"},
        ]
    }

    import json
    kit_path = kits_dir / "demo_drum_kit.json"
    with open(kit_path, "w") as f:
        json.dump(demo_kit, f, indent=2)
    print(f"  Created kit: kits/demo_drum_kit.json")

    # Create output directory for generated MIDI
    output_midi_dir = output_dir / "output"
    output_midi_dir.mkdir(parents=True, exist_ok=True)
    print(f"  Created output directory: output/")

    print(f"\nDone! Created {total} sample files and 1 kit definition.")


def main():
    # Determine output directory
    if len(sys.argv) > 1:
        output_dir = Path(sys.argv[1])
    else:
        # Default to ~/Music/AudioVault
        output_dir = Path.home() / "Music" / "AudioVault"

    generate_demo_vault(output_dir)

    print(f"""
AudioVault Demo Setup Complete!

To use with DAiW:
  1. Set DAIW_AUDIO_VAULT_PATH={output_dir}
  2. Or use: daiw --vault {output_dir}

To scan the vault:
  from music_brain.audio_refinery import scan_audio_vault
  samples = scan_audio_vault("{output_dir}")
  print(f"Found {{len(samples)}} samples")
""")


if __name__ == "__main__":
    main()
