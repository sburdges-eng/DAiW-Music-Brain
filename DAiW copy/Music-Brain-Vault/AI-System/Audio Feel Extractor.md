# Audio Feel Extractor

Extract production characteristics and mix fingerprints from audio files.

---

## What This System Does

The Audio Feel Extractor analyzes audio files to extract:

- **Transient drift** — How much timing varies from a perfect grid
- **RMS swing** — Dynamic groove and loudness variation
- **Spectral movement** — How the tone changes over time
- **Frequency balance** — Mix fingerprint across frequency bands
- **Stereo characteristics** — Width, correlation, mid/side balance
- **Genre matching** — How closely a track matches genre templates

---

## Quick Start

### Installation

```bash
pip install librosa numpy soundfile --break-system-packages
```

### Analyze an Audio File

```bash
python audio_feel_extractor.py analyze song.wav --genre hiphop
```

### Scan a Folder

```bash
python audio_feel_extractor.py scan ~/Music/References --genre pop
```

### Compare Two Tracks

```bash
python audio_feel_extractor.py compare 3 7
```

---

## Commands

### analyze

Analyze a single audio file:

```bash
python audio_feel_extractor.py analyze track.wav
python audio_feel_extractor.py analyze track.mp3 --genre jazz --name "my_reference"
python audio_feel_extractor.py analyze track.flac --duration 120  # Analyze first 2 minutes
```

### scan

Batch analyze a folder:

```bash
python audio_feel_extractor.py scan ~/Music/HipHop --genre hiphop
python audio_feel_extractor.py scan ~/Music/Mixed --no-recursive
```

### list

View all analyses:

```bash
python audio_feel_extractor.py list
python audio_feel_extractor.py list --genre rock
```

### detail

Get full analysis detail:

```bash
python audio_feel_extractor.py detail 5
```

### compare

Compare two analyses:

```bash
python audio_feel_extractor.py compare 3 7
```

### genres

List available genre fingerprints:

```bash
python audio_feel_extractor.py genres
```

---

## What Gets Extracted

### Transient Analysis

| Metric | What It Measures | Interpretation |
|--------|------------------|----------------|
| **Transient Drift (ms)** | Timing variation from grid | Higher = more human/loose |
| **Beat Drift (ms)** | Deviation from beat grid | Higher = more laid-back |
| **On-Beat Ratio** | % of hits on the beat | Lower = more groove |
| **Attack Sharpness** | How sharp transients are | Higher = more punch |

**Typical values:**

| Genre | Drift (ms) |
|-------|------------|
| Metal/EDM | 0-3 |
| Pop/Rock | 2-10 |
| Hip-Hop | 5-20 |
| Jazz | 10-40 |
| Lo-Fi | 15-40 |

### RMS / Dynamics

| Metric | What It Measures | Interpretation |
|--------|------------------|----------------|
| **RMS Swing Ratio** | Loudness variation | Higher = more dynamic |
| **Dynamic Range (dB)** | Quietest to loudest | Higher = less compressed |
| **Crest Factor (dB)** | Peak to average | Higher = more headroom |
| **Approx LUFS** | Integrated loudness | Target varies by genre |

**Typical values:**

| Genre | RMS Swing | Dynamic Range |
|-------|-----------|---------------|
| EDM/Pop | 0.05-0.15 | 3-8 dB |
| Hip-Hop | 0.15-0.35 | 6-12 dB |
| Rock | 0.15-0.35 | 8-14 dB |
| Jazz | 0.30-0.60 | 14-24 dB |
| Classical | 0.40-0.80 | 18-30 dB |

### Spectral Analysis

| Metric | What It Measures | Interpretation |
|--------|------------------|----------------|
| **Brightness** | High frequency content | Higher = brighter mix |
| **Spectral Centroid** | "Center of mass" of spectrum | Higher = brighter |
| **Spectral Movement** | How much tone changes | Higher = more variation |
| **Spectral Flux** | Rate of spectral change | Higher = more activity |

### Frequency Balance

Energy in 8 frequency bands relative to mid (500-2000Hz):

| Band | Frequency Range | Typical Content |
|------|-----------------|-----------------|
| **Sub** | 20-60 Hz | Sub bass, rumble |
| **Bass** | 60-250 Hz | Bass fundamentals, kick |
| **Low Mid** | 250-500 Hz | Bass harmonics, warmth |
| **Mid** | 500-2000 Hz | Vocals, guitars, snare |
| **High Mid** | 2000-4000 Hz | Presence, bite |
| **Presence** | 4000-6000 Hz | Clarity, attack |
| **Brilliance** | 6000-12000 Hz | Sparkle, air |
| **Air** | 12000-20000 Hz | Shimmer, breath |

### Stereo Analysis

| Metric | What It Measures | Interpretation |
|--------|------------------|----------------|
| **Stereo Width** | Side-to-mid ratio | Higher = wider |
| **Correlation** | L/R similarity | 1 = mono, 0 = uncorrelated |
| **Mid/Side Ratio** | Center vs sides | Higher = more centered |

---

## Genre Fingerprints

The system includes reference fingerprints for matching:

| Genre | Sub | Bass | Low Mid | Mid | High Mid | Presence | Brilliance | Air |
|-------|-----|------|---------|-----|----------|----------|------------|-----|
| Hip-Hop | +6 | +4 | -2 | 0 | -1 | +1 | -2 | -4 |
| Trap | +10 | +6 | -4 | 0 | +2 | +3 | +4 | +2 |
| Pop | 0 | +1 | -1 | 0 | +2 | +3 | +2 | +1 |
| Rock | -2 | +2 | +1 | 0 | +2 | +3 | +1 | -1 |
| Metal | +2 | +3 | -2 | 0 | +4 | +5 | +2 | 0 |
| Jazz | -3 | +1 | +2 | 0 | 0 | -1 | -2 | -3 |
| R&B | +5 | +3 | 0 | 0 | +1 | +2 | +1 | 0 |
| EDM | +8 | +5 | -3 | 0 | +2 | +3 | +4 | +2 |
| Lo-Fi | -2 | +2 | +3 | 0 | -3 | -4 | -6 | -8 |
| Classical | -4 | 0 | +1 | 0 | 0 | 0 | -1 | +1 |

---

## Output Format

### JSON Structure

```json
{
  "metadata": {
    "name": "my_track",
    "source_file": "/path/to/track.wav",
    "genre": "hiphop",
    "duration_seconds": 180.5,
    "estimated_bpm": 92.0,
    "estimated_key": "Am"
  },
  "transients": {
    "onset_count": 842,
    "transient_drift_ms": 12.4,
    "attack_sharpness": 0.85
  },
  "dynamics": {
    "rms_swing_ratio": 0.23,
    "dynamic_range_db": 9.4,
    "crest_factor_db": 11.2
  },
  "spectrum": {
    "brightness": 0.18,
    "spectral_movement": 0.34
  },
  "frequency_balance": {
    "relative_to_mid_db": {
      "sub": 5.2,
      "bass": 3.1,
      "low_mid": -1.8,
      "mid": 0,
      "high_mid": -0.5,
      "presence": 1.2,
      "brilliance": -1.9,
      "air": -3.4
    }
  },
  "genre_matches": {
    "hiphop": {"score": 0.87},
    "rnb": {"score": 0.72},
    "trap": {"score": 0.65}
  },
  "stereo": {
    "stereo_width": 0.45,
    "correlation": 0.82
  }
}
```

---

## Example Analysis Output

```
Analyzing: reference_track.wav
  Duration: 180.5s, BPM: 92.0, Key: Am
  Analyzing transients...
    Drift: 12.4ms
  Analyzing dynamics...
    RMS swing: 0.234
    Dynamic range: 9.4dB
  Analyzing spectrum...
    Brightness: 0.183
    Spectral movement: 0.342
  Analyzing frequency balance...
    Best genre match: hiphop (0.87)
  Analyzing stereo field...
    Stereo width: 0.452
    Correlation: 0.823

============================================================
Analysis: reference_track
File: /path/to/reference_track.wav
Genre: hiphop
BPM: 92.0, Key: Am
Duration: 180.5s
============================================================

Transients:
  Onset count: 842
  Transient drift: 12.4ms
  Attack sharpness: 0.852

Dynamics:
  RMS swing ratio: 0.234
  Dynamic range: 9.4dB
  Crest factor: 11.2dB

Spectral:
  Brightness: 0.183
  Centroid: 1847Hz

Frequency Balance (relative to mid):
  sub          +5.2dB
  bass         +3.1dB
  low_mid      -1.8dB
  mid          +0.0dB
  high_mid     -0.5dB
  presence     +1.2dB
  brilliance   -1.9dB
  air          -3.4dB

Genre Matches:
  hiphop       0.87 ████████████████████
  rnb          0.72 ██████████████
  trap         0.65 █████████████

Stereo:
  Width: 0.452
  Correlation: 0.823
```

---

## Workflow Examples

### Workflow 1: Reference Track Analysis

1. Analyze your reference track:
   ```bash
   python audio_feel_extractor.py analyze reference.wav --genre pop --name "target_sound"
   ```

2. Analyze your mix:
   ```bash
   python audio_feel_extractor.py analyze my_mix.wav --name "my_mix"
   ```

3. Compare:
   ```bash
   python audio_feel_extractor.py compare 1 2
   ```

4. Adjust mix to match reference characteristics

### Workflow 2: Genre Study

1. Collect tracks from a genre
2. Batch analyze:
   ```bash
   python audio_feel_extractor.py scan ~/Music/JazzReferences --genre jazz
   ```
3. Query and study:
   ```bash
   python audio_feel_extractor.py list --genre jazz
   python audio_feel_extractor.py detail 5
   ```
4. Note common characteristics

### Workflow 3: Mix Fingerprinting

1. Analyze finished professional mixes
2. Build genre-specific templates
3. Compare your mixes against templates
4. Use frequency balance data for EQ decisions

---

## Integration with Other Tools

### With Groove Extractor (MIDI)

```bash
# Analyze audio feel
python audio_feel_extractor.py analyze track.wav --genre hiphop

# Extract groove from MIDI
python groove_extractor.py extract track.mid --genre hiphop

# Now you have both audio characteristics and MIDI timing data
```

### With Structural Extractor (MIDI)

Combine audio analysis with harmonic analysis for complete track intelligence.

---

## Supported Formats

- WAV (.wav)
- MP3 (.mp3)
- FLAC (.flac)
- AIFF (.aiff, .aif)
- M4A (.m4a)
- OGG (.ogg)

---

## Database Schema

**audio_analyses** — Main analysis info
- name, source_file, genre, duration, sample_rate, bpm, key

**transient_analysis** — Timing characteristics
- onset_count, transient_drift_ms, attack_sharpness

**dynamics_analysis** — RMS and dynamics
- rms_swing_ratio, dynamic_range_db, crest_factor_db

**spectral_analysis** — Tonal characteristics
- brightness, centroid, bandwidth, flux

**frequency_balance** — Per-band energy
- band_name, energy_db, relative_to_mid_db

**stereo_analysis** — Stereo field
- stereo_width, mid_side_ratio, correlation

**genre_matches** — Genre similarity scores
- genre, match_score

---

## Files

| File | Purpose |
|------|---------|
| `audio_feel_extractor.py` | Main analysis tool |
| `genre_mix_fingerprints.json` | Genre reference data |
| `Audio Feel Extractor.md` | This documentation |

---

## Technical Notes

### Analysis Duration

By default, analyzes first 60 seconds. Use `--duration` to change:

```bash
python audio_feel_extractor.py analyze track.wav --duration 120  # 2 minutes
python audio_feel_extractor.py analyze track.wav --duration 0    # Full track
```

### Sample Rate

Audio is resampled to 22050 Hz for analysis (librosa default). Original sample rate is stored in metadata.

### Accuracy

- BPM and key detection are estimates
- Frequency balance is relative, not absolute
- Genre matching is similarity-based, not definitive

---

## Related

- [[Groove Template Library]]
- [[Structural Pattern Library]]
- [[Reference Track Analysis Guide]]
- [[EQ Deep Dive Guide]]
- [[Compression Deep Dive Guide]]

