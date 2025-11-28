# CLAUDE.md - AI Assistant Guide for DAiW-Music-Brain

> This document provides AI assistants with essential context for working with the DAiW (Digital Audio intelligent Workstation) codebase.

## Project Philosophy

**"Interrogate Before Generate"** - The tool shouldn't finish art for people. It should make them braver.

This is a Python toolkit for music production intelligence. The core philosophy is that emotional/creative intent should drive technical decisions, not the other way around. The three-phase "Song Intent Schema" ensures artists explore what they *need* to say before choosing technical parameters.

---

## Project Overview

DAiW-Music-Brain is a CLI toolkit and Python library for:
- **Groove extraction & application** - Extract timing/velocity patterns from MIDI, apply genre templates
- **"Drunken Drummer" humanization** - Psychoacoustically-informed timing jitter and dynamics shaping
- **Chord & harmony analysis** - Roman numeral analysis, key detection, borrowed chord identification
- **Intent-based song generation** - Three-phase deep interrogation system for emotionally-driven composition
- **Therapy-to-music pipeline** - Comprehensive engine integrating affect analysis, harmony generation, and MIDI output
- **Lyrical fragment generation** - Cut-up/Markov engine for creative spark generation
- **Reference DNA analysis** - Learn from reference tracks (tempo, key, brightness, warmth)
- **Dynamic tension curves** - Bar-wise energy shaping for emotional arcs
- **Scale emotional mapping** - 62+ scales with emotional qualities, genre associations, and chord relationships
- **Intentional rule-breaking** - Structured approach to breaking music theory "rules" for emotional effect
- **Interactive teaching** - Lessons on production philosophy and music theory concepts

---

## Directory Structure

```
DAiW-Music-Brain/
├── music_brain/              # Main Python package (v0.3.0)
│   ├── __init__.py          # Package exports
│   ├── cli.py               # CLI entry point (`daiw` command)
│   ├── groove_engine.py     # Simplified groove entry point
│   ├── data/                # JSON/YAML data files
│   │   ├── chord_progressions.json
│   │   ├── genre_pocket_maps.json    # Genre timing characteristics
│   │   ├── humanize_presets.json     # Humanization presets
│   │   ├── song_intent_examples.json
│   │   └── song_intent_schema.yaml
│   ├── groove/              # Groove extraction & application
│   │   ├── extractor.py     # extract_groove(), GrooveTemplate
│   │   ├── applicator.py    # apply_groove()
│   │   ├── templates.py     # Genre templates (funk, jazz, rock, etc.)
│   │   └── groove_engine.py # "Drunken Drummer" humanization
│   ├── structure/           # Harmonic analysis
│   │   ├── chord.py         # Chord, ChordProgression, CHORD_QUALITIES
│   │   ├── progression.py   # diagnose_progression(), generate_reharmonizations()
│   │   ├── sections.py      # Section detection
│   │   ├── comprehensive_engine.py  # TherapySession, AffectAnalyzer, HarmonyPlan
│   │   └── tension_curve.py # Dynamic tension curves for song breathing
│   ├── session/             # Intent schema & teaching
│   │   ├── intent_schema.py # CompleteSongIntent, rule-breaking enums
│   │   ├── intent_processor.py # process_intent(), IntentProcessor
│   │   ├── teaching.py      # RuleBreakingTeacher
│   │   ├── interrogator.py  # SongInterrogator
│   │   └── generator.py     # Generation utilities
│   ├── audio/               # Audio analysis
│   │   ├── feel.py          # analyze_feel(), AudioFeatures
│   │   └── reference_dna.py # Reference track analysis (tempo, key, brightness)
│   ├── text/                # Text/lyric processing
│   │   └── lyrical_mirror.py # Cut-up/Markov lyric fragment generation
│   ├── utils/               # Utilities
│   │   ├── midi_io.py       # MIDI file handling
│   │   ├── instruments.py   # Instrument mappings
│   │   └── ppq.py           # PPQ normalization
│   └── daw/                 # DAW integration
│       ├── logic.py         # Logic Pro integration, LogicProject class
│       └── markers.py       # Emotional structure marker export
├── data/                    # Standalone data utilities
│   └── scales/              # Scale database
│       ├── scale_emotional_map.json  # 62+ scales with emotional mappings
│       └── scale_generator.py        # CLI/library for scale generation
├── vault/                   # Knowledge base (Obsidian-compatible)
│   ├── Songwriting_Guides/
│   │   ├── song_intent_schema.md
│   │   ├── rule_breaking_practical.md
│   │   └── rule_breaking_masterpieces.md
│   ├── Templates/
│   │   └── DAiW_Task_Board.md
│   └── README.md
├── tests/                   # Test suite (12 test files)
│   ├── test_basic.py        # Core functionality tests
│   ├── test_comprehensive_engine.py
│   ├── test_groove_engine.py
│   ├── test_groove_extractor.py
│   ├── test_intent_schema.py
│   ├── test_intent_processor.py
│   ├── test_cli_commands.py
│   ├── test_cli_flow.py
│   ├── test_daw_integration.py
│   ├── test_midi_io.py
│   ├── test_bridge_integration.py
│   └── test_error_paths.py
├── .github/workflows/       # CI/CD
│   └── ci.yml               # GitHub Actions: tests + multi-platform builds
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

### Comprehensive Engine

The therapy-to-music pipeline (`structure/comprehensive_engine.py`):

```
Text Input → AffectAnalyzer → TherapySession → HarmonyPlan → MIDI
                    ↓                  ↓
            AffectResult        TherapyState
            (primary, secondary, (mode, tempo, chords)
             scores, intensity)
```

Key classes:
- **AffectAnalyzer** - Scores text for 9 emotional affects (grief, rage, awe, nostalgia, fear, dissociation, defiance, tenderness, confusion)
- **TherapySession** - Maps affects to modes and generates HarmonyPlan
- **HarmonyPlan** - Complete blueprint with root, mode, tempo, chords, complexity
- **NoteEvent** - Canonical MIDI event structure (pitch, velocity, start_tick, duration_ticks)

### "Drunken Drummer" Humanization

The groove engine (`groove/groove_engine.py`) applies psychoacoustically-informed variations:

- **Complexity axis** (0.0-1.0): Timing looseness, dropout probability
- **Vulnerability axis** (0.0-1.0): Dynamic range, softness, ghost notes

Features:
- Gaussian timing jitter (not uniform random)
- Drum-specific protection levels (kicks rarely drop out)
- Human latency bias (slightly behind the beat)
- Ghost note insertion at high vulnerability
- Per-instrument timing multipliers

### Tension Curves

Dynamic energy shaping over song duration (`structure/tension_curve.py`):

| Curve | Pattern | Use Case |
|-------|---------|----------|
| `verse_chorus` | Low-Low-High-High-Low-High-High-Fade | Standard pop |
| `slow_build` | Gradual 0.4 → 1.2 | Epic builds |
| `catharsis` | Build to 1.3 release | Emotional climax |
| `descent` | 1.0 → 0.3 | Resignation, sadness |
| `spiral` | Escalating chaos | Anxiety, breakdown |
| `static` | ~0.8 throughout | Hypnotic, trance |

### Scale Emotional Map

The `data/scales/scale_emotional_map.json` contains 62+ scales with:
- Interval patterns (semitones)
- Emotional qualities (bright, dark, mysterious, etc.)
- Genre associations
- Chord qualities per scale degree
- Common progressions
- Related scales with relationships

Use the `scale_generator.py` utility:
```bash
python data/scales/scale_generator.py Dorian C           # Get C Dorian notes
python data/scales/scale_generator.py --emotion sad      # Find sad scales
python data/scales/scale_generator.py --compare Dorian Aeolian C  # Compare scales
```

---

## Development Setup

### Installation
```bash
# Clone and install as editable package
git clone https://github.com/sburdges-eng/DAiW-Music-Brain.git
cd DAiW-Music-Brain
pip install -e .

# With optional dependencies
pip install -e ".[dev]"      # pytest, black, flake8, mypy
pip install -e ".[audio]"    # librosa, soundfile (for reference_dna)
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
- **Optional**: `librosa`, `soundfile`, `music21`, `markovify` (for lyrical_mirror)

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
| `test_basic.py` | Imports, templates, chord parsing, teaching |
| `test_comprehensive_engine.py` | AffectAnalyzer, TherapySession, HarmonyPlan |
| `test_groove_engine.py` | Humanization, GrooveSettings |
| `test_groove_extractor.py` | Groove extraction from MIDI |
| `test_intent_schema.py` | Intent schema validation |
| `test_intent_processor.py` | Intent processing pipeline |
| `test_cli_commands.py` | CLI command parsing |
| `test_cli_flow.py` | End-to-end CLI flows |
| `test_daw_integration.py` | LogicProject, marker export |
| `test_midi_io.py` | MIDI file I/O |
| `test_bridge_integration.py` | Cross-module integration |
| `test_error_paths.py` | Error handling and edge cases |

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

### CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`):
- **test**: Runs pytest on Python 3.9 and 3.11
- **build-desktop-macos**: Builds macOS app bundle
- **build-desktop-linux**: Builds Linux executable
- **build-desktop-windows**: Builds Windows executable

Artifacts are uploaded for each platform after successful tests.

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
   - `HarmonyPlan`, `NoteEvent`, `AffectResult`, `TherapyState`
   - `GrooveSettings`, `ReferenceProfile`, `TensionProfile`
   - Support serialization via `to_dict()` / `from_dict()` / `save()` / `load()`

3. **Enums for categorical values**
   - `HarmonyRuleBreak`, `RhythmRuleBreak`, `ArrangementRuleBreak`, `ProductionRuleBreak`
   - `VulnerabilityScale`, `NarrativeArc`, `CoreStakes`, `GrooveFeel`

4. **Graceful degradation**
   - Optional dependencies checked at runtime (`LIBROSA_AVAILABLE`, `MARKOVIFY_AVAILABLE`, etc.)
   - Functions provide fallbacks when dependencies missing

5. **Module-level exports in `__init__.py`**
   - Each subpackage exports its public API via `__all__`
   - Main package exports: `extract_groove`, `apply_groove`, `analyze_chords`, `TherapySession`, `HarmonyPlan`, etc.

---

## Key Files to Understand

### Entry Points
- `music_brain/cli.py` - CLI implementation, all commands
- `music_brain/__init__.py` - Public API exports (v0.3.0)

### Core Logic
- `music_brain/structure/comprehensive_engine.py` - The therapy-to-music pipeline
- `music_brain/session/intent_schema.py` - The heart of the intent system
- `music_brain/session/intent_processor.py` - Converts intent to musical elements
- `music_brain/groove/groove_engine.py` - "Drunken Drummer" humanization
- `music_brain/groove/templates.py` - Genre groove definitions
- `music_brain/structure/progression.py` - Chord parsing and diagnosis
- `music_brain/structure/tension_curve.py` - Dynamic tension application

### Analysis Modules
- `music_brain/audio/reference_dna.py` - Reference track analysis
- `music_brain/text/lyrical_mirror.py` - Cut-up/Markov lyrics

### DAW Integration
- `music_brain/daw/logic.py` - LogicProject class, MIDI export
- `music_brain/daw/markers.py` - Emotional structure markers

### Data Files
- `music_brain/data/genre_pocket_maps.json` - Genre timing characteristics
- `music_brain/data/humanize_presets.json` - Groove engine presets
- `music_brain/data/song_intent_schema.yaml` - Schema definition
- `music_brain/data/chord_progressions.json` - Common progressions
- `data/scales/scale_emotional_map.json` - 62+ scale definitions

---

## Working with This Codebase

### When Adding Features
1. Consider the "Interrogate Before Generate" philosophy
2. Rule-breaking should always have emotional justification
3. Add tests for new functionality (see `tests/` structure)
4. Update `__all__` exports if adding public API
5. Keep CLI startup fast (use lazy imports)
6. Handle optional dependencies gracefully

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

### When Adding New Scales
1. Add entry to `data/scales/scale_emotional_map.json`
2. Include: intervals_semitones, intervals_names, emotional_quality, genre_associations
3. Add chord qualities and common progressions
4. Test with `scale_generator.py`

### Data Flow
```
User Input → CompleteSongIntent → IntentProcessor → Generated Elements
                                                    ├── GeneratedProgression
                                                    ├── GeneratedGroove
                                                    ├── GeneratedArrangement
                                                    └── GeneratedProduction
```

Comprehensive Engine Flow:
```
Text → AffectAnalyzer → TherapySession → HarmonyPlan → render_plan_to_midi → MIDI File
                              ↓
                       (affect → mode mapping)
                       (motivation → length)
                       (chaos → complexity)
```

---

## Important Design Decisions

1. **Emotional intent drives technical choices** - Never generate without understanding the "why"

2. **Rules are broken intentionally** - Every rule break requires justification

3. **Human imperfection is valued** - Lo-fi, pitch drift, room noise are features, not bugs

4. **Phase 0 must come first** - Technical decisions (Phase 2) can't be made without emotional clarity (Phase 0)

5. **Teaching over finishing** - The tool should educate and empower, not just generate

6. **Graceful degradation** - Core features work without optional dependencies

7. **NoteEvent as canonical format** - All MIDI communication uses NoteEvent structure for cross-system compatibility

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
2. Include `groove_settings` with complexity, vulnerability, timing multipliers

### Adding a tension curve
1. Add to `TENSION_CURVES` dict in `structure/tension_curve.py`
2. Document the emotional purpose

---

## API Quick Reference

### Comprehensive Engine
```python
from music_brain.structure.comprehensive_engine import TherapySession, render_plan_to_midi

session = TherapySession()
affect = session.process_core_input("I lost someone I loved")  # Returns "grief"
session.set_scales(motivation=7, chaos=0.4)
plan = session.generate_plan()
render_plan_to_midi(plan, "output.mid")
```

### Groove Engine
```python
from music_brain.groove.groove_engine import apply_groove, GrooveSettings

events = [{"start_tick": 0, "velocity": 80, "pitch": 36}]
humanized = apply_groove(events, complexity=0.5, vulnerability=0.6, ppq=480)
```

### Lyrical Mirror
```python
from music_brain.text.lyrical_mirror import mirror_session

fragments = mirror_session(
    core_wound="She left without saying goodbye",
    core_longing="To understand why",
    max_lines=6
)
```

### Reference DNA
```python
from music_brain.audio.reference_dna import analyze_reference

profile = analyze_reference("reference_track.wav")
print(f"Tempo: {profile.tempo_bpm}, Key: {profile.key_root} {profile.key_mode}")
```

### Tension Curves
```python
from music_brain.structure.tension_curve import apply_tension_curve, get_tension_curve

curve = get_tension_curve("catharsis")
events = apply_tension_curve(note_events, bar_ticks=1920, multipliers=curve)
```

---

## Vault (Knowledge Base)

The `vault/` directory is an Obsidian-compatible knowledge base containing:
- **Songwriting_Guides/** - Intent schema docs, rule-breaking guides
- **Templates/** - Task boards and project templates

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

### Optional features not working
- Reference DNA: `pip install librosa soundfile`
- Lyrical Mirror (Markov mode): `pip install markovify`
- Desktop app: `pip install streamlit pywebview`

### CI build failures
- Check `.github/workflows/ci.yml` for required system dependencies
- Linux builds need: `python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.1`

---

## Meta Principle

> "The audience doesn't hear 'borrowed from Dorian.' They hear 'that part made me cry.'"

When working on this codebase, remember: the technical implementation serves the emotional expression, never the other way around.
