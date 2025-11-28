# Piano & Keys Humanization Guide

Making programmed piano, electric piano, and keys sound like real performances.

---

## Why Keys Sound Fake

Dead giveaways:
- All notes in a chord hit at exactly the same time
- Same velocity throughout
- No pedal expression
- Perfect repetition
- No dynamic variation between phrases

---

## Velocity Is Everything

### Piano Is Extremely Dynamic

Real pianists use a huge velocity range:
- Quiet passages: 30-60
- Medium: 60-90
- Loud: 90-127
- Accents can hit 127

### Layer Velocity

Within a single chord or phrase:

**Melody vs. Accompaniment:**
- Melody notes: Louder (velocity +10-20)
- Accompaniment: Softer
- Right hand often louder than left

**Chord Voicing:**
- Top note (melody) loudest
- Inner voices softer
- Bass note moderate

**Example:**
```
Note:    C3   E3   G3   C4 (melody)
Velocity: 75   65   68   95
```

### Phrase Dynamics

**Shape each phrase:**
- Start softer
- Build toward peak
- Taper at end

**Quick Humanize:**
1. Select piano MIDI
2. MIDI Transform → Humanize
3. Velocity: ±15 (piano needs more variation than most)
4. Apply

---

## Chord Voicing: Don't Hit All Notes Together

### The Problem

When you draw a chord, all notes start at exactly the same tick. No human plays like this.

### The Roll/Spread

Real pianists roll chords slightly:
- Notes hit 5-30ms apart
- Not perfectly even spacing
- Usually bottom-to-top, but not always

### How to Roll Chords in Logic Pro

**Method 1: Manual**
1. Turn off Snap (N key)
2. Nudge individual notes left/right
3. Bottom note first, or top note first
4. Vary the timing between notes

**Method 2: MIDI Transform**
1. Select chord notes
2. Edit → MIDI Transform
3. Create a "spread" effect:
   - Position: Add random offset
   - Or use Humanize

**Method 3: Arpeggiator (Creative)**
1. Add Arpeggiator MIDI FX
2. Set very fast rate
3. Direction: Up or Down
4. Creates instant rolls

### How Much to Roll

| Style | Roll Amount |
|-------|-------------|
| Classical ballad | 20-50ms |
| Pop piano | 10-30ms |
| Tight rhythmic | 5-15ms |
| Jazz voicings | 10-40ms |
| Electric piano | 10-25ms |

### Variation Per Chord

Don't roll every chord identically:
- Some more spread
- Some tighter
- Some top-to-bottom
- Some bottom-to-top

---

## Sustain Pedal

### Why It Matters

Pedal is half of piano expression:
- Connects notes (legato)
- Adds resonance
- Blurs or separates harmonies
- Changes every few beats/bars

### Recording Pedal

**Best Method:**
- Record pedal as you play (CC64)
- Use a sustain pedal on your controller
- Logic captures the MIDI

**Drawing Pedal:**
1. Piano Roll → Show Sustain (CC64)
2. Draw: 127 = on, 0 = off
3. Lift before chord changes (avoid mud)
4. Not just on/off — can be subtle

### Pedal Timing

**Before chord changes:**
```
Chord: | C major . . . | F major . . . |
Pedal: |____↑___↓_____|_____↑___↓____|
       Press  Lift     Press   Lift
              (just before F)
```

**Release and re-catch:**
- Lift just before new chord
- Press again immediately after
- Catches the new harmony clean

### Half-Pedaling

Not just on/off:
- Partial pedal = partial sustain
- Draw CC64 values between 0-127
- Adds nuance

### When NOT to Pedal

- Fast rhythmic passages
- When clarity matters
- Staccato sections
- When it sounds muddy

---

## Left Hand vs. Right Hand

### Different Roles

**Left Hand (Bass/Harmony):**
- Usually slightly softer (velocity -10 from right)
- More consistent timing
- Often follows chord changes on downbeats

**Right Hand (Melody/Lead):**
- More expressive
- More velocity variation
- More timing looseness
- Leads the phrase

### Timing Independence

Hands don't play in perfect sync:
- Left hand might be slightly ahead (driving)
- Or slightly behind (relaxed)
- Vary per phrase

---

## Electric Piano Specifics

### Rhodes/Wurlitzer

**Velocity Response:**
- Lower velocity = softer, darker (bark)
- Higher velocity = louder, brighter, more bark
- Use full range (40-120)

**Tremolo:**
- Classic Rhodes uses tremolo effect
- Automate rate and depth
- More tremolo on sustained notes

**Expression:**
- Not as much pedal as acoustic piano
- More rhythmic playing often
- Velocity variation still critical

### Clavinet

**Highly Percussive:**
- Staccato, funky playing
- Strong velocity accents
- Often muted/dampened
- Less sustain than piano

**Wah Effect:**
- Often paired with auto-wah or wah pedal
- Filter movement = expression

---

## Organ Specifics

### Hammond/B3

**No Velocity:**
- Most organ patches ignore velocity
- Expression comes from volume control (CC7 or CC11)
- Or drawbar automation

**Leslie/Rotary:**
- Slow vs. fast rotor
- Automate speed changes
- Adds massive life

**Swell Pedal:**
- Automate expression (CC11)
- Volume swells on chords
- Essential for organ realism

### Organ Performance Tips

- Glissandos (sliding up/down keys)
- Held bass notes while right hand moves
- Stabs and rhythmic patterns
- Drawbar changes mid-song

---

## Quantization for Keys

### How Much to Quantize

| Style | Quantize Strength |
|-------|-------------------|
| Classical | 50-70% |
| Jazz | 40-60% |
| Pop ballad | 60-80% |
| Pop upbeat | 70-85% |
| Funk/R&B | 55-75% |
| Gospel | 50-70% |

### Groove Templates

Apply grooves to piano parts:
1. Select region
2. Region Inspector → Quantize
3. Choose groove (not just note value)
4. Adjust strength

---

## Common Piano Patterns & How to Humanize

### Ballad Arpeggios

**Pattern:** Broken chord patterns (C-E-G-C...)

**Humanize:**
- Slight velocity crescendo through arpeggio
- First note of each beat slightly stronger
- Timing: slight looseness (±10ms)
- Let notes ring with pedal

### Rhythmic Chords

**Pattern:** Repeated chord stabs

**Humanize:**
- Downbeat slightly stronger
- Not every chord same velocity
- Slight roll on some chords, not all
- Occasional variation in voicing

### Walking Bass (Left Hand)

**Pattern:** Quarter note bass line

**Humanize:**
- Slight timing push or pull
- Accents on strong beats
- Ghost notes occasionally
- Not every note same length

### Block Chords

**Pattern:** Chords moving together

**Humanize:**
- Roll chords slightly
- Top note (melody) louder
- Phrase-level dynamics
- Pedal connecting

---

## Logic Pro Piano Workflow

### Step 1: Play In (If Possible)

Even imperfectly:
- Play the part
- Quantize lightly (60-75%)
- Fix only obvious mistakes
- Natural dynamics captured

### Step 2: Velocity Shaping

After recording:
1. Select all notes
2. Check velocity range (should be wide)
3. MIDI Transform → Humanize (Velocity ±12)
4. Manual tweaks for emphasis

### Step 3: Chord Rolls

For stacked chords:
- Turn off snap
- Nudge notes to roll
- Not all chords identical

### Step 4: Pedal

Record or draw CC64:
- Lift before chord changes
- Press after new chord lands
- Leave gaps for clarity

### Step 5: Final Humanize

Light humanize pass:
- Position: ±5-8 ticks
- Velocity: ±8-12
- Length: ±3-5 ticks

---

## Quick Checklist

Before finalizing piano/keys:

- [ ] Velocity range is wide (30-127)
- [ ] Melody louder than accompaniment
- [ ] Chords rolled slightly (not perfectly together)
- [ ] Sustain pedal recorded/drawn
- [ ] Phrases have dynamic shape
- [ ] Left and right hand feel independent
- [ ] Not quantized to 100%
- [ ] Repetitions have slight variation

---

## Related
- [[Humanizing Your Music]]
- [[Synth Humanization Guide]]
- [[Humanization Cheat Sheet]]

