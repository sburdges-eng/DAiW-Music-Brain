"""
Groove module - extraction, application, and intelligent matching.

Core:
- extractor: Extract groove from MIDI
- applicator: Apply groove to MIDI
- auto_apply: Full automation pipeline

Data:
- genre_templates: Built-in templates and pocket offsets
- template_storage: Versioned template persistence

Analysis:
- drum_analysis: Advanced drum technique analysis
- feel_matching: Intelligent template selection
"""

# Core
from .extractor import GrooveExtractor, extract_groove, GrooveTemplate
from .applicator import GrooveApplicator, apply_groove, ApplicationStats

# Templates (consolidated)
from .genre_templates import (
    GENRE_TEMPLATES, get_genre_template, list_genres,
    validate_template, POCKET_OFFSETS,
    get_pocket, get_push_pull, get_swing,
)
from .template_storage import (
    TemplateStore, TemplateMerger, get_store, TemplateMetadata
)

# Backward compat aliases
TemplateStorage = TemplateStore
get_storage = get_store
GENRE_POCKETS = POCKET_OFFSETS

# Feel matching
from .feel_matching import (
    TemplateMatcher, FeelProfile, TemplateScore,
    SectionGrooveMap, InstrumentVelocityPattern,
    EnergyLevel, SwingFeel,
    match_audio_to_template, rank_templates_for_audio,
    get_section_aware_grooves, get_instrument_velocity_pattern,
    INSTRUMENT_VELOCITY_PATTERNS, SECTION_MODIFIERS
)

# Auto-apply pipeline
from .auto_apply import (
    AutoGrooveApplicator, AutoApplicationConfig, AutoApplicationResult,
    auto_apply_groove, preview_template_match, get_section_grooves
)

# Drum analysis
from .drum_analysis import (
    DrumAnalyzer, analyze_drum_technique,
    DrumTechniqueProfile, SnareBounceSignature, HiHatAlternation
)

__all__ = [
    # Core
    'GrooveExtractor', 'extract_groove', 'GrooveTemplate',
    'GrooveApplicator', 'apply_groove', 'ApplicationStats',
    
    # Templates
    'GENRE_TEMPLATES', 'get_genre_template', 'list_genres',
    'validate_template', 'POCKET_OFFSETS', 'GENRE_POCKETS',
    'get_pocket', 'get_push_pull', 'get_swing',
    'TemplateStore', 'TemplateStorage', 'TemplateMerger',
    'get_store', 'get_storage', 'TemplateMetadata',
    
    # Feel matching
    'TemplateMatcher', 'FeelProfile', 'TemplateScore',
    'SectionGrooveMap', 'InstrumentVelocityPattern',
    'EnergyLevel', 'SwingFeel',
    'match_audio_to_template', 'rank_templates_for_audio',
    'get_section_aware_grooves', 'get_instrument_velocity_pattern',
    'INSTRUMENT_VELOCITY_PATTERNS', 'SECTION_MODIFIERS',
    
    # Auto-apply
    'AutoGrooveApplicator', 'AutoApplicationConfig', 'AutoApplicationResult',
    'auto_apply_groove', 'preview_template_match', 'get_section_grooves',
    
    # Drum analysis
    'DrumAnalyzer', 'analyze_drum_technique',
    'DrumTechniqueProfile', 'SnareBounceSignature', 'HiHatAlternation',
]
