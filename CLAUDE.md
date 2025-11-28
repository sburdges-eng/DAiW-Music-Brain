# CLAUDE.md - AI Assistant Guide for DAiW-Music-Brain

> This document provides AI assistants with essential context for working with the DAiW (Digital Audio intelligent Workstation) codebase.

## Project Philosophy

**"Interrogate Before Generate"** - The tool shouldn't finish art for people. It should make them braver.

This is a Python toolkit for music production intelligence. The core philosophy is that emotional/creative intent should drive technical decisions, not the other way around. The three-phase "Song Intent Schema" ensures artists explore what they *need* to say before choosing technical parameters.

---

## Project Overview

DAiW-Music-Brain is a CLI toolkit and Python library for:
- **Groove extraction & application** - Extract timing/velocity patterns from MIDI, apply genre templates
- **Drum humanization** - "Drunken Drummer" system for emotional MIDI humanization
- **Chord & harmony analysis** - Roman numeral analysis, key detection, borrowed chord identification
- **Intent-based song generation** - Three-phase deep interrogation system for emotionally-driven composition
- **Therapy-to-music pipeline** - Comprehensive engine converting emotional text to MIDI
- **Lyrical fragment generation** - Cut-up/Markov engine for sparking lyrical creativity
- **Reference track analysis** - Extract DNA (tempo, key, brightness) from reference audio
- **Dynamic tension curves** - Apply breathing/energy arcs to song structure
- **Intentional rule-breaking** - Structured approach to breaking music theory "rules" for emotional effect
- **Interactive teaching** - Lessons on production philosophy and music theory concepts

---

## Directory Structure

```
DAiW-Music-Brain/
├── music_brain/                    # Main Python package (v0.3.0)
│   ├── __init__.py                # Package exports
│   ├── cli.py                     # CLI entry point (`daiw` command)
│   ├── groove_engine.py           # Event-based MIDI humanization
│   │
│   ├── data/                      # JSON/YAML data files
│   │   ├── chord_progressions.json
│   │   ├── genre_pocket_maps.json     # Genre timing characteristics
│   │   ├── humanize_presets.json      # Emotional humanization presets
│   │   ├── song_intent_examples.json
│   │   └── song_intent_schema.yaml
│   │
│   ├── groove/                    # Groove extraction & application
│   │   ├── extractor.py           # extract_groove(), GrooveTemplate
│   │   ├── applicator.py          # apply_groove()
│   │   ├── groove_engine.py       # Drum-specific humanization
│   │   └── templates.py           # Genre templates (funk, jazz, rock, etc.)
│   │
│   ├── structure/                 # Harmonic analysis
│   │   ├── chord.py               # Chord, ChordProgression, CHORD_QUALITIES
│   │   ├── progression.py         # diagnose_progression(), generate_reharmonizations()
│   │   ├── sections.py            # Section detection
│   │   ├── comprehensive_engine.py # AffectAnalyzer, TherapySession, HarmonyPlan
│   │   └── tension_curve.py       # Dynamic tension curves (TENSION_CURVES)
│   │
│   ├── session/                   # Intent schema & teaching
│   │   ├── intent_schema.py       # CompleteSongIntent, rule-breaking enums
│   │   ├── intent_processor.py    # process_intent(), IntentProcessor
│   │   ├── teaching.py            # RuleBreakingTeacher
│   │   ├── interrogator.py        # SongInterrogator
│   │   └── generator.py           # Generation utilities
│   │
│   ├── audio/                     # Audio analysis
│   │   ├── feel.py                # analyze_feel(), AudioFeatures
│   │   └── reference_dna.py       # ReferenceProfile, analyze_reference()
│   │
│   ├── text/                      # Text/lyric processing
│   │   └── lyrical_mirror.py      # generate_lyrical_fragments(), cut-up engine
│   │
│   ├── utils/                     # Utilities
│   │   ├── midi_io.py             # MIDI file handling
│   │   ├── instruments.py         # Instrument mappings
│   │   └── ppq.py                 # PPQ normalization
│   │
│   └── daw/                       # DAW integration
│       ├── logic.py               # LogicProject, LOGIC_CHANNELS
│       └── markers.py             # MarkerEvent, emotional structure markers
│
├── vault/                         # Knowledge base (Obsidian-compatible)
│   ├── Songwriting_Guides/
│   │   ├── song_intent_schema.md
│   │   ├── rule_breaking_practical.md
│   │   └── rule_breaking_masterpieces.md
│   ├── Templates/
│   │   └── DAiW_Task_Board.md
│   ├── Songs/                     # Actual song projects
│   │   └── when-i-found-you-sleeping/
│   │       ├── lyrics/
│   │       ├── performance/
│   │       ├── research/
│   │       └── creative/
│   └── README.md
│
├── tests/                         # Test suite
│   ├── test_basic.py              # Core functionality tests
│   ├── test_comprehensive_engine.py
│   ├── test_intent_schema.py
│   ├── test_intent_processor.py
│   ├── test_groove_engine.py
│   ├── test_groove_extractor.py
│   ├── test_daw_integration.py
│   ├── test_bridge_integration.py
│   ├── test_midi_io.py
│   ├── test_cli_commands.py
│   ├── test_cli_flow.py
│   └── test_error_paths.py
│
├── pyproject.toml                 # Package configuration
├── requirements.txt               # Core dependencies
├── setup.py                       # Legacy setup
├── app.py                         # Streamlit UI application
├── launcher.py                    # Native desktop app launcher (pywebview)
├── daiw.spec                      # PyInstaller build configuration
└── LICENSE
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

### The Comprehensive Engine (Therapy-to-Music Pipeline)

The `comprehensive_engine.py` module integrates all phases into a direct MIDI generation pipeline:

```
Text Input → AffectAnalyzer → TherapySession → HarmonyPlan → NoteEvents → MIDI
```

Key classes:
- `AffectAnalyzer` - Detects emotions from text (grief, rage, awe, nostalgia, etc.)
- `TherapySession` - Manages session state, maps affect to mode
- `HarmonyPlan` - Blueprint for generation (root, mode, tempo, chords, complexity)
- `NoteEvent` - Canonical note representation for MIDI output

Affect-to-Mode mapping:
| Affect | Mode |
|--------|------|
| awe | lydian |
| nostalgia | dorian |
| rage, fear | phrygian |
| dissociation, confusion | locrian |
| grief | aeolian |
| defiance | mixolydian |
| tenderness, neutral | ionian |

### Rule-Breaking Categories

Rules are broken **intentionally** based on emotional justification:

| Category | Examples | Effect |
|----------|----------|--------|
| **Harmony** | `HARMONY_AvoidTonicResolution`, `HARMONY_ModalInterchange` | Unresolved yearning, bittersweet color |
| **Rhythm** | `RHYTHM_ConstantDisplacement`, `RHYTHM_TempoFluctuation` | Anxiety, organic breathing |
| **Arrangement** | `ARRANGEMENT_BuriedVocals`, `ARRANGEMENT_ExtremeDynamicRange` | Dissociation, dramatic impact |
| **Production** | `PRODUCTION_PitchImperfection`, `PRODUCTION_ExcessiveMud` | Emotional honesty, claustrophobia |

### Humanization Presets

The `humanize_presets.json` maps emotional states to groove settings:

| Preset | Description | Complexity | Vulnerability |
|--------|-------------|------------|---------------|
| `lofi_depression` | Lo-fi bedroom feel for melancholic content | 0.4 | 0.8 |
| `anxious_driving` | Tight but slightly off, creates unease | 0.25 | 0.4 |
| `defiant_punk` | Raw, aggressive, intentionally sloppy | 0.7 | 0.2 |
| `intimate_vulnerability` | Fragile, breathing, highly dynamic | 0.5 | 0.9 |
| `nostalgic_swing` | Warm, slightly behind the beat | 0.45 | 0.55 |
| `mechanical_dissociation` | Almost robotic, disconnected feel | 0.08 | 0.15 |
| `chaotic_breakdown` | Maximum chaos for emotional breakdown | 0.95 | 0.85 |

### Tension Curves

Dynamic arcs that make music "breathe":

| Curve | Pattern | Use For |
|-------|---------|---------|
| `verse_chorus` | Low, Low, High, High, Low, High, High, Out | Standard pop structure |
| `slow_build` | Gradual increase to climax | Epic, anthemic songs |
| `catharsis` | Build to massive release | Emotional breakthrough |
| `descent` | Falling energy | Sadness, resignation |
| `spiral` | Escalating chaos | Anxiety, unraveling |
| `static` | Hypnotic, minimal variation | Trance, repetitive |

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
- **Optional**: `librosa`, `soundfile`, `music21`, `markovify`

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
| Test File | Coverage |
|-----------|----------|
| `test_basic.py` | Imports, templates, chord parsing, teaching |
| `test_comprehensive_engine.py` | AffectAnalyzer, TherapySession, HarmonyPlan |
| `test_intent_schema.py` | Intent data classes, serialization |
| `test_intent_processor.py` | Intent processing pipeline |
| `test_groove_engine.py` | Humanization, swing, pocket |
| `test_groove_extractor.py` | MIDI groove extraction |
| `test_daw_integration.py` | Logic Pro integration, markers |
| `test_cli_commands.py` | CLI command parsing |
| `test_cli_flow.py` | End-to-end CLI flows |
| `test_midi_io.py` | MIDI file I/O |
| `test_error_paths.py` | Error handling, edge cases |

---

## CLI Usage

The package installs a `daiw` command:

```bash
# Groove operations
daiw extract drums.mid                    # Extract groove from MIDI
daiw apply --genre funk track.mid         # Apply genre groove template

# Drum humanization (Drunken Drummer)
daiw humanize drums.mid                   # Default humanization
daiw humanize drums.mid --style drunk     # Maximum chaos
daiw humanize drums.mid --preset lofi_depression  # Emotional preset
daiw humanize --list-presets              # List all presets

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

### Humanization Styles (Quick Presets)
| Style | Complexity | Vulnerability | Feel |
|-------|------------|---------------|------|
| `tight` | 0.1 | 0.2 | Minimal drift, confident |
| `natural` | 0.4 | 0.5 | Human feel, balanced |
| `loose` | 0.6 | 0.6 | Relaxed, laid back |
| `drunk` | 0.9 | 0.8 | Maximum chaos, fragile |

---

## Desktop Application

DAiW includes a native desktop application.

### Running the UI
```bash
# Streamlit in browser (development)
streamlit run app.py

# Native window (requires pywebview)
python launcher.py

# After building executable
./dist/DAiW/DAiW
```

### Building Standalone Executable
```bash
pip install -e ".[build]"
pyinstaller daiw.spec --clean --noconfirm
```

---

## Code Style & Conventions

### Formatting
- **Line length**: 100 characters (configured in `pyproject.toml`)
- **Formatter**: black
- **Linter**: flake8, mypy

```bash
black music_brain/ tests/
mypy music_brain/
flake8 music_brain/ tests/
```

### Code Patterns

1. **Lazy imports in CLI** (`cli.py`)
   - Heavy modules imported lazily to speed up CLI startup
   - Use `get_*_module()` functions for deferred imports

2. **Data classes for structured data**
   - `CompleteSongIntent`, `HarmonyPlan`, `NoteEvent`, `ReferenceProfile`
   - Support `to_dict()` / `from_dict()` / `save()` / `load()`

3. **Enums for categorical values**
   - `HarmonyRuleBreak`, `RhythmRuleBreak`, `ArrangementRuleBreak`, `ProductionRuleBreak`
   - `VulnerabilityScale`, `NarrativeArc`, `CoreStakes`, `GrooveFeel`

4. **Graceful degradation**
   - Optional dependencies (librosa, markovify) degrade gracefully
   - Check `*_AVAILABLE` flags before using optional features

5. **Module-level exports in `__init__.py`**
   - Each subpackage exports its public API via `__all__`

---

## Key Files to Understand

### Entry Points
- `music_brain/cli.py` - CLI implementation, all commands
- `music_brain/__init__.py` - Public API exports (v0.3.0)

### Core Logic
| File | Purpose |
|------|---------|
| `session/intent_schema.py` | Heart of the intent system |
| `session/intent_processor.py` | Converts intent to musical elements |
| `structure/comprehensive_engine.py` | Therapy-to-MIDI pipeline |
| `structure/tension_curve.py` | Dynamic breathing/energy arcs |
| `groove/templates.py` | Genre groove definitions |
| `groove_engine.py` | MIDI event humanization |
| `text/lyrical_mirror.py` | Lyrical fragment generation |
| `audio/reference_dna.py` | Reference track analysis |
| `daw/markers.py` | Emotional structure markers |

### Data Files
| File | Purpose |
|------|---------|
| `data/genre_pocket_maps.json` | Genre timing characteristics |
| `data/humanize_presets.json` | Emotional humanization presets |
| `data/song_intent_schema.yaml` | Schema definition |
| `data/chord_progressions.json` | Common progressions |

---

## Working with This Codebase

### When Adding Features
1. Consider the "Interrogate Before Generate" philosophy
2. Rule-breaking should always have emotional justification
3. Add tests for new functionality
4. Update `__all__` exports if adding public API
5. Keep CLI startup fast (use lazy imports)
6. Degrade gracefully when optional dependencies missing

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
1. Add entry to `data/humanize_presets.json`
2. Include `description`, `therapy_state`, `groove_settings`
3. Map to a `suggested_genre_template`

### Data Flow
```
User Input → CompleteSongIntent → IntentProcessor → Generated Elements
                                                    ├── GeneratedProgression
                                                    ├── GeneratedGroove
                                                    ├── GeneratedArrangement
                                                    └── GeneratedProduction

Text Input → AffectAnalyzer → TherapySession → HarmonyPlan → render_plan_to_midi() → MIDI
```

---

## Important Design Decisions

1. **Emotional intent drives technical choices** - Never generate without understanding the "why"

2. **Rules are broken intentionally** - Every rule break requires justification

3. **Human imperfection is valued** - Lo-fi, pitch drift, room noise are features, not bugs

4. **Phase 0 must come first** - Technical decisions (Phase 2) can't be made without emotional clarity (Phase 0)

5. **Teaching over finishing** - The tool should educate and empower, not just generate

6. **Graceful degradation** - Work without optional dependencies, providing fallbacks

7. **Canonical data structures** - `NoteEvent` is the API surface for MIDI operations

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

### Adding a new affect type
1. Add keywords to `AffectAnalyzer.KEYWORDS` in `comprehensive_engine.py`
2. Add mode mapping to `TherapySession.AFFECT_TO_MODE`
3. Add emotional labels to `daw/markers.py` mood_labels

### Adding a new tension curve
1. Add entry to `TENSION_CURVES` in `structure/tension_curve.py`
2. Document intended use case

---

## Vault (Knowledge Base)

The `vault/` directory is an Obsidian-compatible knowledge base:

- **Songwriting_Guides/** - Intent schema docs, rule-breaking guides
- **Templates/** - Task boards and templates
- **Songs/** - Actual song projects with lyrics, performance guides, research
  - Example: `when-i-found-you-sleeping/` - Complete song project structure

These markdown files use Obsidian-style `[[wiki links]]` for cross-referencing.

### Song Project Structure
```
vault/Songs/<song-name>/
├── README.md           # Song overview, structure, audio files
├── lyrics/             # Version history, current lyrics with chords
├── performance/        # Timestamped sheets, vowel guides, pitch correction
├── research/           # Genre research, reference songs, emotional context
└── creative/           # Creative explorations, section options
```

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

### Optional feature unavailable
- Check if optional dependency is installed
- Look for `*_AVAILABLE` flag in module
- Feature will degrade to simpler fallback

---

## Meta Principle

> "The audience doesn't hear 'borrowed from Dorian.' They hear 'that part made me cry.'"

When working on this codebase, remember: the technical implementation serves the emotional expression, never the other way around.
