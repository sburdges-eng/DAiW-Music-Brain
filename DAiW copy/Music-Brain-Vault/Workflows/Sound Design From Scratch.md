# Sound Design From Scratch

Creating your own sounds using synths — no presets, pure creation.

---

## Sound Design Basics

### What Makes a Sound

Every sound has:
1. **Pitch** — The note (oscillator)
2. **Tone** — The character (waveform, filter)
3. **Volume shape** — How it starts and ends (amplitude envelope)
4. **Movement** — Changes over time (modulation)

Master these four = master sound design.

---

## The Building Blocks

### Oscillators (The Source)

**Basic Waveforms:**

| Waveform | Character | Use For |
|----------|-----------|---------|
| Sine | Pure, clean, subby | Sub bass, pure tones |
| Triangle | Soft, mellow | Soft leads, pads |
| Saw | Bright, rich, buzzy | Leads, pads, bass |
| Square | Hollow, woody | Leads, bass, chiptune |
| Pulse | Variable hollow | Movement, character |
| Noise | No pitch, texture | Hi-hats, risers, texture |

**In Logic's synths (Alchemy, ES2, Retro Synth):**
- Select waveform in oscillator section
- Start with one oscillator
- Add more for thickness

### Filters (Shape the Tone)

**Filter Types:**

| Type | What It Does | Use For |
|------|--------------|---------|
| Low-pass (LP) | Removes highs | Warmth, bass, pads |
| High-pass (HP) | Removes lows | Thinning, leads |
| Band-pass (BP) | Removes highs AND lows | Nasal, focused |
| Notch | Removes specific frequency | Phase effects |

**Key Parameters:**
- **Cutoff:** Where the filter acts
- **Resonance:** Emphasis at cutoff (can self-oscillate)

**The Classic Move:**
- Start with saw wave
- Low-pass filter
- Adjust cutoff = instant tone shaping

### Envelopes (Shape Over Time)

**ADSR Envelope:**
```
Level
  |    /\
  |   /  \____
  |  /        \
  | /          \
  +---A--D--S---R--- Time
```

- **Attack (A):** How fast it starts
- **Decay (D):** How fast it drops to sustain
- **Sustain (S):** Level while held
- **Release (R):** How fast it fades after release

**Amplitude Envelope Examples:**

| Sound | Attack | Decay | Sustain | Release |
|-------|--------|-------|---------|---------|
| Piano/Pluck | Fast | Medium | Low | Medium |
| Pad | Slow | - | High | Slow |
| Bass | Fast | Short | High | Short |
| String | Medium | - | High | Medium |
| Stab | Fast | Fast | 0 | Short |

### LFOs (Movement)

**Low Frequency Oscillator:**
- Too slow to hear as pitch
- Used to modulate other parameters
- Creates movement and life

**LFO Shapes:**
- Sine: Smooth wobble
- Triangle: Smooth, linear
- Saw: Ramp up or down
- Square: On/off switching
- Sample & Hold: Random stepping

**Common LFO Destinations:**
| Destination | Effect |
|-------------|--------|
| Pitch | Vibrato |
| Filter Cutoff | Wah/wobble |
| Amplitude | Tremolo |
| Pan | Auto-pan |

---

## Basic Sound Recipes

### 1. Simple Bass

**Start here:**
1. One oscillator: Saw or Square
2. Low-pass filter: Cutoff around 500Hz
3. Filter envelope: Fast attack, medium decay
4. Amp envelope: Fast attack, short release
5. Add: Slight filter resonance

**Variations:**
- Lower cutoff = darker
- Add sub oscillator (sine, -1 octave)
- More resonance = more character

### 2. Warm Pad

**Recipe:**
1. Two oscillators: Saws, detuned slightly
2. Low-pass filter: Cutoff medium-high
3. Amp envelope: Slow attack (500ms+), long release
4. Add: Slow LFO to filter cutoff
5. Effects: Reverb, chorus

**Key:** The slow attack and LFO movement.

### 3. Plucky Synth

**Recipe:**
1. One oscillator: Saw or Square
2. Low-pass filter: Cutoff low
3. Filter envelope: Fast attack, medium decay, low sustain
4. Amp envelope: Fast attack, medium decay, low sustain
5. Resonance: Medium (adds ping)

**Key:** Filter envelope creates the pluck character.

### 4. Lead Synth

**Recipe:**
1. Two oscillators: Saws, slightly detuned
2. Low-pass filter: Medium-high cutoff
3. Amp envelope: Fast attack, full sustain
4. Add: Vibrato (LFO to pitch, delayed)
5. Optional: Portamento/glide

**Variations:**
- More oscillators = fatter
- Square wave = more hollow
- Filter movement = expression

### 5. Sub Bass

**Recipe:**
1. One oscillator: SINE wave
2. No filter (or gentle low-pass)
3. Amp envelope: Fast attack, full sustain, short release
4. Keep it simple and pure

**Key:** Sine wave = pure sub frequencies.

### 6. Supersaw

**Recipe:**
1. Multiple saw oscillators (4-8)
2. Detune them against each other (5-15 cents)
3. Low-pass filter: High cutoff
4. Unison mode if available
5. Stereo spread

**Key:** Detuning creates thickness and movement.

---

## Modulation Deep Dive

### Filter Movement Is Everything

Static filter = boring sound.

**Techniques:**
1. **Envelope to filter:** Classic pluck/bass sound
2. **LFO to filter:** Wobble, wah, movement
3. **Velocity to filter:** Expression (harder = brighter)
4. **Manual automation:** Complete control

### Vibrato and Pitch Effects

**Natural vibrato:**
- LFO to pitch
- Rate: 4-6 Hz
- Depth: Very subtle (5-20 cents)
- Delay: Starts after note begins

**Pitch drift:**
- Very slow random LFO to pitch
- Almost imperceptible
- Adds analog character

### Amplitude Modulation

**Tremolo:**
- LFO to amplitude
- Rate: 4-8 Hz
- Creates pulsing effect

**Gating:**
- Fast LFO or sequencer to amplitude
- Creates rhythmic patterns

---

## Logic Pro Synths for Sound Design

### Alchemy

**Best for:** Complex sound design, wavetables, sampling

**Key features:**
- Multiple sound sources (VA, wavetable, sampler)
- Powerful modulation
- Effects built-in
- Morphing between sources

### Retro Synth

**Best for:** Classic analog sounds, simple design

**Key features:**
- Analog, Sync, Wavetable, FM engines
- Simple interface
- Good for learning

### ES2

**Best for:** Subtractive synthesis, complex modulation

**Key features:**
- 3 oscillators
- Complex filter routing
- Deep modulation matrix

### Sculpture

**Best for:** Organic, physical modeling sounds

**Key features:**
- Models physical objects (strings, etc.)
- Unique, evolving sounds
- Great for pads and textures

---

## Sound Categories and Approaches

### Bass Sounds

**Subtractive approach:**
- Start bright (saw)
- Filter down
- Shape with envelopes

**Key elements:**
- Strong fundamental
- Controlled harmonics
- Tight amp envelope

### Pad Sounds

**Layering approach:**
- Multiple detuned oscillators
- Slow everything
- Add movement (LFO)
- Lots of reverb/effects

**Key elements:**
- Slow attack
- Long release
- Constant movement
- Width and space

### Lead Sounds

**Cutting approach:**
- Bright oscillators
- Medium-high filter
- Vibrato
- Portamento

**Key elements:**
- Cuts through mix
- Expressive
- Character

### Pluck Sounds

**Envelope approach:**
- Fast filter decay
- Creates the pluck
- Resonance adds ping

**Key elements:**
- Fast attack
- Quick decay
- Filter envelope is key

### FX and Risers

**Movement approach:**
- Automate everything
- Noise elements
- Filter sweeps
- Pitch rises

**Key elements:**
- Change over time
- Build tension
- Create transitions

---

## Sound Design Workflow

### Step 1: Start Simple

1. One oscillator
2. Choose waveform
3. Set filter and cutoff
4. Shape with amp envelope
5. Listen — is it close?

### Step 2: Add Complexity

6. Add second oscillator (detune)
7. Add filter envelope
8. Add LFO modulation
9. Adjust and refine

### Step 3: Effects

10. Reverb for space
11. Delay for depth
12. Chorus for width
13. Distortion for character

### Step 4: Perform

14. Assign mod wheel
15. Set velocity response
16. Test expressiveness

---

## Quick Reference: Envelope Settings

| Sound Type | Attack | Decay | Sustain | Release |
|------------|--------|-------|---------|---------|
| Bass (tight) | 0ms | 200ms | 70% | 50ms |
| Bass (sub) | 5ms | - | 100% | 100ms |
| Pad (soft) | 500ms+ | - | 100% | 1000ms+ |
| Pluck | 0ms | 300ms | 0% | 200ms |
| Lead | 10ms | - | 100% | 300ms |
| Stab | 0ms | 100ms | 0% | 50ms |
| Keys | 5ms | 500ms | 50% | 300ms |
| Strings | 200ms | - | 100% | 500ms |

---

## Troubleshooting Sounds

| Problem | Solution |
|---------|----------|
| Too thin | Add oscillators, detune |
| Too harsh | Lower filter cutoff |
| Too dull | Raise filter, add harmonics |
| No punch | Faster attack, filter envelope |
| Too static | Add LFO modulation |
| Muddy | High-pass filter, reduce low-mids |
| Doesn't cut through | Brighter filter, mid presence |

---

## Related
- [[Synth Humanization Guide]]
- [[Sound Design Template]]
- [[Theory/Audio Recording Vocabulary]]

