"""
Structure analysis module.
"""

from .chord import ChordAnalyzer, analyze_chords
from .sections import SectionDetector, detect_sections

# Progression analysis (consolidated from progression.py + progression_analysis.py)
from .progression_analysis import (
    ProgressionAnalyzer, analyze_progression,
    ChordDegree, ProgressionMatch, Mode,
    PROGRESSION_PATTERNS, match_progressions
)

# Backward compat alias
ProgressionMatcher = ProgressionAnalyzer
COMMON_PROGRESSIONS = PROGRESSION_PATTERNS

__all__ = [
    'ChordAnalyzer', 'analyze_chords',
    'SectionDetector', 'detect_sections',
    'ProgressionAnalyzer', 'ProgressionMatcher',
    'analyze_progression', 'match_progressions',
    'ChordDegree', 'ProgressionMatch', 'Mode',
    'PROGRESSION_PATTERNS', 'COMMON_PROGRESSIONS',
]
