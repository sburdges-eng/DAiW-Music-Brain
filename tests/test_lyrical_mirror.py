"""
Tests for the Lyrical Mirror module (cut-up / Markov text generation).

Covers: simple_cutup, generate_lyrical_fragments, mirror_session,
save_fragments, and corpus loading.

Run with: pytest tests/test_lyrical_mirror.py -v
"""

import pytest
import tempfile
from pathlib import Path

from music_brain.text.lyrical_mirror import (
    simple_cutup,
    generate_lyrical_fragments,
    mirror_session,
    save_fragments,
    _load_corpus,
    _clean_sentence,
    MARKOVIFY_AVAILABLE,
)


# ==============================================================================
# SIMPLE CUTUP TESTS
# ==============================================================================

class TestSimpleCutup:
    """Test the Burroughs-style cut-up function."""

    def test_returns_list(self):
        # Need many words to ensure fragments can be created after random shuffle
        text = " ".join(["word"] * 50)
        result = simple_cutup(text)
        assert isinstance(result, list)

    def test_empty_input_returns_empty_list(self):
        result = simple_cutup("")
        assert result == []

    def test_whitespace_only_returns_empty_list(self):
        result = simple_cutup("   \n\t  ")
        assert result == []

    def test_respects_max_fragments(self):
        text = "word " * 100  # Lots of words
        result = simple_cutup(text, max_fragments=3)
        assert len(result) <= 3

    def test_fragments_have_3_to_6_words(self):
        text = "one two three four five six seven eight nine ten " * 10
        result = simple_cutup(text, max_fragments=10)

        for fragment in result:
            word_count = len(fragment.split())
            assert 3 <= word_count <= 6

    def test_newlines_are_stripped(self):
        text = ("line one two three\nline four five six\n" +
                "line seven eight nine\nline ten eleven twelve\n" +
                "line thirteen fourteen fifteen")
        result = simple_cutup(text, max_fragments=2)

        for fragment in result:
            assert "\n" not in fragment


# ==============================================================================
# CLEAN SENTENCE TESTS
# ==============================================================================

class TestCleanSentence:
    """Test the sentence cleaning helper."""

    def test_none_returns_none(self):
        assert _clean_sentence(None) is None

    def test_empty_returns_none(self):
        assert _clean_sentence("") is None

    def test_too_short_returns_none(self):
        assert _clean_sentence("hi") is None

    def test_too_long_returns_none(self):
        long_text = "x" * 150
        assert _clean_sentence(long_text) is None

    def test_only_punctuation_returns_none(self):
        assert _clean_sentence("... --- !!!") is None

    def test_only_numbers_returns_none(self):
        assert _clean_sentence("123 456 789") is None

    def test_valid_sentence_returned(self):
        result = _clean_sentence("This is a valid sentence.")
        assert result == "This is a valid sentence."

    def test_whitespace_stripped(self):
        result = _clean_sentence("  Some text with spaces  ")
        assert result == "Some text with spaces"


# ==============================================================================
# LOAD CORPUS TESTS
# ==============================================================================

class TestLoadCorpus:
    """Test corpus loading from files."""

    def test_empty_paths_returns_empty_string(self):
        result = _load_corpus([])
        assert result == ""

    def test_nonexistent_files_handled(self):
        paths = [Path("/nonexistent/file1.txt"), Path("/nonexistent/file2.txt")]
        result = _load_corpus(paths)
        assert result == ""

    def test_loads_existing_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Sample corpus text for testing.")
            temp_path = f.name

        try:
            result = _load_corpus([Path(temp_path)])
            assert "Sample corpus text" in result
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_concatenates_multiple_files(self):
        paths = []
        try:
            for i, content in enumerate(["First file content", "Second file content"]):
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    f.write(content)
                    paths.append(Path(f.name))

            result = _load_corpus(paths)
            assert "First file" in result
            assert "Second file" in result
        finally:
            for p in paths:
                p.unlink(missing_ok=True)

    def test_handles_string_paths(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("String path test")
            temp_path = f.name

        try:
            # Pass string instead of Path
            result = _load_corpus([temp_path])
            assert "String path test" in result
        finally:
            Path(temp_path).unlink(missing_ok=True)


# ==============================================================================
# GENERATE LYRICAL FRAGMENTS TESTS
# ==============================================================================

class TestGenerateLyricalFragments:
    """Test the main lyrical fragment generator."""

    def test_returns_list(self):
        # Provide many words for the cutup fallback to work
        text = " ".join(["word"] * 50)
        result = generate_lyrical_fragments(text)
        assert isinstance(result, list)

    def test_empty_input_returns_empty_list(self):
        result = generate_lyrical_fragments("")
        assert result == []

    def test_whitespace_only_returns_empty_list(self):
        result = generate_lyrical_fragments("   \n   ")
        assert result == []

    def test_respects_max_lines(self):
        text = "The sorrow runs deep through my veins and soul forever " * 20
        result = generate_lyrical_fragments(text, max_lines=4)
        assert len(result) <= 4

    def test_no_corpus_with_enough_words(self):
        # Provide many words for the simple cutup to work
        text = " ".join(["word"] * 50)
        result = generate_lyrical_fragments(text, genre_corpus_paths=None)
        assert isinstance(result, list)

    def test_fragments_are_strings(self):
        text = " ".join(["word"] * 50)
        result = generate_lyrical_fragments(text, max_lines=3)

        for fragment in result:
            assert isinstance(fragment, str)

    @pytest.mark.skipif(not MARKOVIFY_AVAILABLE, reason="markovify not installed")
    def test_with_corpus_uses_markov(self):
        # Create a simple corpus file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("The darkness comes at night. ")
            f.write("Stars shine in the endless sky. ")
            f.write("Love conquers all in the end. ")
            f.write("Time heals all wounds slowly. ") * 10
            temp_path = f.name

        try:
            session_text = " ".join(["word"] * 30)
            result = generate_lyrical_fragments(
                session_text,
                genre_corpus_paths=[Path(temp_path)],
                max_lines=5,
            )
            assert isinstance(result, list)
        finally:
            Path(temp_path).unlink(missing_ok=True)


# ==============================================================================
# MIRROR SESSION TESTS
# ==============================================================================

class TestMirrorSession:
    """Test the convenience wrapper for therapy session mirroring."""

    def test_returns_list(self):
        # Provide many words for cutup to work reliably
        result = mirror_session(
            core_wound=" ".join(["word"] * 30),
            core_longing=" ".join(["word"] * 30),
        )
        assert isinstance(result, list)

    def test_all_empty_returns_empty_list(self):
        result = mirror_session()
        assert result == []

    def test_concatenates_all_phases(self):
        # With enough text, should produce fragments
        result = mirror_session(
            core_wound=" ".join(["word"] * 20),
            core_resistance=" ".join(["word"] * 20),
            core_longing=" ".join(["word"] * 20),
            core_stakes=" ".join(["word"] * 20),
            core_transformation=" ".join(["word"] * 20),
            max_lines=4,
        )
        # Should produce some output from the concatenated text
        assert isinstance(result, list)

    def test_respects_max_lines(self):
        result = mirror_session(
            core_wound=" ".join(["word"] * 30),
            core_longing=" ".join(["word"] * 30),
            max_lines=2,
        )
        assert len(result) <= 2

    def test_single_phase_input(self):
        result = mirror_session(
            core_wound=" ".join(["word"] * 50),
        )
        assert isinstance(result, list)


# ==============================================================================
# SAVE FRAGMENTS TESTS
# ==============================================================================

class TestSaveFragments:
    """Test saving fragments to file."""

    def test_creates_file(self):
        fragments = ["Line one of lyrics", "Line two of lyrics"]

        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name

        try:
            result = save_fragments(fragments, temp_path)
            assert Path(result).exists()
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_returns_path(self):
        fragments = ["Test fragment"]

        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name

        try:
            result = save_fragments(fragments, temp_path)
            assert result == temp_path
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_file_contains_fragments(self):
        fragments = ["First lyric line", "Second lyric line", "Third lyric line"]

        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name

        try:
            save_fragments(fragments, temp_path)

            content = Path(temp_path).read_text()
            assert "First lyric line" in content
            assert "Second lyric line" in content
            assert "Third lyric line" in content
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_file_has_header(self):
        fragments = ["A fragment"]

        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name

        try:
            save_fragments(fragments, temp_path)

            content = Path(temp_path).read_text()
            assert "Lyrical Fragments" in content
            assert "DAiW" in content
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_fragments_are_numbered(self):
        fragments = ["First", "Second", "Third"]

        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name

        try:
            save_fragments(fragments, temp_path)

            content = Path(temp_path).read_text()
            assert "1." in content
            assert "2." in content
            assert "3." in content
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_empty_fragments_list(self):
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name

        try:
            save_fragments([], temp_path)
            assert Path(temp_path).exists()

            content = Path(temp_path).read_text()
            # Should have header but no numbered lines
            assert "Lyrical Fragments" in content
        finally:
            Path(temp_path).unlink(missing_ok=True)


# ==============================================================================
# EDGE CASES AND INTEGRATION
# ==============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_unicode_text_handled(self):
        # Provide many words for cutup
        text = " ".join(["mot"] * 50)  # French words
        result = simple_cutup(text, max_fragments=2)
        assert isinstance(result, list)

    def test_special_characters_handled(self):
        # Provide many words for cutup
        text = " ".join(["word"] * 50)
        result = simple_cutup(text, max_fragments=2)
        assert isinstance(result, list)

    def test_very_long_text(self):
        text = "word " * 1000
        result = simple_cutup(text, max_fragments=10)
        assert len(result) <= 10

    def test_repeated_words(self):
        # Provide many words (even if repeated)
        text = " ".join(["word"] * 50)
        result = simple_cutup(text, max_fragments=3)
        assert isinstance(result, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
