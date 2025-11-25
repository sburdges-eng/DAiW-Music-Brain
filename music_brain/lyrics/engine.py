# music_brain/lyrics/engine.py
"""
DAiW Lyric Mirror
=================
Uses Markov Chains to remix user intent with a stylistic corpus.
"""
import os
from pathlib import Path
from typing import List

import markovify

CORPUS_DIR = Path("./music_brain/data/corpus")


class LyricMirror:
    def __init__(self):
        self.model = None
        self._ensure_corpus_dir()
        self._build_model()

    def _ensure_corpus_dir(self):
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

    def _build_model(self):
        text = ""
        for file in CORPUS_DIR.glob("*.txt"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    text += f.read() + "\n"
            except Exception:
                continue

        if len(text) < 50:
            text += "The void stares back. I am static. The machine breathes.\n"

        self.model = markovify.NewlineText(text, state_size=1)

    def reflect(self, user_wound: str, mood: str = "") -> List[str]:
        fragments: List[str] = []

        # Simple cut-up of the user's words
        words = user_wound.split()
        if len(words) > 3:
            import random

            random.shuffle(words)
            fragments.append("> " + " ".join(words))

        # Generate short sentences
        for _ in range(4):
            try:
                sent = self.model.make_short_sentence(60, tries=10)
                if sent:
                    fragments.append(sent)
            except Exception:
                continue

        return fragments


mirror = LyricMirror()


def get_lyric_fragments(wound: str, mood: str = "") -> List[str]:
    return mirror.reflect(wound, mood)
