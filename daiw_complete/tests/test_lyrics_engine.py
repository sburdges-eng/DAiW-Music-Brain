# tests/test_lyrics_engine.py
from music_brain.lyrics.engine import get_lyric_fragments


def test_lyric_mirror_returns_fragments():
    lines = get_lyric_fragments("I feel broken and static", "grief")
    assert isinstance(lines, list)
    assert len(lines) > 0
    assert all(isinstance(x, str) for x in lines)


def test_lyric_mirror_includes_mood_tag():
    lines = get_lyric_fragments("angry and betrayed", "rage")
    # First line should be mood tag
    assert "[RAGE]" in lines[0].upper()


def test_lyric_mirror_empty_input():
    lines = get_lyric_fragments("", "neutral")
    assert isinstance(lines, list)


def test_lyric_mirror_different_moods():
    grief_lines = get_lyric_fragments("loss and emptiness", "grief")
    rage_lines = get_lyric_fragments("burning anger", "rage")
    
    # Both should produce output
    assert len(grief_lines) > 0
    assert len(rage_lines) > 0
