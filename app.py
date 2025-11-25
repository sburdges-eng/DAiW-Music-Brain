# app.py
"""
DAiW Streamlit UI - Desktop-facing product interface.

Simple flow: talk to TherapySession, show the analysis, render MIDI, offer download.
"""
import os
import tempfile

import streamlit as st

from music_brain.structure.comprehensive_engine import (
    TherapySession,
    render_plan_to_midi,
)


def main() -> None:
    st.set_page_config(
        page_title="DAiW - Digital Audio Intimate Workstation",
        layout="centered",
    )

    st.title("DAiW - Digital Audio Intimate Workstation")
    st.caption("Creative companion, not a factory.")

    st.markdown("### 1. Tell me what hurts")

    default_text = "I feel dead inside because I chose safety over freedom."
    user_text = st.text_area(
        "What is hurting you right now?",
        value=default_text,
        height=140,
    )

    st.markdown("### 2. Set your state")

    col1, col2 = st.columns(2)

    with col1:
        motivation = st.slider(
            "Motivation (1 = sketch, 10 = full piece)",
            min_value=1,
            max_value=10,
            value=7,
        )

    with col2:
        chaos_1_10 = st.slider(
            "Chaos tolerance (1-10)",
            min_value=1,
            max_value=10,
            value=5,
            help="Higher = more unstable tempo and structure.",
        )

    st.markdown("### 3. Generate session")

    if st.button("Generate MIDI session"):
        if not user_text.strip():
            st.error("I need at least one sentence to work with.")
            return

        session = TherapySession()
        affect = session.process_core_input(user_text)
        session.set_scales(motivation, chaos_1_10 / 10.0)
        plan = session.generate_plan()

        st.subheader("Analysis")
        if session.state.affect_result:
            st.write(f"**Primary affect:** `{affect}`")
            if session.state.affect_result.secondary:
                st.write(
                    f"**Secondary undertone:** "
                    f"`{session.state.affect_result.secondary}`"
                )
            st.write(
                f"**Affect intensity:** "
                f"`{session.state.affect_result.intensity:.2f}`"
            )

        st.subheader("Generation directive")
        st.write(f"- Mode: **{plan.root_note} {plan.mode}**")
        st.write(f"- Tempo: **{plan.tempo_bpm} BPM**")
        st.write(f"- Length: **{plan.length_bars} bars**")
        st.write(f"- Progression: `{' - '.join(plan.chord_symbols)}`")
        st.write(f"- Complexity (chaos): `{plan.complexity:.2f}`")

        with st.spinner("Rendering MIDI..."):
            tmpdir = tempfile.mkdtemp(prefix="daiw_")
            midi_path = os.path.join(tmpdir, "daiw_therapy_session.mid")
            midi_path = render_plan_to_midi(plan, midi_path)

        st.success("MIDI generated.")

        try:
            with open(midi_path, "rb") as f:
                st.download_button(
                    label="Download MIDI",
                    data=f.read(),
                    file_name="daiw_therapy_session.mid",
                    mime="audio/midi",
                )
        except OSError:
            st.error("MIDI file could not be read back from disk.")


if __name__ == "__main__":
    main()
