# Synth Humanization Guide

Making synthesizers feel organic and alive instead of cold and static.

---

## Why Synths Sound Fake

The problems:
- Static, unchanging sound
- Perfect timing
- No expression variation
- Machine-like repetition
- Lack of movement

Real instruments change constantly. Synths need to move.

---

## The Golden Rule

**Nothing should stay static.**

Every parameter should move, at least subtly:
- Filter cutoff
- Volume/amplitude
- Pitch (very subtle)
- Modulation depth
- Effects amounts

---

## MIDI Humanization (Same As Other Instruments)

### Velocity Variation

Synths that respond to velocity feel more human:
- Range: 70-120 (varies by patch)
- Accented notes louder
- Passing notes softer
- Random variation ±10

**Logic Pro:**
1. Select synth MIDI
2. MIDI Transform → Humanize
3. Velocity: ±10
4. Apply

### Timing Looseness

- Don't quantize to 100%
- Try 70-85% strength
- Or shift some notes manually

### Note Length

- Not every note same length
- Some legato (overlapping)
- Some staccato (short gaps)
- Let some notes ring, cut others short

---

## Modulation: The Key to Life

### Mod Wheel (CC1)

Record mod wheel movement as you play:
1. Arm the track
2. Move mod wheel while playing
3. Logic records the CC1 data
4. Edit in Piano Roll if needed

**What to modulate with mod wheel:**
- Vibrato depth
- Filter cutoff
- LFO intensity
- Anything mapped in the synth

### Drawing Modulation

If you didn't record it:
1. Piano Roll → Show Modulation lane
2. Draw curves with pencil tool
3. Swell up on sustained notes
4. Back down on releases

### Vibrato Timing

Real players add vibrato AFTER the note starts:
```
Note start → Straight → Vibrato develops → Sustains
    0ms        100ms       300ms+
```

Don't start with full vibrato — let it grow.

---

## Filter Movement

### Why Filters Matter

Static filter = dead synth. Moving filter = alive.

### Techniques

**1. Velocity to Cutoff:**
Set in synth: Higher velocity = filter opens more
- Accented notes brighter
- Soft notes darker
- Automatic expression

**2. Envelope on Filter:**
- Attack: Filter opens as note starts
- Decay: Filter closes to sustain level
- Creates motion on every note

**3. Automate Cutoff:**
- Draw automation curves in Logic
- Open during builds
- Close during verses
- Subtle movement throughout

**4. LFO on Filter (Subtle):**
- Very slow LFO (0.1-0.5 Hz)
- Small amount
- Creates gentle, constant movement
- Not obvious wobble — just life

---

## Pitch Variation

### Subtle Pitch Drift

Real analog synths drift slightly in pitch. Add:

**In the Synth:**
- Look for "Drift," "Analog," "Slop" knobs
- Subtle detune between oscillators
- Very slight pitch randomization

**In Logic (Pitch Bend):**
- Very subtle pitch automation
- ±5-10 cents, slow movement
- Not noticeable as pitch change
- Just adds organic feel

### Portamento/Glide

Notes slide into each other:

**Settings:**
- Glide Time: 20-100ms for subtle
- Mode: Legato (only glides when overlapping)
- Adds expression to melodic lines

### Vibrato

**LFO to Pitch:**
- Rate: 4-6 Hz (natural vibrato speed)
- Depth: Very subtle (5-20 cents)
- Delay: Vibrato starts after note begins

---

## Unison and Detune

### Unison Voices

Multiple voices playing same note, slightly detuned:

**Settings:**
- Voices: 2-4 (more = thicker)
- Detune: 5-15 cents between voices
- Spread: Voices panned across stereo

### Why It Helps

- Adds thickness
- Natural beating/movement
- Sounds less "perfect"
- More like multiple players

### Don't Overdo It

- Too much unison = washy
- For leads: 2-4 voices
- For pads: 4-8 voices
- For bass: 2 voices or none

---

## Pad Humanization

Pads are especially prone to sounding static.

### Essential Pad Movement

**1. Filter Movement:**
- Slow LFO on cutoff
- Or automate manually
- Open and close gradually

**2. Volume Swells:**
- Automate volume for breathing
- Not on/off — gradual swells
- Or use expression (CC11)

**3. Stereo Movement:**
- Slow auto-pan
- Or stereo width automation
- Subtle, not obvious ping-pong

**4. Multiple Layers:**
- Two pads, slightly different
- One brighter, one darker
- Crossfade between them

### Pad Chords

**Don't hit all notes at once:**
- Roll the chord slightly (5-30ms between notes)
- Bottom note first, or top note first
- Not mechanical — slightly random

**Logic Pro:**
1. Select chord
2. Functions → MIDI Transform
3. Spread notes in time
4. Or: Manually nudge with snap off

---

## Lead Synth Humanization

### Expression is Everything

**Velocity:**
- Wide range (60-127)
- Phrase dynamics (louder at peaks)
- Accents on important notes

**Pitch Bend:**
- Bend into notes (like a guitarist)
- Slight bends for emphasis
- Not on every note — tasteful

**Mod Wheel:**
- Vibrato on sustained notes
- More intensity = more mod
- Back off on short notes

### Phrasing

Real players breathe. Add gaps:
- Not every note connected
- Rests between phrases
- Let notes end naturally

### Articulation

Vary how notes start and end:
- Some notes hard attack
- Some notes soft attack
- Some notes ring out
- Some notes cut short

---

## Arpeggiator Humanization

### The Problem

Arpeggios are the most robotic-sounding synth patterns.

### Solutions

**1. Don't quantize the arp:**
- Reduce quantize strength
- Or: Disable arp, play the notes manually

**2. Velocity variation in arp:**
- Set arp to follow input velocity
- Or: Set arp velocity pattern (not all same)

**3. Timing swing:**
- Many arps have swing control
- Try 52-58% for subtle shuffle

**4. Occasional variations:**
- Automate arp rate changes
- Change octave range
- Mute some notes

**5. Record and edit:**
- Record arp output as MIDI
- Turn off arpeggiator
- Now you can humanize the MIDI directly

---

## Automation Ideas

### What to Automate

| Parameter | Effect |
|-----------|--------|
| Filter Cutoff | Brightness changes |
| Resonance | Character changes |
| Volume | Swells, dynamics |
| Pan | Movement in stereo |
| Reverb Send | Depth changes |
| Delay Send | Space changes |
| LFO Rate | Evolving modulation |
| LFO Depth | Intensity changes |

### Automation Tips

- Don't just draw straight lines
- Use curves (S-curves feel natural)
- Movement doesn't have to be dramatic
- Subtle = more human, less obvious

---

## Sound Design for Organic Feel

### Random Modulation

Many synths have random/sample-and-hold LFO:
- Route to pitch (very subtle)
- Route to filter (subtle)
- Route to pan
- Adds unpredictability

### Noise Layer

Adding subtle noise makes synths feel more organic:
- Mix in white/pink noise very quietly
- Or use synth's noise oscillator
- Barely audible — just adds texture

### Sample-Based Layers

Layer a real recording underneath:
- Acoustic piano under synth keys
- String section under synth pad
- Barely audible, adds realism

### Analog Modeling

Use synths or plugins with:
- Oscillator drift
- Component modeling
- "Analog" modes
- Warmth/saturation

---

## Logic Pro Tools

### MIDI Humanize

Edit → MIDI Transform → Humanize
- Position: ±5-10 ticks
- Velocity: ±10
- Length: ±5 ticks

### Automate Everything

1. Press A (show automation)
2. Choose parameter from dropdown
3. Draw with pencil or record with controller
4. Use curves, not just straight lines

### Scripter MIDI FX (No Code Needed)

Logic includes preset scripts:
1. Add Scripter to MIDI FX slot
2. Choose preset (Humanize, Randomize, etc.)
3. Adjust parameters
4. No coding required

### Modulator MIDI FX

Add automatic modulation:
1. MIDI FX → Modulator
2. Draws LFO curves
3. Assign to any parameter
4. Creates constant movement

---

## Quick Checklist

Before finalizing synth parts:

- [ ] Velocity varies throughout
- [ ] Timing not perfectly quantized
- [ ] Filter moves (automation or LFO)
- [ ] Vibrato develops on sustained notes
- [ ] No exact copy-paste repetition
- [ ] Pads swell and breathe
- [ ] Leads have pitch expression
- [ ] Some randomness/drift in sound

---

## Related
- [[Humanizing Your Music]]
- [[Sound Design Template]]
- [[Humanization Cheat Sheet]]

