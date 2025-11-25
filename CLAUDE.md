# CLAUDE.md - AI Assistant Guide for DAiW-Music-Brain

> This document provides AI assistants with essential context for working with the DAiW (Digital Audio intelligent Workstation) codebase.

## Project Philosophy

**"Interrogate Before Generate"** - The tool shouldn't finish art for people. It should make them braver.

This is a Python toolkit for music production intelligence. The core philosophy is that emotional/creative intent should drive technical decisions, not the other way around. The three-phase "Song Intent Schema" ensures artists explore what they *need* to say before choosing technical parameters.

---

## Project Overview

DAiW-Music-Brain is a CLI toolkit and Python library for:
- **Groove extraction & application** - Extract timing/velocity patterns from MIDI, apply genre templates
- **Humanization engine** - Psychoacoustically-informed "Drunken Drummer" algorithm for human feel
- **Chord & harmony analysis** - Roman numeral analysis, key detection, borrowed chord identification
- **Comprehensive therapy-to-music pipeline** - Full affect analysis → harmony plan → MIDI generation
- **Tension curves** - Dynamic bar-by-bar emotional contours for song structure
- **Intent-based song generation** - Three-phase deep interrogation system for emotionally-driven composition
- **Intentional rule-breaking** - Structured approach to breaking music theory "rules" for emotional effect
- **Reference track DNA** - Learn tempo, key, and brightness from reference audio
- **Lyrical fragment generation** - Cut-up / Markov engine for creative sparks
- **DAW marker export** - Emotional structure markers for Logic Pro, Ableton, Reaper
- **Interactive teaching** - Lessons on production philosophy and music theory concepts

---

## Directory Structure

```
DAiW-Music-Brain/
├── music_brain/              # Main Python package (v0.3.0)
│   ├── __init__.py          # Package exports
│   ├── cli.py               # CLI entry point (`daiw` command)
│   ├── groove_engine.py     # Root-level groove engine re-export
│   ├── data/                # JSON/YAML data files
│   │   ├── chord_progressions.json
│   │   ├── genre_pocket_maps.json     # Genre timing characteristics
│   │   ├── humanize_presets.json      # Emotional humanization presets
│   │   ├── song_intent_examples.json
│   │   └── song_intent_schema.yaml
│   ├── groove/              # Groove extraction & application
│   │   ├── extractor.py     # extract_groove(), GrooveTemplate
│   │   ├── applicator.py    # apply_groove()
│   │   ├── groove_engine.py # Humanization "Drunken Drummer" layer
│   │   └── templates.py     # Genre templates (funk, jazz, rock, etc.)
│   ├── structure/           # Harmonic analysis & generation
│   │   ├── chord.py         # Chord, ChordProgression, CHORD_QUALITIES
│   │   ├── progression.py   # diagnose_progression(), parse_progression_string()
│   │   ├── sections.py      # Section detection
│   │   ├── comprehensive_engine.py  # TherapySession, HarmonyPlan, render_plan_to_midi()
│   │   ├── tension.py       # generate_tension_curve() - bar-by-bar emotional contours
│   │   └── tension_curve.py # Preset tension curves & section-based application
│   ├── session/             # Intent schema & teaching
│   │   ├── intent_schema.py # CompleteSongIntent, rule-breaking enums
│   │   ├── intent_processor.py # process_intent(), IntentProcessor
│   │   ├── teaching.py      # RuleBreakingTeacher
│   │   ├── interrogator.py  # SongInterrogator
│   │   └── generator.py     # Generation utilities
│   ├── audio/               # Audio analysis
│   │   ├── feel.py          # analyze_feel(), AudioFeatures
│   │   └── reference_dna.py # ReferenceProfile, analyze_reference()
│   ├── text/                # Lyrical tools
│   │   └── lyrical_mirror.py # Cut-up/Markov lyric fragment generator
│   ├── utils/               # Utilities
│   │   ├── midi_io.py       # MIDI file handling
│   │   ├── instruments.py   # Instrument mappings
│   │   └── ppq.py           # PPQ normalization
│   └── daw/                 # DAW integration
│       ├── logic.py         # LogicProject, LOGIC_CHANNELS
│       └── markers.py       # MarkerEvent, export_markers_midi()
├── vault/                   # Knowledge base (Obsidian-compatible)
│   ├── Songwriting_Guides/
│   │   ├── song_intent_schema.md
│   │   ├── rule_breaking_practical.md
│   │   └── rule_breaking_masterpieces.md
│   ├── Templates/
│   ├── Theory_Reference/
│   └── Production_Workflows/
├── tests/                   # Comprehensive test suite
│   ├── test_basic.py        # Core module tests
│   ├── test_comprehensive_engine.py
│   ├── test_groove_engine.py
│   ├── test_groove_extractor.py
│   ├── test_intent_schema.py
│   ├── test_intent_processor.py
│   ├── test_cli_commands.py
│   ├── test_cli_flow.py
│   ├── test_daw_integration.py
│   ├── test_bridge_integration.py
│   ├── test_midi_io.py
│   └── test_error_paths.py
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

### The Comprehensive Engine (Therapy → MIDI Pipeline)

The comprehensive engine (`music_brain/structure/comprehensive_engine.py`) provides an end-to-end pipeline:

```
Text Input → AffectAnalyzer → TherapyState → HarmonyPlan → render_plan_to_midi() → MIDI File
```

Key classes:
- `AffectAnalyzer` - Analyzes text for emotional keywords (grief, rage, awe, etc.)
- `TherapySession` - Manages session state and generates HarmonyPlan
- `HarmonyPlan` - Blueprint for generation (mode, tempo, chords, structure_type)
- `NoteEvent` - Canonical note representation for MIDI generation

Structure types map mood to emotional contour:
- `"climb"` - Slow build (grief, dissociation)
- `"standard"` - Verse/chorus shape (rage, defiance)
- `"constant"` - Flat loop/mantra (neutral, awe)

### Tension Curves

The tension system (`music_brain/structure/tension.py`) creates bar-by-bar emotional contours:

```python
from music_brain.structure.tension import generate_tension_curve

# Returns array of multipliers (0.5-1.5) for each bar
curve = generate_tension_curve(total_bars=64, structure_type="standard")
# Verse bars: ~0.6-0.7, Chorus: ~1.1, Bridge: ~1.2-1.5, Outro: ~0.5
```

### The Groove Engine (Drunken Drummer)

The groove engine (`music_brain/groove/groove_engine.py`) applies psychoacoustically-informed humanization:

Two key axes:
- **Complexity** (0.0-1.0): Timing looseness, dropout probability
- **Vulnerability** (0.0-1.0): Dynamic range, softness

Features:
- Gaussian timing jitter (not uniform - more human)
- Per-drum-type timing multipliers (kicks tighter, hats looser)
- Protected dropouts (kicks/snares rarely drop)
- Ghost note generation at high vulnerability
- Preset integration from `humanize_presets.json`

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
- **Optional**: `librosa`, `soundfile`, `music21`, `markovify` (for lyrical mirror)

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

### Test Files
| File | Coverage |
|------|----------|
| `test_basic.py` | Core imports, templates, chord parsing, teaching |
| `test_comprehensive_engine.py` | TherapySession, HarmonyPlan, affect analysis |
| `test_groove_engine.py` | Humanization, complexity/vulnerability axes |
| `test_groove_extractor.py` | Groove extraction from MIDI |
| `test_intent_schema.py` | Intent schema validation, serialization |
| `test_intent_processor.py` | Intent processing pipeline |
| `test_cli_commands.py` | CLI command functionality |
| `test_cli_flow.py` | End-to-end CLI workflows |
| `test_daw_integration.py` | LogicProject, MIDI export |
| `test_bridge_integration.py` | Component integration |
| `test_midi_io.py` | MIDI file handling |
| `test_error_paths.py` | Error handling, edge cases |

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
   - `HarmonyPlan`, `TherapyState`, `AffectResult`, `NoteEvent`
   - `GrooveSettings`, `ReferenceProfile`, `MarkerEvent`
   - Support serialization via `to_dict()` / `from_dict()` / `save()` / `load()`

3. **Enums for categorical values**
   - `HarmonyRuleBreak`, `RhythmRuleBreak`, `ArrangementRuleBreak`, `ProductionRuleBreak`
   - `VulnerabilityScale`, `NarrativeArc`, `CoreStakes`, `GrooveFeel`

4. **Module-level exports in `__init__.py`**
   - Each subpackage exports its public API via `__all__`

5. **Graceful degradation**
   - Optional dependencies (librosa, markovify) checked at runtime
   - Functions degrade gracefully if dependencies unavailable

---

## Key Files to Understand

### Entry Points
- `music_brain/cli.py` - CLI implementation, all commands
- `music_brain/__init__.py` - Public API exports (v0.3.0)

### Core Logic
- `music_brain/structure/comprehensive_engine.py` - Therapy → MIDI pipeline
- `music_brain/structure/tension.py` - Bar-by-bar tension curves
- `music_brain/groove/groove_engine.py` - Humanization layer
- `music_brain/session/intent_schema.py` - Intent system core
- `music_brain/session/intent_processor.py` - Converts intent to musical elements
- `music_brain/structure/progression.py` - Chord parsing and diagnosis

### Data Files
- `music_brain/data/genre_pocket_maps.json` - Genre timing characteristics
- `music_brain/data/humanize_presets.json` - Emotional humanization presets
- `music_brain/data/song_intent_schema.yaml` - Schema definition
- `music_brain/data/chord_progressions.json` - Common progressions

---

## Working with This Codebase

### When Adding Features
1. Consider the "Interrogate Before Generate" philosophy
2. Rule-breaking should always have emotional justification
3. Add tests for new functionality
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

### When Extending the Comprehensive Engine
1. `HarmonyPlan` fields drive generation - add new fields there
2. Update `generate_plan()` to set new fields based on mood
3. Update `render_plan_to_midi()` to use new fields
4. Add tests in `test_comprehensive_engine.py`

### Data Flow
```
User Input → CompleteSongIntent → IntentProcessor → Generated Elements
                                                    ├── GeneratedProgression
                                                    ├── GeneratedGroove
                                                    ├── GeneratedArrangement
                                                    └── GeneratedProduction

Text Input → AffectAnalyzer → TherapyState → HarmonyPlan → render_plan_to_midi()
                                                 │
                                                 └── Tension Curve → Per-bar velocity
```

---

## Important Design Decisions

1. **Emotional intent drives technical choices** - Never generate without understanding the "why"

2. **Rules are broken intentionally** - Every rule break requires justification

3. **Human imperfection is valued** - Lo-fi, pitch drift, room noise are features, not bugs

4. **Phase 0 must come first** - Technical decisions (Phase 2) can't be made without emotional clarity (Phase 0)

5. **Teaching over finishing** - The tool should educate and empower, not just generate

6. **Contours over states** - Tension curves give songs shape, not just static intensity

7. **Graceful degradation** - Core functionality works without optional dependencies

---

## Common Tasks

### Creating a new groove genre template
1. Add entry to `music_brain/data/genre_pocket_maps.json`
2. Add template in `music_brain/groove/templates.py`
3. Add to CLI choices in `cli.py`

### Adding a new humanization preset
1. Add entry to `music_brain/data/humanize_presets.json`
2. Include `groove_settings` with complexity, vulnerability, timing mults
3. Add `therapy_state` to document intended emotional use

### Adding a new teaching topic
1. Add content in `music_brain/session/teaching.py`
2. Add to `valid_topics` list in `cmd_teach()`

### Extending intent validation
1. Add validation logic in `validate_intent()` in `intent_schema.py`
2. Consider consistency checks between phases

### Adding a new tension curve structure type
1. Add case in `generate_tension_curve()` in `music_brain/structure/tension.py`
2. Map moods to new type in `TherapySession.generate_plan()`
3. Optionally add preset in `tension_curve.py` TENSION_CURVES dict

---

## Vault (Knowledge Base)

The `vault/` directory is an Obsidian-compatible knowledge base containing:
- **Songwriting_Guides/** - Intent schema docs, rule-breaking guides
- **Theory_Reference/** - Music theory reference materials
- **Production_Workflows/** - Production technique guides, JUCE integration
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

### Tension curve issues
- Ensure numpy is installed: `pip install numpy`
- Verify total_bars > 0

### Reference DNA analysis fails
- Install librosa: `pip install librosa`
- Check audio file format is supported (wav, mp3)

### Lyrical mirror returns empty
- Install markovify: `pip install markovify`
- Ensure input text has sufficient content

### Test failures
- Run with verbose: `pytest -v`
- Check data files exist in `music_brain/data/`

---

## API Quick Reference

### Public Exports (music_brain)
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

### Quick Example: Therapy → MIDI
```python
from music_brain.structure.comprehensive_engine import (
    TherapySession,
    render_plan_to_midi,
)

session = TherapySession()
affect = session.process_core_input("I feel broken and afraid")
session.set_scales(motivation=8, chaos=0.6)
plan = session.generate_plan()

print(f"Mode: {plan.mode}, Tempo: {plan.tempo_bpm}, Structure: {plan.structure_type}")
render_plan_to_midi(plan, "output.mid", vulnerability=0.4)
```

---

## Meta Principle

> "The audience doesn't hear 'borrowed from Dorian.' They hear 'that part made me cry.'"

When working on this codebase, remember: the technical implementation serves the emotional expression, never the other way around. The difference between a loop pack and a writing partner is emotional contour.
