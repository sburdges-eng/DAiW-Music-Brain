"""
DAiW Lyric Mirror
=================
Uses Markov chains to remix the user's wound with a textual corpus.
"""

from __future__ import annotations

from pathlib import Path
from typing import List
import random

try:
    import markovify
    HAS_MARKOVIFY = True
except ImportError:
    HAS_MARKOVIFY = False

CORPUS_DIR = Path(__file__).parent.parent / "data" / "corpus"


class LyricMirror:
    def __init__(self) -> None:
        self.model = None
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
                f.write("I found you sleeping and the world stopped breathing.\n")
                f.write("Your hands were cold when I reached for you.\n")
                f.write("The pills on the nightstand told the whole story.\n")
                f.write("I keep checking if you're breathing.\n")
                f.write("Every bed looks like a crime scene now.\n")
                f.write("I didn't save you. I just found what was left.\n")
                f.write("The last voicemail I never listened to.\n")
                f.write("Static where your voice should be.\n")

    def _build_model(self) -> None:
        if not HAS_MARKOVIFY:
            return
            
        text = ""
        for file in CORPUS_DIR.glob("*.txt"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    text += f.read() + "\n"
            except Exception:
                continue

        if len(text.strip()) < 50:
            text += "The void stares back. I am static. The machine breathes."

        # state_size=1 keeps it broken/poetic
        try:
            self.model = markovify.NewlineText(text, state_size=1)
        except Exception:
            self.model = None

    def reflect(self, user_wound: str, mood: str) -> List[str]:
        """
        Returns a list of short lyric fragments based on wound + corpus.
        """
        fragments: List[str] = []

        mood = (mood or "").lower().strip()
        if mood:
            fragments.append(f"[{mood.upper()}]")

        # Simple cut-up of user's own words
        words = user_wound.split()
        if len(words) > 3:
            shuffled = words.copy()
            random.shuffle(shuffled)
            fragments.append("> " + " ".join(shuffled))

        if self.model is None:
            # Fallback without markovify
            fallback_lines = [
                "The silence is a heavy door.",
                "I walked through the fire and found only static.",
                "Broken glass reflects a sky that does not care.",
                "I found you sleeping and the world stopped breathing.",
            ]
            fragments.extend(random.sample(fallback_lines, min(3, len(fallback_lines))))
            return fragments

        # Intense moods get more lines
        if mood in {"rage", "defiance", "fear"}:
            num_lines = 6
        else:
            num_lines = 4

        for _ in range(num_lines):
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
