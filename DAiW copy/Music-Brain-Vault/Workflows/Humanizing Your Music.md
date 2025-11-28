# Humanizing Your Music

How to make programmed/produced music feel alive, organic, and performed by real humans.

---

## Why Music Sounds Robotic

The enemy of human feel:
- **Perfect timing** — every note exactly on the grid
- **Identical velocity** — every hit the same volume
- **Perfect pitch** — no natural variation
- **Exact repetition** — copy/paste without variation
- **Static sounds** — no movement or evolution
- **Quantized everything** — machine precision

Real humans are imperfect. That imperfection is what sounds "alive."

---

## The Big Picture

### Three Dimensions of Human Feel

1. **TIMING** — When notes happen (ahead/behind the beat)
2. **DYNAMICS** — How hard notes are played (velocity/volume)
3. **TONE** — How the sound itself varies (timbre, articulation)

Master all three = human-sounding music.

---

## MIDI HUMANIZATION

### 1. Don't Quantize to 100%

**The Problem:** 100% quantization = robotic perfection

**The Fix:** Use partial quantization

In Logic Pro:
1. Select MIDI notes
2. Press `Q` or go to Edit → Quantize
3. Set **Strength** to 50-80% (not 100%)
4. This moves notes TOWARD the grid but not exactly ON it

**Starting Points:**
| Genre | Quantize Strength |
|-------|-------------------|
| Electronic/EDM | 90-100% (tighter is okay) |
| Pop | 75-85% |
| Rock | 60-80% |
| Jazz | 50-70% |
| Lo-fi/Soul | 40-60% |

### 2. Vary Your Velocity

**The Problem:** Every note at velocity 100 = lifeless

**The Fix:** Random and intentional velocity variation

**Random Variation (Logic Pro):**
1. Select MIDI notes
2. Functions → MIDI Transform → Humanize
3. Set Velocity random: ±5 to ±15

**Intentional Variation:**
- Downbeats slightly louder (velocity 90-110)
- Upbeats slightly softer (velocity 70-90)
- Accents where a human would accent
- Ghost notes much softer (velocity 30-50)

**Velocity Curves by Instrument:**
| Instrument | Velocity Range | Notes |
|------------|----------------|-------|
| Drums | 60-127 | Wide range, accents matter |
| Bass | 80-110 | More consistent, slight variation |
| Piano | 40-120 | Very expressive, wide range |
| Strings | 60-100 | Moderate variation |
| Synth leads | 90-120 | Less variation often okay |

### 3. Timing Micro-Shifts

**The Problem:** Everything exactly on grid = stiff

**The Fix:** Tiny timing variations

**Manual Method:**
1. Turn OFF snap to grid
2. Nudge some notes slightly early (1-20ms)
3. Nudge some notes slightly late (1-20ms)
4. Keep the important hits (downbeats) closer to grid

**Logic Pro Humanize:**
1. Select notes
2. MIDI Transform → Humanize
3. Position random: ±5 to ±15 ticks

**Guidelines:**
- Drums: Keep kick/snare tight, loosen hi-hats
- Bass: Often slightly behind the beat (lazy feel) or ahead (driving)
- Keys/Guitar: Can be looser
- Lead lines: Subtle timing = expressive

### 4. Note Length Variation

**The Problem:** All notes exactly the same length = unnatural

**The Fix:** Vary note durations

- Some notes held slightly longer
- Some released early
- Overlapping notes (legato) vs. gaps (staccato)
- Not every note needs to ring to its full value

### 5. Avoid Exact Repetition

**The Problem:** Copy/paste the same 4 bars 16 times = boring and fake

**The Fix:** Variations on each repeat

- Change a few velocities each time
- Move a few notes slightly
- Add/remove occasional notes
- Change one chord voicing
- Add fills/variations at phrase ends

**Rule of thumb:** If you copy a section, change at least 2-3 things.

---

## GROOVE & FEEL

### Groove Templates (Logic Pro)

Steal timing from real performances:

1. **Using Built-in Grooves:**
   - Select MIDI region
   - In Region Inspector, find "Quantize"
   - Choose groove template (MPC, SP1200, Live Drummer, etc.)
   - Adjust strength

2. **Create Your Own Groove:**
   - Record yourself playing (even imperfectly)
   - Select the MIDI region
   - Edit → Create Groove Template
   - Apply to other tracks

### Push and Pull

**Pushing (ahead of beat):** Urgent, driving, anxious
- Drums slightly early = drives the track
- Lead vocal early = eager, excited

**Pulling (behind beat):** Laid back, relaxed, groovy
- Snare slightly late = hip-hop swing
- Bass behind = lazy, deep pocket
- Vocals behind = cool, relaxed

**Try This:**
- Keep kick ON the grid
- Put snare 10-30ms LATE
- Put hi-hats slightly early
- = Instant groove

### Swing

Swing shifts every other note (the "ands") late.

**Logic Pro Swing:**
1. Select region
2. In Quantize settings, adjust Swing slider
3. 50% = straight, 66% = triplet swing
4. 54-58% = subtle shuffle
5. 60-66% = heavy swing

**Genre Swing Settings:**
| Genre | Swing Amount |
|-------|--------------|
| Straight rock | 50% (none) |
| Pop | 50-54% |
| Funk | 54-58% |
| Hip-hop | 55-62% |
| Jazz | 58-66% |
| Shuffle blues | 66% (triplet) |

---

## DRUM HUMANIZATION

### Hi-Hats: The Tell

Hi-hats are where robotic programming is most obvious.

**Humanize Hi-Hats:**
1. **Velocity variation:** Range from 60-110, not all the same
2. **Accent pattern:** Emphasize downbeats or upbeats (pick one)
3. **Timing looseness:** Most variation here (±10-20ms)
4. **Articulation changes:** Mix closed, slightly open, open
5. **No perfect repetition:** Every bar slightly different

**Quick Hi-Hat Pattern:**
```
Beat:  1   +   2   +   3   +   4   +
Vel:   90  70  85  65  88  72  82  68
```
Notice: downbeats louder, upbeats softer, but not identical each time.

### Kick & Snare: The Anchor

Keep these tighter but not perfect:
- Kick: slight velocity variation (±5-10)
- Snare: moderate velocity variation (±10-15)
- Timing: keep closer to grid than hi-hats
- Occasional ghost notes on snare (velocity 30-50)

### Ghost Notes

Quiet notes between main hits. Huge for human feel.

**Snare Ghost Notes:**
- Velocity 25-45 (barely audible)
- Usually on 16th notes between main hits
- Not on every beat — sparse is better
- Slightly loose timing

**Example (with ghost notes marked as 'g'):**
```
Beat: 1 e + a 2 e + a 3 e + a 4 e + a
Snare:      g   X g   g     g   X   g
```

### Fills

**Problem:** Programmed fills sound mechanical

**Solutions:**
- Velocity builds through the fill (crescendo)
- Timing gets slightly looser/tighter at fill peak
- Not perfectly even spacing
- Dynamic accent on the downbeat after fill

### Use Logic's Drummer

Logic's Drummer track is already humanized:
- Timing imperfections built in
- Velocity variation
- Musical fills
- Responds to "complexity" and "loudness" sliders

**Tip:** You can convert Drummer region to MIDI and edit further.

---

## BASS HUMANIZATION

### Timing

Bass often sits slightly behind the beat for groove:
- Try shifting entire bass track 10-30ms late
- Or program with individual notes 5-20ms behind
- Creates "pocket" feel

### Velocity & Dynamics

- Root notes often stronger
- Passing notes softer
- Slides and hammer-ons different velocity
- Not every note the same attack

### Articulation

- Mix sustained notes with short/muted notes
- Slides between notes (pitch bend or portamento)
- Dead notes (muted percussive hits)
- Let some notes ring into the next

### Note Length

- Not all notes full length
- Some staccato (short, punchy)
- Some legato (connected)
- Vary throughout the song

---

## KEYS/PIANO HUMANIZATION

### Velocity is Everything

Piano is extremely velocity-sensitive:
- Wide range: 30-120
- Melody notes louder than accompaniment
- Inner chord voices softer than outer
- Crescendos and decrescendos

### Chord Voicing

Humans don't play chords perfectly together:
- Slight roll/arpeggiation (5-20ms between notes)
- Bottom note often slightly first
- Or top note first (different feel)
- Vary per chord

**Logic Pro:** Select chord → Functions → Note Events → Humanize (or manually offset)

### Sustain Pedal

Real pianists use pedal expressively:
- Not just "on" or "off"
- Half-pedaling
- Pedal before chord changes (catches release)
- Don't over-pedal (mud)

**Record pedal as CC64** — or draw it in manually.

### Left Hand vs. Right Hand

- Often different velocities
- Different timing feel
- Left hand (bass) can push or pull independently

---

## STRINGS/ORCHESTRAL HUMANIZATION

### The Hardest to Humanize

Orchestral instruments are tough because:
- Real players have incredible expression
- Vibrato, dynamics, bow changes, breath
- Section playing = slight timing differences between players

### Key Techniques

**1. Expression (CC11):**
Draw in volume swells. Strings don't start and stop abruptly.

**2. Modulation/Vibrato (CC1):**
Add vibrato that develops — starts subtle, increases.

**3. Attack Variation:**
Mix legato and shorter articulations.

**4. Section Spread:**
Double parts slightly detuned and offset in time = section sound.

**5. Velocity Curves:**
Follow the musical line — louder on high/climactic notes.

### Logic's Studio Strings

Use articulation keyswitches:
- Sustain, staccato, pizzicato, tremolo
- Switch articulations like a real player would

---

## VOCAL PRODUCTION (Real Vocals)

Even real vocals can sound "produced" — here's how to keep them human:

### Don't Over-Tune

- Melodyne/Flex Pitch: don't correct to 100%
- Leave some pitch drift on held notes
- Keep natural scoops into notes
- Vibrato should stay natural

### Don't Over-Quantize

- If timing is close, leave it
- Slight push/pull = character
- Robotic timing + perfect pitch = fake

### Breath Matters

- Don't remove all breaths
- Breaths = human
- Just reduce volume if too loud

### Compression Balance

- Over-compression = lifeless
- Let some dynamics through
- Automate volume for control instead

---

## MIXING FOR HUMAN FEEL

### Avoid Perfect Timing Alignment

When layering:
- Don't align every transient perfectly
- Slight offsets = bigger, more natural sound
- Exception: kick and bass often need alignment

### Saturation & Harmonics

- Analog-style saturation adds harmonics
- Makes digital sounds feel more organic
- Tape emulation, tube emulation
- Don't overdo it — subtle warmth

### Room & Space

- Add room reverb for "people in a space" feel
- Short ambience on drums = life
- Stereo spread that isn't extreme
- Contrast: some elements dry, some wet

### Dynamic Range

- Don't smash everything with limiters
- Let the music breathe
- Loud parts louder, quiet parts quieter
- Dynamic contrast = emotional impact

### Imperfect Performances

- That slightly off note might be the magic
- "Fix it in the mix" isn't always the answer
- Sometimes re-record, sometimes embrace

---

## SOUND DESIGN FOR ORGANIC FEEL

### Movement in Sounds

Static sounds = fake. Add:
- Filter movement (cutoff automation)
- LFO on parameters (subtle)
- Envelope modulation
- Pitch drift (very subtle)

### Layer Organic Elements

- Foley (real-world sounds)
- Room tone
- Vinyl crackle (subtle)
- Tape hiss (subtle)
- Breath, string noise, pick noise

### Velocity-Sensitive Patches

Use instruments that respond to velocity:
- Different samples for soft/hard playing
- Filter opens with velocity
- Attack changes with velocity

---

## LOGIC PRO SPECIFIC TOOLS

### MIDI Transform → Humanize

1. Select MIDI notes
2. Edit → MIDI Transform → Humanize
3. Adjust Position, Velocity, Length random ranges
4. Apply

**Recommended Starting Settings:**
- Position: ±8 ticks
- Velocity: ±10
- Length: ±5 ticks

### Groove Templates

Region Inspector → Quantize dropdown → Choose groove

Built-in grooves:
- Apple Drummer grooves
- Classic grooves (MPC, etc.)
- Create your own from performance

### Region Parameters

In Region Inspector:
- **Velocity offset:** Shift all velocities +/-
- **Dynamics:** Compress or expand velocity range
- **Gate Time:** Shorten/lengthen all notes

### Flex Time Varispeed

For audio:
- Flex Time can humanize perfect loops
- Or use Varispeed for subtle tape-style variation

### Drummer Track

Already humanized:
- Use for realistic drum performances
- Convert to MIDI to edit further
- "Follow" feature matches other tracks

---

## PRACTICAL WORKFLOWS

### Workflow 1: Humanize After Programming

1. Program your parts on the grid
2. Record proper velocities as you go
3. After programming, select all
4. Apply humanize transform (light)
5. Apply groove template
6. Manual tweaks to feel

### Workflow 2: Perform, Then Fix

1. Record yourself playing (imperfect)
2. Quantize lightly (50-70%)
3. Fix only obvious mistakes
4. Keep human timing

### Workflow 3: Hybrid

1. Program kick/snare tight
2. Play hi-hats/percussion live
3. Record bass with feel
4. Program synths, humanize after

### Workflow 4: The 80/20 Rule

Focus humanization efforts on:
- Hi-hats (most obvious)
- Lead melody
- Any repeating pattern

Less critical:
- Sub bass
- Pads (already blurry)
- One-shot FX

---

## QUICK CHECKLIST

Before bouncing, check:

- [ ] Velocity variation on drums?
- [ ] Hi-hats not perfectly even?
- [ ] Quantize strength below 100%?
- [ ] No exact copy/paste repetition?
- [ ] Ghost notes on drums?
- [ ] Bass timing in the pocket?
- [ ] Chord voicing slightly rolled?
- [ ] Expression automation on sustained instruments?
- [ ] Some dynamic contrast?
- [ ] Room/ambience on drums?

---

## FURTHER LISTENING

Study these for human feel:

- **D'Angelo - Voodoo** — Questlove's drunk drums
- **J Dilla - Donuts** — Loose, swung, imperfect
- **Steely Dan** — Tight but human session players
- **Vulfpeck** — Intentionally loose
- **Bon Iver - 22, A Million** — Organic + electronic blend
- **Billie Eilish** — Intimate, dynamic, breathing room

---

## Related
- [[Workflows/Mixing Workflow Checklist]]
- [[Theory/Music Theory Vocabulary]]
- [[Gear/Logic Pro Settings]]

