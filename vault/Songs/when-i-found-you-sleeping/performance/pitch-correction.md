# Pitch Correction Guide for "When I Found You Sleeping"
## Handling Voice Breaks, Emotional Expression, and the Lo-Fi Question

---

## THE CORE CHALLENGE

Three interconnected problems:

1. **Voice breaks close to yodeling** — rapid pitch transitions between chest and head register that pitch correction software struggles with
2. **Robotic artifacts** — turning up pitch correction makes the vocal sound mechanical
3. **The irony** — feeling more off-tune than artists who are "not trying" yet sound authentic

---

## PART ONE: UNDERSTANDING WHY VOICE BREAKS ARE HARD TO CORRECT

### What's Actually Happening Physiologically

Voice breaks (the "yodel" effect) involve rapid transitions between:
- **Chest voice (modal register)** — thyroarytenoid muscles dominant, fuller vocal fold vibration
- **Head voice/falsetto** — cricothyroid muscles dominant, thinner fold contact, higher tension

These are **abrupt frequency jumps** — nonlinear dynamics in the larynx where small changes trigger sudden pitch discontinuities.

### Why Pitch Correction Struggles

Pitch correction software (AutoTune, Melodyne) works by:
1. Detecting the pitch of incoming audio
2. Shifting it to the nearest "correct" note

**The problem with register breaks:**
- The software sees rapid pitch changes and tries to "correct" each moment
- Fast retune speeds create audible artifacts at the transitions
- The software may misidentify which note you're aiming for during the break
- Melodyne specifically doesn't handle noise/air well — breath and transition sounds between notes get processed oddly

---

## PART TWO: THE TWO MAJOR APPROACHES

### Approach A: Melodyne (Manual, Surgical)

**Best for:** Transparent, undetectable correction that preserves expression

**How it works:**
- Records audio into the software, then displays notes as visual "blobs"
- You manually adjust each note's pitch, timing, vibrato
- Three independent tools: Pitch Center, Pitch Modulation, Pitch Drift

**Key settings for natural sound:**
- **Pitch Center:** ~80% to start (tunes notes but keeps them sounding realistic)
- **Pitch Drift:** ~80% (keeps sustained notes in tune without making them robotic)
- **Pitch Modulation:** USE SPARINGLY — this is the biggest culprit for unnatural sounds

**Critical technique for voice breaks:**

If there is pitch variation in the course of a sustained note, Melodyne defines its pitch centre as an average value. So when you snap the entire note to the pitch grid, there's no actual guarantee that any individual section of it will be perfectly in tune.

**Solution:** Chop the break into smaller pieces. Separate the transition from the notes before/after. Quantize each piece separately. This gives you control over the break itself.

**For vibrato/expression:**
Don't cut the vibrato; keep it one singular blob if possible. Determine whether the pitch center is flat or sharp. Then, holding the option key, manually move it to where the center of the vibrato is in line with the center of the pitch block.

**The Secret Sauce:**
Separate the notes of the melody from the breaths, vocal scoops, and musical drifts. It's in these 'parts between the notes' that give a performance its life and authenticity.

---

### Approach B: AutoTune (Real-time, Set-and-Forget)

**Best for:** Quick correction, creative "tuned" effect, or working with already mostly-in-tune vocals

**Key parameters:**

| Parameter | What It Does | Robotic Sound | Natural Sound |
|-----------|-------------|---------------|---------------|
| **Retune Speed** | How fast pitch snaps to correct note | 0-10ms (T-Pain effect) | 30-50ms or higher |
| **Flex-Tune** | How much original pitch variation to preserve | 0 (full correction) | 15-50 (allows wavering) |
| **Humanize** | Makes sustained notes less static | 0 | 10-30 or higher |
| **Natural Vibrato** | Preserves singer's vibrato | 0 | Leave natural |

**Settings for your situation:**

**For Subtle, Natural Correction:**
```
Retune Speed: 40-60ms (slower = more natural)
Flex-Tune: 20-50 (allows near-pitch notes to stay untouched)
Humanize: 30-45 (prevents longer notes from sounding robotic)
Natural Vibrato: 0 (preserve what's there)
```

**For Indie Folk / Confessional Acoustic:**
```
Retune Speed: 30-40ms
Flex-Tune: 10-20
Humanize: 30
```

**For Lo-Fi Bedroom (if using any correction at all):**
```
Retune Speed: 50-100ms (barely there)
Flex-Tune: 20-30
Humanize: 45
```

---

## PART THREE: THE HYBRID APPROACH (MELODYNE + AUTOTUNE)

This is what many professional engineers do for the "polished but human" sound:

### Step 1: Clean Up with Melodyne First
- Use Melodyne to fix the most egregious pitch problems
- Control pitch drift and vibrato irregularities
- **Specifically target your voice break moments** — manually adjust the transition

### Step 2: Add Light AutoTune After
- Apply subtle AutoTune (slower retune speed, moderate flex-tune)
- The already-Melodyned vocal will respond more predictably
- You get the smoothness without the artifacts

---

## PART FOUR: THE LO-FI QUESTION — SHOULD YOU EVEN CORRECT?

### The Genre Aesthetic Embraces Imperfection

From the lo-fi and bedroom emo aesthetic:

> "Lo-fi has been characterized by the inclusion of elements normally viewed as undesirable in most professional contexts, such as misplayed notes, environmental interference, or phonographic imperfections."

> "Recordings deemed unprofessional or 'amateurish' are usually with respect to performance (out-of-tune or out-of-time notes)... these imperfections became celebrated as a distinct aesthetic choice."

**The key question:** Is this song meant to have "semblance of polish" or is it meant to be raw?

### Artists Who DON'T Heavily Tune (and why it works)

**Phoebe Bridgers:**
- Uses doubling/layering rather than heavy tuning
- Biggest influence: Elliott Smith (known for raw, unpolished vocals)

**Bon Iver:**
- Uses AutoTune as an **effect**, not a corrective tool
- The imperfection is intentional
- For Emma, Forever Ago was recorded in a cabin with "meager means"

**The Teen Suicide / Elvis Depressedly / Salvia Palth school:**
- Recorded in bedrooms on cheap equipment
- Pitch imperfections are part of the texture
- The vulnerability IS the point

---

## PART FIVE: PRACTICAL RECOMMENDATIONS FOR YOUR SONG

### Option 1: Embrace the Raw (Least Correction)

**Philosophy:** Your voice breaking is the song breaking. The imperfection IS the grief.

**Approach:**
- Record multiple takes, comp the best emotional delivery regardless of pitch
- Use Melodyne ONLY to fix truly egregious notes (more than a semitone off)
- Leave voice breaks completely untouched
- Add room/warmth to disguise minor pitch issues

**When to use:** If your best emotional takes happen to be reasonably on pitch

### Option 2: Surgical Cleanup (Melodyne Only)

**Philosophy:** Fix what hurts the song, preserve what makes it human

**Approach:**
- Import vocal into Melodyne
- Separate voice break transitions from notes before/after
- Fix notes that are clearly wrong (especially on chord changes)
- Leave intentional expression (slides, vibrato, breaks)
- Set Pitch Correction macro to ~60-80% — nudges notes toward correct without snapping

**When to use:** If specific notes are bothering you but the overall feel is good

### Option 3: Light Polish (Melodyne + Very Subtle AutoTune)

**Philosophy:** Get the benefits of correction without losing humanity

**Approach:**
- First pass: Melodyne cleanup of worst offenders
- Second pass: AutoTune with very slow retune speed (50ms+), high humanize (40+)
- Automate: Turn correction DOWN or OFF during fracture moments

**When to use:** If you want it to sound "produced" but not obviously tuned

### Option 4: The "Wrong" Note is the Right Note

**Philosophy:** What you think is "off" might actually be perfect for the song

**Approach:**
- Record your best emotional take
- Listen back the next day without touching it
- Ask: Does the pitch issue actually hurt the song, or does it sound like grief?
- Compare to reference tracks (Bright Eyes, Elliott Smith, Front Porch Step)

---

## PART SIX: SPECIFIC TIPS FOR YOUR VOICE BREAKS

### The Technical Challenge

Voice breaks (chest to head, or vice versa) are essentially:
- A rapid frequency jump
- Often with a moment of instability between registers
- Sometimes with breath/air in the transition

### Solutions

1. **In Melodyne: Cut the break out**
   - Identify the transition moment
   - Use Note Separation tool to isolate it
   - Either leave it unprocessed OR manually nudge just the beginning/end notes
   - Don't try to "correct" the transition itself

2. **In AutoTune: Automate around breaks**
   - Create automation on Retune Speed
   - Slow it WAY down (or bypass) during voice breaks
   - Let the break happen naturally
   - Resume normal settings after

3. **Recording technique: Practice the break**
   - Your voice break is a register shift — it can be trained
   - Practice slow transitions between chest and head voice
   - The goal isn't to eliminate the break, but to make it intentional

4. **Accept the yodel**
   - If the break is happening on an emotional word, it might be perfect
   - The "yodel" is your voice physically manifesting the emotional content
   - Front Porch Step, Bright Eyes, and similar artists have these moments constantly

---

## PART SEVEN: ALTERNATIVE TOOLS

### Soundtoys Little AlterBoy
- Not primarily a pitch corrector, but a pitch/formant manipulator
- Has a "Quantize" mode that acts like AutoTune
- Includes tube saturation (adds warmth)
- Good for creative vocal effects, less good for invisible correction

### Free Options
- **Graillon 2** (Auburn Sounds) — free pitch correction with good natural modes
- **MAutoPitch** (MeldaProduction) — free, less intuitive but functional
- **GSnap** — old but still works for basic correction

### FL Studio / DAW Built-in
- **Newtone** (FL Studio) — similar to Melodyne
- **VariAudio** (Cubase) — similar to Melodyne

---

## QUICK REFERENCE CHEAT SHEET

### AutoTune Settings

| Goal | Retune Speed | Flex-Tune | Humanize |
|------|-------------|-----------|----------|
| Robotic T-Pain | 0-5ms | 0 | 0 |
| Modern Pop | 10-20ms | 5-10 | 20 |
| Natural Polish | 30-50ms | 15-30 | 30-45 |
| Barely There | 50-100ms | 20-50 | 45+ |
| **Your Song** | **40-60ms** | **20-30** | **30-40** |

### Melodyne Quick Settings

| Goal | Pitch Center | Pitch Drift | Pitch Modulation |
|------|-------------|-------------|------------------|
| Aggressive | 100% | 100% | Any (creates artifacts) |
| Natural | 70-80% | 70-80% | AVOID |
| Light Touch | 50-60% | 50-60% | AVOID |
| **Your Song** | **60-75%** | **60-75%** | **Don't touch** |

### Voice Break Protocol

1. Separate break from surrounding notes
2. Fix notes BEFORE and AFTER the break
3. Leave the transition itself alone OR
4. Manually adjust just the landing note
5. Never apply aggressive correction across a register shift

---

## FINAL THOUGHT

> "It's tempting to make every pitch perfectly on key, but overdoing it removes the emotion that makes a vocal believable. Leave slight imperfections that add character and personality to the performance."

Your song is about trauma, freeze, grief, and time that won't move. Perfect pitch would be a lie. The question isn't "how do I sound perfect?" — it's "how do I sound TRUE?"

The voice breaking on "From fucking dusk fucking dawn" might be the truest moment in the whole song.

---

*Document created for Kelly Song project*
*Part of genre/recording research for "When I Found You Sleeping"*
