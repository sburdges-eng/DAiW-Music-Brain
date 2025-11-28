# Humanization Cheat Sheet

Quick reference for making productions feel alive.

---

## The 3 Pillars

| Pillar | What It Is | How to Vary |
|--------|------------|-------------|
| **TIMING** | When notes hit | Quantize <100%, nudge early/late |
| **DYNAMICS** | How hard notes hit | Velocity variation, automation |
| **TONE** | How notes sound | Articulation, filter, expression |

---

## Quantize Strength by Genre

| Genre | Strength | Notes |
|-------|----------|-------|
| EDM/Electronic | 90-100% | Tighter okay |
| Pop | 75-85% | Moderate |
| Rock | 60-80% | Looser |
| R&B/Soul | 50-70% | Pocket feel |
| Jazz | 40-60% | Very loose |
| Lo-fi | 40-60% | Intentionally sloppy |

---

## Velocity Ranges by Instrument

| Instrument | Range | Notes |
|------------|-------|-------|
| Kick | 85-120 | Fairly consistent |
| Snare | 70-127 | Accents + ghosts |
| Hi-hats | 50-110 | Most variation |
| Bass | 75-110 | Moderate |
| Piano | 30-120 | Very expressive |
| Synth lead | 85-120 | Less variation |
| Strings | 50-100 | Follow phrase |

---

## Quick Humanize Settings (Logic Pro)

**MIDI Transform → Humanize:**
```
Position: ±5 to ±15 ticks
Velocity: ±5 to ±15
Length: ±3 to ±10 ticks
```

**Quantize Strength:** 60-85% (not 100%)

**Swing:** 52-58% for subtle, 60-66% for obvious

---

## Timing Feel

| Feel | How to Achieve |
|------|----------------|
| **Driving/Urgent** | Push notes ahead of beat (early) |
| **Laid back/Groovy** | Pull notes behind beat (late) |
| **Tight/Precise** | Keep close to grid |
| **Loose/Human** | Random ±10-20ms |
| **Swung** | Delay every other 8th note |

**Classic groove:** Kick on grid, snare 10-30ms late, hats early

---

## Drums Quick Fixes

| Problem | Solution |
|---------|----------|
| Robotic hi-hats | Vary velocity 60-110, loosen timing |
| Stiff kick/snare | Add ghost notes (vel 30-50) |
| Boring pattern | Change 2-3 things every 4-8 bars |
| No groove | Snare slightly late, apply swing |
| Too perfect | Humanize transform, reduce quantize |

---

## Bass Quick Fixes

| Problem | Solution |
|---------|----------|
| Too stiff | Shift 10-30ms behind beat |
| No groove | Vary note lengths |
| Mechanical | Add slides, dead notes |
| Boring | Vary velocity, octave variations |

---

## Keys/Piano Quick Fixes

| Problem | Solution |
|---------|----------|
| Chords too perfect | Roll notes (5-20ms between) |
| Static dynamics | Wide velocity range (40-120) |
| No expression | Automate sustain pedal |
| Robotic | Quantize 50-70% |

---

## What to Vary Per Repeat

When you copy a section, change:
- [ ] 2-3 note velocities
- [ ] 1-2 note timings
- [ ] Add or remove 1 note
- [ ] Hi-hat pattern slightly
- [ ] Fill at end of phrase

---

## Ghost Notes Formula

```
Velocity: 25-45 (barely audible)
Timing: On 16th note subdivisions
Frequency: Sparse (not every beat)
Where: Between main snare hits
```

---

## Swing Quick Settings

| Amount | Feel |
|--------|------|
| 50% | Straight (no swing) |
| 52-54% | Very subtle shuffle |
| 55-58% | Noticeable groove |
| 60-66% | Heavy swing/triplet |

---

## Expression Automation

For sustained instruments (strings, pads, brass):

| CC | Controls | Use For |
|----|----------|---------|
| CC1 | Modulation | Vibrato depth |
| CC7 | Volume | Overall level |
| CC11 | Expression | Dynamic swells |
| CC64 | Sustain | Piano pedal |

**Rule:** No sustained note should be static — automate something.

---

## The 10-Second Check

Listen to any 4-bar section:
1. Can you hear velocity variation? ✓/✗
2. Is anything slightly off-grid? ✓/✗
3. Does it breathe (dynamics)? ✓/✗
4. Is the next repeat exactly the same? (Should be ✗)

---

## Emergency Humanize

If everything sounds robotic, try this fast fix:

1. Select all MIDI in the section
2. MIDI Transform → Humanize
3. Position: ±10 ticks
4. Velocity: ±12
5. Apply
6. Listen, undo if too much

---

## Related
- [[Humanizing Your Music]] — Full guide
- [[Mixing Workflow Checklist]]
- [[Gear/Logic Pro Settings]]

