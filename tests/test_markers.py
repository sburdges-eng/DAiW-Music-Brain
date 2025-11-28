"""
Tests for the DAW Markers module (structure markers for timeline).

Covers: MarkerEvent, EmotionalSection, get_standard_structure,
get_emotional_structure, export_markers_midi, merge_markers_with_midi.

Run with: pytest tests/test_markers.py -v
"""

import pytest
import tempfile
from pathlib import Path

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False

from music_brain.daw.markers import (
    MarkerEvent,
    EmotionalSection,
    get_standard_structure,
    get_emotional_structure,
    export_markers_midi,
    export_sections_midi,
    merge_markers_with_midi,
    MIDO_AVAILABLE as MODULE_MIDO_AVAILABLE,
)


# ==============================================================================
# MARKER EVENT DATACLASS TESTS
# ==============================================================================

class TestMarkerEvent:
    """Test MarkerEvent dataclass."""

    def test_creation(self):
        marker = MarkerEvent(bar=1, text="Intro")
        assert marker.bar == 1
        assert marker.text == "Intro"

    def test_default_color_is_none(self):
        marker = MarkerEvent(bar=1, text="Test")
        assert marker.color is None

    def test_custom_color(self):
        marker = MarkerEvent(bar=1, text="Test", color="red")
        assert marker.color == "red"

    def test_bar_can_be_any_positive_int(self):
        marker = MarkerEvent(bar=100, text="Late marker")
        assert marker.bar == 100


# ==============================================================================
# EMOTIONAL SECTION DATACLASS TESTS
# ==============================================================================

class TestEmotionalSection:
    """Test EmotionalSection dataclass."""

    def test_creation(self):
        section = EmotionalSection(
            start_bar=1,
            end_bar=8,
            section_type="verse",
            emotional_label="The Wound",
        )
        assert section.start_bar == 1
        assert section.end_bar == 8
        assert section.section_type == "verse"
        assert section.emotional_label == "The Wound"

    def test_default_tension(self):
        section = EmotionalSection(
            start_bar=1,
            end_bar=8,
            section_type="verse",
            emotional_label="Test",
        )
        assert section.tension == 0.8

    def test_custom_tension(self):
        section = EmotionalSection(
            start_bar=1,
            end_bar=8,
            section_type="chorus",
            emotional_label="Test",
            tension=1.2,
        )
        assert section.tension == 1.2


# ==============================================================================
# GET_STANDARD_STRUCTURE TESTS
# ==============================================================================

class TestGetStandardStructure:
    """Test get_standard_structure function."""

    def test_returns_list(self):
        result = get_standard_structure(32)
        assert isinstance(result, list)

    def test_all_items_are_marker_events(self):
        result = get_standard_structure(32)
        for marker in result:
            assert isinstance(marker, MarkerEvent)

    def test_short_form_16_bars(self):
        result = get_standard_structure(16)
        texts = [m.text for m in result]

        assert "Intro" in texts
        assert "Main" in texts
        assert "Outro" in texts

    def test_medium_form_32_bars(self):
        result = get_standard_structure(32)
        texts = [m.text for m in result]

        assert "Intro" in texts
        assert "Verse" in texts
        assert "Chorus" in texts
        assert "Outro" in texts

    def test_long_form_64_bars(self):
        result = get_standard_structure(64)
        texts = [m.text for m in result]

        assert "Verse 1" in texts
        assert "Verse 2" in texts
        assert "Bridge" in texts
        assert "Final Chorus" in texts

    def test_markers_within_song_length(self):
        for length in [8, 16, 32, 48, 64]:
            result = get_standard_structure(length)
            for marker in result:
                assert marker.bar <= length

    def test_markers_are_sorted_by_bar(self):
        result = get_standard_structure(64)
        bars = [m.bar for m in result]
        assert bars == sorted(bars)

    def test_first_marker_is_intro(self):
        result = get_standard_structure(32)
        assert result[0].text == "Intro"
        assert result[0].bar == 1


# ==============================================================================
# GET_EMOTIONAL_STRUCTURE TESTS
# ==============================================================================

class TestGetEmotionalStructure:
    """Test get_emotional_structure function."""

    def test_returns_list(self):
        result = get_emotional_structure(32)
        assert isinstance(result, list)

    def test_all_items_are_marker_events(self):
        result = get_emotional_structure(32)
        for marker in result:
            assert isinstance(marker, MarkerEvent)

    def test_grief_mood_labels(self):
        result = get_emotional_structure(32, mood_profile="grief")
        combined_text = " ".join(m.text for m in result)

        assert "Loss" in combined_text or "Acceptance" in combined_text or "Memories" in combined_text

    def test_rage_mood_labels(self):
        result = get_emotional_structure(32, mood_profile="rage")
        combined_text = " ".join(m.text for m in result)

        assert "Wound" in combined_text or "Burning" in combined_text or "Release" in combined_text

    def test_fear_mood_labels(self):
        result = get_emotional_structure(32, mood_profile="fear")
        combined_text = " ".join(m.text for m in result)

        assert "Threat" in combined_text or "Running" in combined_text or "Standing" in combined_text

    def test_nostalgia_mood_labels(self):
        result = get_emotional_structure(32, mood_profile="nostalgia")
        combined_text = " ".join(m.text for m in result)

        assert "Was" in combined_text or "Changed" in combined_text or "Remains" in combined_text

    def test_defiance_mood_labels(self):
        result = get_emotional_structure(32, mood_profile="defiance")
        combined_text = " ".join(m.text for m in result)

        assert "Challenge" in combined_text or "Fight" in combined_text or "Victory" in combined_text

    def test_neutral_mood_labels(self):
        result = get_emotional_structure(32, mood_profile="neutral")
        combined_text = " ".join(m.text for m in result)

        assert "Beginning" in combined_text or "Development" in combined_text or "Resolution" in combined_text

    def test_unknown_mood_uses_neutral(self):
        result = get_emotional_structure(32, mood_profile="unknown_mood")
        combined_text = " ".join(m.text for m in result)

        # Should fall back to neutral labels
        assert "Beginning" in combined_text or "Development" in combined_text or "Resolution" in combined_text

    def test_short_form_has_fewer_markers(self):
        short = get_emotional_structure(16)
        medium = get_emotional_structure(32)
        long_ = get_emotional_structure(64)

        assert len(short) < len(medium) <= len(long_)


# ==============================================================================
# EXPORT_MARKERS_MIDI TESTS
# ==============================================================================

@pytest.mark.skipif(not MIDO_AVAILABLE, reason="mido not installed")
class TestExportMarkersMidi:
    """Test export_markers_midi function."""

    def test_creates_file(self):
        markers = [
            MarkerEvent(bar=1, text="Intro"),
            MarkerEvent(bar=9, text="Verse"),
        ]

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            result = export_markers_midi(
                markers, ppq=480, beats_per_bar=4, tempo_bpm=120, output_path=temp_path
            )
            assert Path(result).exists()
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_returns_path(self):
        markers = [MarkerEvent(bar=1, text="Test")]

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            result = export_markers_midi(
                markers, ppq=480, beats_per_bar=4, tempo_bpm=120, output_path=temp_path
            )
            assert result == temp_path
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_contains_marker_messages(self):
        markers = [
            MarkerEvent(bar=1, text="Start"),
            MarkerEvent(bar=5, text="Middle"),
        ]

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            export_markers_midi(
                markers, ppq=480, beats_per_bar=4, tempo_bpm=120, output_path=temp_path
            )

            mid = mido.MidiFile(temp_path)
            marker_texts = []
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'marker':
                        marker_texts.append(msg.text)

            assert "Start" in marker_texts
            assert "Middle" in marker_texts
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_contains_tempo(self):
        markers = [MarkerEvent(bar=1, text="Test")]

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            export_markers_midi(
                markers, ppq=480, beats_per_bar=4, tempo_bpm=100, output_path=temp_path
            )

            mid = mido.MidiFile(temp_path)
            tempo_found = False
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'set_tempo':
                        tempo_found = True
                        # 100 BPM = 600000 microseconds
                        assert msg.tempo == 600000

            assert tempo_found
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_empty_markers_creates_valid_midi(self):
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            export_markers_midi(
                [], ppq=480, beats_per_bar=4, tempo_bpm=120, output_path=temp_path
            )

            mid = mido.MidiFile(temp_path)
            assert mid.ticks_per_beat == 480
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_markers_sorted_by_bar(self):
        # Pass markers out of order
        markers = [
            MarkerEvent(bar=9, text="Second"),
            MarkerEvent(bar=1, text="First"),
            MarkerEvent(bar=17, text="Third"),
        ]

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            export_markers_midi(
                markers, ppq=480, beats_per_bar=4, tempo_bpm=120, output_path=temp_path
            )

            mid = mido.MidiFile(temp_path)
            marker_order = []
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'marker':
                        marker_order.append(msg.text)

            assert marker_order == ["First", "Second", "Third"]
        finally:
            Path(temp_path).unlink(missing_ok=True)


# ==============================================================================
# EXPORT_SECTIONS_MIDI TESTS
# ==============================================================================

@pytest.mark.skipif(not MIDO_AVAILABLE, reason="mido not installed")
class TestExportSectionsMidi:
    """Test export_sections_midi function."""

    def test_creates_file(self):
        sections = [
            EmotionalSection(start_bar=1, end_bar=8, section_type="intro", emotional_label="Opening"),
        ]

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            result = export_sections_midi(
                sections, ppq=480, beats_per_bar=4, tempo_bpm=120, output_path=temp_path
            )
            assert Path(result).exists()
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_creates_start_and_end_markers(self):
        sections = [
            EmotionalSection(start_bar=1, end_bar=8, section_type="verse", emotional_label="The Wound"),
        ]

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            export_sections_midi(
                sections, ppq=480, beats_per_bar=4, tempo_bpm=120, output_path=temp_path
            )

            mid = mido.MidiFile(temp_path)
            marker_texts = []
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'marker':
                        marker_texts.append(msg.text)

            # Should have start marker with section type and emotional label
            assert any("VERSE" in t.upper() for t in marker_texts)
            assert any("Wound" in t for t in marker_texts)
            # Should have end marker
            assert any("End" in t for t in marker_texts)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_multiple_sections(self):
        sections = [
            EmotionalSection(start_bar=1, end_bar=8, section_type="intro", emotional_label="Opening"),
            EmotionalSection(start_bar=8, end_bar=16, section_type="verse", emotional_label="Story"),
            EmotionalSection(start_bar=16, end_bar=24, section_type="chorus", emotional_label="Release"),
        ]

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            export_sections_midi(
                sections, ppq=480, beats_per_bar=4, tempo_bpm=120, output_path=temp_path
            )

            mid = mido.MidiFile(temp_path)
            marker_count = sum(
                1 for track in mid.tracks for msg in track if msg.type == 'marker'
            )

            # 3 sections * 2 markers (start + end) = 6 markers
            assert marker_count == 6
        finally:
            Path(temp_path).unlink(missing_ok=True)


# ==============================================================================
# MERGE_MARKERS_WITH_MIDI TESTS
# ==============================================================================

@pytest.mark.skipif(not MIDO_AVAILABLE, reason="mido not installed")
class TestMergeMarkersWithMidi:
    """Test merge_markers_with_midi function."""

    @pytest.fixture
    def simple_midi_file(self):
        """Create a simple MIDI file to merge markers into."""
        mid = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)

        track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))
        track.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        track.append(mido.Message('note_on', note=60, velocity=100, channel=0, time=0))
        track.append(mido.Message('note_off', note=60, velocity=0, channel=0, time=480))
        track.append(mido.MetaMessage('end_of_track', time=0))

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        mid.save(temp_path)
        yield temp_path

        Path(temp_path).unlink(missing_ok=True)

    def test_creates_output_file(self, simple_midi_file):
        markers = [MarkerEvent(bar=1, text="Merged Marker")]

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            result = merge_markers_with_midi(markers, simple_midi_file, output_path)
            assert Path(result).exists()
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_preserves_original_content(self, simple_midi_file):
        markers = [MarkerEvent(bar=1, text="Test")]

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            merge_markers_with_midi(markers, simple_midi_file, output_path)

            mid = mido.MidiFile(output_path)

            # Should still have the original note
            note_on_found = False
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'note_on' and msg.velocity > 0:
                        note_on_found = True
                        assert msg.note == 60

            assert note_on_found
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_adds_markers(self, simple_midi_file):
        markers = [
            MarkerEvent(bar=1, text="Start Here"),
            MarkerEvent(bar=2, text="Second Marker"),
        ]

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            merge_markers_with_midi(markers, simple_midi_file, output_path)

            mid = mido.MidiFile(output_path)
            marker_texts = []
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'marker':
                        marker_texts.append(msg.text)

            assert "Start Here" in marker_texts
            assert "Second Marker" in marker_texts
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_nonexistent_midi_returns_original_path(self):
        markers = [MarkerEvent(bar=1, text="Test")]
        result = merge_markers_with_midi(
            markers, "/nonexistent/file.mid", "/output/path.mid"
        )
        # Should return the original path (not created)
        assert result == "/nonexistent/file.mid"


# ==============================================================================
# EDGE CASES
# ==============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_late_marker(self):
        markers = get_standard_structure(1000)
        # Should handle large bar numbers
        assert isinstance(markers, list)

    def test_single_bar_song(self):
        result = get_standard_structure(1)
        assert len(result) <= 1

    def test_zero_bar_song(self):
        result = get_standard_structure(0)
        assert result == []

    def test_all_mood_profiles(self):
        moods = ["grief", "rage", "fear", "nostalgia", "defiance",
                 "tenderness", "dissociation", "awe", "confusion", "neutral"]

        for mood in moods:
            result = get_emotional_structure(32, mood_profile=mood)
            assert len(result) > 0
            assert all(isinstance(m, MarkerEvent) for m in result)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
