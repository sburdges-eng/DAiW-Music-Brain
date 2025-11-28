# DAiW – Digital Audio Intimate Workstation

**Interrogate Before Generate.**

DAiW is an affect-driven composition engine that transforms emotional input into MIDI compositions. Tell it what hurts, not what chords you want.

## Quick Start

```bash
# Install
pip install -e .

# Or with all optional dependencies
pip install -e ".[all]"

# Run tests
pytest

# MVP test
python mvp_test.py

# Launch UI
streamlit run app.py

# Or as desktop app (requires pywebview)
python launcher.py
```

## Architecture

```
music_brain/
├── daw/
│   └── logic.py          # MIDI export / Logic Pro bridge
├── groove/
│   └── engine.py         # Humanization / timing jitter
├── structure/
│   ├── tension.py        # Bar-level intensity curves
│   ├── progression.py    # Chord parsing
│   └── comprehensive_engine.py  # THE BRAIN
├── lyrics/
│   └── engine.py         # Markov-based lyric mirror
└── audio_refinery.py     # Sample processing pipelines

audio_vault/
├── raw/                  # Drop source samples here
├── refined/              # Processed samples output
├── output/               # Generated MIDI files
└── kits/                 # Kit mapping guides
```

## Core Flow

1. **Input wound text** → `TherapySession.process_core_input()`
2. **Affect analysis** → mood detection (grief, rage, fear, etc.)
3. **Mode selection** → grief→aeolian, rage→phrygian, etc.
4. **Plan generation** → tempo, length, chords, tension curve
5. **MIDI render** → notes shaped by tension curve → groove engine → file

## The Kelly Song

This toolkit was built specifically to support processing grief through music. The affect analyzer understands compound trauma.

## Commands

```bash
# CLI
daiw                    # Interactive mood → MIDI

# Sample processing
daiw-refinery          # Process all samples
python -m music_brain.audio_refinery 02_Rhythm_Drums  # Single folder

# Kit building
python generate_demo_samples.py   # Create synthetic test kit
python build_logic_kit.py         # Generate MIDI mapping guide
```

## License

MIT
