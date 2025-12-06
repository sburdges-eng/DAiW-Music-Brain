# New Python Modules

> Documentation for Python modules added during the Multi-AI collaboration session.

## Overview

Six new Python modules were added to enhance DAiW's capabilities:

| Module | Purpose | AI Author |
|--------|---------|-----------|
| `humanizer.py` | Neural groove humanization | Claude |
| `ai_pipeline.py` | Multi-AI code generation | Claude |
| `recipe_book.py` | Rule-breaking recipes | ChatGPT |
| `intent_wizard.py` | Interactive intent discovery | ChatGPT |
| `critique_protocol.py` | Multi-AI feedback system | ChatGPT |
| `question_bank.py` | 500+ branching questions | All AIs |

---

## Neural Groove Humanizer

**File**: `music_brain/groove/humanizer.py`
**Author**: Claude

Humanizes MIDI patterns by applying learned performance characteristics.

### Humanization Styles

| Style | Character |
|-------|-----------|
| `TIGHT_POCKET` | Minimal variation, studio precision |
| `LAID_BACK` | Behind the beat, relaxed |
| `PUSHED` | Ahead of the beat, energetic |
| `DRUNK` | Loose, imprecise, lo-fi |
| `JAZZ_SWING` | Classic swing with accents |
| `HIP_HOP_BOUNCE` | Head-nod groove |
| `ROCK_DRIVE` | Driving, slightly ahead |
| `LATIN_CLAVE` | Clave-based micro-timing |
| `GOSPEL_PUSH` | Push on 2 and 4 |
| `DETROIT_TECHNO` | Quantized with velocity swing |

### Usage

```python
from music_brain.groove.humanizer import (
    NeuralGrooveHumanizer,
    HumanizationStyle,
    humanize_midi
)

# Simple usage
humanized = humanize_midi(notes, style="laid_back", intensity=0.8)

# Advanced usage
humanizer = NeuralGrooveHumanizer()
result = humanizer.humanize(
    notes,
    style=HumanizationStyle.JAZZ_SWING,
    intensity=1.0,
    instrument=InstrumentRole.HIHAT
)

# Humanize full drum kit with correlated timing
drums = humanizer.humanize_drums(
    kick=kick_notes,
    snare=snare_notes,
    hihat=hihat_notes,
    style=HumanizationStyle.HIP_HOP_BOUNCE
)

# Generate ghost notes
ghosts = humanizer.create_ghost_notes(main_notes, density=0.3)
```

---

## Multi-AI Intent-to-Code Pipeline

**File**: `music_brain/session/ai_pipeline.py`
**Author**: Claude

Orchestrates multiple AI models through a 4-stage code generation pipeline.

### Pipeline Stages

| Stage | AI | Purpose |
|-------|-----|---------|
| 1. Intent Analysis | Claude | Understand emotional intent |
| 2. Research | Gemini | Technical research & patterns |
| 3. Implementation Plan | ChatGPT | Architecture & structure |
| 4. Code Generation | Copilot | Actual code output |

### Usage

```python
from music_brain.session.ai_pipeline import (
    IntentToCodePipeline,
    PipelineStage
)

pipeline = IntentToCodePipeline()

# Submit intent
result = pipeline.process_intent(
    "Create a laid-back groove with ghost notes"
)

# Get stage-specific output
intent_analysis = result.stage_outputs[PipelineStage.INTENT_ANALYSIS]
final_code = result.stage_outputs[PipelineStage.CODE_GENERATION]
```

---

## Rule-Breaking Recipe Book

**File**: `music_brain/session/recipe_book.py`
**Author**: ChatGPT

A collection of musical "rule violations" with emotional context and famous examples.

### Built-in Recipes

| Recipe | The Rule | How to Break It |
|--------|----------|-----------------|
| Unresolved Yearning | Resolve to tonic | End on V or IV |
| Buried Confession | Vocals up front | Bury vocals in mix |
| Rhythmic Anxiety | Stay on grid | Constant micro-displacement |
| Beautiful Mistakes | Pitch perfect | Allow natural pitch drift |
| Harmonic Trespassing | Stay in key | Borrow from parallel modes |
| Dynamic Whisper | Consistent levels | Extreme quiet passages |
| Structural Rebellion | Standard form | No chorus, odd sections |
| Temporal Disorientation | Steady tempo | Subtle tempo drift |

### Usage

```python
from music_brain.session.recipe_book import (
    RecipeBook,
    get_recipe,
    suggest_recipes_for_emotion
)

book = RecipeBook()

# Get specific recipe
recipe = book.get_recipe("unresolved_yearning")
print(recipe.the_rule)
print(recipe.how_to_break)
print(recipe.emotional_effect)

# Get suggestions for emotion
recipes = book.suggest_for_emotion("melancholy")

# Search recipes
results = book.search("vocals")
```

---

## Interactive Intent Wizard

**File**: `music_brain/session/intent_wizard.py`
**Author**: ChatGPT

A guided question system that helps artists discover their emotional intent.

### Question Categories

- **Surface**: Initial exploration
- **Emotional**: Feeling identification
- **Resistance**: What's hard to say
- **Longing**: What you want to feel
- **Stakes**: What's at risk
- **Transformation**: Desired change
- **Technical**: Genre/style (asked last!)

### Usage

```python
from music_brain.session.intent_wizard import (
    IntentWizard,
    run_wizard_cli
)

# CLI mode
run_wizard_cli()

# Programmatic mode
wizard = IntentWizard()
session = wizard.start_session("session-001")

while True:
    question = wizard.get_current_question(session)
    if not question:
        break

    # Get user input...
    response = get_user_input(question)
    wizard.answer_question(session, response)

# Export to intent schema
intent = wizard.export_to_intent(session)
```

---

## Collaborative Critique Protocol

**File**: `music_brain/session/critique_protocol.py`
**Author**: ChatGPT

Enables multiple AIs to provide structured feedback on compositions.

### Critique Roles

| Role | Focus |
|------|-------|
| `ARRANGEMENT` | Structure, dynamics, instrumentation |
| `HARMONY` | Chords, voice leading, key |
| `RHYTHM` | Groove, timing, feel |
| `PRODUCTION` | Mix, sound design, texture |
| `EMOTIONAL` | Impact, intent alignment |
| `LYRICAL` | Words, phrasing, story |
| `COMMERCIAL` | Accessibility, hooks |
| `ARTISTIC` | Creativity, uniqueness |

### AI Role Assignments

| AI | Roles |
|----|-------|
| Claude | Emotional, Lyrical, Artistic |
| ChatGPT | Arrangement, Commercial |
| Gemini | Harmony, Production |
| Copilot | Rhythm, Production |

### Usage

```python
from music_brain.session.critique_protocol import (
    CritiqueProtocol,
    CritiqueRole,
    create_issue,
    create_strength
)

protocol = CritiqueProtocol()
session = protocol.create_session("critique-001", song_title="My Song")

# Each AI submits critique
critique = RoleCritique(
    role=CritiqueRole.EMOTIONAL,
    ai_name="Claude",
    overall_score=7.5,
    issues=[
        create_issue(
            IssueCategory.INTENT_MISMATCH,
            IssueSeverity.IMPORTANT,
            "Hidden anger not evident",
            "The arrangement feels purely melancholic"
        )
    ],
    strengths=[
        create_strength(
            "Authentic vulnerability",
            "The verse melody has beautiful exposed quality"
        )
    ]
)

protocol.submit_critique(session, critique)

# Build consensus and get report
report = protocol.finalize_session(session)
```

---

## Question Bank

**File**: `music_brain/session/question_bank.py`
**Authors**: All AIs (Claude, ChatGPT, Gemini, Copilot)

500+ questions for deep intent discovery. See [[question_bank]] for full documentation.

### Quick Reference

```python
from music_brain.session.question_bank import (
    get_questions_by_ai,
    get_questions_by_domain,
    get_questions_by_depth,
    get_random_questions,
    get_question_stats,
    QuestionDomain
)

# Statistics
stats = get_question_stats()
# {'total_questions': 500, 'therapy_questions': 250, 'musician_questions': 250}
```

---

## Related

- [[song_intent_schema]] - The schema these modules populate
- [[mcp_multi_ai_workstation]] - The collaboration system
- [[cpp_foundation]] - C++ counterparts (future)
