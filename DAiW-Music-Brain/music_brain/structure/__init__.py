"""
Structure Analysis - Chord, section, and progression analysis.

Analyze harmonic content, detect song sections, and work with
chord progressions for reharmonization and diagnosis.

Includes the Comprehensive Engine for therapy-based music generation.
"""

from music_brain.structure.chord import (
    analyze_chords,
    ChordProgression,
    Chord,
    detect_key,
)
from music_brain.structure.sections import (
    detect_sections,
    Section,
    SectionType,
)
from music_brain.structure.progression import (
    diagnose_progression,
    generate_reharmonizations,
    parse_progression_string,
)
from music_brain.structure.comprehensive_engine import (
    # Core classes
    AffectResult,
    AffectAnalyzer,
    TherapyState,
    HarmonyPlan,
    NoteEvent,
    TherapySession,
    # Functions
    get_strategy,
    render_plan_to_midi,
    render_phrase_to_vault,
    generate_lyric_mirror,
    select_kit_for_mood,
    build_tension_curve,
    tension_multiplier,
    run_cli as run_therapy_cli,
)
from music_brain.structure.tension_curve import (
    TENSION_CURVES,
    TensionProfile,
    get_tension_curve,
    list_tension_curves,
    apply_tension_curve,
    apply_section_markers,
    generate_curve_for_bars,
)

__all__ = [
    # Chord analysis
    "analyze_chords",
    "ChordProgression",
    "Chord",
    "detect_key",
    # Section detection
    "detect_sections",
    "Section",
    "SectionType",
    # Progression tools
    "diagnose_progression",
    "generate_reharmonizations",
    "parse_progression_string",
    # Comprehensive Engine (Therapy)
    "AffectResult",
    "AffectAnalyzer",
    "TherapyState",
    "HarmonyPlan",
    "NoteEvent",
    "TherapySession",
    "get_strategy",
    "render_plan_to_midi",
    "render_phrase_to_vault",
    "generate_lyric_mirror",
    "select_kit_for_mood",
    "build_tension_curve",
    "tension_multiplier",
    "run_therapy_cli",
    # Tension Curves (Standalone)
    "TENSION_CURVES",
    "TensionProfile",
    "get_tension_curve",
    "list_tension_curves",
    "apply_tension_curve",
    "apply_section_markers",
    "generate_curve_for_bars",
]
