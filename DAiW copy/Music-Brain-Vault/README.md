# 🎵 Music Brain

**Your Personal Music Production Knowledge Base, AI Assistant & Groove Tools**

---

## What Is This?

A comprehensive music production system with:

- **88+ guides** — Songwriting, production, mixing, business
- **Groove extraction tools** — Extract human feel from MIDI
- **Genre pocket maps** — Pre-built feels for 13+ genres
- **AI integration** — Local AI chat with your knowledge
- **Sample cataloging** — Organize and search your sounds

---

## Quick Navigation

| Folder | What's Inside |
|--------|---------------|
| [[Songwriting/]] | 11 songwriting guides |
| [[Workflows/]] | 34 production & mixing guides |
| [[Business/]] | 10 music business guides |
| [[Gear/]] | Equipment and plugin guides |
| [[Theory/]] | 1,300+ vocabulary terms |
| [[Templates/]] | 13 ready-to-use templates |
| [[AI-System/]] | Tools, setup guides, groove library |

**Start here:** [[Home]] — Your dashboard with live queries

---

## 🥁 Groove Template Library

Extract and apply human groove DNA to your MIDI.

| Tool | Purpose |
|------|---------|
| `groove_extractor.py` | Extract timing/feel from MIDI files |
| `groove_applicator.py` | Apply groove to your productions |
| `genre_pocket_maps.json` | 13 pre-built genre feels |

```bash
# Extract groove from a MIDI file
python groove_extractor.py extract drums.mid --genre hiphop

# Apply hip-hop pocket to your beat
python groove_applicator.py genre my_drums.mid hiphop
```

**Genres:** `hiphop` `trap` `rnb` `funk` `jazz` `rock` `metal` `reggae` `house` `techno` `lofi` `gospel` `country`

See [[Groove Template Library]] for full documentation.

---

## 🎹 Structural Pattern Library

Analyze MIDI for harmonic and melodic patterns.

| Tool | Purpose |
|------|---------|
| `structural_extractor.py` | Chord/melody/progression analysis |
| `chord_progression_families.json` | 50+ common progressions by genre |

```bash
# Analyze a MIDI file
python structural_extractor.py analyze song.mid --genre pop

# Find songs with specific progressions
python structural_extractor.py find-progression "I-V-vi-IV"
```

**Extracts:** Chord families, recurring progressions, melody contours, phrase lengths, harmonic rhythm

See [[Structural Pattern Library]] for full documentation.

---

## 🎧 Audio Feel Extractor

Analyze production characteristics from audio files.

| Tool | Purpose |
|------|---------|
| `audio_feel_extractor.py` | Transient/dynamics/spectral/stereo analysis |
| `genre_mix_fingerprints.json` | 14 genre reference templates |

```bash
# Analyze an audio file
python audio_feel_extractor.py analyze track.wav --genre hiphop

# Compare two tracks
python audio_feel_extractor.py compare 3 7
```

**Extracts:** Transient drift, RMS swing, spectral movement, frequency balance, stereo width, genre matching

See [[Audio Feel Extractor]] for full documentation.

---

## Getting Started

1. **Read guides** — Start with [[Humanizing Your Music]] or any genre guide
2. **Use templates** — Document your songs, sessions, and gear
3. **Run the tools** — Extract grooves, catalog samples
4. **Set up AI** — Follow [[AI Assistant Setup Guide]]

---

## Content Overview

### Songwriting (11 guides)
Fundamentals, melody, lyrics, chords, structure, hooks, co-writing, editing, writer's block, exercises

### Production (34 guides)
- **Humanization:** Drums, bass, synths, vocals, piano, guitar, strings
- **Mixing:** EQ, compression, reverb/delay, reference analysis
- **Genres:** Lo-fi, hip-hop, rock, EDM, jazz, R&B, metal, ambient, folk, pop, country, indie
- **Techniques:** Sound design, sampling, groove, dynamics

### Business (10 guides)
Distribution, release strategy, copyright, sync licensing, fanbase, monetization, live performance, social media

---

## Tags System

### Status
`#status/idea` `#status/in-progress` `#status/mixing` `#status/mastering` `#status/complete` `#status/archived`

### Genre
`#genre/rock` `#genre/electronic` `#genre/hiphop` `#genre/jazz` `#genre/folk` `#genre/ambient`

### Key & Tempo
`#key/C` through `#key/B` | `#key/Am` through `#key/Gm`
`#tempo/slow` (<80) | `#tempo/mid` (80-120) | `#tempo/fast` (>120)

---

## Requirements

**For guides only:** Just Obsidian

**For tools:**
```bash
pip install mido librosa numpy soundfile --break-system-packages
```

---

## Version
- Files: 93 markdown guides + 6 Python tools + 4 JSON data files
- MIDI Tools: Groove extractor/applicator, structural pattern extractor
- Audio Tools: Audio feel extractor, audio cataloger
- Data: Genre pocket maps (13), mix fingerprints (14), chord progressions (50+)
- System: Obsidian + AnythingLLM + Ollama
- Author: Sean

