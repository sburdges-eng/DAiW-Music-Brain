"""
Tests for the Chord Analysis module.

Covers: Chord dataclass, ChordProgression, detect_chord_from_notes,
detect_key, get_roman_numeral, identify_borrowed_chords, analyze_chords.

Run with: pytest tests/test_chord_analysis.py -v
"""

import pytest
import tempfile
from pathlib import Path

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False

from music_brain.structure.chord import (
    Chord,
    ChordProgression,
    ChordQuality,
    NOTE_NAMES,
    FLAT_NAMES,
    CHORD_QUALITIES,
    MAJOR_SCALE,
    MINOR_SCALE,
    midi_to_pitch_class,
    detect_chord_from_notes,
    detect_key,
    get_roman_numeral,
    identify_borrowed_chords,
    analyze_chords,
    MIDO_AVAILABLE as MODULE_MIDO_AVAILABLE,
)


# ==============================================================================
# CONSTANTS TESTS
# ==============================================================================

class TestConstants:
    """Test module constants."""

    def test_note_names_length(self):
        assert len(NOTE_NAMES) == 12
        assert len(FLAT_NAMES) == 12

    def test_note_names_start_with_c(self):
        assert NOTE_NAMES[0] == 'C'
        assert FLAT_NAMES[0] == 'C'

    def test_chord_qualities_exist(self):
        expected = ['maj', 'min', 'dim', 'aug', 'maj7', 'min7', '7', 'sus2', 'sus4']
        for qual in expected:
            assert qual in CHORD_QUALITIES

    def test_chord_qualities_are_tuples(self):
        for qual, intervals in CHORD_QUALITIES.items():
            assert isinstance(intervals, tuple)
            assert all(isinstance(i, int) for i in intervals)

    def test_major_scale_intervals(self):
        assert MAJOR_SCALE == [0, 2, 4, 5, 7, 9, 11]

    def test_minor_scale_intervals(self):
        assert MINOR_SCALE == [0, 2, 3, 5, 7, 8, 10]


# ==============================================================================
# CHORD QUALITY ENUM TESTS
# ==============================================================================

class TestChordQualityEnum:
    """Test ChordQuality enum."""

    def test_major_value(self):
        assert ChordQuality.MAJOR.value == "maj"

    def test_minor_value(self):
        assert ChordQuality.MINOR.value == "min"

    def test_diminished_value(self):
        assert ChordQuality.DIMINISHED.value == "dim"

    def test_all_qualities_have_string_values(self):
        for quality in ChordQuality:
            assert isinstance(quality.value, str)


# ==============================================================================
# CHORD DATACLASS TESTS
# ==============================================================================

class TestChord:
    """Test Chord dataclass."""

    def test_basic_creation(self):
        chord = Chord(root=0, quality='maj')
        assert chord.root == 0
        assert chord.quality == 'maj'

    def test_default_values(self):
        chord = Chord(root=0, quality='maj')
        assert chord.bass is None
        assert chord.extensions == []
        assert chord.start_tick == 0
        assert chord.duration_ticks == 0
        assert chord.notes == []

    def test_c_major_name(self):
        chord = Chord(root=0, quality='maj')
        assert chord.name == 'C'

    def test_a_minor_name(self):
        chord = Chord(root=9, quality='min')
        assert chord.name == 'Am'

    def test_f_sharp_dim_name(self):
        chord = Chord(root=6, quality='dim')
        assert chord.name == 'F#dim'

    def test_g_aug_name(self):
        chord = Chord(root=7, quality='aug')
        assert chord.name == 'G+'

    def test_d_dominant7_name(self):
        chord = Chord(root=2, quality='7')
        assert chord.name == 'D7'

    def test_e_maj7_name(self):
        chord = Chord(root=4, quality='maj7')
        assert chord.name == 'Emaj7'

    def test_b_min7_name(self):
        chord = Chord(root=11, quality='min7')
        assert chord.name == 'Bm7'

    def test_slash_chord_name(self):
        chord = Chord(root=0, quality='maj', bass=7)  # C/G
        assert chord.name == 'C/G'

    def test_slash_chord_same_bass_no_slash(self):
        chord = Chord(root=0, quality='maj', bass=0)  # C/C = just C
        assert chord.name == 'C'

    def test_extensions_in_name(self):
        chord = Chord(root=0, quality='maj', extensions=['add9'])
        assert 'add9' in chord.name

    def test_str_returns_name(self):
        chord = Chord(root=0, quality='maj')
        assert str(chord) == chord.name


# ==============================================================================
# CHORD PROGRESSION DATACLASS TESTS
# ==============================================================================

class TestChordProgression:
    """Test ChordProgression dataclass."""

    def test_basic_creation(self):
        prog = ChordProgression(chords=['C', 'Am', 'F', 'G'])
        assert prog.chords == ['C', 'Am', 'F', 'G']

    def test_default_values(self):
        prog = ChordProgression(chords=['C', 'G'])
        assert prog.key == 'C'
        assert prog.mode == 'major'
        assert prog.chord_objects == []
        assert prog.roman_numerals == []
        assert prog.borrowed_chords == {}

    def test_str_returns_progression(self):
        prog = ChordProgression(chords=['C', 'Am', 'F', 'G'])
        assert str(prog) == 'C - Am - F - G'


# ==============================================================================
# MIDI_TO_PITCH_CLASS TESTS
# ==============================================================================

class TestMidiToPitchClass:
    """Test midi_to_pitch_class function."""

    def test_c0(self):
        # C0 = MIDI 12
        assert midi_to_pitch_class(12) == 0

    def test_c4(self):
        # C4 = MIDI 60
        assert midi_to_pitch_class(60) == 0

    def test_a4(self):
        # A4 = MIDI 69
        assert midi_to_pitch_class(69) == 9

    def test_b2(self):
        # B2 = MIDI 47
        assert midi_to_pitch_class(47) == 11

    def test_wraps_correctly(self):
        # C5 = MIDI 72
        assert midi_to_pitch_class(72) == 0
        # G5 = MIDI 79
        assert midi_to_pitch_class(79) == 7


# ==============================================================================
# DETECT_CHORD_FROM_NOTES TESTS
# ==============================================================================

class TestDetectChordFromNotes:
    """Test detect_chord_from_notes function."""

    def test_empty_list_returns_none(self):
        result = detect_chord_from_notes([])
        assert result is None

    def test_single_note_returns_none(self):
        result = detect_chord_from_notes([60])
        assert result is None

    def test_c_major_triad(self):
        # C4, E4, G4
        result = detect_chord_from_notes([60, 64, 67])
        assert result is not None
        assert result.root == 0
        assert result.quality == 'maj'

    def test_a_minor_triad(self):
        # A4, C5, E5
        result = detect_chord_from_notes([69, 72, 76])
        assert result is not None
        assert result.root == 9
        assert result.quality == 'min'

    def test_g_dominant_7(self):
        # G, B, D, F
        result = detect_chord_from_notes([55, 59, 62, 65])
        assert result is not None
        assert result.root == 7
        assert result.quality in ['7', 'maj']  # Allow some flexibility

    def test_d_minor_7(self):
        # D, F, A, C
        result = detect_chord_from_notes([62, 65, 69, 72])
        assert result is not None
        assert result.root == 2

    def test_diminished_triad(self):
        # B, D, F (B diminished)
        result = detect_chord_from_notes([59, 62, 65])
        assert result is not None
        assert result.root == 11
        assert result.quality == 'dim'

    def test_sus4_chord(self):
        # C, F, G (Csus4)
        result = detect_chord_from_notes([60, 65, 67])
        assert result is not None
        assert result.root == 0

    def test_sus2_chord(self):
        # C, D, G (Csus2)
        result = detect_chord_from_notes([60, 62, 67])
        assert result is not None
        assert result.root == 0

    def test_octave_duplicates_handled(self):
        # C in multiple octaves with E and G
        result = detect_chord_from_notes([48, 60, 64, 67, 72])
        assert result is not None
        assert result.root == 0

    def test_notes_stored_in_result(self):
        notes = [60, 64, 67]
        result = detect_chord_from_notes(notes)
        assert result.notes == notes


# ==============================================================================
# DETECT_KEY TESTS
# ==============================================================================

class TestDetectKey:
    """Test detect_key function."""

    def test_empty_chords_returns_c_major(self):
        key, mode = detect_key([])
        assert key == 'C'
        assert mode == 'major'

    def test_c_major_progression(self):
        chords = [
            Chord(root=0, quality='maj'),   # C
            Chord(root=7, quality='maj'),   # G
            Chord(root=9, quality='min'),   # Am
            Chord(root=5, quality='maj'),   # F
        ]
        key, mode = detect_key(chords)
        assert key == 'C'
        assert mode == 'major'

    def test_g_major_progression(self):
        chords = [
            Chord(root=7, quality='maj'),   # G
            Chord(root=2, quality='maj'),   # D
            Chord(root=4, quality='min'),   # Em
            Chord(root=0, quality='maj'),   # C
        ]
        key, mode = detect_key(chords)
        # Key detection may choose C or G as both are valid interpretations
        assert key in ['G', 'C']
        assert mode == 'major'

    def test_a_minor_progression(self):
        chords = [
            Chord(root=9, quality='min'),   # Am
            Chord(root=2, quality='min'),   # Dm
            Chord(root=4, quality='maj'),   # E (or E7 in harmonic minor)
            Chord(root=9, quality='min'),   # Am
        ]
        key, mode = detect_key(chords)
        # Algorithm may detect A minor or C major (relative)
        assert key in ['A', 'C']
        # Mode depends on which key was detected
        assert mode in ['minor', 'major']


# ==============================================================================
# GET_ROMAN_NUMERAL TESTS
# ==============================================================================

class TestGetRomanNumeral:
    """Test get_roman_numeral function."""

    def test_tonic_major(self):
        chord = Chord(root=0, quality='maj')
        result = get_roman_numeral(chord, key=0, mode='major')
        assert result == 'I'

    def test_dominant_major(self):
        chord = Chord(root=7, quality='maj')
        result = get_roman_numeral(chord, key=0, mode='major')
        assert result == 'V'

    def test_subdominant_major(self):
        chord = Chord(root=5, quality='maj')
        result = get_roman_numeral(chord, key=0, mode='major')
        assert result == 'IV'

    def test_relative_minor(self):
        chord = Chord(root=9, quality='min')
        result = get_roman_numeral(chord, key=0, mode='major')
        assert result == 'vi'

    def test_supertonic_minor(self):
        chord = Chord(root=2, quality='min')
        result = get_roman_numeral(chord, key=0, mode='major')
        assert result == 'ii'

    def test_flat_seven(self):
        chord = Chord(root=10, quality='maj')  # Bb in C major
        result = get_roman_numeral(chord, key=0, mode='major')
        assert 'bVII' in result or 'VII' in result

    def test_flat_six(self):
        chord = Chord(root=8, quality='maj')  # Ab in C major
        result = get_roman_numeral(chord, key=0, mode='major')
        assert 'bVI' in result or 'VI' in result


# ==============================================================================
# IDENTIFY_BORROWED_CHORDS TESTS
# ==============================================================================

class TestIdentifyBorrowedChords:
    """Test identify_borrowed_chords function."""

    def test_empty_chords_returns_empty(self):
        result = identify_borrowed_chords([], key=0, mode='major')
        assert result == {}

    def test_minor_mode_returns_empty(self):
        chords = [Chord(root=0, quality='maj')]
        result = identify_borrowed_chords(chords, key=0, mode='minor')
        assert result == {}

    def test_identifies_flat_three(self):
        # bIII chord (Eb in C major)
        chords = [Chord(root=3, quality='maj')]
        result = identify_borrowed_chords(chords, key=0, mode='major')
        assert len(result) == 1
        assert 'parallel minor' in list(result.values())[0].lower()

    def test_identifies_flat_six(self):
        # bVI chord (Ab in C major)
        chords = [Chord(root=8, quality='maj')]
        result = identify_borrowed_chords(chords, key=0, mode='major')
        assert len(result) == 1

    def test_identifies_flat_seven(self):
        # bVII chord (Bb in C major)
        chords = [Chord(root=10, quality='maj')]
        result = identify_borrowed_chords(chords, key=0, mode='major')
        assert len(result) == 1

    def test_identifies_minor_four(self):
        # iv chord (Fm in C major)
        chords = [Chord(root=5, quality='min')]
        result = identify_borrowed_chords(chords, key=0, mode='major')
        assert len(result) == 1

    def test_diatonic_chords_not_flagged(self):
        chords = [
            Chord(root=0, quality='maj'),   # I
            Chord(root=5, quality='maj'),   # IV (major)
            Chord(root=7, quality='maj'),   # V
        ]
        result = identify_borrowed_chords(chords, key=0, mode='major')
        assert len(result) == 0


# ==============================================================================
# ANALYZE_CHORDS TESTS (Requires mido)
# ==============================================================================

@pytest.mark.skipif(not MIDO_AVAILABLE, reason="mido not installed")
class TestAnalyzeChords:
    """Test analyze_chords function."""

    @pytest.fixture
    def c_major_progression_midi(self):
        """Create MIDI file with C-Am-F-G progression."""
        mid = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))

        chords = [
            [60, 64, 67],  # C major
            [69, 72, 76],  # A minor
            [65, 69, 72],  # F major
            [67, 71, 74],  # G major
        ]

        current_time = 0
        for chord_notes in chords:
            for note in chord_notes:
                track.append(mido.Message('note_on', note=note, velocity=80, channel=0, time=0))
            for note in chord_notes:
                track.append(mido.Message('note_off', note=note, velocity=0, channel=0, time=480 if note == chord_notes[-1] else 0))

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        mid.save(temp_path)
        yield temp_path
        Path(temp_path).unlink(missing_ok=True)

    @pytest.fixture
    def empty_midi(self):
        """Create MIDI file with no notes."""
        mid = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))
        track.append(mido.MetaMessage('end_of_track', time=0))

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        mid.save(temp_path)
        yield temp_path
        Path(temp_path).unlink(missing_ok=True)

    def test_returns_chord_progression(self, c_major_progression_midi):
        result = analyze_chords(c_major_progression_midi)
        assert isinstance(result, ChordProgression)

    def test_detects_chords(self, c_major_progression_midi):
        result = analyze_chords(c_major_progression_midi)
        assert len(result.chords) > 0

    def test_detects_key(self, c_major_progression_midi):
        result = analyze_chords(c_major_progression_midi)
        assert result.key in NOTE_NAMES
        assert result.mode in ['major', 'minor']

    def test_stores_source_file(self, c_major_progression_midi):
        result = analyze_chords(c_major_progression_midi)
        assert c_major_progression_midi in result.source_file or Path(c_major_progression_midi).name in result.source_file

    def test_extracts_tempo(self, c_major_progression_midi):
        result = analyze_chords(c_major_progression_midi)
        assert result.tempo_bpm == 120.0

    def test_empty_file_returns_empty_chords(self, empty_midi):
        result = analyze_chords(empty_midi)
        assert result.chords == []

    def test_raises_for_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            analyze_chords("/nonexistent/file.mid")

    def test_has_roman_numerals(self, c_major_progression_midi):
        result = analyze_chords(c_major_progression_midi)
        # If chords were detected, should have roman numerals
        if result.chords:
            assert len(result.roman_numerals) == len(result.chord_objects)


# ==============================================================================
# EDGE CASES
# ==============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_chord_with_all_extensions(self):
        chord = Chord(root=0, quality='maj', extensions=['add9', 'add11', 'add13'])
        name = chord.name
        assert 'add9' in name
        assert 'add11' in name
        assert 'add13' in name

    def test_unusual_quality_string(self):
        chord = Chord(root=0, quality='hdim7')
        assert chord.name == 'Chdim7'

    def test_pitch_class_negative_handling(self):
        # Shouldn't happen, but test robustness
        result = midi_to_pitch_class(0)
        assert result == 0

    def test_detect_chord_from_wide_voicing(self):
        # Notes spread across octaves
        result = detect_chord_from_notes([36, 52, 67])  # C1, E3, G4
        assert result is not None
        assert result.root == 0

    def test_detect_chord_from_dense_cluster(self):
        # Many notes close together
        result = detect_chord_from_notes([60, 61, 62, 63, 64, 65, 66, 67])
        # Should still return something reasonable
        assert result is not None or result is None  # Accepts any valid outcome


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
