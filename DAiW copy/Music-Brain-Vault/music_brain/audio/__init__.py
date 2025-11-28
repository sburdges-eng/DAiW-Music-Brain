"""
Audio analysis module.

- analyzer: Structured analysis with dataclasses (new)
- feel: Legacy analysis with database support
"""

# New structured analyzer
try:
    from .analyzer import (
        AudioAnalyzer, analyze_audio_feel, quick_analyze,
        AudioFeel, OnsetInfo, SpectralInfo, DynamicInfo, RhythmInfo
    )
    HAS_NEW_ANALYZER = True
except ImportError:
    HAS_NEW_ANALYZER = False
    analyze_audio_feel = None

# Legacy analyzer (has database/CLI features)
from .feel import analyze_audio_feel as analyze_feel_legacy

# Use new analyzer if available, else legacy
if not HAS_NEW_ANALYZER:
    analyze_audio_feel = analyze_feel_legacy

__all__ = [
    'analyze_audio_feel', 'analyze_feel_legacy',
    'AudioAnalyzer', 'quick_analyze',
    'AudioFeel', 'OnsetInfo', 'SpectralInfo', 'DynamicInfo', 'RhythmInfo',
]
