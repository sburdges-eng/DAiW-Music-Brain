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
│   ├── Production_Workflows/ # DAW techniques + C++ architecture
│   │   ├── cpp_audio_architecture.md  # Brain/Body hybrid model
│   │   ├── juce_getting_started.md    # JUCE plugin development
│   │   └── osc_bridge_python_cpp.md   # OSC communication protocol
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

The system supports **45 intentional rule breaks** across **7 categories**:

- **Harmony:** `HarmonyRuleBreak` (6 options) — Modal interchange, parallel motion, unresolved dissonance
- **Rhythm:** `RhythmRuleBreak` (5 options) — Displacement, tempo fluctuation, polyrhythm
- **Arrangement:** `ArrangementRuleBreak` (5 options) — Buried vocals, dynamic extremes
- **Production:** `ProductionRuleBreak` (8 options) — Lo-fi, silence, clipping, mud
- **Melody:** `MelodyRuleBreak` (6 options) — Fragmentation, monotone, anti-climax
- **Texture:** `TextureRuleBreak` (6 options) — Frequency masking, timbral drift, walls of sound
- **Temporal:** `TemporalRuleBreak` (6 options) — Extended intro, abrupt ending, loop hypnosis

Each rule break requires emotional justification.

### Musical Concept Mappings

New enums for comprehensive music generation:

- **AffectState** (14 emotions) — grief, longing, defiance, hope, rage, etc.
- **TextureType** (8 types) — Ethereal, Intimate, Massive, Skeletal, etc.
- **TensionProfile** (8 profiles) — Build-release, sawtooth, slow burn, etc.
- **DensityLevel** (7 levels) — Solo through overwhelming
- **ModalColor** (7 modes) — With emotional associations

### Affect → Mode Mapping

`AFFECT_MODE_MAP` provides musical suggestions per emotion:
```python
get_affect_mapping("grief")
# → {"modes": ["Aeolian", "Phrygian"], "tempo_range": (50, 80), "density": "Sparse"}
```

### Texture → Production Mapping

`TEXTURE_PRODUCTION_MAP` provides production suggestions per texture:
```python
get_texture_production("Ethereal")
# → {"reverb": "long", "delay": "ambient", "stereo_width": "wide", ...}
```

### Full Palette Suggestions

`suggest_full_palette(emotion)` combines all mappings:
```python
suggest_full_palette("grief")
# → affect_mapping + suggested_rules + texture_options with production settings
```

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

## Development Workflow

### Standard Cycle (Python)

```
Change code → Run tests → Run application
```

```bash
# 1. Make changes to code
# 2. Run tests
pytest tests/ -v

# 3. Run/verify application
daiw <command>
```

### Standard Cycle (C++)

```
Change code → Run tests → Run application
```

```bash
# 1. Make changes to code
# 2. Build and run tests
# 3. Run application
```

**Always follow this cycle when making changes.** Tests must pass before committing.

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

## Future Integration / Rewrite Plans

### Comprehensive Engine (Planned)

The `structure/` module is planned for integration with a **Comprehensive Engine** for therapy-based music generation. This will bridge harmonic analysis with emotional/therapeutic workflows.

**Planned Features:**
- Therapy-based music generation workflows
- Emotional mapping to harmonic structures
- Session-aware progression recommendations
- Integration between `structure/` analysis and `session/` intent system

**Architecture Changes In Progress:**
- **Affect → Mode mapping** — Refining emotional-to-musical-mode translations
- **HarmonyPlan structure** — Restructuring harmony generation output
- **New engines being added:**
  - Groove engines (rhythm generation from feel)
  - Tension curves (dynamic tension over time)
  - Section markers (structural annotation)
  - Lyric mirror (text-to-music alignment)
  - Reference analysis (learn from existing tracks)

**Integration Points:**
- `structure/progression.py` → emotional diagnosis hooks
- `structure/chord.py` → mood-based chord suggestions
- `session/intent_processor.py` → harmonic generation from emotional intent

**When Working on Structure Module:**
- Keep APIs stable for future Comprehensive Engine integration
- Consider emotional context when adding chord analysis features
- Document any therapy/wellness-related use cases discovered
- Expect HarmonyPlan dataclass changes — keep dependent code loosely coupled

### Module Consolidation (Considered)

Future refactoring may consolidate:
- `session/` + `structure/` for unified emotion-to-harmony pipeline
- `groove/` + `audio/` for comprehensive feel analysis

### C++ Audio Engine (Future)

DAiW will evolve into a **hybrid Python/C++ architecture**:

| Component | Language | Role |
|-----------|----------|------|
| **Brain** | Python | Therapy logic, NLP, harmony generation, intent processing |
| **Body** | C++ (JUCE) | Real-time audio, plugin UI, DAW integration |

**Why C++ is needed for audio:**
- Python's Garbage Collector causes 5-20ms pauses (audio needs <3ms response)
- Python's GIL blocks multi-threading (audio needs dedicated thread)
- C++ is 50-100x faster for sample-by-sample math

**Why Python is needed for logic (don't port prematurely):**
- Text processing: `text.split()` vs 3 days writing a string splitter in C++
- UI prototyping: `st.slider()` vs weeks fighting JUCE lookAndFeel
- Math: `numpy` + `random` vs raw math functions or dependency hell

**The connection:** OSC (Open Sound Control) bridges Python Brain ↔ C++ Body

**Documentation:**
- `vault/Production_Workflows/cpp_audio_architecture.md` — Full architecture overview
- `vault/Production_Workflows/juce_getting_started.md` — JUCE setup guide
- `vault/Production_Workflows/osc_bridge_python_cpp.md` — OSC communication protocol
- `vault/Production_Workflows/hybrid_development_roadmap.md` — Phased development plan

### Phased Development Roadmap

**Phase 1: Stabilize the Brain (Python-only)** ← CURRENT
- Freeze API: `generate_session(text, motivation, chaos, vulnerability) -> HarmonyPlan`
- Ensure callable programmatically (no CLI/UI dependency)
- Return serializable structure:
  ```python
  {
    "tempo": int,
    "key": str,
    "time_sig": tuple,
    "notes": [{"pitch": int, "start_ms": float, "duration_ms": float, "velocity": int}]
  }
  ```

**Phase 2: Python OSC Server**
- Create `brain_server.py`:
  - Listens on `/daiw/generate`
  - Calls `generate_session(...)`
  - Responds on `/daiw/result`
- Test with Python OSC client (no C++ needed yet)

**Phase 3: JUCE Plugin Skeleton**
- Build basic plugin that:
  - Passes audio through unchanged
  - Has placeholder UI (text area, Generate button, Chaos knob)
  - Outputs fixed MIDI pattern
- Verify: builds as AU/VST3, shows in Logic

**Phase 4: Wire OSC Bridge**
- JUCE sends `/daiw/generate` with parameters
- Python brain processes, returns notes
- JUCE deserializes into `MidiBuffer`
- **DAiW is now: C++ frontend in Logic + Python brain outside + OSC nervous system**

### What Gets Ported to C++ (Eventually)

**Port later (if real-time needed):**
- Groove/humanization (real-time humanization on live MIDI)
- Subset of Harmony logic (play pad → get DAiW chords in real-time)

**Never port:**
- NLP / "what hurts you" therapy logic
- Lyric mirror
- High-level affect analysis

**When porting:**
- Take stable, tested math from Python
- Re-implement as small, deterministic C++ functions
- Leave heavy logic in Python where it belongs

## Notes for AI Assistants

1. **Respect the philosophy:** This tool is about making musicians braver, not replacing creativity
2. **Emotional justification matters:** Rule-breaking must have a "why"
3. **Test changes:** Run `pytest tests/ -v` before suggesting commits
4. **Type safety:** Use type hints and run mypy
5. **Follow Black formatting:** 100 char line limit
6. **Data-driven design:** Large datasets go in `data/` as JSON/YAML
7. **Document changes:** Update docstrings and vault documentation as needed
8. **Future-proof structure/:** Keep Comprehensive Engine integration in mind
