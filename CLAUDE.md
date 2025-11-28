# CLAUDE.md - AI Assistant Guide for DAiW-Music-Brain

> This document provides AI assistants with essential context for working with the DAiW (Digital Audio intelligent Workstation) codebase.

## Project Philosophy

**"Interrogate Before Generate"** - The tool shouldn't finish art for people. It should make them braver.

This is a Python toolkit for music production intelligence. The core philosophy is that emotional/creative intent should drive technical decisions, not the other way around. The three-phase "Song Intent Schema" ensures artists explore what they *need* to say before choosing technical parameters.

---

## Project Overview

DAiW-Music-Brain is a CLI toolkit and Python library for:
- **Groove extraction & application** - Extract timing/velocity patterns from MIDI, apply genre templates
- **Humanization engine** - "Drunken Drummer" algorithm for psychoacoustically-informed timing/velocity variations
- **Chord & harmony analysis** - Roman numeral analysis, key detection, borrowed chord identification
- **Intent-based song generation** - Three-phase deep interrogation system for emotionally-driven composition
- **Therapy-to-MIDI pipeline** - Comprehensive engine that converts emotional text into musical structure
- **Lyrical fragment generation** - Cut-up/Markov engine for sparking creative ideas from therapy text
- **Reference track analysis** - Extract "DNA" (tempo, key, brightness) from reference audio
- **Dynamic tension curves** - Create emotional arcs that make songs "breathe"
- **DAW marker export** - Export emotional structure markers to MIDI for timeline visualization
- **Intentional rule-breaking** - Structured approach to breaking music theory "rules" for emotional effect
- **Interactive teaching** - Lessons on production philosophy and music theory concepts

---

## Directory Structure

```
DAiW-Music-Brain/
├── music_brain/              # Main Python package (v0.3.0)
│   ├── __init__.py          # Package exports
│   ├── cli.py               # CLI entry point (`daiw` command)
│   ├── groove_engine.py     # "Drunken Drummer" humanization (complexity/vulnerability axes)
│   ├── data/                # JSON/YAML data files
│   │   ├── chord_progressions.json
│   │   ├── genre_pocket_maps.json    # Genre timing characteristics
│   │   ├── humanize_presets.json     # Emotion-to-groove presets (lofi_depression, defiant_punk, etc.)
│   │   ├── song_intent_examples.json
│   │   └── song_intent_schema.yaml
│   ├── groove/              # Groove extraction & application
│   │   ├── extractor.py     # extract_groove(), GrooveTemplate
│   │   ├── applicator.py    # apply_groove() (file-based)
│   │   ├── groove_engine.py # apply_groove() (event-based, advanced humanization)
│   │   └── templates.py     # Genre templates (funk, jazz, rock, etc.)
│   ├── structure/           # Harmonic analysis & generation
│   │   ├── chord.py         # Chord, ChordProgression, CHORD_QUALITIES
│   │   ├── progression.py   # parse_progression_string(), diagnose_progression()
│   │   ├── sections.py      # Section detection
│   │   ├── comprehensive_engine.py  # TherapySession, AffectAnalyzer, HarmonyPlan, render_plan_to_midi()
│   │   └── tension_curve.py # Dynamic tension curves (verse_chorus, slow_build, catharsis, etc.)
│   ├── session/             # Intent schema & teaching
│   │   ├── intent_schema.py # CompleteSongIntent, rule-breaking enums
│   │   ├── intent_processor.py # process_intent(), IntentProcessor
│   │   ├── teaching.py      # RuleBreakingTeacher
│   │   ├── interrogator.py  # SongInterrogator
│   │   └── generator.py     # Generation utilities
│   ├── audio/               # Audio analysis
│   │   ├── feel.py          # analyze_feel(), AudioFeatures
│   │   └── reference_dna.py # analyze_reference(), ReferenceProfile (tempo, key, brightness)
│   ├── text/                # Text/lyric generation
│   │   └── lyrical_mirror.py # generate_lyrical_fragments(), mirror_session() (cut-up/Markov)
│   ├── utils/               # Utilities
│   │   ├── midi_io.py       # MIDI file handling
│   │   ├── instruments.py   # Instrument mappings
│   │   └── ppq.py           # PPQ normalization
│   └── daw/                 # DAW integration
│       ├── logic.py         # LogicProject, LOGIC_CHANNELS, export_midi()
│       └── markers.py       # MarkerEvent, export_markers_midi(), emotional structure markers
├── vault/                   # Knowledge base (Obsidian-compatible)
│   ├── Songwriting_Guides/
│   │   ├── song_intent_schema.md
│   │   ├── rule_breaking_practical.md
│   │   └── rule_breaking_masterpieces.md
│   ├── Templates/
│   │   └── DAiW_Task_Board.md
│   └── README.md
├── tests/                   # Test suite (pytest)
│   ├── test_basic.py        # Core functionality tests
│   ├── test_groove_engine.py
│   ├── test_groove_extractor.py
│   ├── test_comprehensive_engine.py
│   ├── test_intent_schema.py
│   ├── test_intent_processor.py
│   ├── test_cli_commands.py
│   ├── test_cli_flow.py
│   ├── test_midi_io.py
│   ├── test_daw_integration.py
│   ├── test_bridge_integration.py
│   └── test_error_paths.py
├── .github/workflows/       # CI/CD
│   └── ci.yml               # GitHub Actions: tests + builds for macOS/Linux/Windows
├── app.py                   # Streamlit UI application
├── launcher.py              # Native desktop app launcher (pywebview)
├── daiw.spec                # PyInstaller build configuration
├── pyproject.toml           # Package configuration
├── setup.py                 # Legacy setup
├── requirements.txt         # Core dependencies
├── LICENSE                  # MIT License
└── README.md
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

### Comprehensive Engine (Therapy → MIDI)

The `comprehensive_engine.py` provides a complete pipeline:

```
Text Input → AffectAnalyzer → TherapySession → HarmonyPlan → render_plan_to_midi() → MIDI File
```

- **AffectAnalyzer**: Detects emotions (grief, rage, awe, nostalgia, fear, dissociation, defiance, tenderness, confusion)
- **TherapySession**: Manages state, maps affect to mode (grief→aeolian, rage→phrygian, awe→lydian)
- **HarmonyPlan**: Blueprint containing root, mode, tempo, chords, complexity
- **Oblique Strategies**: Injects creative prompts based on chaos tolerance

### Humanization ("Drunken Drummer")

The `groove_engine.py` applies psychoacoustically-informed variations:

- **Complexity (0-1)**: Controls timing looseness and dropped notes
- **Vulnerability (0-1)**: Controls dynamic range and softness
- Drum-specific timing multipliers (kicks tight, hi-hats loose)
- Ghost note generation at high vulnerability
- Human latency bias (slightly behind the beat)

### Tension Curves

The `tension_curve.py` creates emotional arcs:

| Curve | Pattern | Use Case |
|-------|---------|----------|
| `verse_chorus` | Low-Low-High-High-Low-High-High-Outro | Standard pop/rock structure |
| `slow_build` | Gradual 0.4→1.2 | Builds to climax |
| `catharsis` | Build-Build-Build-RELEASE | Emotional breakdown/release |
| `descent` | 1.0→0.3 falling | Sadness, resignation |
| `wave` | Ebb and flow | Dynamic variation |
| `static` | Minimal variation | Hypnotic, trance-like |

### Reference DNA

The `reference_dna.py` extracts characteristics from reference tracks:
- Tempo (BPM)
- Key (root + mode)
- Brightness (spectral centroid)
- Energy (RMS)
- Warmth (low-frequency content)

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
- **Audio**: `librosa>=0.9.0`, `soundfile>=0.10.0`
- **Theory**: `music21>=7.0.0`
- **Text**: `markovify` (optional, for lyrical_mirror)

### Python Version
- Requires Python 3.9+
- Tested on 3.9, 3.11 (CI matrix)

---

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_groove_engine.py -v

# Run specific test class
pytest tests/test_basic.py::TestImports -v
```

### Test Files
| File | Coverage |
|------|----------|
| `test_basic.py` | Imports, templates, chord parsing, data files |
| `test_groove_engine.py` | Humanization, GrooveSettings, presets |
| `test_groove_extractor.py` | Groove extraction from MIDI |
| `test_comprehensive_engine.py` | AffectAnalyzer, TherapySession, HarmonyPlan |
| `test_intent_schema.py` | Intent validation, serialization |
| `test_intent_processor.py` | Intent → musical element conversion |
| `test_cli_commands.py` | CLI command parsing |
| `test_cli_flow.py` | End-to-end CLI workflows |
| `test_midi_io.py` | MIDI file reading/writing |
| `test_daw_integration.py` | LogicProject, marker export |
| `test_bridge_integration.py` | Component integration |
| `test_error_paths.py` | Error handling, edge cases |

---

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`):

1. **Test Job**: Runs pytest on Python 3.9 and 3.11
2. **Build Jobs** (after tests pass):
   - macOS: Builds `.app` bundle
   - Linux: Builds executable directory
   - Windows: Builds `.exe`

Artifacts are uploaded for each platform build.

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
   - `GrooveSettings`, `HarmonyPlan`, `NoteEvent`, `ReferenceProfile`
   - Support serialization via `to_dict()` / `from_dict()` / `save()` / `load()`

3. **Enums for categorical values**
   - `HarmonyRuleBreak`, `RhythmRuleBreak`, `ArrangementRuleBreak`, `ProductionRuleBreak`
   - `VulnerabilityScale`, `NarrativeArc`, `CoreStakes`, `GrooveFeel`

4. **Module-level exports in `__init__.py`**
   - Each subpackage exports its public API via `__all__`

5. **Graceful degradation**
   - Optional dependencies checked with `try/except ImportError`
   - Features disable gracefully when deps unavailable (e.g., `LIBROSA_AVAILABLE`, `MARKOVIFY_AVAILABLE`)

---

## Key Files to Understand

### Entry Points
- `music_brain/cli.py` - CLI implementation, all commands
- `music_brain/__init__.py` - Public API exports

### Core Logic
- `music_brain/session/intent_schema.py` - The heart of the intent system
- `music_brain/session/intent_processor.py` - Converts intent to musical elements
- `music_brain/structure/comprehensive_engine.py` - Full therapy → MIDI pipeline
- `music_brain/groove_engine.py` - Humanization with complexity/vulnerability
- `music_brain/groove/templates.py` - Genre groove definitions
- `music_brain/structure/progression.py` - Chord parsing and diagnosis
- `music_brain/structure/tension_curve.py` - Dynamic tension arcs

### Data Files
- `music_brain/data/genre_pocket_maps.json` - Genre timing characteristics
- `music_brain/data/humanize_presets.json` - Emotion-to-groove mappings
- `music_brain/data/song_intent_schema.yaml` - Schema definition
- `music_brain/data/chord_progressions.json` - Common progressions

---

## Public API Exports

From `music_brain/__init__.py`:

```python
# Groove (file-based)
from music_brain import extract_groove, apply_groove, GrooveTemplate

# Groove (event-based humanization)
from music_brain import apply_groove_events

# Structure
from music_brain import analyze_chords, detect_sections, ChordProgression

# Audio
from music_brain import analyze_feel, AudioFeatures

# Comprehensive Engine
from music_brain import AffectAnalyzer, TherapySession, HarmonyPlan, render_plan_to_midi

# Text/Lyrical
from music_brain import generate_lyrical_fragments
```

---

## Working with This Codebase

### When Adding Features
1. Consider the "Interrogate Before Generate" philosophy
2. Rule-breaking should always have emotional justification
3. Add tests for new functionality
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

### When Adding Humanization Presets
1. Add entry to `music_brain/data/humanize_presets.json`
2. Include `therapy_state` mapping and `groove_settings`
3. Reference appropriate `suggested_genre_template`

### Data Flow
```
User Input → CompleteSongIntent → IntentProcessor → Generated Elements
                                                    ├── GeneratedProgression
                                                    ├── GeneratedGroove
                                                    ├── GeneratedArrangement
                                                    └── GeneratedProduction

OR (Comprehensive Engine):

Text → AffectAnalyzer → TherapySession → HarmonyPlan → render_plan_to_midi() → MIDI
                                              ↓
                                    Tension Curves, Markers
```

---

## Important Design Decisions

1. **Emotional intent drives technical choices** - Never generate without understanding the "why"

2. **Rules are broken intentionally** - Every rule break requires justification

3. **Human imperfection is valued** - Lo-fi, pitch drift, room noise are features, not bugs

4. **Phase 0 must come first** - Technical decisions (Phase 2) can't be made without emotional clarity (Phase 0)

5. **Teaching over finishing** - The tool should educate and empower, not just generate

6. **Graceful degradation** - Features work without optional deps, just with reduced capability

7. **Two axes of humanization** - Complexity (chaos) and Vulnerability (dynamics) are independent emotional dimensions

---

## Common Tasks

### Creating a new groove genre template
1. Add entry to `music_brain/data/genre_pocket_maps.json`
2. Add template in `music_brain/groove/templates.py`
3. Add to CLI choices in `cli.py`

### Adding a new humanization preset
1. Add entry to `music_brain/data/humanize_presets.json`
2. Define `therapy_state` (mood, vulnerability, groove_feel)
3. Define `groove_settings` (complexity, vulnerability, timing multipliers, ghost notes)

### Adding a new tension curve
1. Add entry to `TENSION_CURVES` dict in `tension_curve.py`
2. Provide 8-value list of multipliers
3. Document the emotional use case

### Adding a new affect category
1. Add keywords to `AffectAnalyzer.KEYWORDS` in `comprehensive_engine.py`
2. Add mode mapping to `AFFECT_TO_MODE` in `TherapySession`
3. Add emotional labels to `get_emotional_structure()` in `markers.py`

### Adding a new teaching topic
1. Add content in `music_brain/session/teaching.py`
2. Add to `valid_topics` list in `cmd_teach()`

---

## Vault (Knowledge Base)

The `vault/` directory is an Obsidian-compatible knowledge base containing:
- **Songwriting_Guides/** - Intent schema docs, rule-breaking guides
- **Templates/** - Task boards and templates

These markdown files use Obsidian-style `[[wiki links]]` for cross-referencing.

---

## Troubleshooting

### Import errors
- Ensure package is installed: `pip install -e .`
- Check Python version: `python --version` (requires 3.9+)

### MIDI file issues
- Verify mido is installed: `pip install mido`
- Check file exists and is valid MIDI

### Audio analysis not working
- Install audio dependencies: `pip install -e ".[audio]"`
- Verify librosa import: `python -c "import librosa"`

### Lyrical fragments not generating
- Install markovify: `pip install markovify`
- Falls back to simple cut-up if unavailable

### Test failures
- Run with verbose: `pytest -v`
- Check data files exist in `music_brain/data/`

### Build failures
- Check `daiw.spec` for missing hiddenimports
- Run with `console=True` to see error messages

---

## Meta Principle

> "The audience doesn't hear 'borrowed from Dorian.' They hear 'that part made me cry.'"

When working on this codebase, remember: the technical implementation serves the emotional expression, never the other way around.
