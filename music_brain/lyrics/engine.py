# music_brain/lyrics/engine.py
"""
Lyric Mirror - Ghost Writer Engine

Uses Markov chains to remix user emotional input with a corpus,
generating lyrical fragments that reflect back unexpected connections.

Philosophy: The tool shouldn't finish art for people. It should make them braver.
"""
import markovify
import os
from pathlib import Path
import random

CORPUS_DIR = Path("./music_brain/data/corpus")


class LyricMirror:
    """
    Markov-based lyric fragment generator.

    Combines user emotional input with a text corpus to generate
    unexpected lyrical fragments - sparks, not finished lyrics.
    """

    def __init__(self):
        self.model = None
        self._ensure_corpus()
        self._build_model()

    def _ensure_corpus(self):
        """Ensure corpus directory exists with at least a default file."""
        CORPUS_DIR.mkdir(parents=True, exist_ok=True)
        default_file = CORPUS_DIR / "default.txt"
        if not default_file.exists():
            with open(default_file, "w") as f:
                f.write(
                    "The silence is a heavy door.\n"
                    "I found only static.\n"
                    "Broken glass reflects the sky.\n"
                )

    def _build_model(self):
        """Build Markov model from all corpus files."""
        text = ""
        for file in CORPUS_DIR.glob("*.txt"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    text += f.read() + "\n"
            except Exception:
                pass

        if len(text) < 50:
            text += "The machine breathes. I am static."
        self.model = markovify.NewlineText(text, state_size=1)

    def reflect(self, user_wound: str) -> list[str]:
        """
        Generate lyrical fragments from user emotional input.

        Args:
            user_wound: The user's emotional text/wound to reflect

        Returns:
            List of lyrical fragment strings
        """
        fragments = []

        # Method 1: Cut-up (Burroughs-style)
        words = user_wound.split()
        if len(words) > 3:
            random.shuffle(words)
            fragments.append(f"> {' '.join(words)}")

        # Method 2: Ghost Generation (Markov)
        for _ in range(3):
            try:
                sent = self.model.make_short_sentence(60, tries=10)
                if sent:
                    fragments.append(sent)
            except Exception:
                pass

        return fragments


def get_lyric_fragments(wound: str, mood: str = "") -> list[str]:
    """
    Convenience function to get lyric fragments from emotional input.

    Args:
        wound: The emotional text to reflect
        mood: Optional mood context (not yet used, for future expansion)

    Returns:
        List of lyrical fragment strings
    """
    return LyricMirror().reflect(wound)
