# Strings & Orchestral Humanization

Making programmed strings, brass, and woodwinds sound like real players.

---

## Why Orchestral Sounds Fake

The hardest instruments to program because:
- Real players have incredible expression
- Vibrato, dynamics, bow/breath control
- Sections play together but not identically
- Constant tonal variation
- Long tradition of human performance

---

## The Fundamental Problem

**Samples are snapshots.** Real playing is continuous.

You need to fake continuous expression with:
- Automation (constant movement)
- Layering (multiple articulations)
- Velocity and timing variation

---

## Expression: The Most Important Thing

### CC11 (Expression)

**This is your volume swell control.**

Every sustained note needs expression automation:
- Notes swell in
- Notes taper out
- Nothing starts or ends abruptly

**How to Draw Expression:**
1. Piano Roll → Show Expression (CC11)
2. Draw curves, not straight lines
3. Every phrase should have movement

**Basic Expression Shape:**
```
Volume: ___/‾‾‾‾‾‾\___
        Swell up, sustain, fade
```

### CC1 (Modulation)

**Usually controls vibrato depth.**

- Start notes with less vibrato
- Increase vibrato as note sustains
- Not constant — varies with intensity

**Vibrato Timing:**
```
Note starts → Wait 200-400ms → Vibrato develops → Increases → Sustains
```

Don't hit full vibrato immediately.

### Dynamics Over Time

**Every phrase should breathe:**
- Crescendo into climax
- Decrescendo at phrase ends
- Match the emotional arc

---

## Articulation Switching

### What Are Articulations?

Different playing techniques:
- **Sustain/Legato:** Long, connected notes
- **Staccato:** Short, separated notes
- **Spiccato:** Bouncing bow, very short
- **Pizzicato:** Plucked strings
- **Tremolo:** Rapid bowing
- **Marcato:** Strong, accented

### How to Switch (Logic Pro)

Most orchestral libraries use **keyswitches:**
1. Find keyswitch notes (usually very low, like C0, D0, E0)
2. Add keyswitch note before the passage
3. That switches the articulation for following notes

**Example:**
```
C0 (keyswitch: legato)
Notes: C4, D4, E4 (play legato)
D0 (keyswitch: staccato)
Notes: G4, G4, G4 (play staccato)
```

### Mixing Articulations

Don't use one articulation for entire song:
- Legato for melodic, flowing lines
- Staccato for rhythmic punctuation
- Marcato for accents
- Tremolo for tension/drama

---

## Strings Specifically

### Section vs. Solo

**Section strings (multiple players):**
- Slightly looser timing between notes
- More averaged tone
- Layer multiple patches for realism

**Solo strings:**
- More expressive
- More vibrato
- More velocity sensitivity
- Harder to program convincingly

### Layering for Realism

**The Section Effect:**

Real sections have slight variations between players. Fake it:

1. Use the same phrase on two tracks
2. Offset timing by 10-30ms
3. Slight pitch difference (±5-10 cents)
4. Slightly different velocity
5. Pan slightly apart

Creates more realistic "section" sound.

### Legato Lines

**Connect the notes:**
- Notes should overlap slightly
- Or use library's legato mode
- Expression swell between notes
- No gaps in sustained passages

**Logic Pro:**
- Set MIDI region to "No Overlap" if notes are clashing
- Or manually adjust note ends

### Divisi

Real string sections divide parts:
- First violins on melody
- Second violins on harmony
- Violas on inner voice
- Cellos on bass line
- Basses on low support

Don't put everything on one track.

---

## Brass Humanization

### Breath and Attack

Brass players need air:
- Notes have a "bloom" — not instant
- Expression swells into and out of notes
- Natural limit to sustain length

### Brass Dynamics

**ffff doesn't come from nowhere:**
- Build into loud passages
- Crescendo over multiple notes
- Decrescendo on releases

### Brass Articulations

- **Sustain:** Full notes with vibrato
- **Staccato:** Short, punched
- **Sforzando:** Strong attack, quick decay
- **Falls/Doits:** Pitch slides at end

### Horn Section Timing

Not perfectly together:
- Lead player slightly ahead
- Section follows
- Spread hits by 10-30ms
- Creates power without mushiness

---

## Woodwinds Humanization

### Breath and Phrasing

Woodwind players breathe:
- Leave gaps for breaths
- Phrases have natural length limits
- Expression follows air support

### Vibrato

Different than strings:
- Often less vibrato
- Vibrato speed/depth varies by instrument
- Flute: delicate, variable
- Clarinet: less vibrato typically
- Oboe: more focused vibrato

### Articulation

- **Tonguing:** Distinct attacks (ta-ta-ta)
- **Slurred:** Connected (legato)
- **Staccato:** Very short

Alternate tongued and slurred passages.

---

## Building Orchestral Dynamics

### The Volume Stack

From quietest to loudest:

1. **pp:** Solo instruments, minimal
2. **p:** Small section, restrained
3. **mp:** Section playing, moderate
4. **mf:** Full section, present
5. **f:** Full section, strong
6. **ff:** Full orchestra, powerful
7. **fff:** Everything, maximum

### Dynamic Contrast

**The key to emotion:**
- Quiet sections make loud sections impactful
- Build gradually, not suddenly
- The drop-out is as powerful as the crescendo

### Orchestration Dynamics

Adding instruments = louder:
- Start with just strings
- Add woodwinds
- Add brass
- Add percussion
- = Natural crescendo through orchestration

---

## Timing and Rhythm

### Not Too Perfect

Orchestras aren't machines:
- Quantize to 75-85% max
- Slightly looser than pop/rock
- Conductor allows "breathing"

### Section Timing

Different sections have different feel:
- Strings: Most flexible
- Brass: Often slightly late (heavier sound)
- Woodwinds: Can be slightly ahead (lighter)
- Percussion: Anchors the time

### Rubato

**Tempo flexibility:**
- Slow down at phrase ends
- Speed up in building sections
- Use Logic's tempo automation
- Or manual note shifting

---

## Practical Workflow

### Step 1: Sketch First

Get the notes right before humanizing:
- Correct pitches and rhythms
- Proper voice leading
- Right articulation keyswitches

### Step 2: Expression Pass

Go through every track:
- Draw CC11 (expression) curves
- Every sustained note gets a shape
- No static lines

### Step 3: Modulation Pass

Add CC1 (modulation/vibrato):
- Vibrato develops on sustained notes
- More vibrato = more intensity
- Varies by instrument

### Step 4: Velocity Pass

Adjust velocities:
- Accents on strong beats
- Phrase dynamics
- Not all notes the same

### Step 5: Timing Pass

Humanize timing:
- MIDI Transform → Humanize
- Or apply groove template
- Manual adjustment for key moments

### Step 6: Layering

For sections:
- Duplicate and offset
- Create section depth
- Pan for width

---

## Logic Pro Tools

### Automation

1. Press A (show automation)
2. Select CC from dropdown
3. Draw curves with pencil
4. Use curves, not corners

### MIDI Transform

Edit → MIDI Transform:
- Humanize preset
- Adjust position, velocity, length

### Scripter (Preset Scripts)

MIDI FX → Scripter:
- Choose humanize presets
- No coding needed
- Apply to any track

### Articulation Sets

If library supports it:
- Set up articulation sets
- Switch with key commands
- Faster workflow

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| No expression automation | Draw CC11 on every sustained note |
| Instant vibrato | Delay vibrato start 200-400ms |
| Perfect timing | Quantize 75-85%, humanize |
| Same velocity throughout | Dynamic phrases, accents |
| Single articulation | Mix legato, staccato, etc. |
| Section sounds thin | Layer and offset tracks |
| Ends too abrupt | Taper with expression |
| Starts too sudden | Swell into notes |

---

## Quick Checklist

Before finalizing orchestral parts:

- [ ] Expression (CC11) automated on all sustained notes
- [ ] Vibrato (CC1) develops naturally
- [ ] Articulations vary appropriately
- [ ] Dynamics follow the phrase
- [ ] Timing slightly loose (not 100% quantized)
- [ ] Sections layered for depth
- [ ] Notes swell in and taper out
- [ ] Breathing room in wind parts

---

## Related
- [[Humanizing Your Music]]
- [[Synth Humanization Guide]]
- [[Humanization Cheat Sheet]]

