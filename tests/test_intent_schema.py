"""
Tests for the Intent Schema module.

Covers: CompleteSongIntent serialization, validation, rule suggestions,
and all data class functionality.

Run with: pytest tests/test_intent_schema.py -v
"""

import pytest
import json
import tempfile
from pathlib import Path

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
    RULE_BREAKING_EFFECTS,
    suggest_rule_break,
    get_rule_breaking_info,
    validate_intent,
    list_all_rules,
)


# ==============================================================================
# DATA CLASS TESTS
# ==============================================================================

class TestSongRoot:
    """Test SongRoot data class."""

    def test_default_values(self):
        root = SongRoot()
        assert root.core_event == ""
        assert root.core_resistance == ""
        assert root.core_longing == ""
        assert root.core_stakes == ""
        assert root.core_transformation == ""

    def test_custom_values(self):
        root = SongRoot(
            core_event="Lost my best friend",
            core_resistance="Fear of vulnerability",
            core_longing="Peace and acceptance",
            core_stakes="Personal",
            core_transformation="Gratitude for the time we had",
        )
        assert root.core_event == "Lost my best friend"
        assert root.core_resistance == "Fear of vulnerability"


class TestSongIntent:
    """Test SongIntent data class."""

    def test_default_values(self):
        intent = SongIntent()
        assert intent.mood_primary == ""
        assert intent.mood_secondary_tension == 0.5
        assert intent.vulnerability_scale == "Medium"

    def test_custom_values(self):
        intent = SongIntent(
            mood_primary="grief",
            mood_secondary_tension=0.8,
            imagery_texture="Heavy, suffocating",
            vulnerability_scale="High",
            narrative_arc="Descent",
        )
        assert intent.mood_primary == "grief"
        assert intent.mood_secondary_tension == 0.8
        assert intent.vulnerability_scale == "High"


class TestTechnicalConstraints:
    """Test TechnicalConstraints data class."""

    def test_default_values(self):
        tc = TechnicalConstraints()
        assert tc.technical_genre == ""
        assert tc.technical_tempo_range == (80, 120)
        assert tc.technical_rule_to_break == ""

    def test_custom_values(self):
        tc = TechnicalConstraints(
            technical_genre="Alternative Rock",
            technical_tempo_range=(90, 110),
            technical_key="Am",
            technical_mode="aeolian",
            technical_groove_feel="Laid Back",
            technical_rule_to_break="HARMONY_AvoidTonicResolution",
            rule_breaking_justification="The grief never resolves",
        )
        assert tc.technical_genre == "Alternative Rock"
        assert tc.technical_tempo_range == (90, 110)
        assert tc.technical_rule_to_break == "HARMONY_AvoidTonicResolution"


# ==============================================================================
# ENUM TESTS
# ==============================================================================

class TestEnums:
    """Test all enum classes."""

    def test_harmony_rule_break_values(self):
        assert HarmonyRuleBreak.AVOID_TONIC_RESOLUTION.value == "HARMONY_AvoidTonicResolution"
        assert HarmonyRuleBreak.MODAL_INTERCHANGE.value == "HARMONY_ModalInterchange"
        assert HarmonyRuleBreak.PARALLEL_MOTION.value == "HARMONY_ParallelMotion"
        assert len(HarmonyRuleBreak) == 6

    def test_rhythm_rule_break_values(self):
        assert RhythmRuleBreak.CONSTANT_DISPLACEMENT.value == "RHYTHM_ConstantDisplacement"
        assert RhythmRuleBreak.TEMPO_FLUCTUATION.value == "RHYTHM_TempoFluctuation"
        assert len(RhythmRuleBreak) == 5

    def test_arrangement_rule_break_values(self):
        assert ArrangementRuleBreak.BURIED_VOCALS.value == "ARRANGEMENT_BuriedVocals"
        assert ArrangementRuleBreak.EXTREME_DYNAMIC_RANGE.value == "ARRANGEMENT_ExtremeDynamicRange"
        assert len(ArrangementRuleBreak) == 5

    def test_production_rule_break_values(self):
        assert ProductionRuleBreak.EXCESSIVE_MUD.value == "PRODUCTION_ExcessiveMud"
        assert ProductionRuleBreak.PITCH_IMPERFECTION.value == "PRODUCTION_PitchImperfection"
        assert len(ProductionRuleBreak) == 5

    def test_vulnerability_scale(self):
        assert VulnerabilityScale.LOW.value == "Low"
        assert VulnerabilityScale.MEDIUM.value == "Medium"
        assert VulnerabilityScale.HIGH.value == "High"

    def test_narrative_arc_values(self):
        assert NarrativeArc.CLIMB_TO_CLIMAX.value == "Climb-to-Climax"
        assert NarrativeArc.SLOW_REVEAL.value == "Slow Reveal"
        assert NarrativeArc.REPETITIVE_DESPAIR.value == "Repetitive Despair"
        assert len(NarrativeArc) == 8

    def test_core_stakes_values(self):
        assert CoreStakes.PERSONAL.value == "Personal"
        assert CoreStakes.EXISTENTIAL.value == "Existential"
        assert len(CoreStakes) == 6

    def test_groove_feel_values(self):
        assert GrooveFeel.STRAIGHT_DRIVING.value == "Straight/Driving"
        assert GrooveFeel.RUBATO_FREE.value == "Rubato/Free"
        assert len(GrooveFeel) == 8


# ==============================================================================
# COMPLETE SONG INTENT TESTS
# ==============================================================================

class TestCompleteSongIntent:
    """Test CompleteSongIntent serialization and deserialization."""

    @pytest.fixture
    def full_intent(self):
        """Create a fully populated intent for testing."""
        return CompleteSongIntent(
            title="Letting Go",
            created="2024-01-15",
            song_root=SongRoot(
                core_event="My father passed away last year",
                core_resistance="I don't want to seem weak",
                core_longing="To feel connected to his memory",
                core_stakes="Personal",
                core_transformation="Acceptance and peace",
            ),
            song_intent=SongIntent(
                mood_primary="grief",
                mood_secondary_tension=0.7,
                imagery_texture="Heavy rain, gray skies",
                vulnerability_scale="High",
                narrative_arc="Slow Reveal",
            ),
            technical_constraints=TechnicalConstraints(
                technical_genre="Indie Folk",
                technical_tempo_range=(70, 90),
                technical_key="Am",
                technical_mode="aeolian",
                technical_groove_feel="Organic/Breathing",
                technical_rule_to_break="HARMONY_AvoidTonicResolution",
                rule_breaking_justification="The grief doesn't resolve cleanly",
            ),
            system_directive=SystemDirective(
                output_target="Full arrangement",
                output_feedback_loop="Harmony, Groove",
            ),
        )

    def test_to_dict_returns_dict(self, full_intent):
        data = full_intent.to_dict()
        assert isinstance(data, dict)
        assert "title" in data
        assert "song_root" in data
        assert "song_intent" in data
        assert "technical_constraints" in data

    def test_to_dict_preserves_values(self, full_intent):
        data = full_intent.to_dict()
        assert data["title"] == "Letting Go"
        assert data["song_root"]["core_event"] == "My father passed away last year"
        assert data["song_intent"]["mood_primary"] == "grief"
        assert data["technical_constraints"]["technical_key"] == "Am"

    def test_to_dict_converts_tuple_to_list(self, full_intent):
        data = full_intent.to_dict()
        # Tempo range tuple should become list for JSON serialization
        assert data["technical_constraints"]["technical_tempo_range"] == [70, 90]
        assert isinstance(data["technical_constraints"]["technical_tempo_range"], list)

    def test_from_dict_creates_intent(self, full_intent):
        data = full_intent.to_dict()
        restored = CompleteSongIntent.from_dict(data)
        assert restored.title == full_intent.title
        assert restored.song_root.core_event == full_intent.song_root.core_event

    def test_from_dict_roundtrip(self, full_intent):
        """Verify to_dict -> from_dict preserves all data."""
        data = full_intent.to_dict()
        restored = CompleteSongIntent.from_dict(data)

        # Check all fields
        assert restored.title == full_intent.title
        assert restored.created == full_intent.created

        # Song root
        assert restored.song_root.core_event == full_intent.song_root.core_event
        assert restored.song_root.core_resistance == full_intent.song_root.core_resistance
        assert restored.song_root.core_longing == full_intent.song_root.core_longing
        assert restored.song_root.core_stakes == full_intent.song_root.core_stakes
        assert restored.song_root.core_transformation == full_intent.song_root.core_transformation

        # Song intent
        assert restored.song_intent.mood_primary == full_intent.song_intent.mood_primary
        assert restored.song_intent.mood_secondary_tension == full_intent.song_intent.mood_secondary_tension
        assert restored.song_intent.vulnerability_scale == full_intent.song_intent.vulnerability_scale
        assert restored.song_intent.narrative_arc == full_intent.song_intent.narrative_arc

        # Technical constraints
        assert restored.technical_constraints.technical_genre == full_intent.technical_constraints.technical_genre
        assert restored.technical_constraints.technical_key == full_intent.technical_constraints.technical_key
        assert restored.technical_constraints.technical_rule_to_break == full_intent.technical_constraints.technical_rule_to_break

    def test_from_dict_handles_missing_fields(self):
        """from_dict should handle partial data gracefully."""
        partial_data = {
            "title": "Partial Intent",
            "song_root": {
                "core_event": "Something happened",
            },
        }
        intent = CompleteSongIntent.from_dict(partial_data)
        assert intent.title == "Partial Intent"
        assert intent.song_root.core_event == "Something happened"
        assert intent.song_root.core_resistance == ""  # Default
        assert intent.song_intent.mood_primary == ""  # Default

    def test_from_dict_handles_empty_dict(self):
        """from_dict should handle empty dict."""
        intent = CompleteSongIntent.from_dict({})
        assert intent.title == ""
        assert intent.song_root.core_event == ""

    def test_save_creates_file(self, full_intent):
        """save() should create a valid JSON file."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            full_intent.save(temp_path)
            assert Path(temp_path).exists()

            # Verify it's valid JSON
            with open(temp_path) as f:
                data = json.load(f)
            assert data["title"] == "Letting Go"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_load_reads_file(self, full_intent):
        """load() should restore intent from JSON file."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            full_intent.save(temp_path)
            restored = CompleteSongIntent.load(temp_path)

            assert restored.title == full_intent.title
            assert restored.song_root.core_event == full_intent.song_root.core_event
            assert restored.technical_constraints.technical_key == full_intent.technical_constraints.technical_key
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_save_load_roundtrip(self, full_intent):
        """Full save -> load roundtrip."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            full_intent.save(temp_path)
            restored = CompleteSongIntent.load(temp_path)

            # Re-serialize and compare
            original_data = full_intent.to_dict()
            restored_data = restored.to_dict()
            assert original_data == restored_data
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_default_intent(self):
        """Default intent should have sensible defaults."""
        intent = CompleteSongIntent()
        assert intent.title == ""
        assert intent.song_root.core_event == ""
        assert intent.song_intent.mood_secondary_tension == 0.5
        assert intent.technical_constraints.technical_tempo_range == (80, 120)


# ==============================================================================
# VALIDATION TESTS
# ==============================================================================

class TestValidateIntent:
    """Test validate_intent function."""

    def test_valid_intent_returns_empty_list(self):
        """A complete, valid intent should return no issues."""
        intent = CompleteSongIntent(
            song_root=SongRoot(
                core_event="Something happened",
                core_longing="I want peace",
            ),
            song_intent=SongIntent(
                mood_primary="grief",
                mood_secondary_tension=0.5,
                vulnerability_scale="Medium",
            ),
        )
        issues = validate_intent(intent)
        assert issues == []

    def test_missing_core_event(self):
        """Missing core_event should be flagged."""
        intent = CompleteSongIntent(
            song_root=SongRoot(
                core_event="",
                core_longing="I want peace",
            ),
            song_intent=SongIntent(mood_primary="grief"),
        )
        issues = validate_intent(intent)
        assert any("core_event" in issue for issue in issues)

    def test_missing_core_longing(self):
        """Missing core_longing should be flagged."""
        intent = CompleteSongIntent(
            song_root=SongRoot(
                core_event="Something happened",
                core_longing="",
            ),
            song_intent=SongIntent(mood_primary="grief"),
        )
        issues = validate_intent(intent)
        assert any("core_longing" in issue for issue in issues)

    def test_missing_mood_primary(self):
        """Missing mood_primary should be flagged."""
        intent = CompleteSongIntent(
            song_root=SongRoot(
                core_event="Something happened",
                core_longing="I want peace",
            ),
            song_intent=SongIntent(mood_primary=""),
        )
        issues = validate_intent(intent)
        assert any("mood_primary" in issue for issue in issues)

    def test_invalid_tension_range_low(self):
        """Tension below 0 should be flagged."""
        intent = CompleteSongIntent(
            song_root=SongRoot(
                core_event="Something happened",
                core_longing="I want peace",
            ),
            song_intent=SongIntent(
                mood_primary="grief",
                mood_secondary_tension=-0.5,
            ),
        )
        issues = validate_intent(intent)
        assert any("tension" in issue.lower() for issue in issues)

    def test_invalid_tension_range_high(self):
        """Tension above 1 should be flagged."""
        intent = CompleteSongIntent(
            song_root=SongRoot(
                core_event="Something happened",
                core_longing="I want peace",
            ),
            song_intent=SongIntent(
                mood_primary="grief",
                mood_secondary_tension=1.5,
            ),
        )
        issues = validate_intent(intent)
        assert any("tension" in issue.lower() for issue in issues)

    def test_rule_without_justification(self):
        """Rule to break without justification should be flagged."""
        intent = CompleteSongIntent(
            song_root=SongRoot(
                core_event="Something happened",
                core_longing="I want peace",
            ),
            song_intent=SongIntent(mood_primary="grief"),
            technical_constraints=TechnicalConstraints(
                technical_rule_to_break="HARMONY_AvoidTonicResolution",
                rule_breaking_justification="",
            ),
        )
        issues = validate_intent(intent)
        assert any("justification" in issue.lower() for issue in issues)

    def test_rule_with_justification_ok(self):
        """Rule with justification should be OK."""
        intent = CompleteSongIntent(
            song_root=SongRoot(
                core_event="Something happened",
                core_longing="I want peace",
            ),
            song_intent=SongIntent(mood_primary="grief"),
            technical_constraints=TechnicalConstraints(
                technical_rule_to_break="HARMONY_AvoidTonicResolution",
                rule_breaking_justification="The grief never resolves",
            ),
        )
        issues = validate_intent(intent)
        # Should not flag the rule/justification
        assert not any("justification" in issue.lower() for issue in issues)

    def test_consistency_high_vulnerability_low_tension(self):
        """High vulnerability with very low tension should be flagged."""
        intent = CompleteSongIntent(
            song_root=SongRoot(
                core_event="Something happened",
                core_longing="I want peace",
            ),
            song_intent=SongIntent(
                mood_primary="grief",
                mood_secondary_tension=0.1,  # Very low
                vulnerability_scale="High",
            ),
        )
        issues = validate_intent(intent)
        assert any("consistency" in issue.lower() for issue in issues)

    def test_multiple_issues(self):
        """Multiple issues should all be reported."""
        intent = CompleteSongIntent()  # Empty intent
        issues = validate_intent(intent)
        assert len(issues) >= 2  # At least core_event and mood_primary


# ==============================================================================
# RULE SUGGESTION TESTS
# ==============================================================================

class TestSuggestRuleBreak:
    """Test suggest_rule_break function."""

    def test_grief_suggestions(self):
        """Grief should suggest appropriate rules."""
        suggestions = suggest_rule_break("grief")
        assert len(suggestions) > 0
        rule_keys = [s["rule"] for s in suggestions]
        # Grief commonly maps to unresolved harmony
        assert any("HARMONY" in rule for rule in rule_keys)

    def test_anger_suggestions(self):
        """Anger should suggest appropriate rules."""
        suggestions = suggest_rule_break("anger")
        assert len(suggestions) > 0

    def test_nostalgia_suggestions(self):
        """Nostalgia should suggest appropriate rules."""
        suggestions = suggest_rule_break("nostalgia")
        assert len(suggestions) > 0

    def test_defiance_suggestions(self):
        """Defiance should suggest appropriate rules."""
        suggestions = suggest_rule_break("defiance")
        assert len(suggestions) > 0
        rule_keys = [s["rule"] for s in suggestions]
        # Defiance often maps to parallel motion
        assert any("HARMONY_ParallelMotion" in rule for rule in rule_keys)

    def test_case_insensitive(self):
        """Emotion matching should be case-insensitive."""
        lower = suggest_rule_break("grief")
        upper = suggest_rule_break("GRIEF")
        mixed = suggest_rule_break("Grief")

        # All should return suggestions
        assert len(lower) > 0
        assert len(upper) > 0
        assert len(mixed) > 0

    def test_unknown_emotion_returns_empty(self):
        """Unknown emotion should return empty list."""
        suggestions = suggest_rule_break("xyzzy_nonexistent")
        assert suggestions == []

    def test_suggestion_structure(self):
        """Suggestions should have expected fields."""
        suggestions = suggest_rule_break("grief")
        assert len(suggestions) > 0

        for suggestion in suggestions:
            assert "rule" in suggestion
            assert "description" in suggestion
            assert "effect" in suggestion
            assert "use_when" in suggestion


class TestGetRuleBreakingInfo:
    """Test get_rule_breaking_info function."""

    def test_valid_rule_returns_info(self):
        """Valid rule key should return info dict."""
        info = get_rule_breaking_info("HARMONY_AvoidTonicResolution")
        assert info is not None
        assert "description" in info
        assert "effect" in info
        assert "use_when" in info

    def test_invalid_rule_returns_none(self):
        """Invalid rule key should return None."""
        info = get_rule_breaking_info("NONEXISTENT_Rule")
        assert info is None

    def test_all_enum_values_have_info(self):
        """All enum rule values should have corresponding info."""
        for rule in HarmonyRuleBreak:
            info = get_rule_breaking_info(rule.value)
            assert info is not None, f"Missing info for {rule.value}"

        for rule in RhythmRuleBreak:
            info = get_rule_breaking_info(rule.value)
            assert info is not None, f"Missing info for {rule.value}"

        for rule in ArrangementRuleBreak:
            info = get_rule_breaking_info(rule.value)
            assert info is not None, f"Missing info for {rule.value}"

        for rule in ProductionRuleBreak:
            info = get_rule_breaking_info(rule.value)
            assert info is not None, f"Missing info for {rule.value}"


class TestListAllRules:
    """Test list_all_rules function."""

    def test_returns_dict_with_categories(self):
        """Should return dict with category keys."""
        rules = list_all_rules()
        assert isinstance(rules, dict)
        assert "Harmony" in rules
        assert "Rhythm" in rules
        assert "Arrangement" in rules
        assert "Production" in rules

    def test_categories_contain_lists(self):
        """Each category should contain a list of rule values."""
        rules = list_all_rules()
        for category, rule_list in rules.items():
            assert isinstance(rule_list, list)
            assert len(rule_list) > 0

    def test_harmony_rules_match_enum(self):
        """Harmony rules should match HarmonyRuleBreak enum."""
        rules = list_all_rules()
        harmony_rules = rules["Harmony"]

        enum_values = [e.value for e in HarmonyRuleBreak]
        assert set(harmony_rules) == set(enum_values)

    def test_rhythm_rules_match_enum(self):
        """Rhythm rules should match RhythmRuleBreak enum."""
        rules = list_all_rules()
        rhythm_rules = rules["Rhythm"]

        enum_values = [e.value for e in RhythmRuleBreak]
        assert set(rhythm_rules) == set(enum_values)


# ==============================================================================
# RULE_BREAKING_EFFECTS DICTIONARY TESTS
# ==============================================================================

class TestRuleBreakingEffects:
    """Test RULE_BREAKING_EFFECTS dictionary."""

    def test_all_rules_have_required_fields(self):
        """Each rule should have all required fields."""
        required_fields = ["description", "effect", "use_when", "example_emotions"]

        for rule_key, rule_data in RULE_BREAKING_EFFECTS.items():
            for field in required_fields:
                assert field in rule_data, f"Missing {field} in {rule_key}"

    def test_example_emotions_are_lists(self):
        """example_emotions should be lists."""
        for rule_key, rule_data in RULE_BREAKING_EFFECTS.items():
            assert isinstance(rule_data["example_emotions"], list), f"{rule_key} emotions not a list"

    def test_all_fields_are_non_empty(self):
        """All fields should have non-empty values."""
        for rule_key, rule_data in RULE_BREAKING_EFFECTS.items():
            assert rule_data["description"], f"Empty description in {rule_key}"
            assert rule_data["effect"], f"Empty effect in {rule_key}"
            assert rule_data["use_when"], f"Empty use_when in {rule_key}"
            assert len(rule_data["example_emotions"]) > 0, f"Empty emotions in {rule_key}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
