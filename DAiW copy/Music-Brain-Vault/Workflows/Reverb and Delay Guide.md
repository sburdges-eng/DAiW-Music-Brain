# Reverb & Delay Guide

Creating space, depth, and dimension in your mix.

---

## Why Use Reverb and Delay

**Reverb:**
- Places sounds in a space
- Adds depth (front to back)
- Creates cohesion
- Makes things feel natural

**Delay:**
- Adds rhythmic interest
- Creates width
- Thickens sounds
- Adds depth without wash

---

## Reverb Basics

### Reverb Parameters

| Parameter | What It Does |
|-----------|--------------|
| **Pre-delay** | Time before reverb starts |
| **Decay/Time** | How long reverb lasts |
| **Size/Room** | Size of simulated space |
| **Damping** | How quickly highs decay |
| **Mix/Wet-Dry** | Balance of effect |
| **Early Reflections** | First bounces off walls |

### Reverb Types

| Type | Character | Use For |
|------|-----------|---------|
| **Room** | Small, tight, natural | Drums, guitars, general |
| **Plate** | Bright, dense, smooth | Vocals, snare |
| **Hall** | Large, spacious, lush | Strings, pads, ballads |
| **Chamber** | Medium, warm, smooth | Vocals, general |
| **Spring** | Boingy, vintage | Guitar, vintage sound |
| **Ambience** | Very short, subtle | Adding life, width |

---

## Using Reverb

### Send vs. Insert

**Send (Recommended):**
- Multiple tracks share same reverb
- Blend amount per track
- Creates cohesive space
- More CPU efficient

**Insert:**
- Reverb only on that track
- Direct control
- Can be heavier

### Pre-Delay Is Key

**What it does:** Creates gap between dry sound and reverb.

| Pre-delay | Effect |
|-----------|--------|
| 0-10ms | Sound and reverb blend (less defined) |
| 10-30ms | Separation, clarity |
| 30-80ms | Clear separation, upfront vocal |
| 80ms+ | Distinct echo before reverb |

**For vocals:** 20-50ms keeps vocal upfront while adding space.

### Decay Time

| Decay | Feel | Use For |
|-------|------|---------|
| 0.5-1s | Tight, controlled | Drums, uptempo songs |
| 1-2s | Medium, natural | Most mixing |
| 2-4s | Spacious, lush | Ballads, pads |
| 4s+ | Huge, washy | Effects, ambient |

**Rule:** Shorter decay for faster tempos.

### Damping (High Frequency Decay)

**More damping = darker reverb:**
- Less harsh
- More natural
- Sits back in mix

**Less damping = brighter reverb:**
- More presence
- Can be harsh
- Stands out more

**Tip:** Usually some damping sounds more natural.

---

## Reverb by Instrument

### Vocals

**Typical approach:**
- Plate or hall reverb
- Pre-delay: 30-60ms
- Decay: 1.5-2.5s
- Keep it subtle (blend low)

**Tip:** Too much reverb = distant vocals.

### Drums

**Room reverb:**
- Short decay (0.5-1s)
- Adds life and size
- Used on full kit or just snare

**Snare plate:**
- Classic snare sound
- Decay: 1-2s
- Blend to taste

**Tip:** Compress the reverb for bigger sound.

### Guitars

**Room or spring:**
- Short-medium decay
- Adds dimension
- Don't wash out

### Synths/Pads

**Hall reverb:**
- Longer decay okay
- Creates atmosphere
- Blend to taste

### Piano

**Room or hall:**
- Natural space
- Medium decay
- Don't overdo

---

## Delay Basics

### Delay Parameters

| Parameter | What It Does |
|-----------|--------------|
| **Time** | Delay length (ms or note value) |
| **Feedback** | Number of repeats |
| **Mix/Wet-Dry** | Blend amount |
| **Filter/EQ** | Tone of delays |
| **Ping-Pong** | Alternating L/R |
| **Sync** | Lock to tempo |

### Delay Types

| Type | Character | Use For |
|------|-----------|---------|
| **Slapback** | Short, 1 repeat | Vocals, guitars, rockabilly |
| **Tape** | Warm, degrading repeats | Vintage, warmth |
| **Digital** | Clean, precise | Modern, rhythmic |
| **Ping-Pong** | Bouncing L/R | Width, movement |
| **Analog** | Warm, filtered | Character, vintage |

---

## Using Delay

### Tempo-Synced Delay

**Lock delay to BPM:**

| Note Value | Feel |
|------------|------|
| 1/4 note | Strong rhythmic pulse |
| 1/8 note | Faster, tighter |
| Dotted 1/8 | Classic, bouncy |
| 1/16 note | Very fast, thickening |
| Triplet | Different groove |

**Dotted 1/8:** Classic delay sound (U2, The Edge).

### Slapback Delay

**Short delay, 1-2 repeats:**
- Time: 60-120ms
- Feedback: Low (1-2 repeats)
- Effect: Thickens, adds presence

**Great for:** Vocals, guitars, snare.

### Long Delay

**For rhythmic interest:**
- Time: Tempo-synced (1/4 or dotted 1/8)
- Feedback: 3-5 repeats
- Effect: Rhythmic, spacious

**Great for:** Leads, sparse arrangements, breakdowns.

### Filtering Delays

**Darken the repeats:**
- Low-pass filter on delay
- Each repeat darker
- Sits behind the source
- More natural

**Tip:** Almost always filter delays to avoid harshness.

---

## Delay by Instrument

### Vocals

**Slapback:**
- 80-120ms
- Low feedback
- Thickens without wash

**Rhythmic delay:**
- 1/4 or dotted 1/8
- Low-moderate feedback
- Filtered (darker)

**Tip:** Often better than reverb for upfront vocals.

### Guitars

**Slapback:**
- Classic doubling effect
- 60-100ms
- Low feedback

**Rhythmic:**
- Tempo-synced
- Creates movement
- Great for sparse parts

### Synths

**Ping-pong:**
- Width and movement
- Tempo-synced
- Moderate feedback

---

## Combining Reverb and Delay

### The Recipe

**For most sources:**
1. Short delay/slapback (thickening)
2. Medium reverb (space)
3. Balance the two

**Delay before reverb:**
- Delay feeds into reverb
- Creates depth and space
- More dimensional

### Layering Spaces

**Multiple reverbs:**
- Short room (close)
- Longer hall (far)
- Creates depth

**Short delay + long reverb:**
- Delay keeps source present
- Reverb adds space behind

---

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Too much reverb | Washy, distant mix | Use less, use pre-delay |
| Too long decay | Sounds like a cathedral | Shorter decay |
| No damping | Harsh, unnatural | Add high damping |
| Wrong tempo sync | Delays clash with rhythm | Match tempo properly |
| Everything same reverb | All sounds same distance | Use different sends |
| Delay too loud | Distracting | Lower mix/send amount |

---

## Setting Up in Logic Pro

### Reverb Send Setup

1. Create Aux track
2. Insert reverb plugin (100% wet)
3. Route sends from source tracks
4. Adjust send levels per track

### Delay Send Setup

1. Create Aux track
2. Insert delay plugin (100% wet)
3. Route sends from source tracks
4. Sync delay to tempo

### Multiple Reverbs

**Common setup:**
- Send 1: Short room (drums, general)
- Send 2: Medium plate (vocals, snare)
- Send 3: Long hall (pads, ballads)

---

## Creative Techniques

### Reverse Reverb

1. Reverse the audio
2. Add reverb, bounce
3. Reverse the result
4. Reverb swells INTO the sound

### Gated Reverb

1. Add long reverb
2. Gate the reverb (cuts off abruptly)
3. 80s drum sound

### Ducking Reverb

1. Sidechain compressor on reverb aux
2. Keyed by source track
3. Reverb ducks when source plays
4. Swells up in gaps

### Delay Throws

1. Automate delay send
2. Turn up for specific words/notes
3. Effect only where needed

---

## Quick Reference

### Reverb Starting Points

| Source | Type | Pre-delay | Decay |
|--------|------|-----------|-------|
| Vocals | Plate | 30-60ms | 1.5-2.5s |
| Snare | Plate/Room | 0-20ms | 1-2s |
| Drums (kit) | Room | 0-10ms | 0.5-1s |
| Acoustic Guitar | Room | 10-30ms | 1-1.5s |
| Piano | Hall | 20-40ms | 1.5-2.5s |
| Pads | Hall | 0-30ms | 2-4s |

### Delay Starting Points

| Source | Type | Time | Feedback |
|--------|------|------|----------|
| Vocals (thick) | Slapback | 80-120ms | Low |
| Vocals (space) | Tempo | 1/4 or dotted 1/8 | 2-4 repeats |
| Guitars | Slapback | 60-100ms | Low |
| Synth leads | Ping-pong | Dotted 1/8 | 3-5 repeats |

---

## Related
- [[Mixing Workflow Checklist]]
- [[EQ Deep Dive Guide]]
- [[Compression Deep Dive Guide]]

