"""
DAiW Desktop UI (Streamlit)
===========================
Thin face over the TherapySession + Renderer + Lyric Mirror.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import streamlit as st

from music_brain.structure.comprehensive_engine import (
    TherapySession,
    render_plan_to_midi,
    select_kit_for_mood,
)
from music_brain.structure.tension import generate_tension_curve
from music_brain.lyrics.engine import get_lyric_fragments


def main() -> None:
    st.set_page_config(page_title="DAiW", page_icon="🎧", layout="centered")

    st.title("DAiW – Digital Audio Intimate Workstation")
    st.caption("Interrogate before you generate.")

    st.subheader("Phase 0: Core Wound")
    phrase = st.text_area(
        "What is hurting you?",
        height=120,
        placeholder="Type something you would actually put in a song...",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        mot = st.slider("Motivation", 1, 10, 5)
    with col2:
        chaos = st.slider("Chaos", 0, 10, 5)
    with col3:
        vuln = st.slider("Vulnerability", 0.0, 1.0, 0.3)

    if st.button("Generate Session", type="primary"):
        if not phrase.strip():
            st.error("Give me *something* to work with, not just whitespace.")
            return

        session = TherapySession()
        mood = session.process_core_input(phrase)
        session.set_scales(motivation=mot, chaos=chaos / 10.0)
        plan = session.generate_plan()

        st.success("Session generated.")

        left, right = st.columns(2)
        with left:
            st.write(
                f"**Mood:** `{plan.mood_profile}`  ·  "
                f"**Mode:** `{plan.mode}`  ·  "
                f"**Tempo:** `{plan.tempo_bpm} BPM`"
            )
        with right:
            st.write(
                f"**Length:** `{plan.length_bars} bars`  ·  "
                f"**Structure:** `{plan.structure_type}`"
            )

        kit = select_kit_for_mood(plan.mood_profile)
        st.write(f"🎛️ **Suggested Kit:** `{kit}`")

        # Allow user override of macro structure
        override = st.selectbox(
            "Structure override",
            ["Auto (from mood)", "Standard (Verse/Chorus)", "Climb", "Constant"],
            index=0,
        )
        if override == "Standard (Verse/Chorus)":
            plan.structure_type = "standard"
        elif override == "Climb":
            plan.structure_type = "climb"
        elif override == "Constant":
            plan.structure_type = "constant"

        # Generate MIDI into temp file
        tmp_dir = tempfile.mkdtemp(prefix="daiw_")
        midi_path = os.path.join(tmp_dir, "daiw_output.mid")
        midi_path = render_plan_to_midi(
            plan,
            midi_path,
            vulnerability=vuln,
            seed=42,
        )

        try:
            with open(midi_path, "rb") as f:
                midi_bytes = f.read()

            st.download_button(
                label="⬇️ Download MIDI",
                data=midi_bytes,
                file_name="daiw_output.mid",
                mime="audio/midi",
            )
        except Exception as e:
            st.error(f"Couldn't load MIDI: {e}")

        # Visualize tension curve
        st.subheader("Song Structure (Tension)")
        curve = generate_tension_curve(plan.length_bars, plan.structure_type)
        st.line_chart(curve)
        st.caption("Y = intensity, X = bar number.")

        # Lyrical mirror
        st.subheader("📝 Lyrical Mirror")
        st.caption("Fragments to jumpstart the words.")
        frags = get_lyric_fragments(phrase, plan.mood_profile)
        for line in frags:
            st.text(line)
        st.info(
            "Drop .txt files of lyrics/poems into `music_brain/data/corpus` "
            "to train your own ghost."
        )


if __name__ == "__main__":
    main()
