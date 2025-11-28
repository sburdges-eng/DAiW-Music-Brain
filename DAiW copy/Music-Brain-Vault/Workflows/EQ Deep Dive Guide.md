# EQ Deep Dive Guide

Understanding and using equalization to shape your mix.

---

## What EQ Does

EQ (equalization) adjusts the volume of specific frequencies.

**Two main uses:**
1. **Corrective:** Fix problems (remove mud, harshness)
2. **Tonal:** Shape character (add warmth, brightness)

**Rule:** Cut to fix, boost to enhance.

---

## The Frequency Spectrum

### Frequency Ranges

| Range | Frequency | Character | Contains |
|-------|-----------|-----------|----------|
| Sub | 20-60 Hz | Felt, rumble | Sub bass, kick weight |
| Bass | 60-200 Hz | Thump, warmth | Bass, kick body |
| Low-Mid | 200-500 Hz | Body, mud | Vocals, guitars, snare body |
| Mid | 500 Hz-2 kHz | Presence, honk | Most instruments |
| Upper-Mid | 2-6 kHz | Presence, harshness | Vocal clarity, attack |
| High | 6-12 kHz | Brilliance, air | Cymbals, breath |
| Air | 12-20 kHz | Sparkle, air | Highest harmonics |

### What Lives Where

| Instrument | Key Frequencies |
|------------|-----------------|
| Kick drum | Sub: 50-60Hz, Body: 80-100Hz, Click: 3-5kHz |
| Snare | Body: 150-200Hz, Crack: 1-2kHz, Snap: 4-6kHz |
| Bass | Fundamental: 60-100Hz, Presence: 700-1kHz |
| Vocals | Body: 200-300Hz, Presence: 3-5kHz, Air: 10kHz+ |
| Acoustic guitar | Body: 100-250Hz, Clarity: 2-5kHz |
| Electric guitar | Mud: 200-400Hz, Presence: 2-4kHz |
| Piano | Warmth: 100-300Hz, Presence: 2-5kHz |
| Cymbals | Clang: 200-500Hz, Shimmer: 8kHz+ |

---

## EQ Types

### Parametric EQ

**Most flexible:**
- Choose any frequency
- Adjust bandwidth (Q)
- Boost or cut

**Parameters:**
- **Frequency:** Where to affect
- **Gain:** How much to boost/cut
- **Q (bandwidth):** How wide the affected range

**High Q (narrow):** Surgical cuts, specific problems
**Low Q (wide):** Broad tonal shaping

### Shelf EQ

**Affects everything above or below a point:**
- Low shelf: Everything below frequency
- High shelf: Everything above frequency

**Use for:**
- Adding overall warmth (low shelf boost)
- Adding air (high shelf boost)
- Darkening a sound (high shelf cut)

### High-Pass Filter (HPF)

**Removes everything below a frequency:**
- Essential on almost every track
- Removes rumble, mud, unnecessary low end
- Use on everything except bass and kick

**Common settings:**
- Vocals: 80-120 Hz
- Guitars: 80-100 Hz
- Keys: 60-100 Hz
- Hi-hats: 300-500 Hz

### Low-Pass Filter (LPF)

**Removes everything above a frequency:**
- Darkens harsh sounds
- Creates lo-fi effect
- Tames cymbals

---

## Subtractive vs. Additive EQ

### Subtractive (Cutting) — Do First

**Why cut first:**
- Removes problems
- Creates space
- More transparent than boosting
- Less likely to cause clipping

**Common cuts:**
- Mud (200-400 Hz)
- Boxiness (400-600 Hz)
- Harshness (2-4 kHz)
- Rumble (below 60 Hz)

### Additive (Boosting) — Do Second

**Why boost carefully:**
- More noticeable
- Can sound unnatural if overdone
- Adds energy, but also noise/resonances

**Common boosts:**
- Warmth (100-200 Hz)
- Presence (2-5 kHz)
- Air (10 kHz+)

### The 3dB Rule

- Cuts up to 6dB often go unnoticed
- Boosts over 3dB start to sound "EQ'd"
- If you need more than 6dB, consider the source

---

## Finding Problem Frequencies

### The Sweep Method

1. Create a narrow band (high Q)
2. Boost it significantly (+10-15 dB)
3. Sweep across frequencies slowly
4. Listen for where it sounds worst
5. That's your problem frequency
6. Cut there (return Q to normal)

### Common Problem Areas

| Problem | Frequency Range | Solution |
|---------|-----------------|----------|
| Mud | 200-400 Hz | Cut 2-6dB |
| Boxiness | 400-600 Hz | Cut 2-4dB |
| Honk | 500-1000 Hz | Cut 2-4dB |
| Harshness | 2-4 kHz | Cut 1-3dB |
| Sibilance | 5-8 kHz | Cut (or use de-esser) |
| Fizz | 8-12 kHz | Cut 1-3dB |

---

## EQ by Instrument

### Kick Drum

| Goal | Frequency | Action |
|------|-----------|--------|
| More sub weight | 50-60 Hz | Boost 2-4dB |
| More body | 80-100 Hz | Boost 2-3dB |
| Remove mud | 200-400 Hz | Cut 2-6dB |
| More click/attack | 3-5 kHz | Boost 2-4dB |

### Snare Drum

| Goal | Frequency | Action |
|------|-----------|--------|
| More body | 150-200 Hz | Boost 2-3dB |
| Remove boxiness | 400-600 Hz | Cut 2-4dB |
| More crack | 1-2 kHz | Boost 2-4dB |
| More snap | 4-6 kHz | Boost 1-3dB |

### Bass

| Goal | Frequency | Action |
|------|-----------|--------|
| High-pass rumble | Below 40 Hz | HPF |
| More weight | 60-100 Hz | Boost 2-4dB |
| Remove mud | 200-300 Hz | Cut 2-4dB |
| More presence | 700-1000 Hz | Boost 1-3dB |
| String noise | 2-4 kHz | Boost slightly (optional) |

### Vocals

| Goal | Frequency | Action |
|------|-----------|--------|
| High-pass rumble | 80-120 Hz | HPF |
| Remove mud | 200-400 Hz | Cut 2-4dB |
| More body | 150-250 Hz | Boost 1-2dB |
| More presence | 3-5 kHz | Boost 2-4dB |
| More air | 10-12 kHz | Shelf boost 1-3dB |
| Reduce harshness | 2-4 kHz | Cut 1-3dB |

### Acoustic Guitar

| Goal | Frequency | Action |
|------|-----------|--------|
| High-pass | 80-100 Hz | HPF |
| Remove boom | 200-300 Hz | Cut 2-4dB |
| More body | 100-200 Hz | Boost 1-2dB |
| More clarity | 2-5 kHz | Boost 2-3dB |
| More sparkle | 8-12 kHz | Shelf boost 1-2dB |

### Electric Guitar

| Goal | Frequency | Action |
|------|-----------|--------|
| High-pass | 80-100 Hz | HPF |
| Remove mud | 200-400 Hz | Cut 3-6dB |
| More presence | 2-4 kHz | Boost 1-3dB |
| Reduce fizz | 6-10 kHz | Cut 1-3dB |

---

## EQ in Context

### Solo vs. Mix

**Critical:** EQ sounds different in solo vs. in the mix.

- Something that sounds good solo might not fit the mix
- Always check EQ decisions in context
- Final judgments in full mix

### Creating Space

**Carve space for each instrument:**
- Cut frequencies where other instruments live
- Boost frequencies that define that instrument
- Example: Cut bass at 3kHz, vocal presence lives there

### Complementary EQ

**Bass and Kick:**
- One owns 60Hz, other owns 100Hz
- One owns click, other owns sub
- Cut where the other boosts

---

## EQ Tips

### Less Is More

- Small moves (1-3dB) are often enough
- If you need drastic EQ, reconsider the source
- Multiple small cuts > one large cut

### High-Pass Everything

- Almost every track benefits from HPF
- Only kick and bass keep full low end
- Creates cleaner mix

### Use Your Ears

- Frequency charts are guides, not rules
- Every recording is different
- If it sounds good, it is good

### A/B Compare

- Bypass EQ to compare
- Is it actually better?
- Easy to EQ yourself in circles

---

## Logic Pro EQ Tips

### Channel EQ

- Good for most tasks
- Visual display helpful
- Analyzer shows frequency content

### Linear Phase EQ

- No phase distortion
- Good for mix bus
- More CPU intensive
- Can cause pre-ringing

### Match EQ

- Analyzes a reference
- Applies curve to your track
- Use carefully — can sound unnatural

---

## Related
- [[Mixing Workflow Checklist]]
- [[Compression Deep Dive]]
- [[Theory/Audio Recording Vocabulary]]

