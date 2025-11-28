# Vocal Production Guide

Keeping vocals sounding human and natural through recording, editing, and mixing.

---

## The Goal

Vocals should sound:
- Clear and present
- Emotionally connected
- Like a real person singing
- NOT robotic or over-processed

---

## Recording for Natural Sound

### Microphone Technique

**Distance Matters:**
- 6-12 inches typical
- Closer = more intimate, proximity bass boost
- Further = more room, thinner
- Vary distance with dynamics (pull back on loud parts)

**Off-Axis = Less Harsh:**
- Slightly off-center can reduce sibilance
- Try 15-30 degrees off-axis
- Different mics respond differently

**Pop Filter:**
- Essential for plosives (P, B)
- 2-4 inches from mic
- Doesn't affect tone much

### Room Considerations

- Dead room = cleaner, easier to mix
- Some room = more natural, harder to control
- Reflection filters help in untreated spaces
- Record "room tone" for editing

### Performance > Perfection

**Capture emotion first:**
- A passionate take with small flaws > perfect but lifeless
- Coach the performance, not just the notes
- Take breaks to stay fresh
- Keep rough takes — sometimes they're magic

**Multiple Takes:**
- Record 3-5 full takes
- Comp the best phrases together
- Keep the energy consistent between takes

---

## Editing: Less Is More

### When to Edit

**Fix:**
- Timing issues that distract
- Pitch problems that clash with harmony
- Noise, clicks, pops
- Breaths that are too loud

**Don't Fix:**
- Natural pitch variations
- Subtle timing feel
- Emotional imperfections
- Everything

### Breath Editing

**Don't remove all breaths:**
- Breaths = human
- Just reduce volume if too loud (try -6 to -10 dB)
- Keep some audible, remove distracting ones

**Quick Method:**
1. Find breath in waveform
2. Select just the breath
3. Reduce gain (not delete)
4. Or automate volume down

### Timing Edits

**Light Touch:**
- Only fix what's obviously wrong
- Use Flex Time in Logic (Polyphonic mode for vocals)
- Don't snap to grid — move toward correct timing
- Preserve natural push/pull

**Flex Time in Logic:**
1. Enable Flex (click Flex button or press F)
2. Choose Flex Mode: Flex Pitch (for vocals)
3. Drag transients to adjust timing
4. Don't overdo it

### Comping

**Creating the best take:**
1. Record multiple takes (Take Folder)
2. Swipe across best phrases from each take
3. Listen for:
   - Pitch accuracy
   - Timing feel
   - Emotional delivery
   - Tone consistency
4. Crossfade edit points

**Matching Comped Sections:**
- Energy level should match
- Tone should be consistent
- Watch for volume jumps
- Crossfades on zero crossings

---

## Pitch Correction: The Human Way

### The Problem with Over-Tuning

100% pitch correction sounds robotic because:
- No natural pitch drift
- No scoop into notes
- No vibrato variation
- Instant, perfect pitch

### Natural Pitch Correction (Flex Pitch)

**Light Correction:**
1. Open Flex Pitch (double-click region with Flex on)
2. Each note shows pitch center
3. Don't correct notes already close
4. Move only the obvious problems
5. Use "Pitch Drift" and "Vibrato" sliders lightly

**Settings for Natural Sound:**
- Don't correct to 100%
- Try 50-75% correction
- Preserve pitch drift on sustained notes
- Keep natural vibrato (don't flatten)

### What to Correct

| Correct This | Leave This |
|--------------|------------|
| Notes way off key | Notes within ±20 cents |
| Notes that clash with harmony | Natural pitch drift |
| Jarring pitch jumps | Vibrato |
| Sustained notes drifting sharp/flat | Scoop into notes |

### Flex Pitch Specific Settings

**Fine Pitch:** Corrects center pitch
- 0% = no correction
- 100% = perfect pitch
- Try 50-80% for natural

**Pitch Drift:** Corrects movement within note
- 0% = no correction (keep natural drift)
- Higher = more stable sustained notes
- Keep low for most natural sound

**Vibrato:** Affects natural vibrato
- Keep at 0% to preserve original
- Increase only if vibrato is erratic

**Formant Shift:** Changes character
- Usually leave at 0
- Use sparingly for creative effect

---

## Doubling and Harmonies

### Real Doubles vs. Fake

**Best: Actual double track**
- Singer performs the part again
- Natural variation in timing/pitch
- Sounds full and human

**Okay: Copied and processed**
- Duplicate vocal
- Shift pitch slightly (±10 cents)
- Delay slightly (10-30ms)
- Different EQ/processing
- Not as good but workable

### Harmony Recording

- Record harmonies separately
- Different performance = different character
- Slight timing variation from lead is okay
- Pan harmonies wider than lead

### Stack Dynamics

Layered vocals should:
- Support the lead, not overpower
- Be slightly lower in volume
- Blend, not stick out
- Have consistent energy

---

## Mixing Vocals Naturally

### EQ Philosophy

**Subtractive First:**
1. High-pass around 80-100Hz (remove rumble)
2. Find and cut problem frequencies
3. Common problems: 200-400Hz (mud), 2-4kHz (harshness)

**Additive Sparingly:**
- Presence: gentle boost 3-5kHz
- Air: shelf boost 10kHz+
- Warmth: subtle 200Hz (if needed)

**Don't over-EQ:**
- If it needs a lot of EQ, consider re-recording
- Surgical cuts are okay
- Broad boosts should be subtle (1-3dB)

### Compression for Natural Sound

**The Goal:**
- Control dynamics without killing expression
- Loud parts controlled, quiet parts audible
- NO pumping or breathing artifacts

**Starting Point:**
- Ratio: 3:1 to 4:1
- Attack: 10-30ms (let consonants through)
- Release: Auto or 100-200ms
- Gain Reduction: 3-6dB on peaks

**Avoid:**
- Ratio above 8:1 (squashes)
- Super fast attack (kills transients)
- Excessive gain reduction (over 10dB)

**Serial Compression (Better Results):**
Two compressors, each doing less work:
1. First compressor: 2-3dB reduction (gentle)
2. Second compressor: 2-3dB reduction (gentle)
= More transparent than one compressor doing 6dB

### Volume Automation (The Secret Weapon)

**Why:**
- More transparent than heavy compression
- You control exactly what's louder/quieter
- Preserves natural dynamics

**How in Logic:**
1. Press A (automation view)
2. Select Volume
3. Draw or record fader moves
4. Ride quiet words up, loud words down

**What to Automate:**
- Words that get lost in the mix
- Consonants that need emphasis
- Breaths (usually down)
- Phrases that need dynamic shaping

### De-Essing

**When:**
- "S" and "SH" sounds are harsh/distracting
- Usually around 5-8kHz

**How (Logic's DeEsser):**
1. Insert DeEsser on vocal
2. Find the problem frequency (5-8kHz typically)
3. Set threshold so it only catches harsh S's
4. Don't over-do — dull vocals sound weird too

**Natural Alternative:**
- Automate volume down just on harsh S's
- More work but most transparent

---

## Effects for Natural Sound

### Reverb

**Purpose:** Place the vocal in a space

**Natural Settings:**
- Pre-delay: 20-50ms (separates from dry)
- Decay: 1-2 seconds (short-medium room)
- High damping (not too bright)
- Blend: Subtle — should feel, not hear

**Common Mistake:**
- Too much reverb = distant, washed out
- Start with less than you think

### Delay

**Purpose:** Adds depth without wash

**Natural Settings:**
- Short slap (80-120ms): Thickens, not obvious
- Tempo sync (1/4 or 1/8): Rhythmic support
- Feedback: Low (1-3 repeats)
- Filter the delays (darken)

**Send vs. Insert:**
- Use sends for reverb/delay (parallel)
- Blend to taste
- Allows control over wet/dry

### Saturation

**Purpose:** Warmth and presence

**Use Sparingly:**
- Very subtle — if you hear distortion, too much
- Tape-style or tube-style
- Adds harmonics that help cut through mix

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Over-tuned (robotic) | Reduce correction %, preserve drift |
| Over-compressed (flat) | Use less ratio, try serial compression |
| Too much reverb (distant) | Pull back, use pre-delay |
| No breaths (uncanny) | Keep some breaths, reduce volume only |
| Harsh S's | De-esser, but don't over-do |
| Muddy low-mids | High-pass higher (100-120Hz), cut 200-400Hz |
| Buried in mix | Volume automation, cut competing frequencies |
| Disconnected doubles | Record real doubles, match energy |

---

## The Human Touch Checklist

Before final mix, check:

- [ ] Pitch correction subtle (not 100%)
- [ ] Natural pitch drift preserved on sustained notes
- [ ] Vibrato sounds natural
- [ ] Breaths present (but controlled)
- [ ] Dynamics have movement (not flat-lined)
- [ ] Timing feels natural (not robotic)
- [ ] Emotion comes through
- [ ] Effects enhance but don't dominate

---

## Logic Pro Vocal Chain (Starting Point)

**Insert Chain Order:**
1. **Gain/Trim** — Get input level right
2. **EQ (Channel EQ)** — HPF + surgical cuts
3. **Compressor 1 (light)** — 2-3dB reduction
4. **De-Esser** — Catch harsh S's
5. **Compressor 2 (optional)** — 2-3dB more if needed
6. **EQ (tone shaping)** — Presence, air (subtle)
7. **Saturation (optional)** — Very subtle warmth

**Send Effects:**
- Send 1: Short reverb (plate or room)
- Send 2: Longer reverb (hall)
- Send 3: Delay (tempo-sync or slap)

**Volume Automation:**
- Draw/record fader moves for phrase dynamics
- This is where the magic happens

---

## Related
- [[Vocal Recording Workflow]]
- [[Mixing Workflow Checklist]]
- [[Humanizing Your Music]]

