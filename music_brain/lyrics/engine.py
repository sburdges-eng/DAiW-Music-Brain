"""
Lyric Mirror Engine
===================

Markov-chain based lyrical fragment generator.
Reflects user input through a corpus of text to create
evocative, fragmented lyrics.

Philosophy: The mirror doesn't write for you.
It shows you what you might be trying to say.
"""

import random
from pathlib import Path
from typing import List, Optional

# Optional markovify import
try:
    import markovify
    HAS_MARKOVIFY = True
except ImportError:
    HAS_MARKOVIFY = False
    markovify = None

# Corpus location
CORPUS_DIR = Path(__file__).parent.parent / "data" / "corpus"

# Fallback corpus when no files exist
FALLBACK_CORPUS = """
The machine waits.
Static hums in the distance.
I am broken but still here.
The silence speaks louder.
Everything fades to grey.
We were beautiful once.
Now I am numb.
The walls close in.
I remember when we laughed.
Nothing feels real anymore.
The weight of it all.
I keep moving forward.
Through the fog I see light.
But I cannot reach it.
Time stops and starts.
My heart beats alone.
The echo of your voice.
I am lost in the noise.
Something has to change.
I refuse to disappear.
"""


class LyricMirror:
    """
    Reflects user phrases through a Markov model built from corpus text.

    Modes:
    - cut_up: Shuffles words from input
    - ghost: Generates new lines from corpus
    - echo: Repeats fragments with variation
    """

    def __init__(self, state_size: int = 1):
        """
        Initialize the mirror with corpus text.

        Args:
            state_size: Markov chain state size (1=chaotic, 2=coherent)
        """
        self.state_size = state_size
        self.model = None
        self._build_model()

    def _build_model(self) -> None:
        """Build or rebuild the Markov model from corpus files."""
        if not HAS_MARKOVIFY:
            self.model = None
            return

        text = ""

        # Try to load corpus files
        if CORPUS_DIR.exists():
            for txt_file in CORPUS_DIR.glob("*.txt"):
                try:
                    content = txt_file.read_text(encoding="utf-8")
                    text += content + "\n"
                except Exception:
                    pass

        # Use fallback if corpus is empty or too small
        if len(text.strip()) < 100:
            text = FALLBACK_CORPUS

        try:
            self.model = markovify.NewlineText(text, state_size=self.state_size)
        except Exception:
            self.model = None

    def reflect(self, phrase: str, num_lines: int = 4) -> List[str]:
        """
        Reflect a phrase through the mirror.

        Returns a mix of:
        - Cut-up of the input
        - Ghost lines from the corpus
        - Echoed fragments

        Args:
            phrase: User input text
            num_lines: Approximate number of lines to generate

        Returns:
            List of lyrical fragments
        """
        results: List[str] = []

        # 1. Cut-up mode: shuffle input words
        words = phrase.split()
        if len(words) > 3:
            shuffled = words.copy()
            random.shuffle(shuffled)
            results.append(f"> {' '.join(shuffled)}")

        # 2. Ghost mode: generate from model
        if self.model:
            for _ in range(num_lines):
                try:
                    line = self.model.make_short_sentence(60, tries=50)
                    if line:
                        results.append(line)
                except Exception:
                    pass

        # 3. Echo mode: repeat fragments with variation
        if len(words) >= 2:
            # Pick a fragment and repeat it
            frag_len = min(3, len(words))
            start = random.randint(0, max(0, len(words) - frag_len))
            fragment = " ".join(words[start:start + frag_len])
            results.append(f"({fragment})")

        # 4. Fallback: if nothing generated, use simple processing
        if len(results) < 2:
            results.append(f"...{phrase.lower()}...")
            if len(words) > 1:
                results.append(words[-1])

        return [r for r in results if r and r.strip()]

    def generate_line(self, max_chars: int = 60) -> Optional[str]:
        """Generate a single line from the model."""
        if not self.model:
            return random.choice(FALLBACK_CORPUS.strip().split("\n"))

        try:
            return self.model.make_short_sentence(max_chars, tries=50)
        except Exception:
            return None


# Module-level instance for convenience
_mirror: Optional[LyricMirror] = None


def get_lyric_fragments(phrase: str, num_lines: int = 4) -> List[str]:
    """
    Convenience function to get lyric fragments.

    Args:
        phrase: User input text
        num_lines: Number of lines to generate

    Returns:
        List of lyrical fragments
    """
    global _mirror
    if _mirror is None:
        _mirror = LyricMirror()

    return _mirror.reflect(phrase, num_lines)


def add_corpus_file(filepath: Path) -> bool:
    """
    Add a text file to the corpus directory.

    Args:
        filepath: Path to .txt file to add

    Returns:
        True if successful
    """
    global _mirror

    if not filepath.exists():
        return False

    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    target = CORPUS_DIR / filepath.name

    try:
        content = filepath.read_text(encoding="utf-8")
        target.write_text(content, encoding="utf-8")

        # Rebuild model
        _mirror = LyricMirror()
        return True
    except Exception:
        return False
