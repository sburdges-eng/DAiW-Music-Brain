# MIDI Structure Analyzer

Extract chord progressions, melody shapes, phrase patterns, and harmonic rhythm from MIDI files.

---

## What This Tool Does

Analyzes the **harmonic and structural DNA** of MIDI files:

| Analysis Type | What It Extracts |
|---------------|------------------|
| **Chord Detection** | Root, quality, duration, family |
| **Progression Patterns** | ii-V-I, I-V-vi-IV, etc. |
| **Melody Contours** | Shape, direction, step/leap ratio |
| **Phrase Structure** | Lengths, density, common patterns |
| **Harmonic Rhythm** | Chord change frequency, consistency |
| **Key Detection** | Key center and mode |

---

## Quick Start

### Installation

```bash
pip install mido --break-system-packages
```

### Analyze a MIDI File

```bash
python structure_analyzer.py analyze song.mid --genre pop
```

### Scan a Folder

```bash
python structure_analyzer.py scan ~/MIDI/Songs --genre jazz
```

### List Analyses

```bash
python structure_analyzer.py list --key C
```

### View Details

```bash
python structure_analyzer.py detail 5
```

---

## Output Data

### Chord Analysis

For each chord detected:

```json
{
  "bar": 0,
  "beat": 0,
  "root": "C",
  "type": "maj7",
  "family": "major",
  "duration_beats": 4.0,
  "confidence": 0.85
}
```

### Chord Families

Distribution across families:
- **major**: maj, maj7, maj9, 6, add9
- **minor**: min, min7, min9, min6
- **dominant**: dom7, dom9
- **diminished**: dim, dim7, hdim7
- **suspended**: sus2, sus4

### Detected Progressions

Common patterns it recognizes:

| Pattern | Name | Feel |
|---------|------|------|
| I-V-vi-IV | Axis Progression | Anthemic pop |
| ii-V-I | Jazz Standard | Resolution |
| I-IV-V-I | Three Chord Rock | Classic rock |
| I-vi-IV-V | 50s Progression | Doo-wop |
| vi-IV-I-V | Minor Start | Emotional pop |
| i-VII-VI-V | Andalusian | Spanish/dramatic |
| i-iv-v-i | Natural Minor | Dark folk |

### Melody Contours

For each phrase:

```json
{
  "phrase_number": 1,
  "start_bar": 0.0,
  "end_bar": 4.0,
  "contour_type": "arch",
  "direction": "ascending",
  "pitch_range": 12,
  "step_ratio": 0.7
}
```

**Contour Types:**
- `arch` — rises then falls
- `inverse_arch` — falls then rises
- `ascending_arch` — peak at end
- `descending_arch` — peak at start

### Phrase Structure

```json
{
  "count": 8,
  "avg_length": 4.0,
  "std_length": 0.5,
  "common_lengths": [[4, 5], [2, 2], [8, 1]]
}
```

### Harmonic Rhythm

```json
{
  "avg_chord_duration": 4.0,
  "changes_per_bar": 1.0,
  "rhythm_pattern": "whole_note",
  "consistency": 0.85
}
```

**Rhythm Patterns:**
- `whole_note` — chord changes every bar
- `half_note` — two changes per bar
- `quarter_note` — four changes per bar
- `irregular` — varied timing

---

## Chord Progressions Database

The `chord_progressions_db.json` file contains common progressions organized by genre:

### Pop/Rock
- I-V-vi-IV (Axis)
- I-IV-V-I (Three Chord)
- I-vi-IV-V (50s)
- I-bVII-IV (Rock Mixolydian)

### Jazz
- ii-V-I (Standard)
- I-vi-ii-V (Rhythm Changes)
- iii-VI-ii-V (Bird Changes)
- Coltrane Changes

### Blues
- 12-Bar Standard
- Quick Change
- Minor Blues

### Minor Key
- i-VII-VI-V (Andalusian)
- i-iv-v-i (Natural Minor)
- i-VI-III-VII (Descending)

### Modal
- Dorian Vamp (i-IV)
- Mixolydian (I-bVII)
- Phrygian (i-bII)
- Lydian (I-II)

### EDM/Electronic
- i-VI-III-VII (EDM Minor)
- VI-VII-i (Trance Build)

### Gospel/Soul
- I-I7-IV-iv (Gospel Move)
- I-iii-IV-iv (Soul)

---

## Database Schema

### structure_analyses
Main record for each analysis:
- name, source_file, genre
- key_detected, mode_detected
- bpm, time_signature, total_bars

### chord_progressions
Individual chord events:
- bar_number, beat, root_note, chord_type
- chord_family, duration_beats, confidence

### detected_patterns
Recognized progression patterns:
- pattern_name, start_bar
- transposition, confidence

### melody_contours
Phrase-by-phrase melody analysis:
- start_bar, end_bar, contour_type
- pitch_range, direction, step/leap counts

### phrase_structure
Phrase segmentation data:
- start_bar, length_bars
- note_density

### harmonic_rhythm
Overall harmonic pacing:
- avg_chord_duration, changes_per_bar
- rhythm_pattern, consistency

---

## How It Works

### Chord Detection Algorithm

1. Groups notes by beat window
2. Extracts pitch classes (0-11)
3. Compares against chord templates
4. Tries each possible root
5. Scores by template match minus extras
6. Returns best match above threshold

### Key Detection

Uses Krumhansl-Schmuckler algorithm:
1. Counts pitch class distribution
2. Correlates with major/minor profiles
3. Tests all 12 possible keys
4. Returns highest correlation

### Melody Separation

Simple heuristic:
1. Removes drum channel (9)
2. Groups by 16th note windows
3. Highest note = melody
4. Other notes = harmony

### Phrase Detection

1. Finds gaps > half bar
2. Splits at gaps
3. Analyzes each segment

---

## Workflow Examples

### Workflow 1: Analyze Your Song

```bash
# Analyze
python structure_analyzer.py analyze my_song.mid --genre pop

# View results
python structure_analyzer.py detail 1
```

### Workflow 2: Build Progression Library

```bash
# Scan your MIDI collection
python structure_analyzer.py scan ~/MIDI/PopSongs --genre pop
python structure_analyzer.py scan ~/MIDI/JazzStandards --genre jazz

# Query by key
python structure_analyzer.py list --key Am

# Find jazz ii-V-Is
python structure_analyzer.py list --genre jazz
```

### Workflow 3: Compare Songs

Analyze multiple songs, then query:

```bash
python structure_analyzer.py list --genre pop
# Compare harmonic rhythm, key choices, progression patterns
```

---

## Combining with Groove Library

The Structure Analyzer extracts **what** (harmony, melody)
The Groove Extractor extracts **how** (timing, feel)

Together they give complete song DNA:

```
Structure Analyzer → Chord progressions, melody shapes, phrase structure
Groove Extractor → Timing offsets, swing curves, velocity patterns
```

---

## Files

| File | Purpose |
|------|---------|
| `structure_analyzer.py` | Main analysis tool |
| `chord_progressions_db.json` | Common progressions database |

---

## CLI Reference

```bash
# Analyze single file
python structure_analyzer.py analyze song.mid [--name NAME] [--genre GENRE] [--output PATH]

# Scan folder
python structure_analyzer.py scan FOLDER [--genre GENRE] [--no-recursive]

# List analyses
python structure_analyzer.py list [--genre GENRE] [--key KEY] [--limit N]

# Show details
python structure_analyzer.py detail ID

# Initialize database
python structure_analyzer.py init
```

---

## Limitations

- Chord detection works best with clear harmonic content
- Melody separation is heuristic (highest note)
- Complex jazz voicings may confuse detection
- Polyphonic instruments (guitar strums) may be split incorrectly

For best results:
- Use MIDI with separated tracks
- Piano roll exports work well
- Type 1 MIDI (multi-track) preferred

---

## Related

- [[Groove Template Library]]
- [[Chord Progressions for Songwriters]]
- [[Song Structure Guide]]
- [[Music Theory Vocabulary]]

