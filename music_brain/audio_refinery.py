# music_brain/audio_refinery.py
"""
Audio Refinery - Sample Processing Pipelines

Transforms raw audio samples into textured, processed sounds using
audiomentations. Includes presets for Industrial/Glitch and Tape Rot aesthetics.
"""
import os
import librosa
import soundfile as sf
from audiomentations import (
    Compose, AddGaussianNoise, TimeStretch, PitchShift,
    ClippingDistortion, HighPassFilter, LowPassFilter,
    Normalize, Trim, Resample
)

INPUT_DIR = "./audio_vault/raw"
OUTPUT_DIR = "./audio_vault/refined"
SAMPLE_RATE = 44100

# PIPELINES
pipe_industrial = Compose([
    Trim(top_db=20, p=1.0),
    Resample(min_sample_rate=8000, max_sample_rate=22050, p=0.5),
    ClippingDistortion(min_percentile_threshold=0, max_percentile_threshold=20, p=0.8),
    HighPassFilter(min_cutoff_freq=200, max_cutoff_freq=800, p=1.0),
    Normalize(p=1.0)
])

pipe_tape_rot = Compose([
    Trim(top_db=30, p=1.0),
    AddGaussianNoise(min_amplitude=0.001, max_amplitude=0.015, p=1.0),
    PitchShift(min_semitones=-0.5, max_semitones=0.5, p=1.0),
    TimeStretch(min_rate=0.9, max_rate=1.1, p=0.5),
    LowPassFilter(min_cutoff_freq=2000, max_cutoff_freq=6000, p=1.0),
    Normalize(p=1.0)
])


def run_refinery():
    """Process all audio files in INPUT_DIR through appropriate pipelines."""
    print(f"Refinery running on {INPUT_DIR}...")
    if not os.path.exists(INPUT_DIR):
        print("Input directory missing.")
        return

    for root, dirs, files in os.walk(INPUT_DIR):
        for filename in files:
            if filename.lower().endswith(('.wav', '.mp3', '.aiff')):
                # Simple logic: Drums = Industrial, Pads = Tape Rot
                pipeline = pipe_industrial if "Drums" in root else pipe_tape_rot

                input_path = os.path.join(root, filename)
                rel_path = os.path.relpath(input_path, INPUT_DIR)
                output_path = os.path.join(OUTPUT_DIR, rel_path)
                output_path = os.path.splitext(output_path)[0] + ".wav"

                try:
                    y, sr = librosa.load(input_path, sr=SAMPLE_RATE, mono=True)
                    y_proc = pipeline(samples=y, sample_rate=SAMPLE_RATE)
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    sf.write(output_path, y_proc, SAMPLE_RATE)
                    print(f"  [OK] Refined: {filename}")
                except Exception as e:
                    print(f"  [ERR] {filename}: {e}")


if __name__ == "__main__":
    run_refinery()
