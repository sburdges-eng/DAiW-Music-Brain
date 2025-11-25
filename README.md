# DAiW - Digital Audio Intelligent Workstation

> A Python toolkit for music production intelligence: groove extraction, chord analysis, arrangement generation, and AI-assisted songwriting.
>
> **Philosophy: "Interrogate Before Generate"** — The tool shouldn't finish art for people. It should make them braver.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Status: Alpha (v0.3.0)

This project is in **active development**. The current architecture centers on the **TherapySession** engine rather than the originally planned YAML-based intent pipeline.

### Working

| Component | Description | Location |
|-----------|-------------|----------|
| **TherapySession** | Affect analysis → mode/tempo/chord generation | `structure/comprehensive_engine.py` |
| **HarmonyPlan** | Blueprint for generation (root, mode, tempo, bars, chords) | `structure/comprehensive_engine.py` |
| **Groove Engine** | Drunken Drummer humanization (Gaussian jitter, velocity shaping) | `groove/engine.py` |
| **Groove Engine v2** | Advanced humanization with per-drum handling and presets | `groove/groove_engine.py` |
| **Tension Curves** | Bar-wise dynamic tension multipliers | `structure/tension_curve.py` |
| **LogicProject** | MIDI export with proper delta time calculation | `daw/logic.py` |
| **Lyric Mirror** | Markov/cut-up lyric fragment generation | `lyrics/engine.py` |
| **Audio Refinery** | Sample processing (Industrial/Glitch, Tape Rot pipelines) | `audio_refinery.py` |
| **Desktop App** | Streamlit UI + native window via pywebview | `app.py`, `launcher.py` |

### Partial / Legacy

| Component | Status | Notes |
|-----------|--------|-------|
| Full CLI commands | Partial | Many commands exist but not all fully tested |
| Intent YAML pipeline | Legacy | Three-phase schema exists; `TherapySession` is the current interface |
| Teaching module | Legacy | `session/teaching.py` exists but not actively maintained |
| Groove extractor/applicator | Legacy | Template-based system in `groove/extractor.py`, `applicator.py` |
| Sections detection | Partial | `structure/sections.py` exists separately from main engine |
| Audio feel analysis | Partial | Requires optional `librosa` dependency |

### Primary Interface

The recommended interface for this alpha is the **Desktop App**:

```bash
# Option 1: Streamlit in browser
streamlit run app.py

# Option 2: Native window (requires pywebview)
python launcher.py
```

---

## Overview

DAiW (Digital Audio intelligent Workstation) combines:
- **Music Brain** - Python analysis engine for MIDI/audio
- **Intent Schema** - Three-phase deep interrogation for songwriting
- **Rule-Breaking Engine** - Intentional theory violations for emotional impact
- **Vault** - Knowledge base of songwriting guides and theory references
- **CLI** - Command-line tools for groove extraction, chord analysis, and AI-assisted composition

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/DAiW-Music-Brain.git
cd DAiW-Music-Brain

# Install as package
pip install -e .
```

## Quick Start

### Desktop App (Recommended)

The primary interface is the Streamlit desktop app:

```bash
# Install with UI dependencies
pip install -e ".[ui]"

# Run in browser
streamlit run app.py

# Or with native window (requires pywebview)
pip install -e ".[desktop]"
python launcher.py
```

### Python API (Current Engine)

```python
from music_brain.structure.comprehensive_engine import (
    TherapySession,
    HarmonyPlan,
    render_plan_to_midi,
)

# Create a therapy session
session = TherapySession()

# Process emotional input → affect analysis
affect = session.process_core_input("I feel dead inside because I chose safety over freedom")
# Returns: "dissociation" (detected primary affect)

# Set motivation and chaos tolerance
session.set_scales(motivation=7, chaos=0.5)

# Generate harmony plan
plan = session.generate_plan()
# Returns HarmonyPlan with:
#   - root_note: "C"
#   - mode: "locrian" (mapped from dissociation)
#   - tempo_bpm: 100
#   - length_bars: 32
#   - chord_symbols: ["Cdim", "DbMaj7", "Ebm", "Cdim"]

# Render to MIDI
render_plan_to_midi(plan, "output.mid")
```

### Groove Humanization

```python
from music_brain.groove.groove_engine import apply_groove, GrooveSettings

# Humanize note events with "Drunken Drummer" algorithm
events = [{"start_tick": 0, "velocity": 80, "pitch": 36}, ...]
humanized = apply_groove(
    events,
    complexity=0.6,      # Timing chaos (0.0-1.0)
    vulnerability=0.5,   # Dynamic fragility (0.0-1.0)
)
```

### CLI (Partial)

```bash
# Humanize drum MIDI (working)
daiw humanize drums.mid --style natural

# Diagnose harmonic issues (working)
daiw diagnose "F-C-Am-Dm"

# Other commands exist but may not be fully tested
daiw --help
```

---

### Legacy: Intent-Based Generation

> **Note:** The three-phase intent system exists in the codebase but `TherapySession` is the current primary interface.

<details>
<summary>Click to expand legacy intent API</summary>

```python
from music_brain.session import (
    CompleteSongIntent, SongRoot, SongIntent, TechnicalConstraints,
    suggest_rule_break
)
from music_brain.session.intent_processor import process_intent

# Create song intent
intent = CompleteSongIntent(
    song_root=SongRoot(
        core_event="Finding someone I loved after they chose to leave",
        core_resistance="Fear of making it about me",
        core_longing="To process without exploiting the loss",
    ),
    song_intent=SongIntent(
        mood_primary="Grief",
        mood_secondary_tension=0.3,
        vulnerability_scale="High",
        narrative_arc="Slow Reveal",
    ),
    technical_constraints=TechnicalConstraints(
        technical_key="F",
        technical_mode="major",
        technical_rule_to_break="HARMONY_ModalInterchange",
        rule_breaking_justification="Bbm makes hope feel earned and bittersweet",
    ),
)

# Process intent to generate elements
result = process_intent(intent)
```

</details>

## Current Engine (v0.3.x)

### TherapySession

The core engine processes emotional text and generates a `HarmonyPlan`:

```python
session = TherapySession()
affect = session.process_core_input(text)  # Returns: "grief", "rage", "awe", etc.
session.set_scales(motivation, chaos)
plan = session.generate_plan()
```

**Affect → Mode Mapping:**

| Affect | Mode | Typical Tempo |
|--------|------|---------------|
| grief | aeolian | 70 BPM |
| rage | phrygian | 130 BPM |
| awe | lydian | 90 BPM |
| nostalgia | dorian | 100 BPM |
| dissociation | locrian | 100 BPM |
| defiance | mixolydian | 130 BPM |
| tenderness | ionian | 100 BPM |

**Motivation → Length:**

| Motivation | Length |
|------------|--------|
| 1-3 | 16 bars |
| 4-7 | 32 bars |
| 8-10 | 64 bars |

### HarmonyPlan Fields

```python
@dataclass
class HarmonyPlan:
    root_note: str           # "C", "F#"
    mode: str                # "ionian", "aeolian", "phrygian", etc.
    tempo_bpm: int
    time_signature: str      # "4/4"
    length_bars: int
    chord_symbols: List[str] # ["Cm7", "Fm9"]
    harmonic_rhythm: str     # "1_chord_per_bar"
    mood_profile: str
    complexity: float        # 0.0 - 1.0
```

### Groove Engine v2

The "Drunken Drummer" algorithm applies psychoacoustically-informed humanization:

```python
from music_brain.groove.groove_engine import apply_groove

humanized = apply_groove(
    events,
    complexity=0.6,      # Timing chaos: off-grid, occasional dropouts
    vulnerability=0.5,   # Dynamic range: wider variance, softer
    ppq=480,
)
```

- **Gaussian timing jitter** (not uniform) - sounds more human
- **SAFE_DRIFT_LIMIT** prevents notes from drifting too far
- **Velocity shaping** based on vulnerability
- **Per-drum protection** - kicks/snares less likely to drop out

### Tension Curves

Apply bar-wise tension multipliers for dynamic "breathing":

```python
from music_brain.structure.tension_curve import (
    apply_tension_curve, generate_curve_for_bars
)

curve = generate_curve_for_bars(32, "verse_chorus")
events = apply_tension_curve(events, bar_ticks, curve)
```

Presets: `verse_chorus`, `slow_build`, `catharsis`, `descent`, `spiral`, `static`

---

## Legacy: Intent Schema

> **Note:** The three-phase intent system is a design target. Current implementation uses `TherapySession`.

<details>
<summary>Click to expand intent schema documentation</summary>

### Three-Phase Deep Interrogation

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

</details>

## Desktop Application

DAiW includes a native desktop application:

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI - the main interface |
| `launcher.py` | Native window wrapper using pywebview |
| `daiw.spec` | PyInstaller configuration for building executables |

### Running

```bash
# Development (browser)
streamlit run app.py

# Native window
python launcher.py
```

### Building Standalone Executable

```bash
pip install -e ".[build]"
pyinstaller daiw.spec --clean --noconfirm

# Output: dist/DAiW/DAiW (Linux), dist/DAiW.app (macOS), dist/DAiW/DAiW.exe (Windows)
```

---

## Project Structure

```
DAiW-Music-Brain/
├── app.py                    # Streamlit UI (main interface)
├── launcher.py               # Native window wrapper (pywebview)
├── daiw.spec                 # PyInstaller build config
│
├── music_brain/              # Python package
│   ├── __init__.py           # Public API exports (v0.3.0)
│   ├── cli.py                # CLI entry point
│   ├── audio_refinery.py     # Audio Refinery (Industrial/Tape Rot)
│   │
│   ├── structure/            # Core engine
│   │   ├── comprehensive_engine.py  # TherapySession, HarmonyPlan
│   │   ├── tension_curve.py         # Dynamic tension curves
│   │   ├── chord.py                 # Chord parsing
│   │   ├── progression.py           # Progression analysis
│   │   └── sections.py              # Section detection (partial)
│   │
│   ├── groove/               # Groove/humanization
│   │   ├── engine.py                # Drunken Drummer (simple)
│   │   ├── groove_engine.py         # Drunken Drummer (v2 advanced)
│   │   ├── extractor.py             # Legacy template extraction
│   │   ├── applicator.py            # Legacy template application
│   │   └── templates.py             # Genre templates
│   │
│   ├── lyrics/               # Lyric generation
│   │   └── engine.py                # Lyric Mirror (Markov/cut-up)
│   │
│   ├── daw/                  # DAW integration
│   │   └── logic.py                 # LogicProject, MIDI export
│   │
│   ├── text/                 # Legacy text processing
│   │   └── lyrical_mirror.py        # (older implementation)
│   │
│   ├── audio/                # Audio analysis (requires librosa)
│   │   ├── feel.py                  # Feel analysis
│   │   └── reference_dna.py         # Reference track analysis
│   │
│   ├── session/              # Legacy intent system
│   │   ├── intent_schema.py         # Three-phase schema
│   │   ├── intent_processor.py      # Intent processing
│   │   ├── teaching.py              # Teaching module
│   │   └── interrogator.py          # Interrogator
│   │
│   ├── utils/                # Utilities
│   │   ├── midi_io.py
│   │   ├── instruments.py
│   │   └── ppq.py
│   │
│   └── data/                 # JSON/YAML data files
│       └── corpus/           # Lyric corpus for Markov generation
│
├── vault/                    # Knowledge base (Obsidian-compatible)
│
└── tests/                    # Test suite
    ├── test_comprehensive_engine.py
    ├── test_groove_engine.py
    └── ...
```

---

<details>
<summary>Legacy: Rule-Breaking Categories</summary>

### Harmony
| Rule | Effect | Use When |
|------|--------|----------|
| `HARMONY_AvoidTonicResolution` | Unresolved yearning | Grief, longing |
| `HARMONY_ModalInterchange` | Bittersweet color | Making hope feel earned |
| `HARMONY_ParallelMotion` | Power, defiance | Anger, punk energy |

### Rhythm
| Rule | Effect | Use When |
|------|--------|----------|
| `RHYTHM_ConstantDisplacement` | Off-kilter anxiety | Before a dramatic shift |
| `RHYTHM_TempoFluctuation` | Organic breathing | Intimacy, vulnerability |

### Production
| Rule | Effect | Use When |
|------|--------|----------|
| `PRODUCTION_BuriedVocals` | Dissociation, texture | Dreams, distance |
| `PRODUCTION_PitchImperfection` | Emotional honesty | Raw vulnerability |

</details>

## Features

### Current (v0.3.x)

- **Affect-based generation** - Text → mode/tempo/chord mapping via `TherapySession`
- **MIDI export** - Full MIDI rendering via `LogicProject`
- **Drum humanization** - "Drunken Drummer" algorithm with Gaussian jitter
- **Tension curves** - Bar-wise dynamic shaping (verse_chorus, catharsis, etc.)
- **Lyrical fragments** - Markov/cut-up text generation

### Partial

- **CLI commands** - `humanize`, `diagnose` working; others exist but not fully tested
- **Chord analysis** - Basic progression parsing and diagnosis
- **Section detection** - Exists but separate from main engine

### Legacy/Planned

- **Three-phase intent schema** - Design exists in codebase
- **Teaching module** - Exists but not actively maintained
- **Template-based groove** - Legacy extractor/applicator

## Requirements

- Python 3.9+
- mido (MIDI I/O)
- numpy (numerical analysis)

**Optional:**
- streamlit (web UI)
- pywebview (native window)
- librosa (audio analysis)
- music21 (advanced theory)
- markovify (lyric generation)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built for musicians who think in sound, not spreadsheets
- Inspired by the lo-fi bedroom recording philosophy
- **"The wrong note played with conviction is the right note."**
