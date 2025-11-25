"""
DAiW Audio Refinery
===================
Batch processor to transform raw samples into the C2 Industrial / LoFi palette.

Usage (from repo root):
    python -m music_brain.audio_refinery
"""

import os
from typing import Optional

import librosa
import numpy as np
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

# Pipelines
pipe_clean = Compose(
    [
        Trim(top_db=20, p=1.0),
        Normalize(p=1.0),
    ]
)

pipe_industrial = Compose(
    [
        Trim(top_db=20, p=1.0),
        Resample(min_sample_rate=8000, max_sample_rate=22050, p=0.5),
        ClippingDistortion(
            min_percentile_threshold=0, max_percentile_threshold=20, p=0.8
        ),
        HighPassFilter(min_cutoff_freq=200, max_cutoff_freq=800, p=1.0),
        Normalize(p=1.0),
    ]
)

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


def _process_file(file_path: str, output_path: str, pipeline: Compose) -> None:
    try:
        y, _ = librosa.load(file_path, sr=SAMPLE_RATE, mono=True)
        y_proc = pipeline(samples=y, sample_rate=SAMPLE_RATE)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        sf.write(output_path, y_proc, SAMPLE_RATE)
        print(f"  [OK] {os.path.basename(file_path)}")
    except Exception as e:
        print(f"  [ERR] {file_path}: {e}")


def refine_folder(
    input_dir: str,
    output_dir: str,
    pipeline: Optional[Compose] = None,
) -> None:
    """
    Generic folder → folder refinement with a specific pipeline.
    """
    if pipeline is None:
        pipeline = pipe_clean

    if not os.path.exists(input_dir):
        print(f"❌ Input directory not found: {input_dir}")
        return

    for root, _, files in os.walk(input_dir):
        for filename in files:
            if not filename.lower().endswith((".wav", ".aiff", ".flac", ".mp3")):
                continue

            in_path = os.path.join(root, filename)
            rel_path = os.path.relpath(in_path, input_dir)
            out_path = os.path.join(output_dir, rel_path)
            out_path = os.path.splitext(out_path)[0] + ".wav"

            _process_file(in_path, out_path, pipeline)


def run_refinery() -> None:
    print("🏭 DAiW Audio Refinery")
    print(f"   Input : {INPUT_DIR}")
    print(f"   Output: {OUTPUT_DIR}")

    if not os.path.exists(INPUT_DIR):
        print(f"❌ Input directory not found: {INPUT_DIR}")
        print("   Create it and dump your raw samples there.")
        return

    for root, _, files in os.walk(INPUT_DIR):
        if not files:
            continue

        category = os.path.basename(root)
        pipeline = PIPELINE_MAP.get(category, PIPELINE_MAP["default"])

        for filename in files:
            if not filename.lower().endswith((".wav", ".aiff", ".flac", ".mp3")):
                continue

            in_path = os.path.join(root, filename)
            rel_path = os.path.relpath(in_path, INPUT_DIR)
            out_path = os.path.join(OUTPUT_DIR, rel_path)
            out_path = os.path.splitext(out_path)[0] + ".wav"

            _process_file(in_path, out_path, pipeline)

    print("✅ Refinery complete. Use 'refined' folder in your sampler.")


if __name__ == "__main__":
    run_refinery()
