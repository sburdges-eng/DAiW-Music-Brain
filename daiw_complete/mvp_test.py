#!/usr/bin/env python3
"""
MVP test:
    "I feel broken" → plan → MIDI file in audio_vault/output/
"""

from pathlib import Path

from music_brain.structure.comprehensive_engine import TherapySession, render_plan_to_midi

OUT_DIR = Path("audio_vault/output")


def run_mvp():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    session = TherapySession()
    mood = session.process_core_input("I feel broken")
    session.set_scales(motivation=6, chaos=0.4)

    plan = session.generate_plan()
    out_path = OUT_DIR / "i_feel_broken.mid"
    midi_path = render_plan_to_midi(plan, str(out_path), vulnerability=0.6)

    print(f"MVP test complete.")
    print(f"  Mood : {mood}")
    print(f"  Mode : {plan.mode}")
    print(f"  Bars : {plan.length_bars}")
    print(f"  BPM  : {plan.tempo_bpm}")
    print(f"  MIDI : {midi_path}")


if __name__ == "__main__":
    run_mvp()
