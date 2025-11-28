"""
Music Brain
A complete music production analysis and generation toolkit.

Modules:
- groove: Extract and apply groove/feel from MIDI, drum technique analysis
- structure: Chord, progression, and section analysis
- audio: Audio characteristics and mix fingerprinting
- session: Song generation and automation
- daw: DAW integration (Logic Pro)
- utils: MIDI I/O, PPQ handling, instrument classification, orchestral handling
"""

__version__ = '1.0.0'
__author__ = 'Sean'

# Groove
from .groove.extractor import GrooveExtractor, extract_groove
from .groove.applicator import GrooveApplicator, apply_groove
from .groove.pocket_rules import GENRE_POCKETS, get_pocket, list_genres
from .groove.templates import TemplateStorage, TemplateMerger
from .groove.drum_analysis import (
    DrumAnalyzer, analyze_drum_technique,
    DrumTechniqueProfile, SnareBounceSignature, HiHatAlternation
)

# Structure
from .structure.chord import ChordAnalyzer, analyze_chords
from .structure.progression import ProgressionMatcher, match_progressions
from .structure.sections import SectionDetector, detect_sections

# Session
from .session.generator import SongGenerator, generate_song

# DAW
from .daw.logic_pro import LogicProAutomation, create_logic_session

# Utils
from .utils.midi_io import load_midi, save_midi, MidiData, MidiNote
from .utils.ppq import STANDARD_PPQ, normalize_ticks, scale_ticks
from .utils.instruments import classify_note, get_drum_category
from .utils.orchestral import (
    OrchestralAnalyzer, validate_orchestral, is_orchestral_template
)

__all__ = [
    # Groove
    'GrooveExtractor', 'extract_groove',
    'GrooveApplicator', 'apply_groove',
    'GENRE_POCKETS', 'get_pocket', 'list_genres',
    'TemplateStorage', 'TemplateMerger',
    'DrumAnalyzer', 'analyze_drum_technique',
    'DrumTechniqueProfile', 'SnareBounceSignature', 'HiHatAlternation',
    
    # Structure
    'ChordAnalyzer', 'analyze_chords',
    'ProgressionMatcher', 'match_progressions',
    'SectionDetector', 'detect_sections',
    
    # Session
    'SongGenerator', 'generate_song',
    
    # DAW
    'LogicProAutomation', 'create_logic_session',
    
    # Utils
    'load_midi', 'save_midi', 'MidiData', 'MidiNote',
    'STANDARD_PPQ', 'normalize_ticks', 'scale_ticks',
    'classify_note', 'get_drum_category',
    'OrchestralAnalyzer', 'validate_orchestral', 'is_orchestral_template',
]
