# Music Vernacular & Rule-Breaking Database

---
title: Music Vernacular & Rule-Breaking Database
tags: [idaw, music-theory, vernacular, slang, production, rule-breaking, interrogation]
category: Reference_Databases
created: 2025-11-27
updated: 2025-11-27
ai_priority: critical
related_docs:
  - "[[song_intent_schema]]"
  - "[[rule_breaking_practical]]"
  - "[[emotional_harmony_framework]]"
---

> **Purpose:** Unified translation layer between casual musician language and technical implementation. Enables iDAW to understand "make it chuggy" or "needs more glue" and translate to actionable parameters.

---

## PART 1: CASUAL SOUND DESCRIPTIONS (Vernacular → Technical)

### 1.1 Rhythmic Onomatopoeia

These phonetic representations are how musicians communicate groove patterns without notation.

| Vernacular | Meaning | Technical Translation | iDAW Parameter |
|------------|---------|----------------------|----------------|
| **"boots and cats"** | Basic 4/4 beat | Kick on 1,3 / Hi-hat on 2,4 | `groove.pattern: "four_on_floor"` |
| **"untz untz untz"** | Techno/EDM kick pattern | Kick every beat, 4/4 | `groove.pattern: "four_on_floor", tempo: 120-140` |
| **"boom bap"** | Hip-hop groove | Kick on 1, snare on 2-and or 3 | `groove.pattern: "boom_bap"` |
| **"chugga chugga"** | Palm-muted power chords | Muted eighth notes, metal | `groove.feel: "chug", muting: true` |
| **"pew pew"** | Laser synth sounds | High-frequency sweep, pitch bend | `synth.type: "lead", mod: "pitch_sweep"` |
| **"brr"** / **"brrrap"** | Trap hi-hat rolls | 32nd note hi-hat patterns | `hihat.subdivision: 32, pattern: "trap_roll"` |
| **"skrrt"** | Record scratch / brake sound | Vinyl scratch effect | `fx.type: "scratch"` |

### 1.2 Timbre & Texture Descriptions

Producer slang for sound qualities.

| Vernacular | Meaning | Technical Translation | iDAW Parameter |
|------------|---------|----------------------|----------------|
| **"fat"** / **"phat"** | Full low-mid frequencies | Boosted 100-300Hz, saturation | `eq.low_mid: +3dB, saturation: light` |
| **"thin"** | Lacking low frequencies | Cut below 200Hz | `eq.low: -6dB` |
| **"muddy"** | Cluttered low-mids | Too much 200-500Hz | `eq.problem: "mud", target: 200-500Hz` |
| **"crispy"** / **"crunchy"** | Pleasant high-frequency presence | 8-12kHz presence, light distortion | `eq.presence: +2dB, dist: "light_saturation"` |
| **"warm"** | Analog-like, reduced harshness | Gentle high roll-off, tape saturation | `character: "analog", warmth: 0.7` |
| **"bright"** | Emphasized high frequencies | Boosted 5kHz+ | `eq.high: +3dB` |
| **"dark"** | Subdued high frequencies | Rolled-off highs | `eq.high: -4dB, character: "dark"` |
| **"punchy"** | Strong transient attack | Fast attack compression, then release | `comp.attack: fast, punch: high` |
| **"scooped"** | Reduced midrange | Cut 500Hz-2kHz (metal tone) | `eq.mid: -6dB` |
| **"honky"** | Unpleasant nasal midrange | Problem around 800Hz-1.2kHz | `eq.problem: "honk", target: 800-1200Hz` |
| **"boxy"** | Cardboard-like midrange | Problem around 300-600Hz | `eq.problem: "box", target: 300-600Hz` |
| **"glassy"** | Clear, crystalline highs | Clean high frequencies, no distortion | `eq.high_shelf: +2dB, dist: none` |
| **"airy"** | Sense of space in highs | 12kHz+ "air" frequencies | `eq.air: +3dB, target: 12kHz+` |
| **"sizzle"** | Pronounced cymbal/hi-hat | High-frequency cymbal presence | `eq.cymbal_presence: high` |

### 1.3 Mix & Production Terms

| Vernacular | Meaning | Technical Translation | iDAW Parameter |
|------------|---------|----------------------|----------------|
| **"glue"** | Cohesive mix | Bus compression, shared reverb | `bus_comp: true, shared_space: true` |
| **"separation"** | Each element distinct | EQ carving, panning | `eq.carve: true, stereo.spread: wide` |
| **"in your face"** | Aggressive, forward | Less reverb, more compression | `space: "dry", aggression: 0.8` |
| **"lush"** | Rich, layered texture | Multiple voices, reverb, chorus | `layers: many, fx: ["reverb", "chorus"]` |
| **"lo-fi"** | Degraded, vintage quality | Bitcrush, vinyl noise, tape wobble | `character: "lo-fi", degradation: 0.6` |
| **"hi-fi"** | Clean, modern production | Full frequency response, clarity | `character: "hi-fi", clarity: high` |
| **"wet"** | Heavy effects | More reverb/delay | `fx.mix: 0.6+` |
| **"dry"** | No/minimal effects | Direct signal | `fx.mix: 0.1` |
| **"buried"** | Too quiet in mix | Needs volume/presence boost | `production.rule_break: "BURIED_ELEMENT"` |
| **"sitting right"** | Perfect level balance | Well-mixed | `mix.balance: optimal` |
| **"poking out"** | Too loud in mix | Needs attenuation | `level.problem: "too_hot"` |

### 1.4 Feel & Groove Descriptions

| Vernacular | Meaning | Technical Translation | iDAW Parameter |
|------------|---------|----------------------|----------------|
| **"laid back"** | Behind the beat | Slight timing delay (5-30ms) | `groove.pocket: "behind", offset_ms: 15` |
| **"on top"** / **"pushing"** | Ahead of the beat | Slight timing advance | `groove.pocket: "ahead", offset_ms: -10` |
| **"in the pocket"** | Perfect groove lock | Tight to grid or intentional swing | `groove.pocket: "locked"` |
| **"swung"** | Triplet-based timing | Swing ratio (typically 60-67%) | `groove.swing: 0.62` |
| **"straight"** | Even note divisions | No swing | `groove.swing: 0.5` |
| **"tight"** | Precise timing | Quantized, minimal variation | `groove.tightness: 0.95` |
| **"loose"** | Human timing variation | Unquantized, timing drift | `groove.humanize: 0.4` |
| **"driving"** | Forward momentum | Slight push, energy build | `groove.energy: "forward"` |
| **"dragging"** | Losing momentum | Unintentionally slow feel | `groove.problem: "drag"` |
| **"breathing"** | Organic tempo variation | Tempo rubato, human feel | `tempo.rubato: true` |

---

## PART 2: INTERNET MUSICOLOGY (Meme Theory → Real Theory)

These are terms that emerged from online music communities that map to legitimate theory concepts.

### 2.1 Progression Nicknames

| Meme Name | Progression | Technical Name | Emotional Quality | iDAW Mapping |
|-----------|-------------|----------------|-------------------|--------------|
| **"Axis of Awesome"** | I-V-vi-IV | Axis progression | Universal pop emotion | `progression.type: "axis"` |
| **"Mario Cadence"** | ♭VI-♭VII-I | Double plagal / Aeolian cadence | Triumphant, heroic | `progression.type: "mario_cadence"` |
| **"Creep Progression"** | I-III-IV-iv | Major with ♯III and borrowed iv | Yearning, bittersweet | `rule_break: "MODAL_INTERCHANGE"` |
| **"Andalusian Cadence"** | i-♭VII-♭VI-V | Phrygian-influenced descent | Spanish, dramatic | `progression.type: "andalusian"` |
| **"Doo-Wop Changes"** | I-vi-IV-V | '50s progression | Nostalgic, innocent | `progression.type: "doo_wop"` |
| **"Pachelbel's Nightmare"** | I-V-vi-iii-IV-I-IV-V | Canon in D | Overused but effective | `progression.type: "pachelbel"` |
| **"Deceptive Cadence"** | V-vi (instead of V-I) | Deceptive resolution | Surprise, unfulfilled | `cadence.type: "deceptive"` |
| **"♭VI chord"** (Neapolitan adjacent) | ♭VI in major key | Borrowed from parallel minor | Epic, cinematic | `rule_break: "MODAL_INTERCHANGE"` |
| **"The Truck Driver's Gear Change"** | Sudden modulation up half/whole step | Direct modulation | Cheap energy boost | `modulation.type: "truck_driver"` |

### 2.2 Mode Memes

| Meme Description | Mode | Character | Use Case |
|------------------|------|-----------|----------|
| **"Simpsons theme mode"** | Lydian | Bright, floating, magical | Wonder, sci-fi |
| **"Sadboy mode"** | Dorian | Minor but hopeful | Melancholic soul/R&B |
| **"Evil villain mode"** | Phrygian | Dark, exotic, tense | Metal, flamenco |
| **"Generic happy"** | Ionian (Major) | Stable, resolved | Pop, country |
| **"Basic sad"** | Aeolian (Natural Minor) | Sad, resigned | Ballads, emo |
| **"Jazzy minor"** | Melodic Minor | Sophisticated, tense | Jazz, neo-soul |
| **"Spooky mode"** | Locrian | Unstable, eerie | Horror, avant-garde |

### 2.3 YouTube Theory Terms

| Term | Meaning | Real Concept |
|------|---------|--------------|
| **"Borrowed chord"** | Chord from parallel mode | Modal interchange |
| **"Chord substitution"** | Replacing expected chord | Reharmonization |
| **"Secondary dominant"** | V of V, V of ii, etc. | Tonicization |
| **"Passing chord"** | Chromatic connection | Chromatic approach |
| **"Crunchy chord"** | Dissonant voicing | Extensions/alterations |
| **"Spicy"** | Unexpected harmony | Any deviation from diatonic |
| **"Rootless voicing"** | No root in chord | Jazz voicing technique |

---

## PART 3: RULE-BREAKING MASTERPIECES (Theory → Emotion)

### 3.1 Harmonic Rule-Breaking

#### Parallel Fifths and Octaves
**THE RULE:** Parallel P5→P5 and P8→P8 forbidden in common practice (destroys voice independence)

| Artist | Piece | Technique | Emotional Effect | iDAW Code |
|--------|-------|-----------|------------------|-----------|
| Beethoven | Symphony 6 "Pastoral" | Parallel 5ths in Storm | Rustic, folk quality | `HARMONY_ParallelMotion` |
| Debussy | La Cathédrale engloutie | Planing triads | Medieval, impressionist wash | `HARMONY_ParallelMotion` |
| Power Chords | All rock/metal | Root + P5 parallel motion | Massive, unified | `HARMONY_ParallelMotion` |

**Beethoven's Response:** "Well, who has forbidden them? ...Well, I allow them!"

#### Polytonality
**THE RULE:** Music should maintain single tonal center

| Artist | Piece | Technique | Emotional Effect | iDAW Code |
|--------|-------|-----------|------------------|-----------|
| Stravinsky | Rite of Spring | E♭7 + E major simultaneously | Primal chaos, permanent tension | `HARMONY_Polytonality` |
| Stravinsky | Petrushka | C major + F# major (tritone apart) | Dual nature, puppet/human | `HARMONY_Polytonality` |

#### Unresolved Dissonance
**THE RULE:** Dissonances must resolve by step to consonances

| Artist | Piece | Technique | Emotional Effect | iDAW Code |
|--------|-------|-----------|------------------|-----------|
| Monk | 'Round Midnight | Semitone clusters that never resolve | Commentary on expectations | `HARMONY_UnresolvedDissonance` |
| Coltrane | Giant Steps | 26 chords in 16 bars, M3 root motion | Sheets of sound, key shifts every 2 beats | `HARMONY_RapidModulation` |

**Monk Voicings:** Semitone at bottom + 3rd on top (e.g., B-C-E in C major)

#### Modal Mixture
**THE RULE:** Stay within diatonic chords; don't mix major/minor freely

| Artist | Piece | Technique | Emotional Effect | iDAW Code |
|--------|-------|-----------|------------------|-----------|
| Beatles | Norwegian Wood | ♭VII in major key (E-D-E) | Dominant substitute, folk color | `HARMONY_ModalInterchange` |
| Radiohead | Creep | I-III-IV-iv (G-B-C-Cm) | Happy-to-sad ambiguity | `HARMONY_ModalInterchange` |
| Radiohead | Everything in Its Right Place | C Phrygian ↔ F Aeolian oscillation | Floating, unresolved | `HARMONY_ModalInterchange` |

**Radiohead Technique:** Pedal notes tie disparate chords together

### 3.2 Rhythmic Rule-Breaking

#### Irregular Meter
**THE RULE:** Music should maintain consistent meter with predictable strong beats

| Artist | Piece | Technique | Emotional Effect | iDAW Code |
|--------|-------|-----------|------------------|-----------|
| Stravinsky | Rite of Spring "Sacrificial Dance" | 2/16, 3/16, 5/16, 7/8 alternating | Primitive, unpredictable chaos | `RHYTHM_MeterAmbiguity` |
| Radiohead | Pyramid Song | Ambiguous meter (12/8? 6/8? 4/4?) | Unsettled, floating | `RHYTHM_MeterAmbiguity` |

#### Polyrhythm
**THE RULE:** All voices share metric framework

| Artist | Piece | Technique | Emotional Effect | iDAW Code |
|--------|-------|-----------|------------------|-----------|
| Coltrane | Various | Notes grouped in 5s and 7s | Wall-like texture | `RHYTHM_PolyrhythmicGroupings` |

**Coltrane Quote:** "Sometimes what I played didn't work out in 8th notes, 16th notes or triplets. I had to put the notes in uneven groups like fives and sevens."

### 3.3 Structural Rule-Breaking

#### Non-Resolution
**THE RULE:** Pieces should resolve to tonic; form should create closure

| Artist | Piece | Technique | Emotional Effect | iDAW Code |
|--------|-------|-----------|------------------|-----------|
| Chopin | Prelude E minor Op.28/4 | Enharmonic spelling creates ambiguous resolution | Negative action, unfulfilled | `STRUCTURE_NonResolution` |
| Radiohead | Many songs | Double-tonic complex (Am-F-C-G) | Neither key wins | `STRUCTURE_NonResolution` |

### 3.4 The Tritone

**THE RULE:** "Diabolus in musica" - must be resolved

| Artist | Piece | Technique | Emotional Effect | iDAW Code |
|--------|-------|-----------|------------------|-----------|
| Black Sabbath | Black Sabbath | Riff built on unresolved G-D♭ | Tension becomes identity | `HARMONY_TritoneExploitation` |
| Jazz Standard | Tritone Substitution | Replace V7 with ♭II7 | Chromatic bass movement | `HARMONY_TritoneSubstitution` |

**Tritone Sub Explanation:** G7 and D♭7 share same tritone (B-F / C♭-F), so D♭7→C gives chromatic bass while maintaining function.

---

## PART 4: INSTRUMENT-SPECIFIC VERNACULAR

### 4.1 Guitar

| Term | Meaning | Technical |
|------|---------|-----------|
| **"Chimey"** | Bright, bell-like clean | Bridge pickup, chorus, compression |
| **"Jangly"** | Bright acoustic/clean electric | Open strings, moderate attack |
| **"Sludgy"** | Heavy, slow, downtuned | Drop tuning, high gain, slow tempo |
| **"Djent"** | Tight, percussive palm mute | Extended range, precise attack |
| **"Spanky"** | Funky, percussive | Strat bridge, tight playing |
| **"Twangy"** | Country-style snap | Telecaster, clean, compression |
| **"Fuzz face"** | Classic fuzzy distortion | 60s fuzz pedal character |

### 4.2 Synth

| Term | Meaning | Technical |
|------|---------|-----------|
| **"Pad"** | Sustained background texture | Slow attack, long release |
| **"Stab"** | Short, punchy chord hit | Fast attack, short decay |
| **"Pluck"** | Percussive, defined attack | Fast attack, medium decay |
| **"Lead"** | Monophonic melodic voice | Single oscillator, portamento |
| **"Bass"** | Low frequency foundation | Sub oscillator, low pass |
| **"Arp"** | Arpeggiated pattern | Sequenced notes |
| **"Squelchy"** | Resonant filter movement | High resonance, envelope on cutoff |
| **"Saw-wave vibes"** | Bright, buzzy | Sawtooth oscillator |
| **"PWM"** | Pulse width modulation | Animated, hollow to full |

### 4.3 Drums

| Term | Meaning | Technical |
|------|---------|-----------|
| **"Four on the floor"** | Kick on every beat | 4/4 dance groove |
| **"Backbeat"** | Snare on 2 and 4 | Standard rock/pop |
| **"Blast beat"** | Extremely fast alternating | Metal technique |
| **"Ghost notes"** | Quiet snare hits | Dynamic subtlety |
| **"Rimshot"** | Snare + rim simultaneously | Louder, more attack |
| **"Cross-stick"** | Click on rim only | Lighter, Latin feel |
| **"Shuffle"** | Swung eighth notes | Triplet-based groove |
| **"Linear"** | No limbs hit simultaneously | Funk, complex patterns |

---

## PART 5: iDAW INTEGRATION SCHEMA

### 5.1 Vernacular → Intent Translation

```yaml
# Example: User says "I want it to sound fat and laid back"
vernacular_input:
  descriptors: ["fat", "laid back"]
  
translation:
  fat:
    eq_adjustment: 
      low_mid: "+3dB"
      target: "100-300Hz"
    processing:
      saturation: "light"
    
  laid_back:
    groove_offset_ms: 15
    pocket: "behind"
    swing: 0.55
    
generated_parameters:
  groove:
    pocket: "behind"
    offset_ms: 15
    swing: 0.55
  mix:
    eq:
      low_mid: "+3dB"
    saturation: "light"
```

### 5.2 Rule-Breaking → Emotion Mapping

```yaml
rule_breaking_lookup:
  HARMONY_ModalInterchange:
    emotions: ["bittersweet", "nostalgia", "hope", "earned_joy"]
    technique: "Borrow from parallel mode"
    example: "B♭m (iv) in F major for earned sadness"
    
  HARMONY_ParallelMotion:
    emotions: ["power", "defiance", "medieval", "unity"]
    technique: "Parallel fifths/triads"
    example: "Power chord progressions"
    
  HARMONY_UnresolvedDissonance:
    emotions: ["tension", "anxiety", "commentary", "unfinished"]
    technique: "Don't resolve tendency tones"
    example: "Monk's semitone clusters"
    
  RHYTHM_MeterAmbiguity:
    emotions: ["floating", "unsettled", "dreamlike", "chaotic"]
    technique: "Obscure or shift meter"
    example: "Pyramid Song's ambiguous pulse"
    
  STRUCTURE_NonResolution:
    emotions: ["longing", "grief", "unfinished", "yearning"]
    technique: "Avoid tonic resolution"
    example: "End on IV or vi chord"
    
  PRODUCTION_BuriedVocals:
    emotions: ["dissociation", "intimacy", "distance", "dreams"]
    technique: "Vocals behind instruments"
    example: "Shoegaze mix aesthetic"
```

### 5.3 Meme Theory → Formal Theory

```yaml
meme_to_theory:
  mario_cadence:
    formal_name: "Double Plagal Cadence"
    roman: "♭VI-♭VII-I"
    emotional_tag: ["triumphant", "heroic", "video_game"]
    
  creep_progression:
    formal_name: "Modal Interchange with III and iv"
    roman: "I-III-IV-iv"
    emotional_tag: ["yearning", "bittersweet", "90s_alt"]
    rule_break: "HARMONY_ModalInterchange"
    
  axis_of_awesome:
    formal_name: "Axis Progression"
    roman: "I-V-vi-IV"
    emotional_tag: ["universal", "pop", "accessible"]
```

---

## PART 6: QUICK REFERENCE TABLES

### Why Rule-Breaking Works (Meta-Patterns)

| Pattern | Explanation | Example |
|---------|-------------|---------|
| **Context Shift** | Rules for vocal polyphony don't apply to distorted guitars | Power chords = parallel 5ths |
| **Intentional Signification** | "Wrong" notes work because they're meaningfully wrong | Monk's commentary |
| **Historical Reclamation** | Parallel 5ths evoke medieval; polytonality evokes pre-tonal | Debussy's planing |
| **Emotional Authenticity** | Ambiguity better expresses complex states than resolution | Radiohead's floating tonic |
| **Timbral Considerations** | Distortion, sustain, electronics change what works | P5s stay clear with distortion |

### Complete Rule-Break Reference

| Code | Category | Effect | Example Artists |
|------|----------|--------|-----------------|
| `HARMONY_ParallelMotion` | Harmony | Medieval, power, unity | Debussy, Metal |
| `HARMONY_ModalInterchange` | Harmony | Bittersweet, complexity | Beatles, Radiohead |
| `HARMONY_UnresolvedDissonance` | Harmony | Tension, commentary | Monk, Jazz |
| `HARMONY_TritoneSubstitution` | Harmony | Chromatic sophistication | Jazz standards |
| `HARMONY_Polytonality` | Harmony | Chaos, duality | Stravinsky |
| `RHYTHM_MeterAmbiguity` | Rhythm | Floating, unsettled | Radiohead |
| `RHYTHM_ConstantDisplacement` | Rhythm | Anxiety, unease | Experimental |
| `RHYTHM_TempoFluctuation` | Rhythm | Human, intimate | Lo-fi, singer-songwriter |
| `STRUCTURE_NonResolution` | Structure | Longing, unfinished | Chopin, Alt-rock |
| `PRODUCTION_BuriedVocals` | Production | Dissociation, texture | Shoegaze |
| `PRODUCTION_PitchImperfection` | Production | Raw, honest | Lo-fi bedroom |
| `ARRANGEMENT_StructuralMismatch` | Arrangement | Story-driven | Through-composed pieces |

---

*Consolidated from: Gemini Research (Casual Music Sound Descriptions) + rule_breaking_masterpieces.md*
*For iDAW Music Brain integration - November 2025*
*"The audience doesn't hear 'borrowed from Dorian.' They hear 'that part made me cry.'"*
