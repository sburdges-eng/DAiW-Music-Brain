# Groove Template Library

Extract, store, and apply human groove DNA to your MIDI.

---

## What This System Does

The Groove Template Library has two main tools:

1. **groove_extractor.py** — Analyzes MIDI files and extracts:
   - Push/pull signatures (timing offsets from grid)
   - Swing curves (off-beat delays)
   - Velocity curves (dynamics patterns)
   - Instrument stagger (cross-instrument timing)

2. **groove_applicator.py** — Applies groove to MIDI:
   - Genre pocket maps (pre-built genre feels)
   - Extracted templates (from real performances)
   - Basic humanization (random variation)

---

## Quick Start

### Installation

```bash
pip install mido --break-system-packages
```

### Extract Groove from MIDI

```bash
python groove_extractor.py extract drum_loop.mid --genre hiphop
```

### Apply Genre Pocket

```bash
python groove_applicator.py genre my_drums.mid hiphop
```

### Apply Extracted Template

```bash
python groove_applicator.py template my_drums.mid extracted_groove.json
```

---

## Tool 1: Groove Extractor

### What It Extracts

| Data Type | What It Measures |
|-----------|------------------|
| **Push/Pull** | How far ahead/behind each instrument plays from the grid |
| **Swing** | The ratio of on-beat vs off-beat timing |
| **Velocity Curves** | Accent patterns by beat position |
| **Instrument Stagger** | Timing relationships between instruments |

### Commands

**Extract single file:**
```bash
python groove_extractor.py extract song.mid --genre jazz --name "my_jazz_groove"
```

**Scan folder:**
```bash
python groove_extractor.py scan ~/MIDI/DrumLoops --genre hiphop
```

**List templates:**
```bash
python groove_extractor.py list
python groove_extractor.py list --genre jazz
```

**View template details:**
```bash
python groove_extractor.py detail 5
```

**Export template:**
```bash
python groove_extractor.py export 5 --output my_groove.json
```

### Output

Templates are saved to:
- **JSON files:** `~/Music-Brain/groove-library/templates/`
- **SQLite database:** `~/Music-Brain/groove-library/groove_templates.db`

### Example Output

```
Extracting groove from: classic_hiphop_beat.mid
  PPQ: 480, BPM: 92.0
  Instruments found: ['drums_kick', 'drums_snare', 'drums_hihat_closed', 'bass']
  Analyzing: drums_kick (48 notes)
  Analyzing: drums_snare (32 notes)
  Analyzing: drums_hihat_closed (128 notes)
  Analyzing: bass (64 notes)
Saved template: ~/Music-Brain/groove-library/templates/classic_hiphop_beat.json
Saved to database with ID: 1
```

---

## Tool 2: Groove Applicator

### Apply Genre Pocket

Pre-built genre feels based on analysis of many tracks:

```bash
python groove_applicator.py genre my_beat.mid hiphop
python groove_applicator.py genre my_beat.mid jazz --intensity 0.7
python groove_applicator.py genre my_beat.mid lofi --output output.mid
```

**Intensity:** 0.0 = no effect, 1.0 = full effect

### Available Genres

```bash
python groove_applicator.py list-genres
```

| Genre | Feel | Swing |
|-------|------|-------|
| `hiphop` | Laid-back snare, driving hats | 58% |
| `trap` | Tight, straight | 52% |
| `rnb` | Deep pocket, heavy swing | 62% |
| `funk` | Tight, driving, syncopated | 54% |
| `jazz` | Triplet swing, floating | 66% |
| `rock` | Tight, powerful | 50% |
| `metal` | Machine-tight | 50% |
| `reggae` | Behind the beat, one drop | 55% |
| `house` | Four-on-floor, groove in hats | 54% |
| `techno` | Mechanical, hypnotic | 50% |
| `lofi` | Everything behind, heavy swing | 62% |
| `gospel` | Pocket feel, swing | 60% |
| `country` | Train beat, tight | 52% |

### Apply Extracted Template

Use grooves extracted from real performances:

```bash
python groove_applicator.py template my_beat.mid ~/Music-Brain/groove-library/templates/classic_groove.json
```

### Basic Humanization

No template needed — just adds random variation:

```bash
python groove_applicator.py humanize my_beat.mid --timing 15 --velocity 20
```

| Parameter | Description |
|-----------|-------------|
| `--timing` | Timing variation in ticks (default: 10) |
| `--velocity` | Velocity variation (default: 15) |
| `--intensity` | How much to apply (0.0-1.0) |

---

## Understanding the Data

### Push/Pull Signatures

**Positive offset** = behind the beat (laid back)
**Negative offset** = ahead of the beat (driving)

Example:
```
Instrument     Beat   Offset     Meaning
kick           0.0    0.0        On grid (anchor)
snare          2.0    +15.0      15 ticks behind (pocket)
hihat          0.5    -5.0       5 ticks ahead (drives)
bass           0.0    +12.0      Behind with snare
```

### Swing Ratio

| Ratio | Feel |
|-------|------|
| 50% | Straight (no swing) |
| 54% | Subtle shuffle |
| 58% | Noticeable groove |
| 62% | Heavy swing |
| 66% | Triplet feel |

### Instrument Stagger

How instruments relate to each other:

```
snare is 15 ticks behind kick
bass is 12 ticks behind kick
hihat is 5 ticks ahead kick
```

This creates the "pocket" feel.

---

## Workflow Examples

### Workflow 1: Extract from Reference

1. Get MIDI from a track you love (or transcribe it)
2. Extract the groove:
   ```bash
   python groove_extractor.py extract reference_drums.mid --genre hiphop --name "dilla_feel"
   ```
3. Apply to your production:
   ```bash
   python groove_applicator.py template my_drums.mid ~/Music-Brain/groove-library/templates/dilla_feel.json
   ```

### Workflow 2: Genre Pocket

1. Program drums quantized to grid
2. Apply genre pocket:
   ```bash
   python groove_applicator.py genre quantized_drums.mid hiphop --intensity 0.8
   ```
3. Import result into Logic Pro

### Workflow 3: Build Template Library

1. Collect MIDI drum loops by genre
2. Batch extract:
   ```bash
   python groove_extractor.py scan ~/MIDI/HipHop --genre hiphop
   python groove_extractor.py scan ~/MIDI/Jazz --genre jazz
   python groove_extractor.py scan ~/MIDI/Funk --genre funk
   ```
3. Query your library:
   ```bash
   python groove_extractor.py list --genre hiphop
   ```

---

## Integration with Logic Pro

### Export and Import

1. Export quantized MIDI from Logic
2. Process with groove_applicator
3. Import result back into Logic
4. Replace original region

### Using with Logic's Groove Templates

You can also export extracted grooves as Logic-compatible templates (future feature).

---

## Database Schema

The SQLite database stores:

**groove_templates** — Main template info
- name, source_file, genre, subgenre
- bpm_original, time_signature, bars, ppq

**push_pull_signatures** — Timing offsets
- instrument, beat_position, offset_ticks
- velocity_mean, velocity_std

**swing_curves** — Swing data
- instrument, subdivision, swing_ratio

**velocity_curves** — Dynamics patterns
- instrument, beat_position, velocity stats

**instrument_stagger** — Cross-instrument timing
- instrument_a, instrument_b, mean_offset

---

## Technical Notes

### PPQ (Pulses Per Quarter Note)

MIDI timing resolution. Standard is 480 PPQ.
All offsets are normalized to 480 PPQ internally.

### Grid Division

Analysis uses 16th note grid (16 divisions per bar in 4/4).
Swing is calculated on 8th note grid.

### Supported Formats

- .mid and .midi files
- Type 0 and Type 1 MIDI
- Any PPQ (normalized internally)

---

## Files

| File | Purpose |
|------|---------|
| `groove_extractor.py` | Extract grooves from MIDI |
| `groove_applicator.py` | Apply grooves to MIDI |
| `genre_pocket_maps.json` | Pre-built genre feels |

---

## Related
- [[Humanizing Your Music]]
- [[Groove and Rhythm Guide]]
- [[Drum Programming Guide]]

