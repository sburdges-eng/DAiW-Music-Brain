"""
Session - Song generation, teaching modules, and interactive tools.

Interactive teaching for music theory and production concepts.
Interrogation-first songwriting assistance.
Intent-based generation with rule-breaking support.
"""

from music_brain.session.teaching import RuleBreakingTeacher
from music_brain.session.interrogator import SongInterrogator
from music_brain.session.intent_schema import (
    CompleteSongIntent,
    SongRoot,
    SongIntent,
    TechnicalConstraints,
    SystemDirective,
    HarmonyRuleBreak,
    RhythmRuleBreak,
    ArrangementRuleBreak,
    ProductionRuleBreak,
    VulnerabilityScale,
    NarrativeArc,
    CoreStakes,
    GrooveFeel,
    suggest_rule_break,
    get_rule_breaking_info,
    validate_intent,
    list_all_rules,
    RULE_BREAKING_EFFECTS,
    collect_phase1_interactive,
    validate_phase1,
    load_schema_options,
    collect_phase2_interactive,
    validate_phase2,
    suggest_phase2_from_phase1,
)

__all__ = [
    # Teaching
    "RuleBreakingTeacher",
    # Interrogation
    "SongInterrogator",
    # Intent Schema
    "CompleteSongIntent",
    "SongRoot",
    "SongIntent",
    "TechnicalConstraints",
    "SystemDirective",
    # Rule Breaking Enums
    "HarmonyRuleBreak",
    "RhythmRuleBreak",
    "ArrangementRuleBreak",
    "ProductionRuleBreak",
    "VulnerabilityScale",
    "NarrativeArc",
    "CoreStakes",
    "GrooveFeel",
    # Functions
    "suggest_rule_break",
    "get_rule_breaking_info",
    "validate_intent",
    "list_all_rules",
    "RULE_BREAKING_EFFECTS",
    # Phase 1 utilities
    "collect_phase1_interactive",
    "validate_phase1",
    "load_schema_options",
    # Phase 2 utilities
    "collect_phase2_interactive",
    "validate_phase2",
    "suggest_phase2_from_phase1",
]
