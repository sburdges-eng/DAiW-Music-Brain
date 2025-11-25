"""
DAiW - Digital Audio Intimate Workstation
Streamlit UI for the Music Brain toolkit

Philosophy: "Interrogate Before Generate"
The tool shouldn't finish art for people. It should make them braver.
"""

import streamlit as st
import os
import tempfile
from pathlib import Path

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="DAiW - Creative Companion",
    page_icon="musical_note",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for dark, intimate aesthetic
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(15, 15, 35, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Headers */
    h1, h2, h3 {
        color: #e8e8e8 !important;
        font-family: 'Georgia', serif;
    }

    /* Text areas */
    .stTextArea textarea {
        background: rgba(30, 30, 50, 0.8);
        border: 1px solid rgba(100, 100, 150, 0.3);
        color: #e8e8e8;
    }

    /* Sliders */
    .stSlider [data-baseweb="slider"] {
        background: rgba(100, 100, 150, 0.2);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #4a4a6a 0%, #3a3a5a 100%);
        border: 1px solid rgba(150, 150, 200, 0.3);
        color: #e8e8e8;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #5a5a7a 0%, #4a4a6a 100%);
        border-color: rgba(180, 180, 220, 0.5);
    }

    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(90deg, #2d5a27 0%, #1d4a1a 100%);
        border: 1px solid rgba(100, 200, 100, 0.3);
    }

    .stDownloadButton > button:hover {
        background: linear-gradient(90deg, #3d6a37 0%, #2d5a27 100%);
    }

    /* Info boxes */
    .stAlert {
        background: rgba(40, 40, 60, 0.8);
        border: 1px solid rgba(100, 100, 150, 0.3);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(30, 30, 50, 0.6);
        border-radius: 8px;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: rgba(30, 30, 50, 0.6);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(100, 100, 150, 0.2);
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(20, 20, 40, 0.5);
        border-radius: 8px;
        padding: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 6px;
        color: #a0a0b0;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(60, 60, 100, 0.5);
        color: #e8e8e8;
    }
</style>
""", unsafe_allow_html=True)


# Import music_brain modules with error handling
@st.cache_resource
def load_music_brain():
    """Lazy load music brain modules."""
    try:
        from music_brain.structure.comprehensive_engine import (
            TherapySession,
            AffectAnalyzer,
            HarmonyPlan,
            render_plan_to_midi,
            AFFECT_MODE_MAP,
            AFFECT_TEMPO_BASE,
        )
        return {
            "TherapySession": TherapySession,
            "AffectAnalyzer": AffectAnalyzer,
            "HarmonyPlan": HarmonyPlan,
            "render_plan_to_midi": render_plan_to_midi,
            "AFFECT_MODE_MAP": AFFECT_MODE_MAP,
            "AFFECT_TEMPO_BASE": AFFECT_TEMPO_BASE,
            "available": True,
        }
    except ImportError as e:
        st.error(f"Could not load music_brain: {e}")
        return {"available": False}


def init_session_state():
    """Initialize session state variables."""
    if "therapy_session" not in st.session_state:
        st.session_state.therapy_session = None
    if "affect_result" not in st.session_state:
        st.session_state.affect_result = None
    if "harmony_plan" not in st.session_state:
        st.session_state.harmony_plan = None
    if "midi_data" not in st.session_state:
        st.session_state.midi_data = None
    if "current_phase" not in st.session_state:
        st.session_state.current_phase = 0


def render_sidebar():
    """Render the sidebar navigation and info."""
    with st.sidebar:
        st.markdown("### DAiW")
        st.markdown("*Digital Audio Intimate Workstation*")
        st.markdown("---")

        # Navigation
        page = st.radio(
            "Navigate",
            ["Therapy Session", "Quick Generate", "Chord Analysis", "About"],
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Session info
        if st.session_state.affect_result:
            st.markdown("#### Current Session")
            affect = st.session_state.affect_result
            st.markdown(f"**Affect:** {affect.primary}")
            st.markdown(f"**Intensity:** {affect.intensity:.0%}")
            if affect.secondary:
                st.markdown(f"**Secondary:** {affect.secondary}")

        st.markdown("---")
        st.markdown(
            "*'The audience doesn't hear 'borrowed from Dorian.' "
            "They hear 'that part made me cry.'*"
        )

        return page


def render_therapy_session(modules):
    """Render the main therapy session interface."""
    st.markdown("## Interrogate Before Generate")
    st.markdown(
        "Before we make music, let's understand what you *need* to say. "
        "This isn't about finishing art for you - it's about making you braver."
    )

    # Phase 0: Core Wound
    st.markdown("---")
    st.markdown("### Phase 0: The Core Wound")

    col1, col2 = st.columns([2, 1])

    with col1:
        core_text = st.text_area(
            "What happened? What's the emotional core of this song?",
            height=150,
            placeholder=(
                "Write freely - include feelings, images, memories...\n\n"
                "What's the thing you're afraid to say?\n"
                "What keeps you up at night?\n"
                "What do you wish someone understood?"
            ),
            key="core_wound_input",
        )

        if st.button("Analyze Emotional Core", type="primary"):
            if core_text.strip():
                # Create new therapy session
                session = modules["TherapySession"]()
                affect = session.process_core_input(core_text)

                st.session_state.therapy_session = session
                st.session_state.affect_result = affect
                st.session_state.current_phase = 1
                st.rerun()
            else:
                st.warning("Please share something about your emotional experience.")

    with col2:
        if st.session_state.affect_result:
            affect = st.session_state.affect_result
            st.markdown("#### Detected Affect")

            # Primary affect display
            st.metric("Primary", affect.primary.upper())
            st.metric("Intensity", f"{affect.intensity:.0%}")

            if affect.secondary:
                st.metric("Secondary", affect.secondary.capitalize())

            # Mode suggestion
            mode = modules["AFFECT_MODE_MAP"].get(affect.primary, "ionian")
            tempo = modules["AFFECT_TEMPO_BASE"].get(affect.primary, 100)

            st.markdown("---")
            st.markdown("**Suggested:**")
            st.markdown(f"Mode: *{mode}*")
            st.markdown(f"Base tempo: *{tempo} BPM*")

    # Phase 1: Scales (only show if Phase 0 complete)
    if st.session_state.affect_result:
        st.markdown("---")
        st.markdown("### Phase 1: The Scales")

        col1, col2 = st.columns(2)

        with col1:
            motivation = st.slider(
                "Motivation",
                min_value=1,
                max_value=10,
                value=5,
                help="How much energy do you have for this? (1 = barely surviving, 10 = burning to create)",
            )
            st.caption(
                "Low motivation = shorter song, more vulnerable. "
                "High motivation = longer exploration."
            )

        with col2:
            chaos = st.slider(
                "Chaos Tolerance",
                min_value=0,
                max_value=10,
                value=5,
                help="How comfortable are you with disorder? (0 = need control, 10 = embrace the mess)",
            )
            st.caption(
                "Low chaos = tighter timing, predictable. "
                "High chaos = humanized, faster, wilder."
            )

        # Phase 2: Generate
        st.markdown("---")
        st.markdown("### Phase 2: Generation")

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            if st.button("Generate Harmony Plan", type="primary", use_container_width=True):
                session = st.session_state.therapy_session
                session.set_scales(float(motivation), float(chaos) / 10.0)
                plan = session.generate_plan()
                st.session_state.harmony_plan = plan
                st.rerun()

    # Display generated plan
    if st.session_state.harmony_plan:
        render_harmony_plan(st.session_state.harmony_plan, modules)


def render_harmony_plan(plan, modules):
    """Display the generated harmony plan with MIDI export."""
    st.markdown("---")
    st.markdown("### Your Harmony Plan")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Root", plan.root_note)
        st.metric("Mode", plan.mode.capitalize())
        st.metric("Tempo", f"{plan.tempo_bpm} BPM")

    with col2:
        st.metric("Length", f"{plan.length_bars} bars")
        st.metric("Time Sig", plan.time_signature)
        st.metric("Mood", plan.mood_profile.capitalize())

    with col3:
        st.metric("Complexity", f"{plan.complexity:.0%}")
        st.metric("Vulnerability", f"{plan.vulnerability:.0%}")

    # Chord progression display
    st.markdown("#### Chord Progression")
    progression_display = " - ".join(plan.chord_symbols)
    st.code(progression_display, language=None)

    # MIDI Export
    st.markdown("---")
    col1, col2 = st.columns([1, 1])

    with col1:
        include_guides = st.checkbox("Include Guide Tones", value=True)
        st.caption("Guide tones (3rds & 7ths) help with melodic improvisation")

    with col2:
        if st.button("Render to MIDI", type="primary"):
            with st.spinner("Rendering MIDI..."):
                try:
                    # Create temp file for MIDI
                    with tempfile.NamedTemporaryFile(
                        suffix=".mid", delete=False
                    ) as tmp:
                        output_path = tmp.name

                    # Render
                    modules["render_plan_to_midi"](
                        plan,
                        output_path=output_path,
                        include_guide_tones=include_guides,
                    )

                    # Read the file for download
                    with open(output_path, "rb") as f:
                        st.session_state.midi_data = f.read()

                    # Clean up temp file
                    os.unlink(output_path)

                    st.success("MIDI rendered successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error rendering MIDI: {e}")

    # Download button (if MIDI data available)
    if st.session_state.midi_data:
        st.download_button(
            label="Download MIDI File",
            data=st.session_state.midi_data,
            file_name="daiw_session.mid",
            mime="audio/midi",
            use_container_width=True,
        )
        st.info("Drag this file into your DAW and make it yours.")


def render_quick_generate(modules):
    """Quick generation mode - skip therapy, direct parameters."""
    st.markdown("## Quick Generate")
    st.markdown(
        "Skip the deep interrogation and generate directly from parameters. "
        "*Use this when you know what you want.*"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Musical Parameters")

        root_note = st.selectbox(
            "Root Note",
            ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
        )

        mode = st.selectbox(
            "Mode",
            ["ionian", "dorian", "phrygian", "lydian", "mixolydian", "aeolian", "locrian"],
        )

        tempo = st.slider("Tempo (BPM)", 40, 200, 100)

        length = st.select_slider(
            "Length (bars)",
            options=[8, 16, 32, 64, 128],
            value=16,
        )

    with col2:
        st.markdown("### Expression Parameters")

        complexity = st.slider(
            "Complexity",
            0.0, 1.0, 0.5,
            help="How much humanization/chaos in timing",
        )

        vulnerability = st.slider(
            "Vulnerability",
            0.0, 1.0, 0.5,
            help="Affects dynamics - higher = softer, more exposed",
        )

        st.markdown("---")

        include_guides = st.checkbox("Include Guide Tones", value=True)

    if st.button("Generate MIDI", type="primary", use_container_width=True):
        with st.spinner("Generating..."):
            try:
                # Create plan directly
                plan = modules["HarmonyPlan"](
                    root_note=root_note,
                    mode=mode,
                    tempo_bpm=tempo,
                    length_bars=length,
                    complexity=complexity,
                    vulnerability=vulnerability,
                )

                # Render to temp file
                with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tmp:
                    output_path = tmp.name

                modules["render_plan_to_midi"](
                    plan,
                    output_path=output_path,
                    include_guide_tones=include_guides,
                )

                # Read for download
                with open(output_path, "rb") as f:
                    midi_data = f.read()

                os.unlink(output_path)

                st.success("Generated!")
                st.download_button(
                    label="Download MIDI",
                    data=midi_data,
                    file_name=f"daiw_{root_note}_{mode}.mid",
                    mime="audio/midi",
                )

            except Exception as e:
                st.error(f"Generation failed: {e}")


def render_chord_analysis(modules):
    """Chord progression analysis interface."""
    st.markdown("## Chord Analysis")
    st.markdown("Analyze and understand chord progressions.")

    try:
        from music_brain.structure.progression import (
            diagnose_progression,
            parse_progression_string,
        )

        chord_input = st.text_input(
            "Enter chord progression",
            placeholder="Am - F - C - G",
            help="Use dashes to separate chords (e.g., Am-F-C-G or Am - F - C - G)",
        )

        if chord_input:
            st.markdown("---")

            # Parse and analyze
            parsed = parse_progression_string(chord_input.replace(" ", ""))

            if parsed:
                st.markdown("### Parsed Chords")

                cols = st.columns(min(len(parsed), 4))
                for i, chord in enumerate(parsed):
                    with cols[i % 4]:
                        st.markdown(f"**{chord.original}**")
                        st.caption(f"Root: {chord.root_num}")

                # Run diagnosis
                st.markdown("---")
                st.markdown("### Diagnosis")

                diagnosis = diagnose_progression(chord_input)

                for item in diagnosis:
                    if item.startswith("["):
                        st.info(item)
                    else:
                        st.markdown(f"- {item}")
            else:
                st.warning("Could not parse the chord progression. Try format: Am-F-C-G")

    except ImportError:
        st.warning("Chord analysis module not available.")


def render_about():
    """About page with philosophy and documentation."""
    st.markdown("## About DAiW")

    st.markdown("""
    ### Philosophy

    **"Interrogate Before Generate"**

    This tool shouldn't finish art for people. It should make them braver.

    The three-phase "Song Intent Schema" ensures artists explore what they *need* to say
    before choosing technical parameters:

    1. **Phase 0: Core Wound/Desire** - Deep interrogation about emotional truth
    2. **Phase 1: Emotional Intent** - Validated by the core wound exploration
    3. **Phase 2: Technical Constraints** - Implementation that serves the emotion

    ---

    ### The Engine

    DAiW analyzes your emotional text for **affects** - fundamental emotional states that
    map to musical modes:

    | Affect | Mode | Character |
    |--------|------|-----------|
    | Grief | Aeolian | Melancholy, loss |
    | Rage | Phrygian | Intensity, Spanish fire |
    | Awe | Lydian | Ethereal, transcendent |
    | Nostalgia | Mixolydian | Bittersweet, folk |
    | Fear | Locrian | Unstable, dark |
    | Defiance | Mixolydian | Power, determination |
    | Tenderness | Ionian | Warmth, comfort |

    ---

    ### Rule-Breaking

    Rules in music exist to be broken - *intentionally*. Every broken rule should have
    emotional justification:

    - **Avoid tonic resolution** = Unresolved yearning
    - **Buried vocals** = Dissociation, overwhelm
    - **Tempo drift** = Organic breathing, anxiety
    - **Pitch imperfection** = Raw emotional honesty

    ---

    ### Credits

    DAiW Music Brain - v0.3.0

    *"The audience doesn't hear 'borrowed from Dorian.' They hear 'that part made me cry.'"*
    """)


def main():
    """Main application entry point."""
    init_session_state()

    # Load modules
    modules = load_music_brain()

    if not modules.get("available"):
        st.error(
            "Music Brain modules could not be loaded. "
            "Please ensure the package is installed correctly."
        )
        st.stop()

    # Sidebar navigation
    page = render_sidebar()

    # Route to appropriate page
    if page == "Therapy Session":
        render_therapy_session(modules)
    elif page == "Quick Generate":
        render_quick_generate(modules)
    elif page == "Chord Analysis":
        render_chord_analysis(modules)
    elif page == "About":
        render_about()


if __name__ == "__main__":
    main()
