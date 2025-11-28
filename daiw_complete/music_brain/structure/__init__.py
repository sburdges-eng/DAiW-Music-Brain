"""Structure, harmony, and composition modules."""
from .tension import generate_tension_curve, choose_structure_type_for_mood
from .progression import parse_progression_string, ParsedChord
from .comprehensive_engine import (
    TherapySession,
    HarmonyPlan,
    AffectResult,
    render_plan_to_midi,
    select_kit_for_mood,
)

__all__ = [
    "generate_tension_curve",
    "choose_structure_type_for_mood",
    "parse_progression_string",
    "ParsedChord",
    "TherapySession",
    "HarmonyPlan",
    "AffectResult",
    "render_plan_to_midi",
    "select_kit_for_mood",
]
