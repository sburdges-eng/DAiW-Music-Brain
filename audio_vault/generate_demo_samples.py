#!/usr/bin/env python3
# audio_vault/generate_demo_samples.py
"""
Generate demo/test audio samples using synthesized tones.

Creates basic waveforms for testing the Audio Refinery pipeline
without needing external sample files.

Usage:
    python -m audio_vault.generate_demo_samples
    python -m audio_vault.generate_demo_samples --output ./samples
"""

import argparse
import os
from pathlib import Path

import numpy as np

# Optional: soundfile for writing audio
try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False


SAMPLE_RATE = 44100
DEFAULT_OUTPUT = Path(__file__).parent / "samples"


def generate_sine(frequency: float, duration: float, amplitude: float = 0.5) -> np.ndarray:
    """Generate a sine wave."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    return (amplitude * np.sin(2 * np.pi * frequency * t)).astype(np.float32)


def generate_square(frequency: float, duration: float, amplitude: float = 0.5) -> np.ndarray:
    """Generate a square wave."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    return (amplitude * np.sign(np.sin(2 * np.pi * frequency * t))).astype(np.float32)


def generate_noise(duration: float, amplitude: float = 0.3) -> np.ndarray:
    """Generate white noise."""
    samples = int(SAMPLE_RATE * duration)
    return (amplitude * np.random.randn(samples)).astype(np.float32)


def generate_kick(duration: float = 0.3) -> np.ndarray:
    """Generate a synthetic kick drum."""
    samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, samples, endpoint=False)

    # Pitch envelope: starts high, drops quickly
    freq_start = 150
    freq_end = 40
    freq = freq_start * np.exp(-t * 20) + freq_end

    # Generate sine with pitch envelope
    phase = np.cumsum(2 * np.pi * freq / SAMPLE_RATE)
    wave = np.sin(phase)

    # Amplitude envelope
    envelope = np.exp(-t * 10)

    return (0.8 * wave * envelope).astype(np.float32)


def generate_snare(duration: float = 0.2) -> np.ndarray:
    """Generate a synthetic snare drum."""
    samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, samples, endpoint=False)

    # Tone component
    tone = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 20)

    # Noise component
    noise = np.random.randn(samples) * np.exp(-t * 15)

    return (0.5 * (tone + 0.7 * noise)).astype(np.float32)


def generate_hihat(duration: float = 0.1) -> np.ndarray:
    """Generate a synthetic hi-hat."""
    samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, samples, endpoint=False)

    # Filtered noise
    noise = np.random.randn(samples)

    # High-pass effect (simple differentiation)
    filtered = np.diff(noise, prepend=noise[0])

    # Fast decay
    envelope = np.exp(-t * 40)

    return (0.3 * filtered * envelope).astype(np.float32)


def write_sample(audio: np.ndarray, path: Path) -> None:
    """Write audio to file."""
    if not SOUNDFILE_AVAILABLE:
        print(f"  [SKIP] soundfile not installed, cannot write {path.name}")
        return

    sf.write(str(path), audio, SAMPLE_RATE)
    print(f"  [OK] {path.name}")


def main():
    parser = argparse.ArgumentParser(description="Generate demo audio samples")
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output directory for samples"
    )
    args = parser.parse_args()

    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating demo samples in {output_dir}")
    print()

    if not SOUNDFILE_AVAILABLE:
        print("WARNING: soundfile not installed. Install with: pip install soundfile")
        print("Samples will not be written to disk.")
        print()

    # Tonal samples
    print("Tonal samples:")
    write_sample(generate_sine(440, 1.0), output_dir / "sine_440hz.wav")
    write_sample(generate_sine(220, 1.0), output_dir / "sine_220hz.wav")
    write_sample(generate_square(440, 1.0), output_dir / "square_440hz.wav")
    write_sample(generate_noise(1.0), output_dir / "white_noise.wav")

    # Drum samples
    print("\nDrum samples:")
    write_sample(generate_kick(), output_dir / "kick_synth.wav")
    write_sample(generate_snare(), output_dir / "snare_synth.wav")
    write_sample(generate_hihat(), output_dir / "hihat_synth.wav")

    # Musical notes (C major scale)
    print("\nMusical notes (C major):")
    note_freqs = {
        "C4": 261.63,
        "D4": 293.66,
        "E4": 329.63,
        "F4": 349.23,
        "G4": 392.00,
        "A4": 440.00,
        "B4": 493.88,
        "C5": 523.25,
    }
    for note, freq in note_freqs.items():
        write_sample(generate_sine(freq, 0.5), output_dir / f"note_{note}.wav")

    print("\nDone!")


if __name__ == "__main__":
    main()
