# Drum Programming That Sounds Human

Making programmed drums feel like a real drummer played them.

---

## Why Drums Sound Fake

The dead giveaways:
1. **Hi-hats** — Same velocity, perfect timing
2. **No ghost notes** — Real drummers play quiet notes between hits
3. **Exact repetition** — Same pattern for 4 minutes
4. **No dynamics** — Verse and chorus identical energy
5. **Quantized to death** — Machine-gun precision
6. **No fills** — Or fills that sound programmed

---

## The Drum Priority List

Focus your humanization efforts in this order:

1. **Hi-hats/Cymbals** — Most obvious problem
2. **Snare** — Ghost notes and accents
3. **Fills** — Easy to sound fake
4. **Kick** — Usually less critical
5. **Overall dynamics** — Section-to-section variation

---

## Hi-Hats: The #1 Problem

### Velocity Pattern

Real drummer's hi-hat velocity follows a pattern:

**Basic pattern (downbeat accent):**
```
8ths: 1   +   2   +   3   +   4   +
Vel:  95  65  85  60  90  68  82  58
```

**Upbeat accent (more driving):**
```
8ths: 1   +   2   +   3   +   4   +
Vel:  70  95  65  90  68  92  62  88
```

### Add Randomness

After setting pattern, add random variation ±5-10 velocity.

**Logic Pro:**
1. Select hi-hat notes
2. MIDI Transform → Humanize
3. Velocity: ±8
4. Position: ±10 ticks

### Timing Looseness

Hi-hats should be the LOOSEST element:
- Random timing variation: ±10-20ms
- Can push slightly ahead of beat (driving feel)
- Or behind (lazy feel)

### Articulation Variety

Don't use the same hi-hat sample every hit:
- Closed tight
- Closed loose
- Slightly open
- Open
- Foot splash

**Pattern idea:**
```
1   +   2   +   3   +   4   +
Cl  Cl  Cl  Lo  Cl  Cl  Cl  Op
```

### Open Hi-Hat Timing

Open hi-hats typically:
- Hit on an "and" (upbeat)
- Close ON the next downbeat (not before)
- Velocity 80-110

---

## Snare: Ghost Notes Are Everything

### What Are Ghost Notes?

Very quiet snare hits (velocity 25-45) between the main backbeat.

### Basic Ghost Note Pattern

**Without ghosts (robotic):**
```
1 e + a 2 e + a 3 e + a 4 e + a
        X               X
```

**With ghosts (human):**
```
1 e + a 2 e + a 3 e + a 4 e + a
    g   X g       g     X   g
Vel:35  100 40    30    100 38
```

### Ghost Note Rules

- Velocity: 25-45 (barely audible in the mix)
- Usually on 16th notes ("e" and "a")
- Not on every 16th — sparse
- Slightly looser timing than main hits
- More ghosts = busier feel

### Main Snare Variation

Even the main backbeat shouldn't be identical:
- Velocity range: 95-115
- Slight timing drift: ±5-10ms
- Maybe 2 hits per bar are slightly quieter

### Snare Rolls and Drags

**Drag (flam-like):**
- Two hits very close together
- First hit: velocity 40-60, slightly early
- Second hit: velocity 100+, on the beat

**Roll:**
- Crescendo velocity through the roll
- Start: 50, End: 120
- Slight timing looseness

---

## Kick Drum

### Keep It Tight (Mostly)

Kick can be tighter than other elements:
- Timing: ±5ms (not much drift)
- Velocity: Range of 85-110
- Downbeats stronger

### Velocity Variation

```
1   +   2   +   3   +   4   +
K           K       K
100         95      90
```

Downbeat slightly strongest.

### Double Kicks

When programming quick double kicks:
- First hit: velocity 85-95
- Second hit: velocity 95-110 (accent on landing)
- Or reverse for different feel

---

## Fills

### The Fill Trap

Fills are where programmed drums die. Avoid:
- Perfectly even 16th notes
- All same velocity
- No crescendo
- Landing too perfect

### Natural Fill Characteristics

1. **Crescendo:** Gets louder toward downbeat
   ```
   Fill:  1 e + a 2 e + a 3 e + a 4 e + a | 1
   Vel:   60 70 80 85 90 95 100 105 110 115 | CRASH
   ```

2. **Timing loosens slightly** at peak intensity

3. **Landing hit is strong** — crash + kick on 1

4. **Setup hit before fill** — often a kick or snare accent

### Simple vs. Complex

Match fill complexity to:
- Genre (jazz = simple, metal = complex)
- Song energy
- Drummer skill you're emulating

**Simple fill (universal):**
```
Beat 4: floor tom → snare → snare → kick | crash on 1
```

**Busier fill:**
```
Beat 3-4: snare-tom-tom-snare-tom-floor-floor-kick | crash
```

### Fill Frequency

- Every 4 bars: Small fill or variation
- Every 8 bars: Medium fill
- Section changes: Bigger fill
- Not every fill should be big

---

## Building a Full Pattern

### Step-by-Step Workflow

**Step 1: Kick pattern**
- Program on grid
- Velocity 95-110
- Keep tight

**Step 2: Snare backbeat**
- Hits on 2 and 4
- Velocity 95-110
- Slight timing variation (±5ms)

**Step 3: Add ghost notes**
- Very quiet (vel 30-45)
- On 16th divisions
- Sparse — don't overdo

**Step 4: Hi-hat pattern**
- Velocity pattern (accent downbeat or upbeat)
- Random variation added
- Loose timing (±10-20ms)
- Mix articulations

**Step 5: Humanize pass**
- Select all
- MIDI Transform → Humanize (light)
- Or apply groove template

**Step 6: Variation**
- Every 2-4 bars, change something small
- Fill at end of 4 or 8 bars

---

## Groove Templates

### Using Groove Templates (Logic Pro)

1. Select drum MIDI region
2. Region Inspector → Quantize
3. Choose groove (not just note value)
4. Adjust Q-Strength

### Good Built-in Grooves

- **Drummer grooves** — From Logic's Drummer
- **MPC grooves** — Hip-hop swing
- **Vinyl grooves** — Sampled feel

### Making Your Own Groove

1. Find a drum loop you love
2. Import to Logic
3. Convert to MIDI (or tap it in)
4. Select region → Edit → Create Groove Template
5. Apply to your programmed drums

---

## Per-Genre Guidelines

### Rock
- Kick/snare tight
- Hi-hats moderate variation
- Crashes on section changes
- Fills on 4s and 8s
- Ghost notes: sparse to moderate

### Hip-Hop
- Kick tight, snare slightly late (10-30ms)
- Hi-hats loose, often 16ths
- Heavy swing (55-62%)
- Ghost notes: moderate
- Fills: simple or none

### Pop
- Moderate tightness overall
- Clear backbeat
- Predictable patterns
- Fills at section changes
- Ghost notes: sparse

### Jazz
- Very loose timing (all elements)
- Ride cymbal = main timekeeper
- Ghost notes: heavy
- Kick and snare = conversational, not rigid
- Fills: musical, responsive

### Electronic/EDM
- Tighter overall (okay)
- Variation through sound design instead
- Filter sweeps on hats
- Builds through layers, not looseness
- Can be more machine-like (intentional aesthetic)

### Lo-fi
- Very loose (50-60% quantize)
- Heavy swing
- Velocity randomization
- "Mistakes" left in
- Sampled/crunchy sounds help

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Same hi-hat velocity | Create velocity pattern + randomize |
| No ghost notes | Add sparse quiet snare hits |
| Copy/paste 4 bars forever | Vary something each repeat |
| Fills same velocity | Crescendo through fill |
| Crash on every 1 | Save crashes for section changes |
| Too much going on | Simplify, let it breathe |
| Toms same velocity | First hit slightly softer |

---

## Quick Reference

### Velocity Ranges
| Element | Min | Max | Notes |
|---------|-----|-----|-------|
| Kick | 85 | 115 | Downbeat strongest |
| Snare (main) | 90 | 120 | Slight variation |
| Snare (ghost) | 25 | 45 | Barely audible |
| Hi-hat | 55 | 110 | Wide range |
| Toms | 80 | 120 | Crescendo in fills |
| Crash | 100 | 127 | Strong |

### Timing Guidelines
| Element | Variation | Notes |
|---------|-----------|-------|
| Kick | ±5ms | Keep tight |
| Snare | ±5-10ms | Can be slightly late |
| Hi-hat | ±10-20ms | Loosest |
| Fills | Loosen at peak | Natural push |

---

## Hear It In Action

### Reference Tracks for Drum Feel

- **D'Angelo "Untitled"** — Questlove's "drunk" drums
- **J Dilla "Don't Cry"** — Swung, imperfect
- **Led Zeppelin "When The Levee Breaks"** — Bonham's pocket
- **Anderson .Paak "Come Down"** — Modern groove
- **Vulfpeck "Dean Town"** — Intentionally loose

---

## Related
- [[Humanizing Your Music]]
- [[Humanization Cheat Sheet]]
- [[Mixing Workflow Checklist]]

