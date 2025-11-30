# app.py
"""
DAiW Streamlit UI - Desktop-facing product interface.

Features:
- Therapy session processing
- Structure visualization
- Lyric fragment generation
- MIDI download
- Kit recommendations
"""
import os
import tempfile

import streamlit as st

from music_brain.structure.comprehensive_engine import (
    TherapySession,
    render_plan_to_midi,
    render_phrase_to_vault,
    select_kit_for_mood,
)

# Optional imports for enhanced features
try:
    from music_brain.lyrics.engine import get_lyric_fragments
    HAS_LYRICS = True
except ImportError:
    HAS_LYRICS = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def main() -> None:
    st.set_page_config(
        page_title="DAiW - Digital Audio Intimate Workstation",
        layout="centered",
    )

    st.title("DAiW Core")
    st.caption("Creative companion, not a factory. Interrogate before generate.")

    # ==========================================================================
    # INPUT SECTION
    # ==========================================================================
    st.markdown("### Input Wound")

    default_text = "I feel dead inside because I chose safety over freedom."
    user_text = st.text_area(
        "What is hurting you right now?",
        value=default_text,
        height=100,
        label_visibility="collapsed",
    )

    # ==========================================================================
    # CONTROLS
    # ==========================================================================
    col1, col2, col3 = st.columns(3)

    with col1:
        motivation = st.slider(
            "Motivation",
            min_value=1,
            max_value=10,
            value=7,
            help="1 = sketch (16 bars), 10 = full piece (64 bars)",
        )

    with col2:
        chaos_1_10 = st.slider(
            "Chaos",
            min_value=1,
            max_value=10,
            value=5,
            help="Higher = more unstable tempo and complexity",
        )

    with col3:
        vulnerability = st.slider(
            "Vulnerability",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            help="Higher = more humanization, softer dynamics",
        )

    # ==========================================================================
    # GENERATE BUTTON
    # ==========================================================================
    if st.button("Generate", type="primary"):
        if not user_text.strip():
            st.error("Speak. I need words to build structure.")
            return

        # Process
        session = TherapySession()
        session.set_scales(motivation, chaos_1_10 / 10.0)
        affect = session.process_core_input(user_text)
        plan = session.generate_plan()

        # Kit recommendation
        kit = select_kit_for_mood(plan.mood_profile)

        # ==========================================================================
        # RESULTS
        # ==========================================================================
        st.success(f"Created: **{kit}**")

        # Summary row
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Mode", f"{plan.root_note} {plan.mode}")
        with col_b:
            st.metric("BPM", plan.tempo_bpm)
        with col_c:
            st.metric("Bars", plan.length_bars)

        # Progression
        st.code(f"Progression: {' - '.join(plan.chord_symbols)}")

        # ==========================================================================
        # STRUCTURE MAP VISUALIZATION
        # ==========================================================================
        st.subheader("Structure Map")

        try:
            from music_brain.structure.structure_engine import StructuralArchitect

            architect = StructuralArchitect(plan.tempo_bpm)

            # Select form based on mood
            if plan.mode in ["phrygian", "locrian"]:
                form = "electronic_build"
            elif plan.mood_profile in ["rage", "defiance"]:
                form = "punk_assault"
            elif plan.mood_profile in ["grief", "nostalgia"]:
                form = "ballad"
            else:
                form = "pop_standard"

            structure_map = architect.generate_map(form, total_bars=plan.length_bars)

            if HAS_PANDAS and structure_map:
                chart_data = [
                    {"Bar": s["bar_index"], "Energy": s["velocity_target"]}
                    for s in structure_map
                ]
                df = pd.DataFrame(chart_data).set_index("Bar")
                st.line_chart(df)

                # Show section boundaries
                boundaries = architect.get_section_boundaries(structure_map)
                sections_text = " → ".join([b["name"] for b in boundaries])
                st.caption(f"Sections: {sections_text}")
            else:
                st.info("Structure generated (pandas not available for visualization)")

        except ImportError:
            st.info("Structure visualization not available")

        # ==========================================================================
        # LYRIC MIRROR
        # ==========================================================================
        if HAS_LYRICS:
            st.subheader("Mirror")
            fragments = get_lyric_fragments(user_text, num_lines=4)
            for line in fragments:
                st.write(line)

        # ==========================================================================
        # DETAILED ANALYSIS (expandable)
        # ==========================================================================
        with st.expander("Detailed Analysis"):
            st.write(f"**Primary affect:** `{affect}`")
            if session.state.affect_result:
                if session.state.affect_result.secondary:
                    st.write(
                        f"**Secondary undertone:** "
                        f"`{session.state.affect_result.secondary}`"
                    )
                st.write(
                    f"**Affect intensity:** "
                    f"`{session.state.affect_result.intensity:.2f}`"
                )
            st.write(f"**Structure type:** `{plan.structure_type}`")
            st.write(f"**Complexity:** `{plan.complexity:.2f}`")
            st.write(f"**Suggested kit:** `{kit}`")

        # ==========================================================================
        # MIDI GENERATION
        # ==========================================================================
        with st.spinner("Rendering MIDI..."):
            tmpdir = tempfile.mkdtemp(prefix="daiw_")
            midi_path = os.path.join(tmpdir, "daiw_session.mid")
            midi_path = render_plan_to_midi(plan, midi_path, vulnerability)

        st.success("MIDI generated.")

        try:
            with open(midi_path, "rb") as f:
                st.download_button(
                    label="Download MIDI",
                    data=f.read(),
                    file_name="daiw_session.mid",
                    mime="audio/midi",
                )
        except OSError:
            st.error("MIDI file could not be read back from disk.")

        # Next steps
        st.markdown("---")
        st.markdown(
            """
            **Next steps:**
            1. Drag the MIDI file into your DAW
            2. Load the suggested kit or similar sounds
            3. The tension curve is baked into the velocities
            """
        )


if __name__ == "__main__":
    main()
