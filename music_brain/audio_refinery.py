# music_brain/audio_refinery.py
"""
DAiW Audio Refinery
===================
Batch processor to transform raw samples into the C2 Industrial Palette.
Uses 'audiomentations' to apply stochastic DSP chains (glitch, distort, tape).

Usage:
    python music_brain/audio_refinery.py
"""

import os
import numpy as np
import librosa
import soundfile as sf
from audiomentations import (
    Compose,
    AddGaussianNoise,
    TimeStretch,
    PitchShift,
    ClippingDistortion,
    HighPassFilter,
    LowPassFilter,
    Normalize,
    Trim,
    Resample,
)

INPUT_DIR = "./audio_vault/raw"
OUTPUT_DIR = "./audio_vault/refined"
SAMPLE_RATE = 44100

# Pipeline A: Cleaner (bass / foundation)
pipe_clean = Compose(
    [
        Trim(top_db=20, p=1.0),
        Normalize(p=1.0),
    ]
)

# Pipeline B: Industrial / Rage
pipe_industrial = Compose(
    [
        Trim(top_db=20, p=1.0),
        Resample(min_sample_rate=8000, max_sample_rate=22050, p=0.5),
        ClippingDistortion(min_percentile_threshold=0, max_percentile_threshold=20, p=0.8),
        HighPassFilter(min_cutoff_freq=200, max_cutoff_freq=800, p=1.0),
        Normalize(p=1.0),
    ]
)

# Pipeline C: Rotting Tape (pads / textures)
pipe_tape_rot = Compose(
    [
        Trim(top_db=30, p=1.0),
        AddGaussianNoise(min_amplitude=0.001, max_amplitude=0.015, p=1.0),
        PitchShift(min_semitones=-0.5, max_semitones=0.5, p=1.0),
        TimeStretch(min_rate=0.9, max_rate=1.1, p=0.5),
        LowPassFilter(min_cutoff_freq=2000, max_cutoff_freq=6000, p=1.0),
        Normalize(p=1.0),
    ]
)

PIPELINE_MAP = {
    "01_Foundation_Bass": pipe_clean,
    "02_Rhythm_Drums": pipe_industrial,
    "03_Harmony_Pads": pipe_tape_rot,
    "04_Texture_Foley": pipe_tape_rot,
    "default": pipe_clean,
}


def process_file(file_path: str, output_path: str, pipeline: Compose) -> None:
    """Loads, processes, and saves a single audio file."""
    try:
        y, _ = librosa.load(file_path, sr=SAMPLE_RATE, mono=True)
        y_processed = pipeline(samples=y, sample_rate=SAMPLE_RATE)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        sf.write(output_path, y_processed, SAMPLE_RATE)
        print(f"  [OK] {os.path.basename(file_path)}")
    except Exception as exc:
        print(f"  [ERR] Failed {file_path}: {exc}")


def run_refinery():
    print("DAiW Audio Refinery")
    print(f"   Input : {INPUT_DIR}")
    print(f"   Output: {OUTPUT_DIR}")

    if not os.path.exists(INPUT_DIR):
        print(f"Input directory not found: {INPUT_DIR}")
        print("   Create it and drop your raw samples in subfolders.")
        return

    for root, _, files in os.walk(INPUT_DIR):
        for filename in files:
            if not filename.lower().endswith((".wav", ".mp3", ".aiff", ".flac")):
                continue

            category = os.path.basename(root)
            pipeline = PIPELINE_MAP.get(category, PIPELINE_MAP["default"])

            input_path = os.path.join(root, filename)
            rel_path = os.path.relpath(input_path, INPUT_DIR)
            output_path = os.path.join(OUTPUT_DIR, rel_path)
            output_path = os.path.splitext(output_path)[0] + ".wav"

            process_file(input_path, output_path, pipeline)

    print("\nRefinery complete. Use 'refined' folder inside your DAW sampler.")


if __name__ == "__main__":
    run_refinery()
