# CLAUDE.md - AI Assistant Guide for DAiW-Music-Brain

> This document provides AI assistants with essential context for working with the DAiW (Digital Audio intelligent Workstation) codebase.

## Project Philosophy

**"Interrogate Before Generate"** - The tool shouldn't finish art for people. It should make them braver.

This is a Python toolkit for music production intelligence. The core philosophy is that emotional/creative intent should drive technical decisions, not the other way around. The three-phase "Song Intent Schema" ensures artists explore what they *need* to say before choosing technical parameters.

---

## Project Overview

DAiW-Music-Brain is a CLI toolkit and Python library for:
- **Groove extraction & humanization** - Extract timing/velocity patterns from MIDI, apply genre templates, humanize drum tracks
- **Chord & harmony analysis** - Roman numeral analysis, key detection, borrowed chord identification
- **Intent-based song generation** - Three-phase deep interrogation system for emotionally-driven composition
- **Comprehensive therapy-to-MIDI pipeline** - AffectAnalyzer, TherapySession, HarmonyPlan generation
- **Lyrical fragment generation** - Cut-up/Markov engine for creative sparks
- **Reference track DNA analysis** - Learn tempo, key, brightness from reference audio
- **Dynamic tension curves** - Make songs "breathe" with verse/chorus energy arcs
- **DAW marker export** - Timeline markers reflecting emotional structure
- **Intentional rule-breaking** - Structured approach to breaking music theory "rules" for emotional effect
- **Interactive teaching** - Lessons on production philosophy and music theory concepts

---

## Directory Structure

```
DAiW-Music-Brain/
├── music_brain/              # Main Python package (v0.3.0)
│   ├── __init__.py          # Package exports
│   ├── cli.py               # CLI entry point (`daiw` command)
│   ├── groove_engine.py     # Event-based groove humanization
│   ├── data/                # JSON/YAML data files
│   │   ├── chord_progressions.json
│   │   ├── genre_pocket_maps.json    # Genre timing characteristics
│   │   ├── humanize_presets.json     # Humanization preset settings
│   │   ├── song_intent_examples.json
│   │   └── song_intent_schema.yaml
│   ├── groove/              # Groove extraction & application
│   │   ├── extractor.py     # extract_groove(), GrooveTemplate
│   │   ├── applicator.py    # apply_groove()
│   │   ├── groove_engine.py # Event-based humanization
│   │   └── templates.py     # Genre templates (funk, jazz, rock, etc.)
│   ├── structure/           # Harmonic analysis & generation
│   │   ├── chord.py         # Chord, ChordProgression, CHORD_QUALITIES
│   │   ├── progression.py   # diagnose_progression(), parse_progression_string()
│   │   ├── sections.py      # Section detection
│   │   ├── comprehensive_engine.py  # AffectAnalyzer, TherapySession, HarmonyPlan
│   │   └── tension_curve.py # Dynamic tension curves (verse_chorus, slow_build, etc.)
│   ├── session/             # Intent schema & teaching
│   │   ├── intent_schema.py # CompleteSongIntent, rule-breaking enums
│   │   ├── intent_processor.py # process_intent(), IntentProcessor
│   │   ├── teaching.py      # RuleBreakingTeacher
│   │   ├── interrogator.py  # SongInterrogator
│   │   └── generator.py     # Generation utilities
│   ├── text/                # Lyrical generation
│   │   └── lyrical_mirror.py # generate_lyrical_fragments(), simple_cutup()
│   ├── audio/               # Audio analysis
│   │   ├── feel.py          # analyze_feel(), AudioFeatures
│   │   └── reference_dna.py # ReferenceProfile, analyze_reference()
│   ├── utils/               # Utilities
│   │   ├── midi_io.py       # MIDI file handling
│   │   ├── instruments.py   # Instrument mappings
│   │   └── ppq.py           # PPQ normalization
│   └── daw/                 # DAW integration
│       ├── logic.py         # LogicProject, LOGIC_CHANNELS
│       └── markers.py       # MarkerEvent, export_markers_midi()
├── vault/                   # Knowledge base (Obsidian-compatible)
│   ├── README.md
│   ├── Songwriting_Guides/  # Intent schema docs, rule-breaking guides
│   └── Templates/           # Task boards and templates
├── tests/                   # Comprehensive test suite
│   ├── test_basic.py        # Core import and function tests
│   ├── test_comprehensive_engine.py  # Therapy pipeline tests
│   ├── test_groove_engine.py    # Humanization tests
│   ├── test_groove_extractor.py # Groove extraction tests
│   ├── test_intent_schema.py    # Intent schema tests
│   ├── test_intent_processor.py # Intent processing tests
│   ├── test_midi_io.py          # MIDI I/O tests
│   ├── test_cli_commands.py     # CLI command tests
│   ├── test_cli_flow.py         # CLI workflow tests
│   ├── test_daw_integration.py  # DAW export tests
│   ├── test_bridge_integration.py # Bridge integration tests
│   └── test_error_paths.py      # Error handling tests
├── emotion_thesaurus.py     # 6×6×6 emotion taxonomy interface
├── *.json                   # Emotion thesaurus data files
│   ├── angry.json, sad.json, happy.json, fear.json
│   ├── surprise.json, disgust.json, blends.json
│   └── metadata.json
├── app.py                   # Streamlit UI application
├── launcher.py              # Native desktop app launcher (pywebview)
├── daiw.spec                # PyInstaller build configuration
├── pyproject.toml           # Package configuration
├── setup.py                 # Legacy setup
└── requirements.txt         # Core dependencies
```

---

## Key Concepts

### The Three-Phase Intent Schema

1. **Phase 0: Core Wound/Desire** - Deep interrogation
   - `core_event` - What happened?
   - `core_resistance` - What holds you back from saying it?
   - `core_longing` - What do you want to feel?
   - `core_stakes` - What's at risk?
   - `core_transformation` - How should you feel when done?

2. **Phase 1: Emotional Intent** - Validated by Phase 0
   - `mood_primary` - Dominant emotion
   - `mood_secondary_tension` - Internal conflict (0.0-1.0)
   - `vulnerability_scale` - Low/Medium/High
   - `narrative_arc` - Climb-to-Climax, Slow Reveal, Repetitive Despair, etc.

3. **Phase 2: Technical Constraints** - Implementation
   - `technical_genre`, `technical_key`, `technical_mode`
   - `technical_rule_to_break` - Intentional rule violation
   - `rule_breaking_justification` - WHY break this rule (required!)

### Comprehensive Engine Pipeline

The comprehensive engine (`comprehensive_engine.py`) integrates everything into a single production pipeline:

```
Text Input → AffectAnalyzer → AffectResult (primary/secondary emotions, intensity)
                ↓
          TherapySession → TherapyState (scales, mode suggestions)
                ↓
          generate_plan() → HarmonyPlan (tempo, mode, chords, length)
                ↓
      render_plan_to_midi() → MIDI File (using LogicProject)
```

Key classes:
- `AffectAnalyzer` - Analyzes text for emotional content using weighted keywords
- `TherapySession` - Manages therapy state and generates harmony plans
- `HarmonyPlan` - Complete blueprint for generation (root, mode, tempo, chords)
- `NoteEvent` - Canonical note representation for MIDI/DAW interop

### Rule-Breaking Categories

Rules are broken **intentionally** based on emotional justification:

| Category | Examples | Effect |
|----------|----------|--------|
| **Harmony** | `HARMONY_AvoidTonicResolution`, `HARMONY_ModalInterchange` | Unresolved yearning, bittersweet color |
| **Rhythm** | `RHYTHM_ConstantDisplacement`, `RHYTHM_TempoFluctuation` | Anxiety, organic breathing |
| **Arrangement** | `ARRANGEMENT_BuriedVocals`, `ARRANGEMENT_ExtremeDynamicRange` | Dissociation, dramatic impact |
| **Production** | `PRODUCTION_PitchImperfection`, `PRODUCTION_ExcessiveMud` | Emotional honesty, claustrophobia |

### Tension Curves

Preset tension curves for song dynamics (`tension_curve.py`):

| Curve | Pattern | Use Case |
|-------|---------|----------|
| `verse_chorus` | Low-Low-High-High-Low-High-High-Out | Standard pop structure |
| `slow_build` | Gradual increase to climax | Ambient, post-rock |
| `catharsis` | Build to massive release | Emotional climax |
| `descent` | Falling energy | Sadness, resignation |
| `spiral` | Escalating chaos | Tension, anxiety |
| `static` | Minimal variation | Hypnotic, trance |

---

## Development Setup

### Installation
```bash
# Clone and install as editable package
git clone https://github.com/yourusername/DAiW-Music-Brain.git
cd DAiW-Music-Brain
pip install -e .

# With optional dependencies
pip install -e ".[dev]"      # pytest, black, flake8, mypy
pip install -e ".[audio]"    # librosa, soundfile
pip install -e ".[theory]"   # music21
pip install -e ".[ui]"       # streamlit (web UI only)
pip install -e ".[desktop]"  # streamlit + pywebview (native app)
pip install -e ".[build]"    # + pyinstaller (build executables)
pip install -e ".[all]"      # Everything
```

### Dependencies
- **Core**: `mido>=1.2.10`, `numpy>=1.21.0`
- **Dev**: `pytest>=7.0.0`, `black>=22.0.0`, `flake8>=4.0.0`, `mypy>=0.900`
- **UI**: `streamlit>=1.28.0`
- **Desktop**: `streamlit`, `pywebview>=4.0.0`
- **Build**: `pyinstaller>=6.0.0`
- **Optional**: `librosa`, `soundfile`, `music21`, `markovify` (for lyrical generation)

### Python Version
- Requires Python 3.9+
- Tested on 3.9, 3.10, 3.11, 3.12

---

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_comprehensive_engine.py -v

# Run specific test class
pytest tests/test_basic.py::TestImports -v
```

### Test Coverage Areas
- `test_basic.py` - Core imports, groove templates, chord parsing
- `test_comprehensive_engine.py` - AffectAnalyzer, TherapySession, HarmonyPlan
- `test_groove_engine.py` - Humanization, swing, pocket functions
- `test_intent_schema.py` - Intent validation, serialization
- `test_intent_processor.py` - Intent processing pipeline
- `test_midi_io.py` - MIDI file read/write
- `test_cli_commands.py` - CLI command execution
- `test_daw_integration.py` - DAW export functionality
- `test_error_paths.py` - Error handling and edge cases

---

## CLI Usage

The package installs a `daiw` command:

```bash
# Groove operations
daiw extract drums.mid                    # Extract groove from MIDI
daiw apply --genre funk track.mid         # Apply genre groove template

# Humanization (Drunken Drummer)
daiw humanize drums.mid                   # Apply natural humanization
daiw humanize drums.mid --style tight     # Minimal drift, confident
daiw humanize drums.mid --style loose     # Relaxed, laid back
daiw humanize drums.mid --style drunk     # Maximum chaos, fragile

# Chord analysis
daiw analyze --chords song.mid            # Analyze chord progression
daiw diagnose "F-C-Am-Dm"                 # Diagnose harmonic issues
daiw reharm "F-C-Am-Dm" --style jazz      # Generate reharmonizations

# Intent-based generation
daiw intent new --title "My Song"         # Create intent template
daiw intent process my_intent.json        # Generate from intent
daiw intent suggest grief                 # Suggest rules to break
daiw intent list                          # List all rule-breaking options
daiw intent validate my_intent.json       # Validate intent file

# Teaching
daiw teach rulebreaking                   # Interactive teaching mode
```

### Humanization Styles
| Style | Complexity | Vulnerability | Feel |
|-------|------------|---------------|------|
| `tight` | 0.1 | 0.2 | Minimal drift, confident |
| `natural` | 0.4 | 0.5 | Human feel, balanced |
| `loose` | 0.6 | 0.6 | Relaxed, laid back |
| `drunk` | 0.9 | 0.8 | Maximum chaos, fragile |

---

## Desktop Application

DAiW includes a native desktop application that provides a graphical interface without requiring a browser.

### Running the UI

```bash
# Option 1: Streamlit in browser (development)
streamlit run app.py

# Option 2: Native window (requires pywebview)
python launcher.py

# Option 3: After building executable
./dist/DAiW/DAiW        # Linux
./dist/DAiW/DAiW.exe    # Windows
open dist/DAiW.app      # macOS
```

### Building Standalone Executable

```bash
# Install build dependencies
pip install -e ".[build]"

# Build the application
pyinstaller daiw.spec --clean --noconfirm

# Output location
# Linux/Windows: dist/DAiW/DAiW (or DAiW.exe)
# macOS: dist/DAiW.app
```

---

## Code Style & Conventions

### Formatting
- **Line length**: 100 characters (configured in `pyproject.toml`)
- **Formatter**: black
- **Linter**: flake8, mypy

```bash
# Format code
black music_brain/ tests/

# Type check
mypy music_brain/

# Lint
flake8 music_brain/ tests/
```

### Code Patterns

1. **Lazy imports in CLI** (`cli.py`)
   - Heavy modules are imported lazily to speed up CLI startup
   - Use `get_*_module()` functions for deferred imports

2. **Data classes for structured data**
   - `CompleteSongIntent`, `SongRoot`, `SongIntent`, `TechnicalConstraints`
   - `AffectResult`, `TherapyState`, `HarmonyPlan`, `NoteEvent`
   - `ReferenceProfile`, `TensionProfile`, `MarkerEvent`
   - Support serialization via `to_dict()` / `from_dict()` / `save()` / `load()`

3. **Graceful degradation**
   - Optional dependencies checked at runtime (librosa, markovify, music21)
   - Functions degrade gracefully when dependencies missing
   - Example: `if not LIBROSA_AVAILABLE: return None`

4. **Enums for categorical values**
   - `HarmonyRuleBreak`, `RhythmRuleBreak`, `ArrangementRuleBreak`, `ProductionRuleBreak`
   - `VulnerabilityScale`, `NarrativeArc`, `CoreStakes`, `GrooveFeel`

5. **Module-level exports in `__init__.py`**
   - Each subpackage exports its public API via `__all__`

---

## Key Files to Understand

### Entry Points
- `music_brain/cli.py` - CLI implementation, all commands
- `music_brain/__init__.py` - Public API exports

### Core Logic
- `music_brain/session/intent_schema.py` - The heart of the intent system
- `music_brain/session/intent_processor.py` - Converts intent to musical elements
- `music_brain/structure/comprehensive_engine.py` - Therapy-to-MIDI pipeline
- `music_brain/groove/templates.py` - Genre groove definitions
- `music_brain/structure/progression.py` - Chord parsing and diagnosis

### Humanization
- `music_brain/groove_engine.py` - Core humanization functions
- `music_brain/structure/tension_curve.py` - Dynamic tension curves
- `music_brain/data/humanize_presets.json` - Preset configurations

### Text & Lyrical
- `music_brain/text/lyrical_mirror.py` - Cut-up/Markov lyric generation
- `emotion_thesaurus.py` - 6×6×6 emotion taxonomy interface

### Audio Analysis
- `music_brain/audio/feel.py` - Audio feature extraction
- `music_brain/audio/reference_dna.py` - Reference track analysis

### DAW Integration
- `music_brain/daw/logic.py` - LogicProject MIDI export
- `music_brain/daw/markers.py` - Timeline marker export

### Data Files
- `music_brain/data/genre_pocket_maps.json` - Genre timing characteristics
- `music_brain/data/song_intent_schema.yaml` - Schema definition
- `music_brain/data/chord_progressions.json` - Common progressions
- `music_brain/data/humanize_presets.json` - Humanization presets

---

## Public API

The main package exports these key functions and classes:

```python
from music_brain import (
    # Groove (file-based)
    extract_groove,
    apply_groove,
    GrooveTemplate,

    # Groove (event-based)
    apply_groove_events,

    # Structure
    analyze_chords,
    detect_sections,
    ChordProgression,

    # Audio
    analyze_feel,
    AudioFeatures,

    # Comprehensive Engine
    AffectAnalyzer,
    TherapySession,
    HarmonyPlan,
    render_plan_to_midi,

    # Text/Lyrical
    generate_lyrical_fragments,
)
```

---

## Working with This Codebase

### When Adding Features
1. Consider the "Interrogate Before Generate" philosophy
2. Rule-breaking should always have emotional justification
3. Add tests in appropriate `tests/test_*.py` file
4. Update `__all__` exports if adding public API
5. Keep CLI startup fast (use lazy imports)
6. Add graceful degradation for optional dependencies

### When Modifying Intent Schema
1. Update both `intent_schema.py` and `song_intent_schema.yaml`
2. Ensure `to_dict()` / `from_dict()` handle new fields
3. Add validation in `validate_intent()`
4. Update vault documentation in `vault/Songwriting_Guides/`

### When Adding Rule-Breaking Options
1. Add enum value in appropriate class (`HarmonyRuleBreak`, etc.)
2. Add entry in `RULE_BREAKING_EFFECTS` dict
3. Implement processor function in `intent_processor.py`
4. Update CLI help text if needed

### When Adding Tension Curves
1. Add preset to `TENSION_CURVES` dict in `tension_curve.py`
2. Document the emotional use case
3. Add test coverage

### Data Flow
```
User Input → CompleteSongIntent → IntentProcessor → Generated Elements
                                                    ├── GeneratedProgression
                                                    ├── GeneratedGroove
                                                    ├── GeneratedArrangement
                                                    └── GeneratedProduction

Therapy Text → AffectAnalyzer → AffectResult → TherapySession
                                                     ↓
                                              HarmonyPlan → render_plan_to_midi() → MIDI
```

---

## Important Design Decisions

1. **Emotional intent drives technical choices** - Never generate without understanding the "why"

2. **Rules are broken intentionally** - Every rule break requires justification

3. **Human imperfection is valued** - Lo-fi, pitch drift, room noise are features, not bugs

4. **Phase 0 must come first** - Technical decisions (Phase 2) can't be made without emotional clarity (Phase 0)

5. **Teaching over finishing** - The tool should educate and empower, not just generate

6. **Graceful degradation** - Features work without optional dependencies, just with reduced capability

7. **Event-based processing** - NoteEvent is the canonical format for MIDI interop

---

## Common Tasks

### Creating a new groove genre template
1. Add entry to `music_brain/data/genre_pocket_maps.json`
2. Add template in `music_brain/groove/templates.py`
3. Add to CLI choices in `cli.py`

### Adding a new teaching topic
1. Add content in `music_brain/session/teaching.py`
2. Add to `valid_topics` list in `cmd_teach()`

### Extending intent validation
1. Add validation logic in `validate_intent()` in `intent_schema.py`
2. Consider consistency checks between phases

### Adding a humanization preset
1. Add entry to `music_brain/data/humanize_presets.json`
2. Test with `daiw humanize --preset <name>`

### Adding emotional markers
1. Use `get_emotional_structure()` from `markers.py`
2. Customize `mood_labels` dict for new moods
3. Export with `export_markers_midi()`

---

## Emotion Thesaurus

The emotion thesaurus provides a 6×6×6 taxonomy for music therapy integration:

```python
from emotion_thesaurus import EmotionThesaurus

thesaurus = EmotionThesaurus()

# Find emotions by synonym
matches = thesaurus.find_by_synonym("melancholy")

# Get intensity synonyms
synonyms = thesaurus.get_intensity_synonyms("SAD", "GRIEF", "bereaved", tier=4)

# Find emotional blends
blend = thesaurus.find_blend("guilt")
```

Data files: `angry.json`, `sad.json`, `happy.json`, `fear.json`, `surprise.json`, `disgust.json`, `blends.json`

---

## Troubleshooting

### Import errors
- Ensure package is installed: `pip install -e .`
- Check Python version: `python --version` (requires 3.9+)

### MIDI file issues
- Verify mido is installed: `pip install mido`
- Check file exists and is valid MIDI

### Optional features not working
- Audio analysis: `pip install librosa soundfile`
- Lyrical generation: `pip install markovify`
- Music theory: `pip install music21`

### Test failures
- Run with verbose: `pytest -v`
- Check data files exist in `music_brain/data/`

---

## Meta Principle

> "The audience doesn't hear 'borrowed from Dorian.' They hear 'that part made me cry.'"

When working on this codebase, remember: the technical implementation serves the emotional expression, never the other way around.
