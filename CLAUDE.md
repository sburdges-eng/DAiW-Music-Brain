# CLAUDE.md - AI Assistant Guide for DAiW-Music-Brain

> This document provides AI assistants with essential context for working with the DAiW (Digital Audio intelligent Workstation) codebase.

## Project Philosophy

**"Interrogate Before Generate"** - The tool shouldn't finish art for people. It should make them braver.

This is a Python toolkit for music production intelligence. The core philosophy is that emotional/creative intent should drive technical decisions, not the other way around. The three-phase "Song Intent Schema" ensures artists explore what they *need* to say before choosing technical parameters.

---

## Project Overview

DAiW-Music-Brain is a CLI toolkit and Python library for:
- **Groove extraction & application** - Extract timing/velocity patterns from MIDI, apply genre templates
- **Chord & harmony analysis** - Roman numeral analysis, key detection, borrowed chord identification
- **Intent-based song generation** - Three-phase deep interrogation system for emotionally-driven composition
- **Intentional rule-breaking** - Structured approach to breaking music theory "rules" for emotional effect
- **Interactive teaching** - Lessons on production philosophy and music theory concepts

---

## Directory Structure

```
DAiW-Music-Brain/
├── music_brain/              # Main Python package
│   ├── __init__.py          # Package exports (v0.2.0)
│   ├── cli.py               # CLI entry point (`daiw` command)
│   ├── data/                # JSON/YAML data files
│   │   ├── chord_progressions.json
│   │   ├── genre_pocket_maps.json    # Genre timing characteristics
│   │   ├── song_intent_examples.json
│   │   └── song_intent_schema.yaml
│   ├── groove/              # Groove extraction & application
│   │   ├── extractor.py     # extract_groove(), GrooveTemplate
│   │   ├── applicator.py    # apply_groove()
│   │   └── templates.py     # Genre templates (funk, jazz, rock, etc.)
│   ├── structure/           # Harmonic analysis
│   │   ├── chord.py         # Chord, ChordProgression, analyze_chords()
│   │   ├── progression.py   # diagnose_progression(), generate_reharmonizations()
│   │   └── sections.py      # Section detection
│   ├── session/             # Intent schema & teaching
│   │   ├── intent_schema.py # CompleteSongIntent, rule-breaking enums
│   │   ├── intent_processor.py # process_intent(), IntentProcessor
│   │   ├── teaching.py      # RuleBreakingTeacher
│   │   ├── interrogator.py  # SongInterrogator
│   │   └── generator.py     # Generation utilities
│   ├── audio/               # Audio feel analysis
│   │   └── feel.py          # analyze_feel(), AudioFeatures
│   ├── utils/               # Utilities
│   │   ├── midi_io.py       # MIDI file handling
│   │   ├── instruments.py   # Instrument mappings
│   │   └── ppq.py           # PPQ normalization
│   └── daw/                 # DAW integration
│       └── logic.py         # Logic Pro integration
├── vault/                   # Knowledge base (Obsidian-compatible)
│   ├── Songwriting_Guides/
│   │   ├── song_intent_schema.md     # Intent schema documentation
│   │   ├── rule_breaking_practical.md
│   │   └── rule_breaking_masterpieces.md
│   ├── Templates/
│   ├── Theory_Reference/
│   ├── Production_Workflows/
│   └── Data_Files/
├── tests/                   # Test suite
│   └── test_basic.py        # Pytest tests
├── examples/                # Example files
│   └── midi/                # Example MIDI files
├── docs/                    # Documentation
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

### Rule-Breaking Categories

Rules are broken **intentionally** based on emotional justification:

| Category | Examples | Effect |
|----------|----------|--------|
| **Harmony** | `HARMONY_AvoidTonicResolution`, `HARMONY_ModalInterchange` | Unresolved yearning, bittersweet color |
| **Rhythm** | `RHYTHM_ConstantDisplacement`, `RHYTHM_TempoFluctuation` | Anxiety, organic breathing |
| **Arrangement** | `ARRANGEMENT_BuriedVocals`, `ARRANGEMENT_ExtremeDynamicRange` | Dissociation, dramatic impact |
| **Production** | `PRODUCTION_PitchImperfection`, `PRODUCTION_ExcessiveMud` | Emotional honesty, claustrophobia |

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
- **Optional**: `librosa`, `soundfile`, `music21`

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

# Run specific test class
pytest tests/test_basic.py::TestImports -v
```

### Test Categories in `test_basic.py`
- `TestImports` - Verify all modules can be imported
- `TestGrooveTemplates` - Genre template functionality
- `TestChordParsing` - Chord string parsing
- `TestDiagnoseProgression` - Harmonic diagnosis
- `TestTeachingModule` - Teaching/lesson functionality
- `TestInterrogator` - Song interrogation system
- `TestDataFiles` - Data file accessibility

---

## CLI Usage

The package installs a `daiw` command:

```bash
# Groove operations
daiw extract drums.mid                    # Extract groove from MIDI
daiw apply --genre funk track.mid         # Apply genre groove template

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

### Desktop Architecture

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI - the actual interface |
| `launcher.py` | Native window wrapper using pywebview |
| `daiw.spec` | PyInstaller configuration for building executables |

The launcher:
1. Finds a free port
2. Starts Streamlit server in background
3. Opens a native window (no browser chrome)
4. Cleans up server when window closes

### Troubleshooting Builds

If the built app opens and immediately closes:
1. Edit `daiw.spec`: change `console=False` to `console=True`
2. Rebuild: `pyinstaller daiw.spec --clean --noconfirm`
3. Run from terminal to see error messages
4. Add missing modules to `hiddenimports` list in spec file

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

2. **Data classes for structured data** (`intent_schema.py`)
   - `CompleteSongIntent`, `SongRoot`, `SongIntent`, `TechnicalConstraints`
   - Support serialization via `to_dict()` / `from_dict()` / `save()` / `load()`

3. **Enums for categorical values**
   - `HarmonyRuleBreak`, `RhythmRuleBreak`, `ArrangementRuleBreak`, `ProductionRuleBreak`
   - `VulnerabilityScale`, `NarrativeArc`, `CoreStakes`, `GrooveFeel`

4. **Module-level exports in `__init__.py`**
   - Each subpackage exports its public API via `__all__`

---

## Key Files to Understand

### Entry Points
- `music_brain/cli.py` - CLI implementation, all commands
- `music_brain/__init__.py` - Public API exports

### Core Logic
- `music_brain/session/intent_schema.py` - The heart of the intent system
- `music_brain/session/intent_processor.py` - Converts intent to musical elements
- `music_brain/groove/templates.py` - Genre groove definitions
- `music_brain/structure/progression.py` - Chord parsing and diagnosis

### Data Files
- `music_brain/data/genre_pocket_maps.json` - Genre timing characteristics
- `music_brain/data/song_intent_schema.yaml` - Schema definition
- `music_brain/data/chord_progressions.json` - Common progressions

---

## Working with This Codebase

### When Adding Features
1. Consider the "Interrogate Before Generate" philosophy
2. Rule-breaking should always have emotional justification
3. Add tests for new functionality in `tests/test_basic.py`
4. Update `__all__` exports if adding public API
5. Keep CLI startup fast (use lazy imports)

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

### Data Flow
```
User Input → CompleteSongIntent → IntentProcessor → Generated Elements
                                                    ├── GeneratedProgression
                                                    ├── GeneratedGroove
                                                    ├── GeneratedArrangement
                                                    └── GeneratedProduction
```

---

## Important Design Decisions

1. **Emotional intent drives technical choices** - Never generate without understanding the "why"

2. **Rules are broken intentionally** - Every rule break requires justification

3. **Human imperfection is valued** - Lo-fi, pitch drift, room noise are features, not bugs

4. **Phase 0 must come first** - Technical decisions (Phase 2) can't be made without emotional clarity (Phase 0)

5. **Teaching over finishing** - The tool should educate and empower, not just generate

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

---

## Vault (Knowledge Base)

The `vault/` directory is an Obsidian-compatible knowledge base containing:
- **Songwriting_Guides/** - Intent schema docs, rule-breaking guides
- **Theory_Reference/** - Music theory reference materials
- **Production_Workflows/** - Production technique guides
- **Templates/** - Task boards and templates
- **Data_Files/** - Supporting data

These markdown files use Obsidian-style `[[wiki links]]` for cross-referencing.

---

## Troubleshooting

### Import errors
- Ensure package is installed: `pip install -e .`
- Check Python version: `python --version` (requires 3.9+)

### MIDI file issues
- Verify mido is installed: `pip install mido`
- Check file exists and is valid MIDI

### Test failures
- Run with verbose: `pytest -v`
- Check data files exist in `music_brain/data/`

---

## Meta Principle

> "The audience doesn't hear 'borrowed from Dorian.' They hear 'that part made me cry.'"

When working on this codebase, remember: the technical implementation serves the emotional expression, never the other way around.
