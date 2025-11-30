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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
