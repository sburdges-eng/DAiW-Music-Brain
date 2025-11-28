"""
Progression - Backward Compatibility Shim
Import from progression_analysis instead.
"""

from .progression_analysis import (
    ProgressionAnalyzer as ProgressionMatcher,
    ProgressionAnalyzer,
    ProgressionMatch,
    match_progressions,
    analyze_progression,
    ChordDegree,
    Mode,
    PROGRESSION_PATTERNS,
)

# Alias for old interface
COMMON_PROGRESSIONS = PROGRESSION_PATTERNS

__all__ = [
    'ProgressionMatcher', 'ProgressionAnalyzer',
    'ProgressionMatch', 'match_progressions',
    'analyze_progression', 'ChordDegree', 'Mode',
    'PROGRESSION_PATTERNS', 'COMMON_PROGRESSIONS',
]
