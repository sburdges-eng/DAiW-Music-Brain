#!/usr/bin/env python3
"""
Basic Therapy to MIDI Example
=============================

Minimal example showing how to go from emotional text input to MIDI output.

Usage:
    python examples/basic_therapy_to_midi.py "I feel broken but still here"
    python examples/basic_therapy_to_midi.py --help

Output:
    Creates a MIDI file (default: output.mid) that you can drag into any DAW.
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Generate MIDI from emotional text input using DAiW therapy engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python examples/basic_therapy_to_midi.py "I miss my grandmother"
    python examples/basic_therapy_to_midi.py "I am furious" -o rage_session.mid
    python examples/basic_therapy_to_midi.py "Everything feels numb" --motivation 3 --chaos 0.2
        """,
    )
    parser.add_argument(
        "text",
        help="Emotional text input (what is hurting you?)",
    )
    parser.add_argument(
        "-o", "--output",
        default="output.mid",
        help="Output MIDI file path (default: output.mid)",
    )
    parser.add_argument(
        "-m", "--motivation",
        type=int,
        default=5,
        choices=range(1, 11),
        metavar="1-10",
        help="Motivation scale 1-10 (default: 5). Higher = longer output.",
    )
    parser.add_argument(
        "-c", "--chaos",
        type=float,
        default=0.5,
        help="Chaos tolerance 0.0-1.0 (default: 0.5). Higher = more complexity.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed analysis output",
    )

    args = parser.parse_args()

    # Import after argparse to keep --help fast
    try:
        from music_brain.structure.comprehensive_engine import (
            TherapySession,
            render_plan_to_midi,
        )
    except ImportError as e:
        print(f"Error: Could not import music_brain. Make sure it's installed:")
        print(f"    pip install -e .")
        print(f"\nDetails: {e}")
        sys.exit(1)

    # Create therapy session
    session = TherapySession()

    # Phase 0: Process the core emotional input
    affect = session.process_core_input(args.text)

    if args.verbose:
        print(f"\n{'='*50}")
        print("EMOTIONAL ANALYSIS")
        print(f"{'='*50}")
        print(f"Input: \"{args.text}\"")
        print(f"Primary affect: {affect}")
        if session.state.affect_result:
            if session.state.affect_result.secondary:
                print(f"Secondary affect: {session.state.affect_result.secondary}")
            print(f"Intensity: {session.state.affect_result.intensity:.2f}")
        print(f"Suggested mode: {session.state.suggested_mode}")

    # Set motivation and chaos scales
    chaos = max(0.0, min(1.0, args.chaos))
    session.set_scales(args.motivation, chaos)

    # Generate the harmony plan
    plan = session.generate_plan()

    if args.verbose:
        print(f"\n{'='*50}")
        print("GENERATION PLAN")
        print(f"{'='*50}")
        print(f"Key: {plan.root_note} {plan.mode}")
        print(f"Tempo: {plan.tempo_bpm} BPM")
        print(f"Length: {plan.length_bars} bars")
        print(f"Structure: {plan.structure_type}")
        print(f"Progression: {' - '.join(plan.chord_symbols)}")
        print(f"Complexity: {plan.complexity:.2f}")

    # Render to MIDI
    output_path = render_plan_to_midi(plan, args.output)

    print(f"\n{'='*50}")
    print("OUTPUT")
    print(f"{'='*50}")
    print(f"MIDI file written to: {output_path}")
    print(f"\nNext steps:")
    print(f"  1. Open your DAW (Logic, Ableton, FL Studio, etc.)")
    print(f"  2. Drag {output_path} onto a track")
    print(f"  3. Load a piano or pad instrument")
    print(f"  4. Hit play")


if __name__ == "__main__":
    main()
