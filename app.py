# app.py
"""
DAiW Streamlit UI - Desktop-facing product interface.

Enhanced flow with:
- Tension curve visualization
- Kit selection for sample processing
- Lyric mirror integration

Simple flow: talk to TherapySession, show the analysis, render MIDI, offer download.
"""

import os
import tempfile

import streamlit as st
import numpy as np

from music_brain.structure.comprehensive_engine import (
    TherapySession,
    render_plan_to_midi,
)
from music_brain.structure.tension import generate_tension_curve

# Optional imports
try:
    from music_brain.lyrics.engine import get_lyric_fragments
    LYRICS_AVAILABLE = True
except ImportError:
    LYRICS_AVAILABLE = False

try:
    from music_brain.audio_refinery import PIPELINE_MAP
    AUDIO_REFINERY_AVAILABLE = True
except ImportError:
    AUDIO_REFINERY_AVAILABLE = False


# Kit options for sample processing
KIT_OPTIONS = {
    "Clean": "clean",
    "Industrial (gritty, distorted)": "industrial",
    "Tape Rot (warm, degraded)": "tape_rot",
}


def render_tension_curve(total_bars: int, structure_type: str) -> None:
    """Render tension curve visualization using Streamlit."""
    curve = generate_tension_curve(total_bars, structure_type)

    if len(curve) == 0:
        st.warning("No tension curve generated.")
        return

    # Create chart data
    import pandas as pd
    chart_data = pd.DataFrame({
        "Bar": list(range(1, len(curve) + 1)),
        "Tension": curve.tolist(),
    })

    st.bar_chart(chart_data, x="Bar", y="Tension", height=200)


def render_lyric_fragments(core_text: str, affect: str) -> None:
    """Render lyric mirror suggestions."""
    if not LYRICS_AVAILABLE:
        st.info("Lyric Mirror unavailable (install markovify)")
        return

    st.markdown("#### Lyric Fragments")
    st.caption("Cut-up suggestions based on your input")

    fragments = get_lyric_fragments(core_text, affect, count=4)

    if fragments:
        for frag in fragments:
            st.markdown(f"_{frag}_")
    else:
        st.write("_No fragments generated. Feed the corpus with more text._")


def main() -> None:
    st.set_page_config(
        page_title="DAiW - Digital Audio Intimate Workstation",
        layout="centered",
    )

    st.title("DAiW - Digital Audio Intimate Workstation")
    st.caption("Creative companion, not a factory.")

    # Sidebar for kit selection
    with st.sidebar:
        st.header("Settings")

        selected_kit = st.selectbox(
            "Sample Kit Style",
            options=list(KIT_OPTIONS.keys()),
            index=0,
            help="Affects how samples are processed through the Audio Refinery",
        )
        kit_pipeline = KIT_OPTIONS[selected_kit]

        if AUDIO_REFINERY_AVAILABLE:
            st.success(f"Kit: {selected_kit}")
        else:
            st.info("Audio Refinery unavailable")
            st.caption("Install audiomentations for sample processing")

        st.divider()

        st.caption("DAiW v0.3.0-alpha")
        st.caption("\"Interrogate Before Generate\"")

    # Main content
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

    # Structure type selection
    structure_type = st.selectbox(
        "Tension Arc",
        options=["standard", "climb", "constant"],
        index=0,
        help=(
            "climb = builds throughout, "
            "standard = verse/chorus dynamics, "
            "constant = flat energy"
        ),
    )

    st.markdown("### 3. Generate session")

    if st.button("Generate MIDI session", type="primary"):
        if not user_text.strip():
            st.error("I need at least one sentence to work with.")
            return

        session = TherapySession()
        affect = session.process_core_input(user_text)
        session.set_scales(motivation, chaos_1_10 / 10.0)
        plan = session.generate_plan()

        # Override structure type from UI selection
        plan.structure_type = structure_type

        st.divider()

        # Analysis section
        col_analysis, col_tension = st.columns([1, 1])

        with col_analysis:
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

        with col_tension:
            st.subheader("Tension Curve")
            render_tension_curve(plan.length_bars, plan.structure_type)

        st.divider()

        st.subheader("Generation directive")
        directive_col1, directive_col2 = st.columns(2)

        with directive_col1:
            st.write(f"- Mode: **{plan.root_note} {plan.mode}**")
            st.write(f"- Tempo: **{plan.tempo_bpm} BPM**")
            st.write(f"- Length: **{plan.length_bars} bars**")

        with directive_col2:
            st.write(f"- Progression: `{' - '.join(plan.chord_symbols)}`")
            st.write(f"- Complexity (chaos): `{plan.complexity:.2f}`")
            st.write(f"- Structure: `{plan.structure_type}`")

        # Lyric mirror section
        if LYRICS_AVAILABLE:
            st.divider()
            with st.expander("Lyric Mirror (experimental)", expanded=False):
                render_lyric_fragments(user_text, affect)

        # MIDI rendering
        st.divider()

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

        # Show selected kit info
        if AUDIO_REFINERY_AVAILABLE:
            st.info(f"Sample processing kit: **{selected_kit}** ({kit_pipeline})")


if __name__ == "__main__":
    main()
