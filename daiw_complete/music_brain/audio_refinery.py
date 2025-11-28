"""
DAiW Audio Refinery
===================
Batch processor to transform raw samples into the C2 Industrial / LoFi palette.

Usage (from repo root):

  python -m music_brain.audio_refinery
  python -m music_brain.audio_refinery 02_Rhythm_Drums

If a subfolder name is given, only that category is processed.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional, Callable

try:
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
    HAS_AUDIO_LIBS = True
except ImportError:
    HAS_AUDIO_LIBS = False

INPUT_DIR = Path("./audio_vault/raw")
OUTPUT_DIR = Path("./audio_vault/refined")
SAMPLE_RATE = 44100


def _get_pipelines():
    """Build pipelines only if libs available."""
    if not HAS_AUDIO_LIBS:
        return {}, None, None, None
    
    pipe_clean = Compose([
        Trim(top_db=20, p=1.0),
        Normalize(p=1.0),
    ])

    pipe_industrial = Compose([
        Trim(top_db=20, p=1.0),
        Resample(min_sample_rate=8000, max_sample_rate=22050, p=0.5),
        ClippingDistortion(
            min_percentile_threshold=0,
            max_percentile_threshold=20,
            p=0.8,
        ),
        HighPassFilter(min_cutoff_freq=200, max_cutoff_freq=800, p=1.0),
        Normalize(p=1.0),
    ])

    pipe_tape_rot = Compose([
        Trim(top_db=30, p=1.0),
        AddGaussianNoise(min_amplitude=0.001, max_amplitude=0.015, p=1.0),
        PitchShift(min_semitones=-0.5, max_semitones=0.5, p=1.0),
        TimeStretch(min_rate=0.9, max_rate=1.1, p=0.5),
        LowPassFilter(min_cutoff_freq=2000, max_cutoff_freq=6000, p=1.0),
        Normalize(p=1.0),
    ])

    pipeline_map = {
        "01_Foundation_Bass": pipe_clean,
        "02_Rhythm_Drums": pipe_industrial,
        "03_Harmony_Pads": pipe_tape_rot,
        "04_Texture_Foley": pipe_tape_rot,
        "default": pipe_clean,
    }
    
    return pipeline_map, pipe_clean, pipe_industrial, pipe_tape_rot


PIPELINE_MAP, pipe_clean, pipe_industrial, pipe_tape_rot = _get_pipelines()


def process_file(file_path: str, output_path: str, pipeline) -> None:
    """Process a single audio file through the pipeline."""
    if not HAS_AUDIO_LIBS:
        print("❌ Audio libraries not installed (librosa, soundfile, audiomentations)")
        return
        
    try:
        y, _ = librosa.load(file_path, sr=SAMPLE_RATE, mono=True)
        y_proc = pipeline(samples=y, sample_rate=SAMPLE_RATE)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        sf.write(output_path, y_proc, SAMPLE_RATE)
        print(f"  [OK] {os.path.basename(file_path)}")
    except Exception as e:
        print(f"  [ERR] {file_path}: {e}")


def refine_folder(
    input_dir: Path,
    output_dir: Path,
    pipeline = None,
) -> None:
    """
    Generic folder → folder refinement with a specific pipeline.
    """
    if not HAS_AUDIO_LIBS:
        print("❌ Audio libraries not installed")
        return
        
    if pipeline is None:
        pipeline = pipe_clean

    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return

    for root, _, files in os.walk(input_dir):
        for filename in files:
            if not filename.lower().endswith((".wav", ".aiff", ".flac", ".mp3")):
                continue

            in_path = Path(root) / filename
            rel_path = in_path.relative_to(input_dir)
            out_path = output_dir / rel_path
            out_path = out_path.with_suffix(".wav")

            process_file(str(in_path), str(out_path), pipeline)


def run_refinery(target_subfolder: Optional[str] = None) -> None:
    if not HAS_AUDIO_LIBS:
        print("❌ Audio libraries not installed. Run:")
        print("   pip install librosa soundfile audiomentations")
        return
        
    print("🏭 DAiW Audio Refinery")
    print(f"   Input : {INPUT_DIR}")
    print(f"   Output: {OUTPUT_DIR}")

    if not INPUT_DIR.exists():
        print(f"❌ Input directory not found: {INPUT_DIR}")
        print("   Create it and dump your raw samples there.")
        return

    if target_subfolder:
        root = INPUT_DIR / target_subfolder
        pipeline = PIPELINE_MAP.get(target_subfolder, PIPELINE_MAP.get("default"))
        if not root.exists():
            print(f"❌ Subfolder '{target_subfolder}' not found under {INPUT_DIR}")
            return
        print(f"→ Refining only: {target_subfolder}")
        refine_folder(root, OUTPUT_DIR / target_subfolder, pipeline)
        print("✅ Done.")
        return

    # Full walk
    for root, _, files in os.walk(INPUT_DIR):
        if not files:
            continue

        category = os.path.basename(root)
        pipeline = PIPELINE_MAP.get(category, PIPELINE_MAP.get("default"))

        print(f"\n[Category] {category}")
        for filename in files:
            if not filename.lower().endswith((".wav", ".aiff", ".flac", ".mp3")):
                continue

            in_path = Path(root) / filename
            rel_path = in_path.relative_to(INPUT_DIR)
            out_path = OUTPUT_DIR / rel_path
            out_path = out_path.with_suffix(".wav")

            process_file(str(in_path), str(out_path), pipeline)

    print("\n✅ Refinery complete. Use 'refined' folder in your sampler.")


if __name__ == "__main__":
    sub = sys.argv[1] if len(sys.argv) > 1 else None
    run_refinery(sub)
