"""
Lyrical Mirror: Cut-Up / Markov Engine

Takes therapy text + genre corpus and generates lyrical fragments.
Not full verses - just sparks to ignite creativity.

Philosophy: The tool shouldn't finish art for people. It should make them braver.
"""

import random
from pathlib import Path
from typing import List, Optional

try:
    import markovify
    MARKOVIFY_AVAILABLE = True
except ImportError:
    markovify = None
    MARKOVIFY_AVAILABLE = False


def _load_corpus(paths: List[Path]) -> str:
    """
    Load and concatenate text from multiple corpus files.

    Args:
        paths: List of file paths to load

    Returns:
        Concatenated text from all readable files
    """
    chunks = []
    for p in paths:
        try:
            if isinstance(p, str):
                p = Path(p)
            if p.exists():
                chunks.append(p.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
    return "\n".join(chunks)


def simple_cutup(text: str, max_fragments: int = 6) -> List[str]:
    """
    Very crude fallback: cut words into chunks, shuffle, recombine.

    This is the Burroughs-inspired cut-up technique - break the text
    into pieces and reassemble to find unexpected connections.

    Args:
        text: Source text to cut up
        max_fragments: Maximum number of fragments to generate

    Returns:
        List of text fragments (3-6 words each)
    """
    # Clean and split into words
    words = text.replace("\n", " ").split()

    # Remove empty strings and excessive whitespace
    words = [w.strip() for w in words if w.strip()]

    if not words:
        return []

    # Shuffle to break original structure
    random.shuffle(words)
    fragments = []

    # Create 3-6 word fragments
    while words and len(fragments) < max_fragments:
        n = random.randint(3, min(6, len(words)))
        chunk = words[:n]
        words = words[n:]
        if chunk:
            fragments.append(" ".join(chunk))

    return fragments


def _clean_sentence(sentence: Optional[str]) -> Optional[str]:
    """
    Clean up a generated sentence for lyrical use.

    Args:
        sentence: Raw generated sentence

    Returns:
        Cleaned sentence or None
    """
    if not sentence:
        return None

    # Strip whitespace
    sentence = sentence.strip()

    # Skip if too short or too long for a lyric line
    if len(sentence) < 5 or len(sentence) > 120:
        return None

    # Skip if it's just punctuation or numbers
    if not any(c.isalpha() for c in sentence):
        return None

    return sentence


def generate_lyrical_fragments(
    session_text: str,
    genre_corpus_paths: Optional[List[Path]] = None,
    max_lines: int = 8,
    state_size: int = 2,
    blend_ratio: float = 0.5,
) -> List[str]:
    """
    Generate lyric-like fragments from the user's therapy text, optionally
    fused with a genre corpus.

    Uses markovify if available, otherwise falls back to simple cut-up.

    The fragments are meant to be sparks - not finished lyrics. They reveal
    unexpected connections in the emotional material.

    Args:
        session_text: Concatenation of therapy session answers
        genre_corpus_paths: Optional list of paths to genre lyric corpora
        max_lines: Maximum number of fragments to generate
        state_size: Markov chain state size (2 = pairs, 3 = triplets)
        blend_ratio: How much to weight corpus vs session text (0-1)

    Returns:
        List of short lyrical phrases/fragments
    """
    if not session_text.strip():
        return []

    # Handle paths parameter
    if genre_corpus_paths is None:
        genre_corpus_paths = []

    corpus_text = _load_corpus(genre_corpus_paths)

    # If no markovify or no external corpus, use simple cut-up
    if not MARKOVIFY_AVAILABLE or not corpus_text.strip():
        return simple_cutup(session_text, max_fragments=max_lines)

    try:
        # Build combined text with weighting
        # More session text = more personal; more corpus = more genre-flavored
        if blend_ratio > 0 and corpus_text.strip():
            # Repeat session text to weight it against potentially larger corpus
            session_weight = int(10 * (1 - blend_ratio)) + 1
            combined = (session_text.strip() + "\n") * session_weight + corpus_text
        else:
            combined = session_text.strip()

        # Build Markov model
        model = markovify.Text(combined, state_size=state_size)

        lines = []
        attempts = 0
        max_attempts = max_lines * 5  # Allow more attempts for variety

        while len(lines) < max_lines and attempts < max_attempts:
            attempts += 1

            # Try to make a short sentence (more lyric-like)
            sentence = model.make_short_sentence(
                max_chars=80,
                min_chars=10,
                tries=10
            )

            # Fall back to regular sentence if short fails
            if not sentence:
                sentence = model.make_sentence(tries=5)

            cleaned = _clean_sentence(sentence)
            if cleaned and cleaned not in lines:  # Avoid duplicates
                lines.append(cleaned)

        return lines

    except Exception:
        # If markovify fails for any reason, fall back to cut-up
        return simple_cutup(session_text, max_fragments=max_lines)


def mirror_session(
    core_wound: str = "",
    core_resistance: str = "",
    core_longing: str = "",
    core_stakes: str = "",
    core_transformation: str = "",
    genre_corpus_paths: Optional[List[Path]] = None,
    max_lines: int = 8,
) -> List[str]:
    """
    Convenience function to generate fragments from a therapy session's
    Phase 0 answers.

    This mirrors back the user's own emotional material in fragmented form,
    helping them see patterns and unexpected connections.

    Args:
        core_wound: The inciting moment/realization
        core_resistance: What's holding you back
        core_longing: What you ultimately want to feel
        core_stakes: What's at risk
        core_transformation: How you want to feel when done
        genre_corpus_paths: Optional paths to genre lyric corpora
        max_lines: Maximum fragments to generate

    Returns:
        List of lyrical fragments
    """
    # Concatenate all phase 0 answers
    session_parts = [
        core_wound,
        core_resistance,
        core_longing,
        core_stakes,
        core_transformation,
    ]

    session_text = " ".join(part.strip() for part in session_parts if part.strip())

    return generate_lyrical_fragments(
        session_text=session_text,
        genre_corpus_paths=genre_corpus_paths,
        max_lines=max_lines,
    )


def save_fragments(fragments: List[str], output_path: str) -> str:
    """
    Save generated fragments to a text file.

    Args:
        fragments: List of lyrical fragments
        output_path: Path to save file

    Returns:
        Path to saved file
    """
    path = Path(output_path)

    content = "# Lyrical Fragments\n"
    content += "# Generated by DAiW Lyrical Mirror\n"
    content += "# These are sparks, not finished lyrics.\n"
    content += "#" + "-" * 40 + "\n\n"

    for i, fragment in enumerate(fragments, 1):
        content += f"{i}. {fragment}\n\n"

    path.write_text(content, encoding="utf-8")
    return str(path)
