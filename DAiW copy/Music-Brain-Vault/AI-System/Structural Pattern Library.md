# Structural Pattern Library

Analyze MIDI files for harmonic and melodic DNA.

---

## What This System Does

The Structural Pattern Library extracts:

- **Chord detection** — Identifies chords from MIDI notes
- **Chord families** — Classifies as major/minor/dominant/diminished/etc.
- **Progression patterns** — Matches against known progressions (I-V-vi-IV, ii-V-I, etc.)
- **Recurring progressions** — Finds patterns that repeat in the song
- **Melody contours** — Analyzes shape (ascending, arch, zigzag)
- **Phrase lengths** — Detects natural phrase boundaries
- **Harmonic rhythm** — How often chords change

---

## Quick Start

### Installation

```bash
pip install mido --break-system-packages
```

### Analyze a MIDI File

```bash
python structural_extractor.py analyze song.mid --genre pop
```

### Scan a Folder

```bash
python structural_extractor.py scan ~/MIDI/Songs --genre jazz
```

### Find Songs by Progression

```bash
python structural_extractor.py find-progression "I-V-vi-IV"
```

---

## Commands

### analyze

Analyze a single MIDI file:

```bash
python structural_extractor.py analyze song.mid
python structural_extractor.py analyze song.mid --genre jazz --name "my_analysis"
python structural_extractor.py analyze song.mid --output result.json
```

### scan

Batch analyze a folder:

```bash
python structural_extractor.py scan ~/MIDI/Collection
python structural_extractor.py scan ~/MIDI/Jazz --genre jazz
python structural_extractor.py scan ~/MIDI/Pop --genre pop --no-recursive
```

### list

View all analyses:

```bash
python structural_extractor.py list
python structural_extractor.py list --genre rock
python structural_extractor.py list --limit 100
```

### detail

Get full analysis detail:

```bash
python structural_extractor.py detail 5
```

### find-progression

Search by chord progression:

```bash
python structural_extractor.py find-progression "I-V-vi-IV"
python structural_extractor.py find-progression "ii-V-I"
python structural_extractor.py find-progression "Am"
```

---

## What Gets Extracted

### Chord Detection

The system identifies chords by matching note combinations against templates:

| Chord Type | Intervals | Example |
|------------|-----------|---------|
| maj | 0-4-7 | C E G |
| min | 0-3-7 | C Eb G |
| 7 | 0-4-7-10 | C E G Bb |
| maj7 | 0-4-7-11 | C E G B |
| min7 | 0-3-7-10 | C Eb G Bb |
| dim | 0-3-6 | C Eb Gb |
| aug | 0-4-8 | C E G# |
| sus2 | 0-2-7 | C D G |
| sus4 | 0-5-7 | C F G |

### Chord Families

Chords are grouped into functional families:

| Family | Chord Types |
|--------|-------------|
| **major** | maj, maj7, maj9, add9 |
| **minor** | min, min7, min9, minmaj7 |
| **dominant** | 7, 9, 11, 13, aug7 |
| **diminished** | dim, dim7, m7b5 |
| **suspended** | sus2, sus4 |
| **augmented** | aug |
| **power** | 5 |

### Progression Pattern Matching

The system matches against common progressions:

| Pattern | Name | Genres |
|---------|------|--------|
| I-IV-V-I | Three Chord Song | Rock, Country, Blues |
| I-V-vi-IV | Pop/Axis Progression | Pop, Rock |
| I-vi-IV-V | 50s/Doo-Wop | Pop, Oldies |
| ii-V-I | Jazz Cadence | Jazz, R&B, Neo-Soul |
| vi-IV-I-V | Sensitive Female | Pop, Singer-Songwriter |
| 12-bar-blues | Blues Form | Blues, Rock, Jazz |
| i-bVII-bVI-bVII | Andalusian | Flamenco, Rock |

### Melody Contour Types

| Contour | Description |
|---------|-------------|
| ascending | Notes generally go up |
| descending | Notes generally go down |
| arch | Up then down |
| inverted_arch | Down then up |
| flat | Stays in narrow range |
| zigzag | Alternating up/down |

### Harmonic Rhythm

How often chords change:

| Pattern | Changes/Bar | Feel |
|---------|-------------|------|
| slow | ≤1 | One chord per bar or less |
| moderate | 1-2 | Standard pop/rock |
| active | 2-4 | Jazz, complex pop |
| rapid | >4 | Bebop, complex harmony |

---

## Output Format

### JSON Structure

```json
{
  "metadata": {
    "name": "my_song",
    "source_file": "/path/to/song.mid",
    "genre": "pop",
    "key_signature": "C",
    "bpm": 120,
    "total_bars": 32
  },
  "chords": [
    {
      "bar": 0,
      "beat": 0.0,
      "root": "C",
      "type": "maj",
      "family": "major",
      "duration_beats": 4.0
    }
  ],
  "progressions": [
    {
      "bar_start": 0,
      "bar_end": 3,
      "text": "Cmaj - Gmaj - Am - Fmaj",
      "degrees": [0, 7, 9, 5],
      "pattern_matches": [["I-V-vi-IV", 1.0]]
    }
  ],
  "recurring_progressions": [
    {
      "pattern": [0, 7, 9, 5],
      "count": 4,
      "locations": [0, 8, 16, 24]
    }
  ],
  "melody_analysis": [
    {
      "bar_start": 0,
      "length_beats": 8.0,
      "contour_type": "arch",
      "pitch_range": 12,
      "note_count": 16
    }
  ],
  "harmonic_rhythm": {
    "changes_per_bar": 1.0,
    "avg_duration": 4.0,
    "pattern": "slow"
  }
}
```

---

## Example Analysis Output

```
Analyzing structure: pop_song.mid
  PPQ: 480, BPM: 120.0
  Key signature: C
  Total notes: 1247 (892 melodic)
  Detecting chords...
    Found 32 chord changes
  Analyzing progressions...
    Found 3 recurring patterns
  Analyzing melody...
    Found 8 phrases
  Analyzing harmonic rhythm...
    Pattern: slow (1.0 changes/bar)

============================================================
Analysis: pop_song
Genre: pop
Key: C, BPM: 120.0
Bars: 32
============================================================

Chord Families:
  major: 16
  minor: 12
  dominant: 4

Progressions:
  Cmaj - Gmaj - Am - Fmaj [I-V-vi-IV]
  Cmaj - Gmaj - Am - Fmaj [I-V-vi-IV]
  Am - Fmaj - Cmaj - Gmaj [vi-IV-I-V]

Harmonic Rhythm: slow (1.0 changes/bar)

Melody Contours:
  arch: 4 phrases
  ascending: 2 phrases
  descending: 2 phrases
```

---

## Database Schema

The SQLite database stores:

**structural_analyses** — Main analysis info
- name, source_file, genre, key_signature, bpm, total_bars

**chords** — Individual chord data
- bar_number, beat_position, root, type, family, duration

**chord_progressions** — Progression sequences
- bar_start, bar_end, progression_text, degrees, pattern_match

**melody_patterns** — Phrase analysis
- bar_start, length_beats, contour_type, pitch_range, note_count

**harmonic_rhythm** — Rhythm patterns
- changes_per_bar, avg_duration, pattern

**recurring_patterns** — Repeated elements
- pattern_type, pattern_content, occurrence_count, locations

---

## Workflow Examples

### Workflow 1: Study a Genre

1. Collect MIDI files from a genre
2. Batch analyze:
   ```bash
   python structural_extractor.py scan ~/MIDI/Jazz --genre jazz
   ```
3. Find common progressions:
   ```bash
   python structural_extractor.py find-progression "ii-V-I"
   ```

### Workflow 2: Write in a Style

1. Analyze reference tracks
2. Note the common progressions
3. Use similar patterns in your writing
4. Vary the harmonic rhythm to match

### Workflow 3: Build Progression Library

1. Scan your MIDI collection
2. Query by progression type
3. Export interesting patterns
4. Reference when writing

---

## Chord Progression Reference

See `chord_progression_families.json` for a complete reference of common progressions by genre, including:

- Universal progressions (I-V-vi-IV, I-IV-V, etc.)
- Jazz progressions (ii-V-I, rhythm changes)
- Blues progressions (12-bar, 8-bar, minor)
- Rock progressions (mixolydian vamps, power moves)
- Minor key progressions
- Modal progressions
- EDM progressions
- Hip-hop/R&B progressions
- Gospel progressions
- Functional categories (tonic, subdominant, dominant)
- Cadence types (authentic, plagal, deceptive)

---

## Integration with Other Tools

### With Groove Extractor

```bash
# Analyze structure
python structural_extractor.py analyze song.mid

# Extract groove
python groove_extractor.py extract song.mid

# Now you have both harmonic DNA and timing DNA
```

### With Audio Cataloger

Combine MIDI analysis with audio sample organization for complete production intelligence.

---

## Files

| File | Purpose |
|------|---------|
| `structural_extractor.py` | Main analysis tool |
| `chord_progression_families.json` | Progression reference data |
| `Structural Pattern Library.md` | This documentation |

---

## Technical Notes

### Chord Detection Algorithm

1. Quantize notes to beat grid
2. Collect pitch classes at each time point
3. Try each pitch class as potential root
4. Match against chord templates
5. Score matches by completeness
6. Return highest-scoring match

### Progression Matching

1. Convert chords to scale degrees relative to tonic
2. Compare degree sequences to known patterns
3. Allow transposition (pattern in any key)
4. Return matched pattern names with confidence

### Melody Analysis

1. Identify melody track (highest average pitch, most notes)
2. Detect phrase boundaries (gaps > 2 beats)
3. Analyze contour of each phrase
4. Calculate pitch range, intervals, density

---

## Related

- [[Groove Template Library]]
- [[Chord Progressions for Songwriters]]
- [[Song Structure Guide]]
- [[Music Theory Vocabulary]]

