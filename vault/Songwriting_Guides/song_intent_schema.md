---
title: Song Intent Schema - Deep Interrogation System
tags: [songwriting, intent, schema, interrogation, rule-breaking, daiw]
category: Songwriting_Guides
created: 2025-11-25
updated: 2025-11-25
ai_priority: high
related_docs:
  - "[[rule_breaking_practical]]"
  - "[[rule_breaking_masterpieces]]"
---

# Song Intent Schema

> "Interrogate Before Generate"

The Song Intent Schema is a three-phase system for capturing what a song NEEDS to express before making any technical decisions.

## Philosophy

**The tool shouldn't finish art for people — it should make them braver.**

Traditional music generation asks: "What genre? What tempo? What key?"

The Intent Schema asks:
- What do you NEED to say?
- What are you afraid to say?
- How should you FEEL when it's done?

Only then do we translate to technical parameters.

---

## The Three Phases

### Phase 0: The Core Wound/Desire

The deep interrogation. Find the truth before the song.

| Field | Question |
|-------|----------|
| `core_event` | What happened? The inciting moment. |
| `core_resistance` | What's holding you back from saying it? |
| `core_longing` | What do you ultimately want to feel? |
| `core_stakes` | What's at risk if you don't say it? |
| `core_transformation` | How should you feel when the song ends? |

### Phase 1: Emotional & Intent

Validated by Phase 0. Guides all technical decisions.

| Field | Description | Options |
|-------|-------------|---------|
| `mood_primary` | Dominant emotion | Grief, Joy, Defiance, Longing, etc. |
| `mood_secondary_tension` | Internal conflict level | 0.0 (calm) to 1.0 (anxious) |
| `imagery_texture` | Visual/tactile quality | Sharp, Muffled, Open/Vast, etc. |
| `vulnerability_scale` | Emotional exposure | Low, Medium, High |
| `narrative_arc` | Structural emotion | See Narrative Arc Options |

### Phase 2: Technical Constraints

Implementation of intent into music.

| Field | Description |
|-------|-------------|
| `technical_genre` | Genre/style |
| `technical_tempo_range` | BPM range [low, high] |
| `technical_key` | Musical key |
| `technical_mode` | Mode (major, minor, modal) |
| `technical_groove_feel` | Rhythmic feel |
| `technical_rule_to_break` | Intentional rule break |
| `rule_breaking_justification` | WHY break this rule |

---

## Narrative Arc Options

| Arc | Description | Structure Implication |
|-----|-------------|----------------------|
| **Climb-to-Climax** | Building intensity to peak | Traditional build |
| **Slow Reveal** | Gradual truth emergence | Through-composed |
| **Repetitive Despair** | Cycling, stuck pattern | Minimal variation |
| **Static Reflection** | Meditative, unchanging | Drone-like sections |
| **Sudden Shift** | Dramatic pivot point | Long build → explosion |
| **Descent** | Progressive darkening | Energy decreases |
| **Rise and Fall** | Full emotional cycle | Peak in middle |
| **Spiral** | Intensifying repetition | Same section, building |

---

## Rule-Breaking Categories

### Harmony Rules

| Rule | What It Does | Use When |
|------|--------------|----------|
| `HARMONY_AvoidTonicResolution` | End on IV or VI, not I | Longing, grief, questions |
| `HARMONY_ParallelMotion` | Parallel 5ths/octaves | Power, defiance, punk |
| `HARMONY_ModalInterchange` | Borrow from other modes | Bittersweet, complexity |
| `HARMONY_TritoneSubstitution` | Replace V7 with bII7 | Jazz sophistication |
| `HARMONY_UnresolvedDissonance` | Leave 7ths/9ths hanging | Tension, incompleteness |

### Rhythm Rules

| Rule | What It Does | Use When |
|------|--------------|----------|
| `RHYTHM_ConstantDisplacement` | Shift all hits late | Anxiety, instability |
| `RHYTHM_TempoFluctuation` | Gradual BPM drift | Human feel, breathing |
| `RHYTHM_MetricModulation` | Implied time change | Mental state shift |
| `RHYTHM_DroppedBeats` | Remove expected hits | Emphasis through absence |

### Arrangement Rules

| Rule | What It Does | Use When |
|------|--------------|----------|
| `ARRANGEMENT_StructuralMismatch` | Wrong structure for genre | Story over convention |
| `ARRANGEMENT_BuriedVocals` | Vocals behind instruments | Dissociation, texture |
| `ARRANGEMENT_ExtremeDynamicRange` | Exceed normal limits | Dramatic impact |
| `ARRANGEMENT_PrematureClimax` | Peak early | Aftermath is the point |

### Production Rules

| Rule | What It Does | Use When |
|------|--------------|----------|
| `PRODUCTION_ExcessiveMud` | Keep 200-400Hz | Weight, claustrophobia |
| `PRODUCTION_PitchImperfection` | No pitch correction | Emotional honesty |
| `PRODUCTION_RoomNoise` | Keep ambient sound | Authenticity, lo-fi |
| `PRODUCTION_Distortion` | Allow clipping | Anger, damage, decay |
| `PRODUCTION_MonoCollapse` | Narrow stereo | Claustrophobia, focus |

---

## Complete Example: Grief with Misdirection

```yaml
# PHASE 0: THE CORE WOUND
song_root:
  core_event: "Finding someone I loved after they chose to leave."
  core_resistance: "Fear of making it about me."
  core_longing: "To process without exploiting the loss."
  core_stakes: "Relational"
  core_transformation: "Feel the grief witnessed and released."

# PHASE 1: EMOTIONAL INTENT
song_intent:
  mood_primary: "Grief"
  mood_secondary_tension: 0.3
  imagery_texture: "Muffled, like hearing through water"
  vulnerability_scale: "High"
  narrative_arc: "Slow Reveal"

# PHASE 2: TECHNICAL
song_technical_constraints:
  technical_genre: "Lo-Fi Bedroom/Confessional Acoustic"
  technical_tempo_range: [70, 85]
  technical_key: "F major"
  technical_mode: "major with borrowed minor"
  technical_groove_feel: "Organic/Breathing"
  technical_rule_to_break: "HARMONY_ModalInterchange"
  rule_breaking_justification: "Bbm (iv) makes hope feel earned and bittersweet"

# SYSTEM OUTPUT
system_directive:
  output_target: "Verse progression with misdirection"
  output_feedback_loop: "Harmony and Arrangement"
```

**Result:**
- Progression: F - C - Am - Dm (love song feel) → F - C - Bbm - F (reveal)
- Every line sounds like falling in love until the borrowed chord reveals grief
- Production: Intimate, imperfect, room sound preserved

---

## DAiW CLI Usage

```bash
# Create new intent from template
daiw intent new --save my_song.yaml

# Process intent to generate elements
daiw intent process my_song.yaml

# Suggest rules to break based on emotion
daiw intent suggest --emotion grief

# Validate intent for completeness
daiw intent validate my_song.yaml
```

---

## Connection to DAiW Modules

| Intent Field | DAiW Module | Output |
|--------------|-------------|--------|
| `technical_rule_to_break` (HARMONY_*) | `structure/progression.py` | Chord progression |
| `technical_rule_to_break` (RHYTHM_*) | `groove/templates.py` | Timing offsets |
| `narrative_arc` | `structure/sections.py` | Section structure |
| `vulnerability_scale` | `session/teaching.py` | Production guidelines |

---

## The Meta-Principle

> "Rules are broken INTENTIONALLY based on emotional justification."

Every technical decision flows from Phase 0. If you don't know what wound you're processing, you don't know which rules to break.

The schema ensures you've done the emotional work BEFORE you touch the technical tools.

---

*"The audience doesn't hear 'borrowed from Dorian.' They hear 'that part made me cry.'"*
