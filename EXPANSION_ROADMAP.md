# DAiW-Music-Brain Expansion Roadmap

> What needs expanding next, prioritized by impact and dependency

---

## Priority 1: Critical Bug Fixes (Required for Phase 1 Completion)

### 1.1 Fix Borrowed Chord Detection
**Impact:** High | **Effort:** 2 hours | **File:** `music_brain/structure/progression.py`

**Current Bug:**
```python
diagnose_progression("F-C-Bbm-F")
# Returns: {'issues': []}  ← Should detect Bbm as borrowed!
```

**Problem:** The code only checks if the chord ROOT is diatonic. Bb is the IV in F major, so it passes. But **Bbm** (minor quality) is borrowed from F minor.

**Fix Strategy:**
```python
# Add expected diatonic qualities
MAJOR_DIATONIC_QUALITIES = {
    0: 'maj',   # I
    2: 'min',   # ii
    4: 'min',   # iii
    5: 'maj',   # IV
    7: 'maj',   # V
    9: 'min',   # vi
    11: 'dim',  # vii°
}

# In diagnose_progression(), after checking root:
if interval in scale:
    expected_quality = MAJOR_DIATONIC_QUALITIES.get(interval, 'maj')
    if chord.quality == 'min' and expected_quality == 'maj':
        issues.append(f"{chord.original}: iv (borrowed from parallel minor)")
```

---

### 1.2 Fix Roman Numeral → Chord Conversion
**Impact:** High | **Effort:** 2 hours | **File:** `music_brain/session/intent_processor.py`

**Current Bug:**
```python
generate_progression_modal_interchange('F', 'major')
# Returns: ['F', 'E', 'F', 'C']  ← E should be Ab!
# Roman numerals: ['I', 'bIII', 'IV', 'V']
```

**Problem:** `_roman_to_chord()` function (line 275-319) has bugs in:
1. `flat_offset` applied incorrectly
2. Wrong interval lookup for borrowed chords

**Fix Strategy:**
```python
def _roman_to_chord(roman: str, key: str, intervals: List[int]) -> str:
    key_idx = _get_note_index(key)

    # Handle flats BEFORE degree lookup
    has_flat = roman.upper().startswith('B') and len(roman) > 1 and roman[1:2].upper() in ['I', 'V']
    if has_flat:
        flat_offset = -1
        roman_clean = roman[1:]
    else:
        flat_offset = 0
        roman_clean = roman

    # Get scale degree
    degree = _parse_degree(roman_clean)  # I=0, II=1, etc.

    # Calculate root: key + scale_interval + flat_adjustment
    if has_flat:
        # bIII in F = Bb + minor_third = Ab... wait, no:
        # bIII means "flatted third degree" = minor third from tonic
        root_interval = 3  # minor third, not major third
    else:
        root_interval = intervals[degree]

    root_idx = (key_idx + root_interval + flat_offset) % 12
    # ...
```

---

### 1.3 Sync Tests with Current API
**Impact:** Medium | **Effort:** 2 hours | **Files:** `tests/test_*.py`

**Failing Tests:**
- `HarmonyPlan.__init__()` - Update test fixtures
- `TherapyState` attributes - Update test assertions
- `ProductionRuleBreak` enum - Update expected count (8 not 5)

**Strategy:** Run `pytest -x --tb=short` and fix tests one by one.

---

## Priority 2: Feature Enhancements

### 2.1 MIDI Generation from Harmony
**Impact:** Very High | **Effort:** 4 hours | **New File:** `music_brain/harmony/midi_writer.py`

**Why:** Currently, harmony is generated as chord symbols only. Users want MIDI files.

**Needed:**
```python
def generate_midi_from_harmony(
    progression: GeneratedProgression,
    output_path: str,
    tempo_bpm: int = 120,
    bars_per_chord: int = 1,
    voicing: str = "close"  # close, open, spread
) -> str:
    """Convert chord progression to MIDI file."""
```

**Implementation:**
1. Parse chord symbols to MIDI notes
2. Apply voicing (root position, inversions)
3. Write using mido
4. Optionally add bass line

---

### 2.2 Expand Borrowed Chord Detection
**Impact:** Medium | **Effort:** 3 hours | **File:** `music_brain/structure/progression.py`

**Current:** Only detects bIII, bVI, bVII in major.

**Expand to detect:**
- `iv` in major (Bbm in F) ← **Critical for Kelly song**
- `II` (major II) in minor
- `#IV` (Lydian)
- Secondary dominants (V/V, V/vi)
- Neapolitan (bII)
- Augmented 6th chords

---

### 2.3 Emotional Function Labels
**Impact:** Medium | **Effort:** 2 hours | **File:** `music_brain/structure/progression.py`

**Add to diagnosis output:**
```python
{
    'chords': ['F', 'C', 'Bbm', 'F'],
    'roman_numerals': ['I', 'V', 'iv', 'I'],
    'emotional_functions': [
        'home/stable',
        'tension/reaching',
        'borrowed sadness/intrusion',
        'return/transformed'
    ]
}
```

---

### 2.4 Groove Template Expansion
**Impact:** Low | **Effort:** 2 hours | **File:** `music_brain/groove/templates.py`

**Current templates:** funk, jazz, rock, hiphop, edm, latin, blues, bedroom_lofi

**Add:**
- gospel (rolling triplets, call-response)
- reggae (one-drop, emphasis on 3)
- afrobeat (complex polyrhythm)
- trap (hi-hat rolls, triplet flow)
- boom_bap (classic 90s hip-hop)
- dilla (drunk drums, late snare)

---

## Priority 3: New Capabilities

### 3.1 Scale/Mode Recommendations
**Impact:** Medium | **Effort:** 4 hours | **New Module**

```python
def suggest_scales_for_emotion(emotion: str, context: dict) -> List[Scale]:
    """
    Given an emotion, suggest scales that evoke it.

    'grief' → [D Dorian, A Aeolian, F# Locrian]
    'hope' → [C Lydian, G Ionian, E Mixolydian]
    """
```

Data exists in `data/scales/scale_emotional_map.json`.

---

### 3.2 Voice Leading Optimizer
**Impact:** High | **Effort:** 6 hours | **New Module**

```python
def optimize_voice_leading(
    chords: List[str],
    num_voices: int = 4
) -> List[List[int]]:
    """
    Given chord symbols, return optimal MIDI notes per chord
    minimizing voice movement.

    Input: ['Fmaj7', 'C', 'Bbm', 'F']
    Output: [[F3, A3, C4, E4], [E3, G3, C4, E4], ...]
    """
```

---

### 3.3 Reference Track DNA Matching
**Impact:** High | **Effort:** 8 hours | **Expand:** `music_brain/audio/reference_dna.py`

Extract and match:
- Harmonic DNA (progression patterns)
- Rhythmic DNA (groove signature)
- Timbral DNA (frequency profile)
- Dynamic DNA (loudness envelope)

```python
def match_reference(my_track: str, reference: str) -> MatchReport:
    """Compare my track to reference and suggest adjustments."""
```

---

### 3.4 Real-time MIDI Processing
**Impact:** Medium | **Effort:** 10 hours | **New Module**

For live DAW integration:
```python
def process_midi_realtime(input_port: str, output_port: str):
    """Apply groove humanization in real-time."""
```

Requires: `python-rtmidi` or `mido` with rtmidi backend.

---

## Priority 4: Infrastructure

### 4.1 Streamlit UI Completion
**Impact:** High for UX | **Effort:** 6 hours | **File:** `app.py`

Current UI exists but may need:
- Intent wizard with guided questions
- Visual chord progression editor
- Groove comparison A/B player
- Export to DAW formats

---

### 4.2 DAW Plugin Bridge
**Impact:** Very High | **Effort:** 20+ hours | **New System**

Create VST/AU wrapper or OSC/MIDI bridge for:
- Logic Pro X
- Ableton Live
- FL Studio

---

### 4.3 API Server
**Impact:** Medium | **Effort:** 4 hours | **New File:** `api.py`

REST API for web integration:
```
POST /analyze/progression {"chords": "F-C-Bbm-F"}
POST /generate/harmony {"intent": {...}}
POST /apply/groove {"midi": base64, "genre": "funk"}
```

---

## Dependency Graph

```
Priority 1 (Bugs)
    ├── 1.1 Borrowed Chord Detection
    ├── 1.2 Roman Numeral Conversion
    └── 1.3 Test Sync
            │
            ▼
Priority 2 (Enhancements)
    ├── 2.1 MIDI Generation ← Depends on 1.2
    ├── 2.2 Expand Detection ← Depends on 1.1
    ├── 2.3 Emotional Labels
    └── 2.4 Groove Templates
            │
            ▼
Priority 3 (New Capabilities)
    ├── 3.1 Scale Recommendations
    ├── 3.2 Voice Leading ← Depends on 2.1
    ├── 3.3 Reference DNA
    └── 3.4 Real-time MIDI
            │
            ▼
Priority 4 (Infrastructure)
    ├── 4.1 UI Completion
    ├── 4.2 DAW Plugin
    └── 4.3 API Server
```

---

## Recommended Next Session

**Goal:** Complete Phase 1 (100%)

1. **Fix borrowed chord detection** (1.1) - Makes Kelly song analysis work
2. **Fix Roman numeral conversion** (1.2) - Makes harmony generation correct
3. **Run and fix tests** (1.3) - Validates everything works
4. **Optional:** Add MIDI generation (2.1) - High user value

**Estimated time:** 4-6 hours

---

## Success Metrics

### Phase 1 Complete When:
- [ ] `diagnose_progression("F-C-Bbm-F")` detects `iv` as borrowed
- [ ] `generate_progression_modal_interchange('F')` outputs correct notes
- [ ] All 470 tests pass (currently 309)
- [ ] Kelly song workflow documented end-to-end

### Phase 2 Ready When:
- [ ] MIDI generation from harmony works
- [ ] Voice leading optimization exists
- [ ] At least 12 groove templates available
- [ ] Streamlit UI is production-ready
