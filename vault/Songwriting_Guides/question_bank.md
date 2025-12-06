# Question Bank (500+ Questions)

> Deep interrogation questions for song intent discovery, split between therapy-based emotional exploration and musician-based technical decisions.

## Overview

The Question Bank contains 500+ branching questions designed to help artists discover their true emotional intent before making any technical decisions. This implements the **"Interrogate Before Generate"** philosophy.

## Distribution

| Domain | AI Assigned | Count |
|--------|-------------|-------|
| **Therapy** | Claude | 125 |
| **Therapy** | ChatGPT | 125 |
| **Musician** | Gemini | 125 |
| **Musician** | Copilot | 125 |
| **Total** | | **500** |

## Therapy Questions (250)

### Claude's Domain (125 questions)

#### Core Wound Exploration (30)
Deep questions about origin wounds and formative experiences.
- "What's the oldest memory connected to this feeling?"
- "Who taught you to feel this way about yourself?"
- "What part of you is still waiting for permission?"

#### Emotional Identification (25)
Naming and locating emotions in the body.
- "What emotion is sitting just beneath the surface right now?"
- "Where do you feel this emotion in your body?"
- "What color would this emotion be?"

#### Vulnerability (25)
Exploring openness and self-protection.
- "What's the most vulnerable thing you could say right now?"
- "What armor are you ready to take off?"
- "When did vulnerability become dangerous for you?"

#### Shadow Work (25)
Integrating hidden or rejected parts of self.
- "What part of yourself do you try to hide from others?"
- "What trait in others triggers you the most?"
- "What gift is hidden in your darkness?"

#### Inner Child (20)
Reconnecting with younger selves and unmet needs.
- "What did you need as a child that you never got?"
- "What promise did you make to yourself as a kid?"
- "What would it take to make your inner child feel safe?"

### ChatGPT's Domain (125 questions)

#### Relationship Dynamics (30)
Understanding interpersonal patterns and connections.
- "Who is this song really for?"
- "What pattern do you keep repeating in relationships?"
- "What version of yourself did you become around them?"

#### Self-Identity (25)
Exploring who you are and who you're becoming.
- "Who are you when no one is watching?"
- "What labels have you outgrown?"
- "What would you name this chapter of your life?"

#### Coping Mechanisms (20)
How we handle difficult emotions.
- "What do you do when you can't handle your feelings?"
- "What habit do you know is unhealthy but keep doing anyway?"
- "What survival mechanism have you outgrown?"

#### Attachment (20)
Patterns of connection and disconnection.
- "Do you chase people or push them away?"
- "What's your biggest fear in relationships?"
- "What would secure love actually feel like?"

#### Boundaries (15)
Protecting yourself while staying open.
- "What boundary do you struggle to hold?"
- "When do you say yes when you mean no?"
- "What resentment are you holding because you didn't set a boundary?"

#### Forgiveness (15)
Releasing and moving forward.
- "Who do you need to forgive?"
- "What apology are you waiting for that may never come?"
- "What would freedom from this resentment feel like?"

## Musician Questions (250)

### Gemini's Domain (125 questions)

#### Harmony (30)
Chord choices and harmonic movement.
- "What key feels right for this emotion?"
- "Do you want the chords to resolve or stay unresolved?"
- "How much dissonance can this song handle?"

#### Melody (25)
Melodic shape and character.
- "Should the melody be stepwise or have big jumps?"
- "Where should the melodic climax be?"
- "How catchy vs. subtle should the melody be?"

#### Theory (25)
Time, tempo, and rhythmic structure.
- "What time signature feels right?"
- "Should there be any rubato (tempo flexibility)?"
- "Do you want the downbeat emphasized or hidden?"

#### Key & Mode (20)
Tonal center and modal color.
- "Does this emotion feel sharp or flat?"
- "Would a modal approach work better than major/minor?"
- "Does Dorian mode's bittersweet quality fit?"

#### Chord Progressions (15)
Progression structure and movement.
- "Do you want a circular or linear progression?"
- "Should the progression feel familiar or unusual?"
- "Do you want the bridge to go somewhere harmonically unexpected?"

#### Voice Leading (10)
How notes move between chords.
- "Should the voice leading be smooth or have dramatic jumps?"
- "Should any voices sustain across chord changes?"
- "Do you want any chromatic voice leading?"

### Copilot's Domain (125 questions)

#### Production (30)
Sound design and processing choices.
- "Should this sound polished or raw?"
- "Do you want any lo-fi elements?"
- "Should vocals have heavy processing or be natural?"

#### Arrangement (30)
Song structure and instrumentation.
- "What's the song structure?"
- "Should there be a bridge or breakdown?"
- "Should the final chorus be bigger than the others?"

#### Rhythm & Groove (25)
Drums and rhythmic feel.
- "Should the drums be tight/quantized or loose/human?"
- "Do you want any ghost notes on the drums?"
- "Should the groove feel aggressive or relaxed?"

#### Sound Design (20)
Synths, textures, and sonic character.
- "What synth sounds fit this emotion?"
- "Do you want any atmospheric textures?"
- "Should synths evolve over time or stay static?"

#### Mix (10)
Balance and spatial considerations.
- "Should the mix feel wide or narrow?"
- "Do you want the vocals up front or blended?"
- "Do you want the mix to feel spacious or intimate?"

#### Genre (10)
Style and convention choices.
- "What genre is this song closest to?"
- "Are there any genre conventions you want to break?"
- "What reference track captures the vibe?"

## Depth Levels

| Level | Name | Purpose | Count |
|-------|------|---------|-------|
| 1 | Surface | Initial exploration, easy entry points | ~150 |
| 2 | Deeper | More probing, requires reflection | ~250 |
| 3 | Core | Deep truth, may be uncomfortable | ~100 |

## Usage

```python
from music_brain.session.question_bank import (
    get_questions_by_ai,
    get_questions_by_domain,
    get_questions_by_depth,
    get_random_questions,
    get_question_stats,
    QuestionDomain
)

# Get all Claude's questions
claude_qs = get_questions_by_ai("Claude")

# Get all therapy questions
therapy_qs = get_questions_by_domain(QuestionDomain.THERAPY)

# Get deep/core questions only
core_qs = get_questions_by_depth(3)

# Get 10 random musician questions
random_qs = get_random_questions(10, QuestionDomain.MUSICIAN)

# Get statistics
stats = get_question_stats()
```

## Integration with Intent Wizard

The Question Bank feeds into the [[intent_wizard]], which uses branching logic to select appropriate follow-up questions based on user responses. Not all 500 questions are asked - the wizard navigates through relevant paths.

## Related

- [[song_intent_schema]] - The intent schema these questions populate
- [[intent_wizard]] - The interactive wizard using these questions
- [[mcp_multi_ai_workstation]] - The multi-AI system that created these
