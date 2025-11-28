# Music Brain

A complete music production analysis toolkit for MIDI and audio.

## Features

### Groove Analysis & Application
- **Extract groove** from any MIDI file — timing offsets, swing, velocity curves
- **13 pre-built genre pockets** — hip-hop, trap, R&B, funk, jazz, rock, metal, reggae, house, techno, lo-fi, gospel, country
- **Per-instrument timing** — kick stays on grid, snare behind, hihat ahead
- **Track-safe MIDI modification** — preserves structure, doesn't flatten

### Structure Analysis
- **Chord detection** — major, minor, 7th, extended chords
- **Progression matching** — I-V-vi-IV, ii-V-I, 12-bar blues, etc.
- **Section detection** — intro, verse, chorus, bridge, outro
- **Pattern recognition** — find recurring progressions

### Audio Analysis
- **Transient drift** — timing looseness measurement
- **RMS swing** — dynamic groove
- **Frequency balance** — mix fingerprint by band
- **Genre matching** — compare against 14 genre templates

## Installation

```bash
# Basic (MIDI only)
pip install mido

# Full (with audio analysis)
pip install mido librosa numpy soundfile

# Install package
cd music_brain
pip install .
```

## Quick Start

### Command Line

```bash
# === GROOVE ===
# Extract groove from MIDI
music-brain groove extract drums.mid --genre hiphop --save

# Apply hip-hop pocket to your beat
music-brain groove apply my_drums.mid hiphop --intensity 0.8

# Basic humanization
music-brain groove humanize quantized.mid --timing 10 --velocity 15

# List available genres
music-brain groove genres

# === STRUCTURE ===
# Analyze chords
music-brain structure analyze song.mid

# Show progressions for a genre
music-brain structure progressions jazz

# Detect sections
music-brain sections song.mid

# === GENERATE ===
# Generate a new song!
music-brain new-song --genre hiphop --bpm 92 --key Am --title "Midnight Dreams"

# === DAW ===
# Create Logic Pro session setup
music-brain daw setup hiphop "My New Track" --bpm 92 --script setup.scpt

# Show track templates for a genre
music-brain daw tracks rock

# === INFO ===
# Show MIDI info
music-brain info song.mid
```

### Python API

```python
from music_brain import (
    # Groove
    extract_groove, apply_groove, GENRE_POCKETS,
    # Structure
    load_midi, analyze_chords, detect_sections,
    # Generate
    generate_song,
    # DAW
    create_logic_session
)

# === EXTRACT GROOVE ===
template = extract_groove('drums.mid', genre='hiphop')
print(f"Swing: {template.swing}")
print(f"Push/pull: {template.push_pull}")

# === APPLY GENRE POCKET ===
apply_groove('my_drums.mid', 'output.mid', 'hiphop', intensity=0.8)

# === ANALYZE STRUCTURE ===
data = load_midi('song.mid')
chords = analyze_chords(data.all_notes, ppq=data.ppq)
sections = detect_sections(data)

# === GENERATE A SONG ===
structure, midi_path = generate_song(
    genre='lofi',
    bpm=75,
    key=9,  # A
    title='Rainy Night',
    humanize=True
)
print(f"Generated: {midi_path}")
print(f"Structure: {[s.name for s in structure.sections]}")

# === DAW SETUP ===
session = create_logic_session(
    genre='hiphop',
    name='My Beat',
    bpm=92,
    output_script='setup.scpt'
)

# === GET GENRE POCKET ===
pocket = GENRE_POCKETS['jazz']
print(f"Jazz swing: {pocket['swing']}")  # 0.66 (triplet)
```

## Genre Pockets

| Genre | Swing | Snare | Hihat | Feel |
|-------|-------|-------|-------|------|
| hiphop | 58% | +15 behind | -5 ahead | Laid-back pocket |
| trap | 52% | +5 | 0 | Tight, hard |
| rnb | 62% | +20 | +5 | Deep pocket |
| funk | 54% | 0 grid | -5 ahead | Tight, driving |
| jazz | 66% | +8 | +3 | Floating, loose |
| rock | 50% | 0 | -3 | Straight, powerful |
| metal | 50% | 0 | 0 | Machine-tight |
| lofi | 62% | +20 | +10 | Lazy, behind |

## Architecture

```
music_brain/
├── groove/
│   ├── extractor.py      # Multi-bar histogram, swing detection
│   ├── applicator.py     # Track-safe, beat-aware application
│   ├── templates.py      # Storage, versioning, merging
│   └── pocket_rules.py   # 13 genre pocket maps
├── structure/
│   ├── chord.py          # Chord detection
│   ├── progression.py    # Pattern matching (30+ progressions)
│   └── sections.py       # Section boundary detection
├── session/
│   └── generator.py      # Auto song generation
├── daw/
│   └── logic_pro.py      # Logic Pro AppleScript automation
├── audio/
│   └── feel.py           # Audio analysis (librosa)
├── utils/
│   ├── midi_io.py        # Track-safe MIDI I/O
│   ├── ppq.py            # PPQ normalization & scaling
│   └── instruments.py    # GM instrument classification
└── cli.py                # Unified command line
```

## Key Technical Features

### Track-Safe MIDI Modification
Unlike naive implementations that flatten all tracks into soup, Music Brain:
- Preserves per-track event boundaries
- Maintains controller curves, pitch bends, meta events
- Rebuilds delta-time correctly after modification
- Sorts by absolute time, then re-deltas

### PPQ Normalization
- Normalizes all input to 480 PPQ standard
- Scales timing values when applying to different PPQ files
- Templates are portable across DAWs and files

### Beat-Position-Aware Application
- Applies correct offset for each grid position
- Doesn't randomly pick indices
- Snare on beat 2 gets different treatment than hihat on beat 1

### Real Swing Extraction
- Actually measures on-beat to off-beat ratios
- Doesn't hardcode 0.0
- Detects triplet feel vs. straight vs. shuffle

## Credits

Built by merging the best ideas from multiple AI systems:
- Claude: Genre pocket maps, per-instrument offsets, chord analysis
- ChatGPT: Multi-bar histograms, template versioning, CLI structure
- Final integration: This unified package

## License

MIT
