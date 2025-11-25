#!/usr/bin/env python3
# audio_vault/mvp_test.py
"""
MVP Test - Quick validation of the DAiW pipeline.

Runs through the core workflow:
1. TherapySession with sample input
2. HarmonyPlan generation
3. MIDI rendering
4. (Optional) Audio processing if samples available

Usage:
    python -m audio_vault.mvp_test
    python -m audio_vault.mvp_test --verbose
    python -m audio_vault.mvp_test --full  # Include audio processing
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path


def check_import(module_name: str, verbose: bool = False) -> bool:
    """Check if a module can be imported."""
    try:
        __import__(module_name)
        if verbose:
            print(f"  [OK] {module_name}")
        return True
    except ImportError as e:
        if verbose:
            print(f"  [FAIL] {module_name}: {e}")
        return False


def test_imports(verbose: bool = False) -> bool:
    """Test that all core modules can be imported."""
    print("Testing imports...")

    core_modules = [
        "music_brain",
        "music_brain.structure.comprehensive_engine",
        "music_brain.structure.tension",
        "music_brain.groove.engine",
        "music_brain.daw.logic",
    ]

    optional_modules = [
        "music_brain.lyrics.engine",
        "music_brain.audio_refinery",
    ]

    all_ok = True
    for mod in core_modules:
        if not check_import(mod, verbose):
            all_ok = False

    if verbose:
        print("\nOptional modules:")
    for mod in optional_modules:
        check_import(mod, verbose)

    return all_ok


def test_therapy_session(verbose: bool = False) -> bool:
    """Test TherapySession workflow."""
    print("\nTesting TherapySession...")

    try:
        from music_brain.structure.comprehensive_engine import (
            TherapySession,
            render_plan_to_midi,
        )

        session = TherapySession()

        # Process input
        affect = session.process_core_input(
            "I feel trapped between who I am and who I'm supposed to be"
        )
        if verbose:
            print(f"  Detected affect: {affect}")

        # Set scales
        session.set_scales(motivation=7, complexity=0.5)

        # Generate plan
        plan = session.generate_plan()
        if verbose:
            print(f"  Generated plan:")
            print(f"    Mode: {plan.root_note} {plan.mode}")
            print(f"    Tempo: {plan.tempo_bpm} BPM")
            print(f"    Length: {plan.length_bars} bars")
            print(f"    Chords: {' - '.join(plan.chord_symbols)}")

        # Render MIDI
        with tempfile.TemporaryDirectory() as tmpdir:
            midi_path = os.path.join(tmpdir, "test_session.mid")
            result = render_plan_to_midi(plan, midi_path)

            if os.path.exists(result) and os.path.getsize(result) > 0:
                if verbose:
                    print(f"  MIDI rendered: {os.path.getsize(result)} bytes")
                return True
            else:
                print("  [FAIL] MIDI file not created or empty")
                return False

    except Exception as e:
        print(f"  [FAIL] {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def test_tension_curves(verbose: bool = False) -> bool:
    """Test tension curve generation."""
    print("\nTesting tension curves...")

    try:
        from music_brain.structure.tension import generate_tension_curve
        import numpy as np

        for preset in ["climb", "standard", "constant"]:
            curve = generate_tension_curve(32, preset)
            if verbose:
                print(f"  {preset}: min={curve.min():.2f}, max={curve.max():.2f}, len={len(curve)}")

            if len(curve) != 32:
                print(f"  [FAIL] {preset} returned wrong length")
                return False

        return True

    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def test_groove_engine(verbose: bool = False) -> bool:
    """Test groove engine humanization."""
    print("\nTesting groove engine...")

    try:
        from music_brain.groove.engine import apply_groove

        test_notes = [
            {"start_tick": 0, "velocity": 80, "pitch": 60, "duration_ticks": 480},
            {"start_tick": 480, "velocity": 80, "pitch": 62, "duration_ticks": 480},
            {"start_tick": 960, "velocity": 80, "pitch": 64, "duration_ticks": 480},
        ]

        processed = apply_groove(test_notes, complexity=0.5, vulnerability=0.5)

        if verbose:
            print(f"  Input notes: {len(test_notes)}")
            print(f"  Output notes: {len(processed)}")
            for i, (orig, new) in enumerate(zip(test_notes, processed)):
                drift = new["start_tick"] - orig["start_tick"]
                vel_change = new["velocity"] - orig["velocity"]
                print(f"    Note {i}: drift={drift:+d} ticks, vel={vel_change:+d}")

        return True

    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def test_audio_processing(verbose: bool = False) -> bool:
    """Test audio refinery (optional)."""
    print("\nTesting audio refinery...")

    try:
        from music_brain.audio_refinery import process_sample, PIPELINE_MAP
        import numpy as np

        # Generate test audio
        sr = 44100
        duration = 0.5
        t = np.linspace(0, duration, int(sr * duration))
        test_audio = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)

        for pipeline_name in ["clean", "industrial"]:
            if pipeline_name in PIPELINE_MAP:
                processed = process_sample(test_audio, sr, pipeline_name)
                if verbose:
                    print(f"  {pipeline_name}: in={len(test_audio)}, out={len(processed)}")

        return True

    except ImportError as e:
        if verbose:
            print(f"  [SKIP] audiomentations not installed: {e}")
        return True  # Not a failure, just optional

    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="DAiW MVP Test")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--full", "-f", action="store_true", help="Include audio tests")
    args = parser.parse_args()

    print("=" * 50)
    print("DAiW MVP Test")
    print("=" * 50)

    results = {}

    results["imports"] = test_imports(args.verbose)
    results["therapy_session"] = test_therapy_session(args.verbose)
    results["tension_curves"] = test_tension_curves(args.verbose)
    results["groove_engine"] = test_groove_engine(args.verbose)

    if args.full:
        results["audio_processing"] = test_audio_processing(args.verbose)

    print("\n" + "=" * 50)
    print("Results:")
    print("=" * 50)

    all_passed = True
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
