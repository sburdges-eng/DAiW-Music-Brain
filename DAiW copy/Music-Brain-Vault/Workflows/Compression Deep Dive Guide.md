# Compression Deep Dive Guide

Understanding and using compression to control dynamics and add punch.

---

## What Compression Does

Compression reduces the volume of loud sounds, making the overall dynamic range smaller.

**Results:**
- Quiet parts become more audible
- Loud parts are controlled
- More consistent level
- Can add punch, glue, or character

---

## The Basic Parameters

### Threshold

**What it does:** Sets the level where compression starts.

- Signals below threshold: Unchanged
- Signals above threshold: Compressed

**Setting it:**
- Lower threshold = more compression
- Watch the gain reduction meter
- Start with threshold that catches peaks

### Ratio

**What it does:** How much compression is applied.

| Ratio | Meaning | Use For |
|-------|---------|---------|
| 2:1 | Gentle, 2dB over becomes 1dB | Subtle control |
| 3:1 | Moderate | Vocals, guitars |
| 4:1 | Standard | Most sources |
| 6:1 | Aggressive | Drums, punchy sounds |
| 10:1+ | Limiting | Peaks, protection |
| ∞:1 | Brick wall | Limiting |

### Attack

**What it does:** How fast compression kicks in.

| Attack | Effect | Use For |
|--------|--------|---------|
| Fast (0-10ms) | Catches transients, reduces punch | Control, smoothing |
| Medium (10-30ms) | Lets transients through, then controls | Vocals, balance |
| Slow (30-100ms+) | Transients pass, body compressed | Punch, impact |

**Key insight:** Slow attack = more punch (transients pass through).

### Release

**What it does:** How fast compression lets go.

| Release | Effect | Use For |
|---------|--------|---------|
| Fast (50-100ms) | Quick recovery, pumping possible | Drums, pumping effect |
| Medium (100-300ms) | Natural, transparent | Most sources |
| Slow (300ms+) | Smooth, sustained reduction | Gentle control |
| Auto | Adjusts to source | Convenience |

**Tip:** Release should recover before the next transient hits.

### Makeup Gain

**What it does:** Adds volume back after compression.

- Compression reduces level
- Makeup gain compensates
- Match bypassed level for fair comparison

---

## Gain Reduction Amounts

### How Much Is Right?

| Amount | Result | Use For |
|--------|--------|---------|
| 1-3 dB | Subtle control | Gentle shaping |
| 3-6 dB | Noticeable control | Most mixing tasks |
| 6-10 dB | Heavy compression | Drums, aggressive sound |
| 10+ dB | Extreme | Effects, pumping |

### The Sweet Spot

For most mixing:
- 3-6 dB gain reduction
- Compression working, but not obvious
- Sound is controlled, not squashed

---

## Compression Techniques

### Basic Compression (Control)

**Goal:** Even out dynamics.

**Settings:**
- Ratio: 3:1 to 4:1
- Attack: Medium (15-30ms)
- Release: Medium (100-200ms) or Auto
- Gain reduction: 3-6 dB on peaks

### Punchy Compression

**Goal:** Add impact and punch.

**Settings:**
- Ratio: 4:1 to 6:1
- Attack: SLOW (30-50ms) — lets transients through
- Release: Medium-fast (50-150ms)
- Gain reduction: 4-8 dB

**Key:** Slow attack preserves transients.

### Glue Compression (Bus)

**Goal:** Make elements sound cohesive.

**Settings:**
- Ratio: 2:1 to 4:1
- Attack: Medium-slow (10-30ms)
- Release: Auto or medium
- Gain reduction: 1-3 dB (gentle)

**Use on:** Drum bus, mix bus, groups.

### Parallel Compression

**Goal:** Add power without losing dynamics.

**Method:**
1. Original track stays uncompressed
2. Send to aux with heavy compression
3. Blend compressed signal underneath

**Aux Settings:**
- Ratio: 8:1 to 10:1
- Fast attack
- Medium release
- Smash it (10+ dB reduction)
- Blend to taste

**Result:** Dynamics preserved + power added.

### Serial Compression

**Goal:** Transparent control using multiple stages.

**Method:**
1. First compressor: Light (2-3 dB)
2. Second compressor: Light (2-3 dB)
3. Total: 4-6 dB (but more transparent)

**Why it works:** Each compressor works less hard = less artifacts.

---

## Compression by Instrument

### Vocals

**Goal:** Consistent level, present but natural.

**Settings:**
- Ratio: 3:1 to 4:1
- Attack: Medium (10-30ms) — let consonants through
- Release: Medium (100-200ms) or Auto
- Gain reduction: 3-6 dB on peaks

**Tips:**
- Fast attack kills consonants
- Consider serial compression
- Automate volume first for extreme dynamics

### Drums (Kick)

**Goal:** Punch and control.

**Settings:**
- Ratio: 4:1 to 6:1
- Attack: Slow (30-50ms) — preserve transient
- Release: Fast (50-100ms) — recover before next hit
- Gain reduction: 4-8 dB

### Drums (Snare)

**Goal:** Snap and body.

**Settings:**
- Ratio: 4:1 to 6:1
- Attack: Medium-slow (20-40ms) — preserve crack
- Release: Medium (100-150ms)
- Gain reduction: 4-8 dB

### Drums (Bus)

**Goal:** Glue the kit together.

**Settings:**
- Ratio: 2:1 to 4:1
- Attack: Medium (10-30ms)
- Release: Auto or matched to tempo
- Gain reduction: 2-4 dB

**Tip:** Parallel compression on drum bus = power.

### Bass

**Goal:** Consistent low end.

**Settings:**
- Ratio: 4:1 to 6:1
- Attack: Medium-fast (10-20ms)
- Release: Medium (100-200ms)
- Gain reduction: 4-8 dB

**Tip:** Bass often needs more compression than you think.

### Acoustic Guitar

**Goal:** Even dynamics, present but natural.

**Settings:**
- Ratio: 3:1 to 4:1
- Attack: Medium (15-30ms)
- Release: Medium (150-250ms)
- Gain reduction: 3-6 dB

### Electric Guitar

**Goal:** Control peaks, add sustain.

**Settings:**
- Ratio: 3:1 to 4:1
- Attack: Medium (10-30ms)
- Release: Medium (100-200ms)
- Gain reduction: 3-6 dB

**Note:** Distorted guitars are already compressed by the amp.

### Piano/Keys

**Goal:** Even dynamics across range.

**Settings:**
- Ratio: 2:1 to 3:1 (gentle)
- Attack: Medium (20-40ms)
- Release: Medium-slow (200-400ms)
- Gain reduction: 2-4 dB

---

## Mix Bus Compression

### Why Use It

- Glues the mix together
- Adds cohesion
- Can add punch and energy

### Settings

- Ratio: 2:1 to 4:1
- Attack: Medium-slow (10-30ms)
- Release: Auto or matched to tempo
- Gain reduction: 1-3 dB (SUBTLE)

### Important

- Use from early in mixing
- Mix INTO the compressor
- Don't add at the end and crank it

---

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Too much compression | Sounds squashed, lifeless | Reduce ratio or raise threshold |
| Attack too fast | Kills transients, no punch | Slow down attack |
| Release too fast | Pumping artifacts | Slow down release |
| Release too slow | Compression doesn't recover | Speed up release |
| Only compressing | Level still uneven | Use volume automation too |
| Not A/B comparing | Can't tell if it's better | Bypass and compare |

---

## Compressor Types (Character)

### VCA (Clean)

- Fast, precise
- Transparent
- Good for: Drums, mix bus
- Logic: Compressor (Platinum Digital)

### Opto (Smooth)

- Slow, smooth
- Natural sound
- Good for: Vocals, bass, guitars
- Logic: Compressor (Vintage Opto)

### FET (Aggressive)

- Fast, punchy
- Adds color/grit
- Good for: Drums, aggressive vocals
- Logic: Compressor (Vintage FET)

### Tube/Variable-Mu (Warm)

- Slow, warm
- Gentle, musical
- Good for: Mix bus, mastering
- Logic: Compressor (Vintage VCA)

---

## Logic Pro Compressor Modes

| Mode | Character | Use For |
|------|-----------|---------|
| Platinum Digital | Clean, precise | Surgical control |
| Vintage VCA | Punchy, snappy | Drums, bus |
| Vintage FET | Aggressive, fast | Drums, vocals |
| Vintage Opto | Smooth, slow | Vocals, bass |
| Studio VCA | Modern, clean | General purpose |
| Studio FET | Modern aggressive | Parallel compression |

---

## Quick Reference

### Starting Points

| Source | Ratio | Attack | Release | GR |
|--------|-------|--------|---------|-----|
| Vocals | 3:1 | 15-30ms | Auto | 3-6dB |
| Kick | 4:1 | 30-50ms | 50-100ms | 4-8dB |
| Snare | 4:1 | 20-40ms | 100-150ms | 4-8dB |
| Bass | 4:1 | 10-20ms | 100-200ms | 4-8dB |
| Acoustic | 3:1 | 15-30ms | 150-250ms | 3-6dB |
| Drum Bus | 3:1 | 10-30ms | Auto | 2-4dB |
| Mix Bus | 2:1 | 20-30ms | Auto | 1-3dB |

---

## Related
- [[EQ Deep Dive Guide]]
- [[Mixing Workflow Checklist]]
- [[Vocal Production Guide]]

