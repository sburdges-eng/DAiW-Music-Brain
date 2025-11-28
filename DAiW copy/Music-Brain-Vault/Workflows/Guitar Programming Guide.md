# Guitar Programming Guide

Making programmed guitars sound like a real player — acoustic, electric, and bass.

---

## Why Programmed Guitar Sounds Fake

The tells:
- No string noise or fret sounds
- Perfect timing on strums
- All strings hit at once
- No palm muting variation
- Same tone on every note
- No slides, bends, or vibrato

---

## Strumming: The Biggest Challenge

### Real Strums Take Time

A guitarist's pick travels across strings — it's not instant.

**Strum Spread:**
| Direction | Order | Timing |
|-----------|-------|--------|
| Down strum | Low to high | 20-50ms total |
| Up strum | High to low | 20-50ms total |

### How to Program Strums

**Method 1: Manual**
1. Draw chord (all notes stacked)
2. Turn off Snap
3. Stagger notes by 5-10ms each
4. Low E first for downstrum, high E first for upstrum

**Example (Down Strum):**
```
E2: |====
A2:  |====
D3:   |====
G3:    |====
B3:     |====
E4:      |====
     Time →  (about 30-40ms total spread)
```

**Method 2: Arpeggiator (Quick)**
1. Add Arpeggiator MIDI FX
2. Set Rate very fast (1/64 or faster)
3. Direction: Up (for down strum) or Down (for up strum)
4. Adjust rate to taste

### Strum Pattern Variation

Don't strum every chord the same way:
- Some tighter (faster strum)
- Some looser (slower strum)
- Some partial (not all strings)
- Mix down and up strums

**Pattern Example:**
```
Beat:   1     +     2     +     3     +     4     +
Strum:  D           D     U           D     U     
Tight:  Yes         No    Yes         Yes   No
```

---

## Velocity Dynamics

### Accent Patterns

**Basic Strum Accents:**
```
Beat:   1     +     2     +     3     +     4     +
Vel:    100   70    85    65    95    72    80    68
        Accent      medium      accent      
```

Downbeats stronger, upbeats lighter.

### Per-String Velocity

Within a single strum:
- Bass strings slightly stronger
- High strings slightly lighter
- Or vice versa for different feel

**Example:**
```
E2: velocity 95
A2: velocity 90
D3: velocity 85
G3: velocity 80
B3: velocity 75
E4: velocity 70
```

---

## Note Length and Muting

### Staccato vs. Sustained

**Sustained chords:**
- Notes ring full length
- Overlap into next chord
- More open, ringing sound

**Muted/Staccato:**
- Notes cut short
- Gaps between chords
- Tighter, more rhythmic

**Mix both:**
```
Beat:   1     +     2     +     3     +     4     +
Type:   Long        Short Short       Long  Short
```

### Palm Muting

If your guitar library has palm mute samples:
- Use on rhythmic parts
- Mix muted and open
- Creates dynamic variation

**Common Pattern (rock):**
```
PM: mute mute mute open | mute mute mute open
    chug chug chug ring | chug chug chug ring
```

---

## Articulations: Slides, Bends, Vibrato

### Slides

**Slide Into Note:**
- Start pitch 2-5 semitones below
- Pitch bend up to target
- Takes 50-150ms

**Slide Out of Note:**
- Bend down at end of note
- Falls off naturally

**Logic Pro:**
1. Piano Roll → Show Pitch Bend
2. Draw bend before/during note
3. Bend range: Usually ±2 semitones

### Bends

**Blues/Rock Bends:**
- Bend up 1-2 semitones
- Hold at peak
- Release back down

**Bend Shape:**
```
Pitch:  ___/‾‾‾‾\___
        Attack hold release
```

**Velocity on Bent Notes:**
- Usually stronger (100-120)
- Expressive moments

### Vibrato

**LFO on Pitch:**
- Rate: 4-6 Hz
- Depth: ±20-50 cents
- Delay: Don't start immediately — let note settle, then add

**Manual Vibrato:**
- Draw pitch bend wobbles
- Not perfectly regular
- Varies in speed and depth

---

## Hammer-Ons and Pull-Offs

### What They Are

Fast notes without re-picking:
- Hammer-on: Lower note → higher note (finger slams down)
- Pull-off: Higher note → lower note (finger pulls off)

### How to Program

**Hammer-On:**
- Second note slightly softer (velocity -15 to -25)
- No gap between notes (legato)
- First note cut short when second starts

**Pull-Off:**
- Same but reversed pitch direction
- Second note even softer sometimes

**Example:**
```
Note 1: velocity 100, ends when note 2 starts
Note 2: velocity 75, overlaps slightly or immediately follows
```

---

## Power Chords and Riffs

### Power Chord Basics

Just root and fifth (and often octave):
- E5 = E + B
- A5 = A + E

### Programming Power Chords

**Tight and Punchy:**
- Notes hit nearly together (2-5ms spread max)
- Strong velocity (95-115)
- Often palm muted between hits
- Staccato on rhythmic parts

**The Chunk:**
Muted "chunk" sounds between power chords:
- Very short notes
- Palm mute articulation
- Lower velocity
- Adds rhythm and aggression

---

## Fingerpicking Patterns

### The Pattern

Thumb plays bass, fingers play melody/harmony:
```
String: E A D G B e
Finger: T T   i m a  (T=thumb, i=index, m=middle, a=ring)
```

### How to Program

**Bass Notes (Thumb):**
- Stronger velocity (90-105)
- On beats 1 and 3 typically
- Longer sustain

**Treble Notes (Fingers):**
- Softer velocity (65-85)
- More timing variation
- Arpeggiated patterns

### Travis Picking Pattern

Classic alternating bass pattern:
```
Beat:    1   +   2   +   3   +   4   +
Bass:    E       A       E       A
Treble:      G+B     G+B     G+B     G+B
```

---

## Acoustic vs. Electric

### Acoustic Guitar

**More Organic Feel:**
- Wider velocity range
- More timing looseness
- String noise matters more
- Body resonance (let notes ring)

**Strumming:**
- Slower strum spread (30-50ms)
- Full chord strums common
- Pick or finger differences

### Electric Guitar

**Can Be Tighter:**
- Palm muting common
- Power chords
- Sustain and feedback
- More articulations (bends, wah, etc.)

**Tone Variation:**
- Clean vs. dirty
- Pickup position changes
- Amp dynamics

---

## Double Tracking

### Why Double Track

Standard practice for thick guitar sound:
- Two performances (slightly different)
- Panned left and right
- Sounds huge

### Programming Doubles

**Don't just copy/paste.**

Method:
1. Create original guitar part
2. Duplicate to new track
3. Change timing slightly (±5-15ms random)
4. Change velocity slightly (±8-12)
5. Can change some notes/voicings
6. Pan one left, one right

**Detune Option:**
- Pitch one copy up 5-10 cents
- Pitch other copy down 5-10 cents
- Creates natural chorus/width

---

## String Noise and Realism

### What's Missing

Real guitars have:
- Finger squeaks on wound strings
- Fret buzz (subtle)
- Pick attack noise
- String scrapes between chords

### How to Add

**Use Libraries With Noise:**
- Many guitar libraries include noise samples
- Map to unused keys
- Trigger occasionally

**Layer Noise:**
- Find guitar noise samples/loops
- Mix very quietly underneath
- Adds subliminal realism

**Pick Sound:**
- Some libraries have "pick only" samples
- Ghost notes with just pick attack
- Very low velocity

---

## Logic Pro Workflow

### Step 1: Basic Part

Program notes/chords on grid with reasonable velocity.

### Step 2: Strum Spread

For chords:
- Turn off Snap
- Stagger notes to create strum
- Alternate up/down strum patterns

### Step 3: Articulations

Add expression:
- Pitch bends for slides/bends
- Velocity variation for dynamics
- Note lengths for sustain/muting

### Step 4: Humanize Pass

MIDI Transform → Humanize:
- Position: ±5-10 ticks
- Velocity: ±10-15
- Length: ±5 ticks

### Step 5: Groove

Apply groove template or manually adjust timing feel.

---

## Amp Simulation Tips

### Dynamic Response

Good amp sims respond to velocity/input:
- Play softer = cleaner tone
- Play harder = more breakup/drive
- Use this dynamically

### Don't Over-Gain

Too much distortion:
- Hides mistakes (but also hides expression)
- Loses note definition
- Gets muddy in a mix

Less gain + right technique = better tone.

---

## Quick Checklist

Before finalizing guitar parts:

- [ ] Strums spread across time (not instant)
- [ ] Velocity varies (accents on downbeats)
- [ ] Mix of sustained and muted notes
- [ ] Slides/bends on appropriate notes
- [ ] Double tracks are actually different
- [ ] Not quantized to 100%
- [ ] Feels like someone's playing

---

## Related
- [[Humanizing Your Music]]
- [[Guitar Recording Workflow]]
- [[Bass Programming Guide]]

