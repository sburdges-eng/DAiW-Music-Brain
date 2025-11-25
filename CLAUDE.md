# CLAUDE.md - AI Assistant Guide for DAiW-Music-Brain

> This document provides AI assistants with essential context for working with the DAiW (Digital Audio intelligent Workstation) codebase.

## Status

**This is an alpha (v0.3.0).**

- The core emotional engine (`TherapySession` + `HarmonyPlan` + Groove/Tension) is **working**.
- The desktop app prototype (`app.py` + `launcher.py`) is **working**.
- The CLI commands are **implemented** but some underlying modules may need integration work.
- The Intent Schema system exists but `TherapySession` is the primary working pipeline.

If something in this README doesn't match the code, **trust the code**.

---

## Project Philosophy

**"Interrogate Before Generate"** - The tool shouldn't finish art for people. It should make them braver.

This is a Python toolkit for music production intelligence. The core philosophy is that emotional/creative intent should drive technical decisions, not the other way around.

---

## Current Working Features (v0.3.0)

### 1. Therapy-Driven Song Planner (`comprehensive_engine.py`)

The primary working pipeline:

```python
from music_brain.structure.comprehensive_engine import (
    TherapySession,
    HarmonyPlan,
    render_plan_to_midi,
)

session = TherapySession()
affect = session.process_core_input("I feel broken and afraid")
session.set_scales(motivation=8, chaos_tolerance=0.6)  # Note: chaos_tolerance not chaos
plan = session.generate_plan()

print(f"Mode: {plan.mode}, Tempo: {plan.tempo_bpm}")
print(f"Structure: {plan.structure_type}, Vulnerability: {plan.vulnerability}")
render_plan_to_midi(plan, "output.mid", vulnerability=plan.vulnerability)
```

Key classes:
- `AffectAnalyzer` - Analyzes text for emotional keywords (grief, rage, awe, etc.)
- `TherapySession` - Manages session state and generates HarmonyPlan
- `HarmonyPlan` - Blueprint with: mode, tempo, chords, structure_type, vulnerability, complexity
- `ProductionRuleBreak` - Enum for intentional production rule violations
- `NoteEvent` - Canonical note representation for MIDI generation

Structure types map mood to emotional contour:
- `"climb"` - Slow build (grief, dissociation)
- `"standard"` - Verse/chorus shape (rage, defiance)
- `"constant"` - Flat loop/mantra (neutral, awe)

### 2. Groove Engine V2 - Humanization (`groove/groove_engine.py`)

Psychoacoustically-informed "Drunken Drummer" algorithm:

```python
from music_brain.groove.groove_engine import apply_groove, GrooveSettings

settings = GrooveSettings(
    complexity=0.5,      # Timing looseness (0-1)
    vulnerability=0.6,   # Dynamic range/fragility (0-1)
)
humanized_notes = apply_groove(notes, settings)
```

Features:
- Gaussian timing jitter (not uniform - more human)
- Per-drum-type timing multipliers (kicks tighter, hats looser)
- Protected dropouts (kicks/snares rarely drop)
- Ghost note generation at high vulnerability
- Preset integration from `humanize_presets.json`

### 3. Tension Curves (`structure/tension.py`)

Bar-by-bar emotional intensity contours:

```python
from music_brain.structure.tension import generate_tension_curve

# Returns array of multipliers (0.5-1.5) for each bar
curve = generate_tension_curve(total_bars=64, structure_type="standard")
# Verse bars: ~0.6-0.7, Chorus: ~1.1, Bridge: ~1.2-1.5, Outro: ~0.5
```

### 4. Desktop Application

```bash
# Streamlit in browser (development)
streamlit run app.py

# Native window (requires pywebview)
python launcher.py
```

---

## Planned / Legacy Systems

> These systems exist in code but may not be fully wired end-to-end with the main TherapySession pipeline.

### Three-Phase Intent Schema (`session/intent_schema.py`)

A declarative system for song intent:
- **Phase 0**: Core Wound/Desire (deep interrogation)
- **Phase 1**: Emotional Intent (mood, vulnerability, narrative arc)
- **Phase 2**: Technical Constraints (genre, key, rule-to-break)

The Intent system is being superseded by the simpler `TherapySession` approach but the rule-breaking enums and validation logic remain useful.

### Old Groove Extraction (`groove/extractor.py`, `groove/applicator.py`)

Template-based groove extraction and application. The newer `groove_engine.py` (Humanization) is the recommended approach for adding human feel.

### Teaching Module (`session/teaching.py`)

Interactive lessons on rule-breaking and music theory. Works via CLI.

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
│   │   ├── genre_pocket_maps.json
│   │   ├── humanize_presets.json
│   │   ├── song_intent_examples.json
│   │   └── song_intent_schema.yaml
│   ├── groove/              # Groove extraction & humanization
│   │   ├── extractor.py     # Legacy groove extraction
│   │   ├── applicator.py    # Legacy groove application
│   │   ├── groove_engine.py # **ACTIVE** Humanization layer
│   │   └── templates.py     # Genre templates (used by legacy)
│   ├── structure/           # Harmonic analysis & generation
│   │   ├── chord.py         # Chord, ChordProgression, CHORD_QUALITIES
│   │   ├── progression.py   # diagnose_progression(), parse_progression_string()
│   │   ├── sections.py      # Section detection
│   │   ├── comprehensive_engine.py  # **ACTIVE** TherapySession pipeline
│   │   ├── tension.py       # **ACTIVE** Bar-by-bar tension curves
│   │   └── tension_curve.py # Preset tension curves
│   ├── session/             # Intent schema & teaching
│   │   ├── intent_schema.py # CompleteSongIntent, rule-breaking enums
│   │   ├── intent_processor.py # process_intent()
│   │   ├── teaching.py      # RuleBreakingTeacher
│   │   ├── interrogator.py  # SongInterrogator
│   │   └── generator.py     # Generation utilities
│   ├── audio/               # Audio analysis (requires librosa)
│   │   ├── feel.py          # analyze_feel(), AudioFeatures
│   │   └── reference_dna.py # ReferenceProfile
│   ├── text/                # Lyrical tools (requires markovify)
│   │   └── lyrical_mirror.py
│   ├── utils/               # Utilities
│   │   ├── midi_io.py
│   │   ├── instruments.py
│   │   └── ppq.py
│   └── daw/                 # DAW integration
│       ├── logic.py         # LogicProject, LOGIC_CHANNELS
│       └── markers.py       # MarkerEvent, export_markers_midi()
├── vault/                   # Knowledge base (Obsidian-compatible)
├── tests/                   # Test suite
├── app.py                   # Streamlit UI
├── launcher.py              # pywebview native wrapper
├── daiw.spec                # PyInstaller config
├── pyproject.toml           # Package configuration
└── requirements.txt         # Core dependencies
```

---

## Development Setup

### Installation
```bash
git clone https://github.com/yourusername/DAiW-Music-Brain.git
cd DAiW-Music-Brain
pip install -e .

# With optional dependencies
pip install -e ".[dev]"      # pytest, black, flake8, mypy
pip install -e ".[audio]"    # librosa, soundfile
pip install -e ".[theory]"   # music21
pip install -e ".[ui]"       # streamlit
pip install -e ".[desktop]"  # streamlit + pywebview
pip install -e ".[all]"      # Everything
```

### Dependencies
- **Core**: `mido>=1.2.10`, `numpy>=1.21.0`
- **Dev**: `pytest>=7.0.0`, `black>=22.0.0`, `flake8>=4.0.0`, `mypy>=0.900`
- **UI**: `streamlit>=1.28.0`
- **Desktop**: `streamlit`, `pywebview>=4.0.0`
- **Optional**: `librosa`, `soundfile`, `music21`, `markovify`

### Python Version
- Requires Python 3.9+

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_comprehensive_engine.py -v

# Run specific test
pytest tests/test_basic.py::TestImports -v
```

### Test Files
| File | Coverage |
|------|----------|
| `test_basic.py` | Core imports, templates, chord parsing |
| `test_comprehensive_engine.py` | TherapySession, HarmonyPlan, affect analysis |
| `test_groove_engine.py` | Humanization, complexity/vulnerability axes |
| `test_groove_extractor.py` | Legacy groove extraction |
| `test_intent_schema.py` | Intent schema validation |
| `test_intent_processor.py` | Intent processing pipeline |
| `test_cli_commands.py` | CLI command functionality |
| `test_cli_flow.py` | End-to-end CLI workflows |
| `test_daw_integration.py` | LogicProject, MIDI export |
| `test_bridge_integration.py` | Component integration |
| `test_midi_io.py` | MIDI file handling |
| `test_error_paths.py` | Error handling, edge cases |

---

## CLI Usage

The `daiw` command is installed with the package:

```bash
# Humanization (Drunken Drummer) - WORKING
daiw humanize drums.mid --style natural
daiw humanize drums.mid --complexity 0.6 --vulnerability 0.4
daiw humanize --list-presets

# Groove operations - requires underlying module integration
daiw extract drums.mid
daiw apply --genre funk track.mid

# Chord analysis
daiw diagnose "F-C-Am-Dm"
daiw analyze --chords song.mid

# Intent system
daiw intent new --title "My Song"
daiw intent process my_intent.json
daiw intent suggest grief
daiw intent list

# Teaching
daiw teach rulebreaking
```

---

## Code Style & Conventions

### Formatting
- **Line length**: 100 characters
- **Formatter**: black
- **Linter**: flake8, mypy

```bash
black music_brain/ tests/
mypy music_brain/
flake8 music_brain/ tests/
```

### Code Patterns

1. **Lazy imports in CLI** - Heavy modules imported only when needed
2. **Dataclasses** - `HarmonyPlan`, `TherapyState`, `AffectResult`, `NoteEvent`, `GrooveSettings`
3. **Enums** - `ProductionRuleBreak`, `HarmonyRuleBreak`, `VulnerabilityScale`, etc.
4. **Graceful degradation** - Optional deps checked at runtime

---

## Key API Signatures

### TherapySession
```python
session = TherapySession()
session.process_core_input(text: str) -> str  # Returns primary affect
session.set_scales(motivation: int, chaos_tolerance: float) -> None
plan = session.generate_plan() -> HarmonyPlan
```

### HarmonyPlan
```python
@dataclass
class HarmonyPlan:
    root_note: str           # "C", "F#"
    mode: str                # "ionian", "aeolian", "phrygian"
    tempo_bpm: int
    time_signature: str      # "4/4"
    length_bars: int
    chord_symbols: List[str]
    harmonic_rhythm: str
    mood_profile: str
    complexity: float        # 0.0 - 1.0
    vulnerability: float     # 0.0 - 1.0
    structure_type: str      # "standard" | "climb" | "constant"
```

### render_plan_to_midi
```python
render_plan_to_midi(
    plan: HarmonyPlan,
    output_path: str,
    vulnerability: float = 0.0
) -> str
```

### ProductionRuleBreak
```python
class ProductionRuleBreak(Enum):
    EXCESSIVE_MUD = "PRODUCTION_ExcessiveMud"
    PITCH_IMPERFECTION = "PRODUCTION_PitchImperfection"
    BURIED_VOCALS = "PRODUCTION_BuriedVocals"
    ROOM_NOISE = "PRODUCTION_RoomNoise"
    DISTORTION = "PRODUCTION_Distortion"
    MONO_COLLAPSE = "PRODUCTION_MonoCollapse"
```

---

## Important Design Decisions

1. **Emotional intent drives technical choices** - Never generate without understanding the "why"
2. **Rules are broken intentionally** - Every rule break requires justification
3. **Human imperfection is valued** - Lo-fi, pitch drift, room noise are features
4. **Contours over states** - Tension curves give songs shape
5. **Graceful degradation** - Core works without optional dependencies

---

## Common Tasks

### When Extending the Comprehensive Engine
1. Add fields to `HarmonyPlan` if new generation parameters needed
2. Update `generate_plan()` to set new fields based on mood
3. Update `render_plan_to_midi()` to use new fields
4. Add tests in `test_comprehensive_engine.py`

### When Adding Humanization Presets
1. Add entry to `music_brain/data/humanize_presets.json`
2. Include `groove_settings` with complexity, vulnerability
3. Add `therapy_state` to document intended emotional use

### When Adding Tension Curve Types
1. Add case in `generate_tension_curve()` in `tension.py`
2. Map moods to new type in `TherapySession.generate_plan()`

---

## Troubleshooting

### Import errors
- Ensure package is installed: `pip install -e .`
- Check Python version: `python --version` (requires 3.9+)

### Test failures
- Run with verbose: `pytest -v`
- Check data files exist in `music_brain/data/`

### MIDI generation issues
- Verify mido is installed
- Check `render_plan_to_midi()` has valid LogicProject/CHORD_QUALITIES imports

---

## Meta Principle

> "The audience doesn't hear 'borrowed from Dorian.' They hear 'that part made me cry.'"

The technical implementation serves emotional expression, never the other way around.
