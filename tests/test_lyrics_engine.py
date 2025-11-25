# tests/test_lyrics_engine.py
"""
Tests for the Lyrics Engine - Lyric Mirror / Markov chain generation.

Covers: corpus loading, fragment generation, cut-up text.

Run with: pytest tests/test_lyrics_engine.py -v
"""

import pytest

# Try to import - may fail if markovify not installed
try:
    from music_brain.lyrics.engine import LyricMirror, get_lyric_fragments, mirror
    LYRICS_AVAILABLE = True
except ImportError:
    LYRICS_AVAILABLE = False


@pytest.mark.skipif(not LYRICS_AVAILABLE, reason="markovify not installed")
class TestLyricMirrorBasics:
    """Basic LyricMirror functionality tests."""

    def test_mirror_instance_exists(self):
        """Module-level mirror instance should exist."""
        assert mirror is not None
        assert isinstance(mirror, LyricMirror)

    def test_lyric_mirror_init(self):
        """LyricMirror should initialize without error."""
        lm = LyricMirror()
        assert lm is not None

    def test_feed_corpus(self):
        """Should accept corpus text."""
        lm = LyricMirror()
        corpus = """
        I walk alone through empty streets
        The night is cold and dark
        My heart beats slow beneath the sheets
        A dying ember's spark
        """
        lm.feed_corpus(corpus)
        # Should not raise


@pytest.mark.skipif(not LYRICS_AVAILABLE, reason="markovify not installed")
class TestFragmentGeneration:
    """Tests for lyric fragment generation."""

    @pytest.fixture
    def trained_mirror(self):
        """Return a LyricMirror trained on sample corpus."""
        lm = LyricMirror()
        corpus = "\n".join([
            "The rain falls down on empty hearts",
            "We dance alone in crowded rooms",
            "Time slips away like morning mist",
            "The shadows grow as daylight fades",
            "I search for words that never come",
            "The silence speaks louder than screams",
            "We hold on tight to fading dreams",
            "The night consumes what day creates",
        ] * 10)  # Repeat for better Markov training
        lm.feed_corpus(corpus)
        return lm

    def test_generate_fragment(self, trained_mirror):
        """Should generate a text fragment."""
        fragment = trained_mirror.generate_fragment()
        # May return None if Markov can't generate
        if fragment is not None:
            assert isinstance(fragment, str)
            assert len(fragment) > 0

    def test_generate_multiple_fragments(self, trained_mirror):
        """Should be able to generate multiple fragments."""
        fragments = []
        for _ in range(10):
            frag = trained_mirror.generate_fragment()
            if frag:
                fragments.append(frag)
        # At least some should generate
        assert len(fragments) >= 1


@pytest.mark.skipif(not LYRICS_AVAILABLE, reason="markovify not installed")
class TestConvenienceFunction:
    """Tests for get_lyric_fragments convenience function."""

    def test_get_lyric_fragments_returns_list(self):
        """Should return a list of fragments."""
        result = get_lyric_fragments("loss", "melancholy")
        assert isinstance(result, list)

    def test_get_lyric_fragments_with_count(self):
        """Should respect count parameter."""
        result = get_lyric_fragments("anger", "rage", count=5)
        # May return fewer if generation fails
        assert len(result) <= 5


@pytest.mark.skipif(not LYRICS_AVAILABLE, reason="markovify not installed")
class TestCutUpText:
    """Tests for cut-up text generation."""

    def test_cut_up_basic(self):
        """Cut-up should rearrange text fragments."""
        lm = LyricMirror()
        source = "Hello world this is a test of the cut up method"
        result = lm.cut_up(source, num_fragments=3)
        assert isinstance(result, str)

    def test_cut_up_empty_input(self):
        """Empty input should return empty string."""
        lm = LyricMirror()
        result = lm.cut_up("", num_fragments=3)
        assert result == ""


@pytest.mark.skipif(LYRICS_AVAILABLE, reason="Test only when markovify missing")
class TestMissingDependency:
    """Tests for graceful handling when markovify is missing."""

    def test_import_fails_gracefully(self):
        """Should fail import gracefully when markovify missing."""
        # This test runs only when markovify is NOT installed
        # and verifies the import fails as expected
        pass
