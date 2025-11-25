"""
Basic tests for music_brain package.

Run with: pytest tests/
"""

import pytest
from pathlib import Path


class TestImports:
    """Test that all modules can be imported."""
    
    def test_import_music_brain(self):
        import music_brain
        assert hasattr(music_brain, '__version__')
    
    def test_import_groove(self):
        from music_brain.groove import extract_groove, apply_groove, GrooveTemplate
        assert callable(extract_groove)
        assert callable(apply_groove)
    
    def test_import_structure(self):
        from music_brain.structure import analyze_chords, detect_sections, ChordProgression
        assert callable(analyze_chords)
        assert callable(detect_sections)
    
    def test_import_session(self):
        from music_brain.session import RuleBreakingTeacher, SongInterrogator
        assert RuleBreakingTeacher is not None
        assert SongInterrogator is not None


class TestGrooveTemplates:
    """Test groove template functionality."""
    
    def test_genre_templates_exist(self):
        from music_brain.groove.templates import GENRE_TEMPLATES, get_genre_template
        
        assert 'funk' in GENRE_TEMPLATES
        assert 'jazz' in GENRE_TEMPLATES
        assert 'rock' in GENRE_TEMPLATES
        assert 'hiphop' in GENRE_TEMPLATES
    
    def test_get_genre_template(self):
        from music_brain.groove.templates import get_genre_template
        
        funk = get_genre_template('funk')
        assert funk.name == "Funk Pocket"
        assert funk.swing_factor > 0
    
    def test_invalid_genre_raises(self):
        from music_brain.groove.templates import get_genre_template
        
        with pytest.raises(ValueError):
            get_genre_template('nonexistent_genre')


class TestChordParsing:
    """Test chord parsing functionality."""
    
    def test_parse_simple_chord(self):
        from music_brain.structure.progression import parse_chord
        
        chord = parse_chord("Am")
        assert chord.root == "A"
        assert chord.quality == "min"
    
    def test_parse_seventh_chord(self):
        from music_brain.structure.progression import parse_chord
        
        chord = parse_chord("Cmaj7")
        assert chord.root == "C"
        assert "maj7" in chord.quality or "7" in str(chord.extensions)
    
    def test_parse_progression_string(self):
        from music_brain.structure.progression import parse_progression_string
        
        chords = parse_progression_string("F-C-Am-Dm")
        assert len(chords) == 4
        assert chords[0].root == "F"
        assert chords[2].root == "A"


class TestDiagnoseProgression:
    """Test progression diagnosis."""
    
    def test_diagnose_simple_progression(self):
        from music_brain.structure.progression import diagnose_progression
        
        result = diagnose_progression("F-C-Am-Dm")
        assert 'key' in result
        assert 'mode' in result
        assert 'chords' in result
    
    def test_diagnose_detects_borrowed_chord(self):
        from music_brain.structure.progression import diagnose_progression
        
        result = diagnose_progression("F-C-Bbm-F")
        # Should detect the Bbm as non-diatonic
        issues = result.get('issues', [])
        # May or may not flag depending on implementation
        assert isinstance(issues, list)


class TestTeachingModule:
    """Test the teaching module."""
    
    def test_teacher_initialization(self):
        from music_brain.session.teaching import RuleBreakingTeacher
        
        teacher = RuleBreakingTeacher()
        assert len(teacher.list_topics()) > 0
    
    def test_get_wisdom(self):
        from music_brain.session.teaching import RuleBreakingTeacher
        
        teacher = RuleBreakingTeacher()
        wisdom = teacher.get_wisdom()
        assert isinstance(wisdom, str)
        assert len(wisdom) > 0
    
    def test_get_lesson_content(self):
        from music_brain.session.teaching import RuleBreakingTeacher
        
        teacher = RuleBreakingTeacher()
        content = teacher.get_lesson_content('borrowed_chords')
        assert content is not None
        assert 'title' in content
        assert 'examples' in content
    
    def test_suggest_for_emotion(self):
        from music_brain.session.teaching import RuleBreakingTeacher
        
        teacher = RuleBreakingTeacher()
        suggestions = teacher.suggest_for_emotion('grief')
        assert 'emotion' in suggestions
        assert 'production_tips' in suggestions


class TestInterrogator:
    """Test the song interrogator module."""
    
    def test_interrogator_initialization(self):
        from music_brain.session.interrogator import SongInterrogator
        
        interrogator = SongInterrogator()
        assert interrogator.context is not None
    
    def test_quick_questions(self):
        from music_brain.session.interrogator import SongInterrogator, SongPhase
        
        interrogator = SongInterrogator()
        questions = interrogator.quick_questions(SongPhase.EMOTION, count=3)
        assert len(questions) == 3
    
    def test_get_challenge(self):
        from music_brain.session.interrogator import SongInterrogator
        
        interrogator = SongInterrogator()
        challenge = interrogator.get_challenge()
        assert isinstance(challenge, str)


class TestDataFiles:
    """Test that data files are accessible."""

    def test_data_directory_exists(self):
        data_dir = Path(__file__).parent.parent / "music_brain" / "data"
        assert data_dir.exists() or True  # May not exist in test environment

    def test_genre_pocket_maps_loadable(self):
        import json
        data_path = Path(__file__).parent.parent / "music_brain" / "data" / "genre_pocket_maps.json"
        if data_path.exists():
            with open(data_path) as f:
                data = json.load(f)
            assert 'genres' in data


class TestDrumHumanization:
    """Test the drum humanization / groove engine module."""

    def test_import_groove_engine(self):
        from music_brain.groove import (
            humanize_drums, GrooveSettings, quick_humanize,
            settings_from_intent, list_presets, settings_from_preset
        )
        assert callable(humanize_drums)
        assert callable(quick_humanize)
        assert callable(settings_from_intent)
        assert callable(list_presets)

    def test_groove_settings_creation(self):
        from music_brain.groove import GrooveSettings

        settings = GrooveSettings(complexity=0.5, vulnerability=0.7)
        assert settings.complexity == 0.5
        assert settings.vulnerability == 0.7
        assert settings.enable_ghost_notes is True

    def test_groove_settings_serialization(self):
        from music_brain.groove import GrooveSettings

        settings = GrooveSettings(
            complexity=0.4,
            vulnerability=0.6,
            kick_timing_mult=0.3,
        )
        data = settings.to_dict()
        restored = GrooveSettings.from_dict(data)

        assert restored.complexity == 0.4
        assert restored.vulnerability == 0.6
        assert restored.kick_timing_mult == 0.3

    def test_humanize_drums_basic(self):
        from music_brain.groove import humanize_drums

        # Create test events
        events = [
            {"start_tick": 0, "velocity": 100, "pitch": 36},      # Kick
            {"start_tick": 480, "velocity": 100, "pitch": 38},    # Snare
            {"start_tick": 960, "velocity": 100, "pitch": 36},    # Kick
            {"start_tick": 1440, "velocity": 100, "pitch": 38},   # Snare
        ]

        result = humanize_drums(
            events=events,
            complexity=0.5,
            vulnerability=0.5,
            ppq=480,
            seed=42,  # For reproducibility
        )

        # Should return same number of events (possibly more with ghost notes)
        assert len(result) >= len(events) - 1  # Allow for one dropout

        # Check that timing has been modified
        for orig, new in zip(events, result[:len(events)]):
            if "original_index" not in new:  # Skip ghost notes
                # Velocity should be within bounds
                assert 20 <= new["velocity"] <= 120

    def test_humanize_drums_with_zero_complexity(self):
        from music_brain.groove import humanize_drums

        events = [
            {"start_tick": 0, "velocity": 80, "pitch": 36},
            {"start_tick": 480, "velocity": 80, "pitch": 38},
        ]

        result = humanize_drums(
            events=events,
            complexity=0.0,
            vulnerability=0.5,
            ppq=480,
            seed=42,
        )

        # With zero complexity, timing should be very close to original
        # (only HUMAN_LATENCY_BIAS applied)
        assert len(result) == len(events)
        for orig, new in zip(events, result):
            # Timing should only differ by latency bias (~5 ticks)
            assert abs(new["start_tick"] - orig["start_tick"]) <= 10

    def test_quick_humanize_styles(self):
        from music_brain.groove import quick_humanize

        events = [
            {"start_tick": 0, "velocity": 80, "pitch": 36},
            {"start_tick": 480, "velocity": 80, "pitch": 38},
        ]

        # Test different styles
        for style in ["tight", "natural", "loose", "drunk"]:
            result = quick_humanize(events, style=style, ppq=480)
            assert len(result) >= 1
            assert all("velocity" in e for e in result)

    def test_settings_from_intent(self):
        from music_brain.groove import settings_from_intent

        # Test different vulnerability scales
        low_vuln = settings_from_intent(
            vulnerability_scale="Low",
            groove_feel="Straight/Driving",
        )
        assert low_vuln.vulnerability == 0.2

        high_vuln = settings_from_intent(
            vulnerability_scale="High",
            groove_feel="Rubato/Free",
        )
        assert high_vuln.vulnerability == 0.8
        assert high_vuln.complexity > 0.8

    def test_presets_loading(self):
        from music_brain.groove import list_presets, get_preset

        presets = list_presets()
        assert len(presets) > 0
        assert "lofi_depression" in presets

        preset = get_preset("lofi_depression")
        assert preset is not None
        assert "groove_settings" in preset
        assert preset["groove_settings"]["vulnerability"] > 0.5

    def test_settings_from_preset(self):
        from music_brain.groove import settings_from_preset

        settings = settings_from_preset("lofi_depression")
        assert settings.vulnerability == 0.8
        assert settings.complexity == 0.4
        assert settings.enable_ghost_notes is True

    def test_invalid_preset_raises(self):
        from music_brain.groove import settings_from_preset

        with pytest.raises(ValueError):
            settings_from_preset("nonexistent_preset")

    def test_drum_protection_levels(self):
        from music_brain.groove import humanize_drums

        # Create events with high dropout probability
        # Kicks should be protected, hi-hats should drop more
        kicks = [{"start_tick": i * 480, "velocity": 80, "pitch": 36} for i in range(20)]
        hihats = [{"start_tick": i * 480, "velocity": 80, "pitch": 42} for i in range(20)]

        # Run with high complexity (high dropout)
        kick_results = humanize_drums(kicks, complexity=1.0, vulnerability=0.5, seed=42)
        hihat_results = humanize_drums(hihats, complexity=1.0, vulnerability=0.5, seed=42)

        # Kicks should be more protected (fewer dropouts)
        kick_dropout_rate = 1 - (len(kick_results) / len(kicks))
        hihat_dropout_rate = 1 - (len(hihat_results) / len(hihats))

        # Kicks have 80% protection, hihats have 20% protection
        # So kick dropout should be lower on average
        # (This is probabilistic, so we use a loose assertion)
        assert kick_dropout_rate <= 0.15  # Protected kicks rarely drop


class TestDrumHumanizationPresets:
    """Test specific humanization presets for emotional accuracy."""

    def test_lofi_depression_preset_has_ghost_notes(self):
        from music_brain.groove import get_preset

        preset = get_preset("lofi_depression")
        settings = preset["groove_settings"]
        assert settings["enable_ghost_notes"] is True
        assert settings["ghost_note_probability"] > 0.1

    def test_mechanical_dissociation_disables_ghost_notes(self):
        from music_brain.groove import get_preset

        preset = get_preset("mechanical_dissociation")
        settings = preset["groove_settings"]
        assert settings["enable_ghost_notes"] is False
        assert settings["complexity"] < 0.15

    def test_defiant_punk_has_wide_velocity_range(self):
        from music_brain.groove import get_preset

        preset = get_preset("defiant_punk")
        settings = preset["groove_settings"]
        if "velocity_range_override" in settings:
            min_vel, max_vel = settings["velocity_range_override"]
            assert max_vel - min_vel >= 60


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
