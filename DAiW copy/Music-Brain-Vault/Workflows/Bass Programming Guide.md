# Bass Programming That Sounds Human

Making programmed bass feel like a real player.

---

## Why Bass Sounds Fake

Dead giveaways:
- Every note same length
- Every note same velocity
- Perfectly on the grid
- No slides or articulation
- Static tone throughout

---

## The Pocket: Timing Is Everything

### Where Bass Sits in Time

| Feel | Timing | Use For |
|------|--------|---------|
| **On the grid** | Exact | Tight pop, EDM |
| **Behind the beat** | 10-30ms late | Hip-hop, R&B, soul, groove |
| **Ahead of the beat** | 5-15ms early | Driving rock, punk, urgent |

### How to Shift Timing in Logic Pro

**Entire Track:**
1. Select all bass MIDI
2. Option+drag slightly left or right
3. Or: Region Inspector → Delay (in ms)
4. Try +15ms for laid back feel

**Individual Notes:**
1. Turn off Snap (N key)
2. Nudge notes slightly by hand
3. Not all notes — just some

### The Classic Pocket

Bass slightly behind + drums on grid = deep groove

Try: Set bass region delay to +20ms, leave drums at 0.

---

## Velocity Variation

### Basic Principles

- **Root notes:** Stronger (velocity 95-110)
- **Passing notes:** Softer (velocity 75-90)
- **Dead notes:** Muted hits (velocity 50-70)
- **Ghost notes:** Very soft (velocity 40-60)

### Pattern Example

```
Beat:  1   +   2   +   3   +   4   +
Note:  E       G   A   E       D   E
Vel:   100     80  85  95      78  88
```

Downbeats stronger, movement notes lighter.

### Quick Velocity Humanize

1. Select bass notes
2. MIDI Transform → Humanize
3. Velocity: ±8 to ±12
4. Apply

---

## Note Length Variation

### The Big Secret

Real bass players don't hold every note the same length.

| Technique | Note Length | When to Use |
|-----------|-------------|-------------|
| **Sustained** | Full value | Ballads, legato lines |
| **Staccato** | Short, punchy | Funk, tight grooves |
| **Mixed** | Varies | Most natural |

### How to Vary

1. Select some notes
2. Drag the end shorter
3. Leave gaps between some notes
4. Let others ring into the next

**Example:**
```
Note:  |====|  |==|  |======|  |=|
       Long   Short  Long      Short
```

### Dead Notes (Muted Hits)

Percussive muted notes add groove:
- Very short duration
- Lower velocity (50-70)
- Often on 16th subdivisions
- Use a muted bass sample/articulation if available

---

## Slides and Articulation

### Slides Between Notes

Real bassists slide into and out of notes.

**In Logic Pro (Pitch Bend):**
1. Open Piano Roll
2. Show Pitch Bend lane (click disclosure arrow)
3. Draw bend before or after notes
4. Bend range: Usually ±2 semitones

**Quick Slide Shapes:**

Slide UP into note:
```
Pitch: ___/‾‾‾‾‾
       Bend up, then sustain
```

Slide DOWN out of note:
```
Pitch: ‾‾‾‾‾\___
       Sustain, then bend down
```

### Hammer-Ons and Pull-Offs

Faster, connected notes:
- Second note slightly softer
- Minimal gap between notes
- Can overlap slightly (legato)

### String Noise

Some bass instruments include:
- Finger slides on strings
- Fret buzz
- Pick attack

These add realism. Use samples that have them, or layer in subtle string noise.

---

## Octave Playing

### When to Use Octaves

- Builds energy
- Fills out thin sections
- Common in funk, disco, rock

### Programming Octaves

**Pattern:**
```
Beat:  1   +   2   +   3   +   4   +
Note:  E   E'  E   E'  E   E'  G   A
       Low Hi  Low Hi  Low Hi  (movement)
```

**Velocity:**
- Low note: 95-105
- High octave: 85-95 (slightly softer)

**Timing:**
- Can be exactly together
- Or high note slightly after (5-10ms)

---

## Genre-Specific Tips

### Funk Bass

- Tight, staccato notes
- Lots of dead notes
- 16th note patterns
- Strong velocity accents on 1 and 3
- Octave jumps
- Slightly ahead or on the beat

### Hip-Hop/R&B Bass

- Behind the beat (15-30ms)
- Longer, sustained notes
- Sub-heavy, less high frequencies
- Simple patterns
- Heavier swing (55-60%)
- Ghost notes between main hits

### Rock Bass

- Follows kick drum closely
- Moderate note lengths
- On the beat or slightly ahead
- Root notes emphasized
- Fills on section changes

### Pop Bass

- Clean, supportive
- Moderate everything
- Follows chord roots
- Not too busy
- On the beat mostly

### Jazz/Neo-Soul

- Very loose timing
- Walking bass = each note different length
- Lots of chromatic passing tones
- Velocity very expressive
- Behind the beat

---

## Synth Bass Humanization

### Same Principles Apply

Even synth bass benefits from:
- Velocity variation
- Timing looseness
- Note length variation

### Filter Movement

Add life with filter automation:
1. Automate filter cutoff
2. Open slightly on accented notes
3. Close on softer notes
4. Or: Modulate with velocity (in synth)

### Pitch Drift

Subtle pitch instability = analog warmth:
- Use synth's built-in drift/detune
- Or: Slight pitch bend automation
- Very subtle: ±5-10 cents

### Portamento/Glide

Set synth to glide between notes:
- Glide time: 20-80ms for subtle
- Legato mode for connected notes only
- Adds expressiveness

---

## Working With Kick Drum

### The Relationship

Kick and bass need to work together.

**Option 1: Bass follows kick**
- Bass notes hit with kick
- Tightest, most common

**Option 2: Bass between kicks**
- Bass fills gaps
- More movement, less competition

**Option 3: Bass slightly after kick**
- Kick hits, bass follows (10-20ms)
- Separates them in time

### Sidechain (If Needed)

Not humanization, but helps clarity:
- Bass ducks slightly when kick hits
- Creates pumping effect (optional)
- Or just EQ to separate

---

## Logic Pro Tools for Bass

### MIDI Transform → Humanize

1. Select bass MIDI
2. Edit → MIDI Transform → Humanize
3. Settings:
   - Position: ±5 to ±10 ticks
   - Velocity: ±8 to ±12
   - Length: ±5 ticks
4. Apply

### Region Delay

1. Select bass region
2. Region Inspector (left panel)
3. Set Delay: +15 to +30ms for behind-the-beat

### Groove Templates

1. Select bass region
2. Region Inspector → Quantize
3. Choose a groove (not just "1/8 note")
4. Adjust Q-Strength to taste

---

## Quick Checklist

Before you're done with bass:

- [ ] Velocity varies (not all 100)
- [ ] Timing not perfectly on grid
- [ ] Note lengths vary (not all full value)
- [ ] Some slides or pitch movement
- [ ] Relates well to kick drum
- [ ] Feels like it's breathing, not machine

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| All notes same velocity | Stronger on roots, softer on passing |
| Perfectly quantized | Shift track 10-30ms late or loosen |
| All notes same length | Mix staccato and sustained |
| No slides | Add pitch bends into/out of notes |
| Too busy | Simplify, let notes breathe |
| Fighting the kick | Adjust timing or EQ separation |

---

## Related
- [[Humanizing Your Music]]
- [[Drum Programming Guide]]
- [[Humanization Cheat Sheet]]

