"""
Structure Analysis - Chord, section, progression analysis, and comprehensive engine.

Analyze harmonic content, detect song sections, work with
chord progressions, and run the therapy-to-music pipeline.
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
    AffectAnalyzer,
    AffectResult,
    TherapySession,
    TherapyState,
    HarmonyPlan,
    render_plan_to_midi,
    run_cli,
)
from music_brain.structure.tension_curve import (
    apply_tension_curve,
    get_tension_curve,
    list_tension_curves,
    generate_curve_for_bars,
    TENSION_CURVES,
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
    # Comprehensive engine
    "AffectAnalyzer",
    "AffectResult",
    "TherapySession",
    "TherapyState",
    "HarmonyPlan",
    "render_plan_to_midi",
    "run_cli",
    # Tension curves
    "apply_tension_curve",
    "get_tension_curve",
    "list_tension_curves",
    "generate_curve_for_bars",
    "TENSION_CURVES",
]
