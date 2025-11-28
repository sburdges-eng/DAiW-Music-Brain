# Logic Pro X Import Guide

## Your MIDI File: `kelly_song_harmony.mid`

### File Details
| Property | Value |
|----------|-------|
| **Tempo** | 82 BPM |
| **Duration** | 4 bars (~12 seconds) |
| **PPQ** | 480 (Logic Pro native) |
| **Key** | F Major |
| **Progression** | F - C - Dm - Bb (I-V-vi-IV) |

### Chord Voicings
```
Bar 1: F major   (F3, A3, C4)
Bar 2: C major   (C3, E3, G3)
Bar 3: D minor   (D3, F3, A3)
Bar 4: Bb major  (Bb3, Db4, F4)
```

---

## Quick Import Steps

### 1. Open Logic Pro X
```
File → New → Empty Project
```

### 2. Create Software Instrument Track
- Choose **Software Instrument**
- Select a piano/keys patch initially

### 3. Import MIDI
```
File → Import → MIDI File...
```
Navigate to: `examples/midi/kelly_song_harmony.mid`

### 4. Set Project Tempo
- Logic should detect 82 BPM automatically
- If not: double-click tempo display → enter `82`

---

## Adding Vocals & Guitar

### For Vocals
1. Create **Audio Track**
2. Select input (microphone)
3. Record over the chord progression
4. The I-V-vi-IV progression supports:
   - Strong melodic hooks
   - Emotional, anthemic vocals
   - Both major and minor melodic lines

### For Guitar
1. Create **Audio Track** (mic'd amp) OR **Software Instrument** (amp sim)
2. Options:
   - **Acoustic**: Strum along with progression
   - **Electric clean**: Arpeggiate the chords
   - **Electric lead**: Solo over the changes

---

## Arrangement Tips

### Song Structure Blueprint
```
Intro:     1x through (4 bars)
Verse:     2x through (8 bars)  - Vocals enter, guitar strums
Chorus:    2x through (8 bars)  - Full arrangement
Verse 2:   2x through (8 bars)
Chorus:    2x through (8 bars)
Bridge:    New progression or half-time feel
Chorus:    2x through (8 bars)  - Biggest arrangement
Outro:     1x through (4 bars)  - Fade or tag ending
```

### Dynamic Build
| Section | Elements |
|---------|----------|
| Intro | Piano/keys only |
| Verse | + Bass, light drums |
| Chorus | + Full drums, guitar |
| Bridge | Strip back, build tension |
| Final Chorus | Everything + doubles |

---

## Export Ready

### Logic Pro Export Settings
When ready to ship:
```
File → Bounce → Project or Section...
```

**Recommended settings:**
- Format: WAV or AIFF
- Sample Rate: 44.1 kHz (or 48 kHz for video)
- Bit Depth: 24-bit
- Normalize: Off (use limiter instead)

---

## CLI Commands

### Prepare MIDI for Logic (already done for you)
```bash
daiw export-logic examples/midi/kelly_song_harmony.mid
```

### Analyze the progression
```bash
daiw diagnose "F-C-Dm-Bb"
```

---

## File Locations

```
examples/midi/
├── kelly_song_harmony.mid       # Main harmony (use this!)
├── kelly_diatonic_comparison.mid # Diatonic version for comparison
└── kelly_song_harmony_logic.mid  # Logic-optimized (if exported)
```

**Ship it!** 🎵
