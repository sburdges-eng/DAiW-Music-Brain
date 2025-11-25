"""
DAiW Lyric Mirror
=================
Uses Markov chains to remix the user's wound with a textual corpus.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

import markovify

CORPUS_DIR = Path("./music_brain/data/corpus")


class LyricMirror:
    def __init__(self) -> None:
        self.model: markovify.NewlineText | None = None
        self._ensure_corpus_dir()
        self._build_model()

    def _ensure_corpus_dir(self) -> None:
        CORPUS_DIR.mkdir(parents=True, exist_ok=True)
        default_file = CORPUS_DIR / "default.txt"
        if not default_file.exists():
            with open(default_file, "w", encoding="utf-8") as f:
                f.write("The silence is a heavy door.\n")
                f.write("I walked through the fire and found only static.\n")
                f.write("The machine hums a song of forgotten iron.\n")
                f.write("Broken glass reflects a sky that does not care.\n")
                f.write("We are wires crossed in the dark.\n")
                f.write("Tear it down to build a cage.\n")

    def _build_model(self) -> None:
        text = ""
        for file in CORPUS_DIR.glob("*.txt"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    text += f.read() + "\n"
            except Exception:
                # If a file is broken, ignore it instead of blowing up
                continue

        if len(text.strip()) < 50:
            text += "The void stares back. I am static. The machine breathes."

        self.model = markovify.NewlineText(text, state_size=1)

    def reflect(self, user_wound: str, mood: str) -> List[str]:
        """
        Returns a list of short lyric fragments based on the wound + corpus.
        """
        fragments: List[str] = []

        # Simple cut-up of user's own words
        words = user_wound.split()
        if len(words) > 3:
            import random

            random.shuffle(words)
            fragments.append("> " + " ".join(words))

        if self.model is None:
            return fragments

        # Ghost text from corpus
        for _ in range(4):
            try:
                sent = self.model.make_short_sentence(80, tries=10)
                if sent:
                    fragments.append(sent)
            except Exception:
                continue

        return fragments


_mirror = LyricMirror()


def get_lyric_fragments(wound: str, mood: str) -> List[str]:
    return _mirror.reflect(wound, mood)
