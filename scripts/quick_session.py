#!/usr/bin/env python3
"""
Quick Session - Run a therapy-to-MIDI session from command line.

This is a convenience script for running the full DAiW pipeline
from text input to MIDI output.

Usage:
    python scripts/quick_session.py "Your emotional text here"
    python scripts/quick_session.py --motivation 8 --chaos 3 "I feel lost"
    python scripts/quick_session.py -o output.mid "Something needs to change"

Examples:
    python scripts/quick_session.py "I chose safety over freedom"
    python scripts/quick_session.py --motivation 10 "Ready to fight back"
    python scripts/quick_session.py --chaos 7 "Everything is falling apart"
"""

import argparse
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from music_brain.structure.comprehensive_engine import (
    TherapySession,
    render_plan_to_midi,
    select_kit_for_mood,
)


def run_quick_session(
    text: str,
    motivation: int = 7,
    chaos: int = 5,
    vulnerability: float = 0.5,
    output_path: str = "session_output.mid",
) -> dict:
    """
    Run a quick therapy-to-MIDI session.

    Args:
        text: Emotional input text
        motivation: 1-10 scale (affects length: 1=16bars, 10=64bars)
        chaos: 1-10 scale (affects tempo stability and complexity)
        vulnerability: 0-1 scale (affects dynamics and humanization)
        output_path: Where to save the MIDI file

    Returns:
        Session results dictionary
    """
    print(f"\n{'='*60}")
    print("DAiW Quick Session")
    print(f"{'='*60}\n")

    print(f"Input: \"{text}\"")
    print(f"Motivation: {motivation}/10")
    print(f"Chaos: {chaos}/10")
    print(f"Vulnerability: {vulnerability:.1f}")
    print()

    # Create and configure session
    session = TherapySession()
    session.set_scales(motivation, chaos / 10.0)

    # Process input
    print("Processing emotional content...")
    affect = session.process_core_input(text)
    print(f"  Primary affect: {affect}")

    if session.state.affect_result:
        if session.state.affect_result.secondary:
            print(f"  Secondary: {session.state.affect_result.secondary}")
        print(f"  Intensity: {session.state.affect_result.intensity:.2f}")

    # Generate plan
    print("\nGenerating harmony plan...")
    plan = session.generate_plan()

    print(f"  Mode: {plan.root_note} {plan.mode}")
    print(f"  Tempo: {plan.tempo_bpm} BPM")
    print(f"  Length: {plan.length_bars} bars")
    print(f"  Progression: {' - '.join(plan.chord_symbols)}")
    print(f"  Structure: {plan.structure_type}")
    print(f"  Complexity: {plan.complexity:.2f}")

    # Kit recommendation
    kit = select_kit_for_mood(plan.mood_profile)
    print(f"\nRecommended kit: {kit}")

    # Render MIDI
    print(f"\nRendering MIDI to: {output_path}")
    midi_path = render_plan_to_midi(plan, output_path, vulnerability)
    print(f"  Done: {midi_path}")

    # Summary
    print(f"\n{'='*60}")
    print("Session Complete!")
    print(f"{'='*60}")
    print(f"""
Next steps:
  1. Drag {output_path} into your DAW
  2. Load the '{kit}' kit or similar sounds
  3. The tension curve is baked into the velocities
  4. Iterate and make it yours
""")

    return {
        "affect": affect,
        "plan": plan,
        "kit": kit,
        "midi_path": midi_path,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Run a quick therapy-to-MIDI session",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "I feel lost in the darkness"
  %(prog)s --motivation 10 "Ready to fight back"
  %(prog)s --chaos 7 -o my_session.mid "Everything is chaos"
        """
    )

    parser.add_argument(
        "text",
        help="Your emotional input text"
    )
    parser.add_argument(
        "-m", "--motivation",
        type=int,
        default=7,
        choices=range(1, 11),
        metavar="1-10",
        help="Motivation level (affects length, default: 7)"
    )
    parser.add_argument(
        "-c", "--chaos",
        type=int,
        default=5,
        choices=range(1, 11),
        metavar="1-10",
        help="Chaos level (affects tempo/complexity, default: 5)"
    )
    parser.add_argument(
        "-v", "--vulnerability",
        type=float,
        default=0.5,
        help="Vulnerability 0-1 (affects dynamics, default: 0.5)"
    )
    parser.add_argument(
        "-o", "--output",
        default="session_output.mid",
        help="Output MIDI file path (default: session_output.mid)"
    )

    args = parser.parse_args()

    # Clamp vulnerability
    vulnerability = max(0.0, min(1.0, args.vulnerability))

    run_quick_session(
        text=args.text,
        motivation=args.motivation,
        chaos=args.chaos,
        vulnerability=vulnerability,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
