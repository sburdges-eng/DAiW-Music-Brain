#!/usr/bin/env python3
# audio_vault/build_industrial_kit.py
"""
Build an industrial/lo-fi sample kit using the Audio Refinery.

Takes clean samples and processes them through industrial pipelines
to create gritty, textured variants.

Usage:
    python -m audio_vault.build_industrial_kit --input ./samples
    python -m audio_vault.build_industrial_kit --input ./samples --pipeline tape_rot
"""

import argparse
import os
from pathlib import Path
from typing import Optional

import numpy as np

# Optional dependencies
try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

try:
    from music_brain.audio_refinery import process_sample, PIPELINE_MAP
    REFINERY_AVAILABLE = True
except ImportError:
    REFINERY_AVAILABLE = False


DEFAULT_INPUT = Path(__file__).parent / "samples"
DEFAULT_OUTPUT = Path(__file__).parent / "kits" / "industrial"


def process_to_industrial(
    input_path: Path,
    output_path: Path,
    pipeline: str = "industrial",
) -> bool:
    """Process a single sample through the industrial pipeline."""

    if not SOUNDFILE_AVAILABLE:
        print(f"  [SKIP] soundfile not installed")
        return False

    if not REFINERY_AVAILABLE:
        print(f"  [SKIP] audio_refinery not available (missing audiomentations?)")
        return False

    try:
        # Load audio
        audio, sr = sf.read(str(input_path))

        # Ensure mono
        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)

        # Process through refinery
        processed = process_sample(audio, sr, pipeline)

        # Write output
        sf.write(str(output_path), processed, sr)

        return True

    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Build industrial sample kit using Audio Refinery"
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        default=DEFAULT_INPUT,
        help="Input directory containing clean samples"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output directory for processed kit"
    )
    parser.add_argument(
        "--pipeline", "-p",
        default="industrial",
        choices=["clean", "industrial", "tape_rot"] if REFINERY_AVAILABLE else ["clean", "industrial", "tape_rot"],
        help="Processing pipeline to use"
    )
    args = parser.parse_args()

    print(f"Building industrial kit")
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print(f"Pipeline: {args.pipeline}")
    print()

    if not SOUNDFILE_AVAILABLE:
        print("ERROR: soundfile not installed. Install with: pip install soundfile")
        return

    if not REFINERY_AVAILABLE:
        print("WARNING: Audio Refinery not available.")
        print("Install audiomentations with: pip install audiomentations")
        print("Falling back to simple copy...")
        print()

    args.output.mkdir(parents=True, exist_ok=True)

    # Find audio files
    audio_extensions = {'.wav', '.aif', '.aiff', '.flac'}
    samples = []
    for ext in audio_extensions:
        samples.extend(args.input.glob(f"*{ext}"))

    if not samples:
        print(f"No audio files found in {args.input}")
        return

    success_count = 0
    for sample in sorted(samples):
        # Create output filename with pipeline suffix
        stem = sample.stem
        suffix = sample.suffix
        output_name = f"{stem}_{args.pipeline}{suffix}"
        output_path = args.output / output_name

        print(f"Processing: {sample.name}")

        if REFINERY_AVAILABLE:
            if process_to_industrial(sample, output_path, args.pipeline):
                print(f"  → {output_name}")
                success_count += 1
        else:
            # Fallback: just copy
            import shutil
            shutil.copy2(sample, output_path)
            print(f"  → {output_name} (copied, not processed)")
            success_count += 1

    print(f"\nProcessed {success_count}/{len(samples)} samples")


if __name__ == "__main__":
    main()
