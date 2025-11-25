"""
Text Processing Module - Lyrical fragment generation.

Provides tools for generating lyrical sparks from therapy text
and genre corpora using Markov chains or simple cut-up techniques.
"""

from music_brain.text.lyrical_mirror import (
    generate_lyrical_fragments,
    simple_cutup,
)

__all__ = [
    "generate_lyrical_fragments",
    "simple_cutup",
]
