# CLAUDE.md - AI Assistant Guide for DAiW-Music-Brain

This document provides guidance for AI assistants working with the DAiW (Digital Audio Intelligent Workstation) codebase.

## Project Overview

**DAiW-Music-Brain** is a Python toolkit for music production intelligence that combines:
- Music analysis engine (MIDI/audio processing)
- Intent-based song generation with emotional grounding
- Groove extraction and application
- Chord and harmony analysis
- Interactive music theory teaching
- DAW integration utilities

**Philosophy: "Interrogate Before Generate"** — The tool shouldn't finish art for people; it should make them braver.

**Version:** 0.2.0 (Alpha)
**License:** MIT
**Python Support:** 3.9, 3.10, 3.11, 3.12

## Repository Structure

```
DAiW-Music-Brain/
├── music_brain/              # Core Python package
│   ├── __init__.py           # Package exports (v0.2.0)
│   ├── cli.py                # Command-line interface
│   ├── groove/               # Groove analysis & application
│   │   ├── extractor.py      # Extract timing/velocity patterns
│   │   ├── applicator.py     # Apply groove templates
│   │   └── templates.py      # 8 genre templates (funk, jazz, rock, etc.)
│   ├── structure/            # Harmonic analysis
│   │   ├── chord.py          # Chord detection & Roman numeral analysis
│   │   ├── progression.py    # Progression diagnosis & reharmonization
│   │   └── sections.py       # Song structure detection
│   ├── session/              # Intent-based generation (core innovation)
│   │   ├── intent_schema.py  # Three-phase intent system
│   │   ├── intent_processor.py # Rule-breaking execution
│   │   ├── interrogator.py   # Deep songwriting questions
│   │   ├── teaching.py       # Interactive theory lessons
│   │   └── generator.py      # Song structure generation
│   ├── audio/                # Audio analysis
│   │   └── feel.py           # Audio feature extraction
│   ├── utils/                # Utility functions
│   │   ├── midi_io.py        # MIDI file I/O
│   │   ├── instruments.py    # GM instrument/drum mappings
│   │   └── ppq.py            # PPQ normalization across DAWs
│   ├── daw/                  # DAW integration
│   │   └── logic.py          # Logic Pro project utilities
│   └── data/                 # Knowledge base (JSON/YAML)
│       ├── song_intent_schema.yaml
│       ├── song_intent_examples.json
│       ├── chord_progressions.json
│       └── genre_pocket_maps.json
├── vault/                    # Obsidian-compatible knowledge base
│   ├── Songwriting_Guides/   # Rule-breaking guides
│   ├── Theory_Reference/     # Music theory documentation
│   ├── Production_Workflows/ # DAW techniques
│   └── Templates/            # Task templates
├── tests/                    # Test suite
│   └── test_basic.py         # Import & feature tests
├── pyproject.toml            # Modern Python packaging config
├── setup.py                  # Legacy setuptools config
├── requirements.txt          # Core dependencies
└── README.md                 # Project documentation
```

## Development Commands

### Installation

```bash
# Development install
pip install -e .

# With audio analysis support
pip install -e .[audio]

# With advanced music theory
pip install -e .[theory]

# With all extras
pip install -e .[all]

# With dev tools
pip install -e .[dev]
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test class
pytest tests/test_basic.py::TestGrooveTemplates -v
```

### Code Quality

```bash
# Format code with Black (100 char line length)
black music_brain/

# Lint with flake8
flake8 music_brain/

# Type check with mypy
mypy music_brain/
```

### CLI Commands

The package exposes a `daiw` CLI:

```bash
# Groove operations
daiw extract <midi_file>           # Extract groove from MIDI
daiw apply --genre <genre> <midi>  # Apply genre template

# Chord analysis
daiw analyze --chords <midi>       # Analyze chords
daiw diagnose <progression>        # Diagnose harmonic issues
daiw reharm <progression> --style <s>  # Reharmonization

# Intent-based generation
daiw intent new [--title <t>]      # Create intent template
daiw intent process <file>         # Generate from intent
daiw intent suggest <emotion>      # Suggest rules to break
daiw intent list                   # List all rule-breaking options
daiw intent validate <file>        # Validate intent file

# Teaching
daiw teach <topic>                 # Interactive lessons
```

## Code Conventions

### Python Style

- **Line length:** 100 characters (Black formatter)
- **Type hints:** Required on all function signatures (Python 3.9+ compatible)
- **Docstrings:** Module-level and function-level with Args/Returns sections
- **Naming:**
  - `snake_case` for functions and variables
  - `PascalCase` for classes and enums
  - `UPPER_CASE` for module-level constants

### Data Structures

Heavy use of `@dataclass` for all data models:

```python
@dataclass
class GrooveTemplate:
    """Extracted groove pattern."""
    name: str = "Untitled Groove"
    ppq: int = 480
    swing_factor: float = 0.0
    timing_deviations: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Serialize to dictionary for JSON export."""
```

### Enum Usage

Rule-breaking categories and musical concepts use Enums:

```python
class HarmonyRuleBreak(Enum):
    AVOID_TONIC_RESOLUTION = "HARMONY_AvoidTonicResolution"
    MODAL_INTERCHANGE = "HARMONY_ModalInterchange"
```

### Optional Dependencies Pattern

Graceful handling of missing packages:

```python
try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False

def load_midi(path: str):
    if not MIDO_AVAILABLE:
        raise ImportError("mido package required")
```

### Module Organization

- All subpackages define `__all__` with public API
- Clean import paths: `from music_brain.groove import extract_groove`
- Package-level exports in `__init__.py`

## Key Concepts

### Three-Phase Intent System

The core innovation of DAiW is the intent-based approach to song generation:

**Phase 0: Core Wound/Desire**
- `core_event` — What happened?
- `core_resistance` — What holds you back from saying it?
- `core_longing` — What do you want to feel?
- `core_stakes` — What's at risk?
- `core_transformation` — How should you feel when done?

**Phase 1: Emotional Intent**
- `mood_primary` — Dominant emotion
- `mood_secondary_tension` — Internal conflict (0.0-1.0)
- `imagery_texture` — Visual/tactile quality
- `vulnerability_scale` — Emotional exposure level
- `narrative_arc` — Structural emotion pattern

**Phase 2: Technical Implementation**
- `technical_genre` — Genre/style
- `technical_key` — Musical key
- `technical_rule_to_break` — Intentional rule violation
- `rule_breaking_justification` — WHY break this rule

### Rule-Breaking Categories

The system supports 21 intentional rule breaks across 4 categories:

- **Harmony:** `HarmonyRuleBreak` (6 options)
- **Rhythm:** `RhythmRuleBreak` (5 options)
- **Arrangement:** `ArrangementRuleBreak` (5 options)
- **Production:** `ProductionRuleBreak` (5 options)

Each rule break requires emotional justification.

### Genre Groove Templates

Pre-defined templates available: funk, jazz, rock, hiphop, edm, latin, blues, bedroom_lofi

## Dependencies

**Core (required):**
- `mido>=1.2.10` — MIDI file I/O
- `numpy>=1.21.0` — Numerical operations

**Optional:**
- `librosa>=0.9.0` — Audio analysis
- `soundfile>=0.10.0` — Audio file I/O
- `music21>=7.0.0` — Advanced music theory

**Development:**
- `pytest>=7.0.0` — Testing
- `black>=22.0.0` — Code formatting
- `flake8>=4.0.0` — Linting
- `mypy>=0.900` — Type checking

## Testing Conventions

Tests are organized by feature area:

- `TestImports` — Module import verification
- `TestGrooveTemplates` — Groove functionality
- `TestChordParsing` — Chord/progression parsing
- `TestDiagnoseProgression` — Harmonic analysis
- `TestTeachingModule` — Teaching system
- `TestInterrogator` — Song interrogation
- `TestDataFiles` — Data file accessibility

Run tests before committing any changes.

## Important Files

| File | Purpose |
|------|---------|
| `music_brain/session/intent_schema.py` | Core intent system and rule-breaking enums |
| `music_brain/session/intent_processor.py` | Intent processing and music generation |
| `music_brain/groove/templates.py` | Genre groove templates |
| `music_brain/structure/progression.py` | Chord parsing and diagnosis |
| `music_brain/cli.py` | CLI entry point |
| `music_brain/data/song_intent_schema.yaml` | Schema specification |
| `music_brain/data/song_intent_examples.json` | Working intent examples |

## Common Tasks

### Adding a New Rule Break

1. Add enum value to appropriate class in `intent_schema.py`
2. Add effect description to `RULE_BREAKING_EFFECTS` dict
3. Update processing logic in `intent_processor.py`
4. Add documentation in `vault/Songwriting_Guides/`

### Adding a New Genre Template

1. Add template dict to `GENRE_TEMPLATES` in `groove/templates.py`
2. Include: name, swing_factor, tempo_range, timing_deviations, velocity_curve
3. Add to genre pocket maps in `data/genre_pocket_maps.json`

### Extending Chord Analysis

1. Modify `structure/chord.py` for detection logic
2. Update `structure/progression.py` for diagnosis
3. Add test cases to `tests/test_basic.py`

## Notes for AI Assistants

1. **Respect the philosophy:** This tool is about making musicians braver, not replacing creativity
2. **Emotional justification matters:** Rule-breaking must have a "why"
3. **Test changes:** Run `pytest tests/ -v` before suggesting commits
4. **Type safety:** Use type hints and run mypy
5. **Follow Black formatting:** 100 char line limit
6. **Data-driven design:** Large datasets go in `data/` as JSON/YAML
7. **Document changes:** Update docstrings and vault documentation as needed
