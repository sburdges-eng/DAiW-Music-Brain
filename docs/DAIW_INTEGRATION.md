# DAiW Full Integration Script

## Prerequisites

1. Clone your repo (if not already):
```bash
git clone https://github.com/seanburdgeseng/DAiW-Music-Brain.git
cd DAiW-Music-Brain
```

2. Install Claude Code (if not already):
```bash
npm install -g @anthropic-ai/claude-code
```

3. Authenticate:
```bash
claude login
```

---

## Step 1: Run Claude Code Integration

From your repo root, run:

```bash
claude "I need you to integrate new emotional mapping and rule-breaking modules into DAiW.

STEP 1: Check current structure
- Run: find . -type f -name '*.py' | head -30
- Run: ls -la music_brain/ 2>/dev/null || echo 'music_brain not found'

STEP 2: Create directories
- mkdir -p music_brain/models
- mkdir -p music_brain/data
- mkdir -p tests/models
- mkdir -p .claude
- mkdir -p docs/research

STEP 3: Tell me the current state before I give you files to create"
```

---

## Step 2: After Claude Shows Structure, Run This

```bash
claude "Now create these files:

FILE 1: music_brain/models/__init__.py
---
from .emotional_mapping import (
    EmotionalState,
    MusicalParameters,
    EMOTIONAL_PRESETS,
    EMOTION_MODIFIERS,
    INTERVAL_EMOTIONS,
    get_parameters_for_state,
    get_interrogation_prompts,
    describe_parameters,
)

__all__ = [
    'EmotionalState',
    'MusicalParameters', 
    'EMOTIONAL_PRESETS',
    'EMOTION_MODIFIERS',
    'INTERVAL_EMOTIONS',
    'get_parameters_for_state',
    'get_interrogation_prompts',
    'describe_parameters',
]
---

FILE 2: .claude/settings.json
---
{
  \"project\": {
    \"name\": \"DAiW-Music-Brain\",
    \"description\": \"Digital Audio intelligent Workstation - translates psychological states into MIDI\",
    \"language\": \"python\",
    \"version\": \"3.11+\",
    \"frameworks\": [\"music21\", \"librosa\", \"mido\", \"typer\", \"streamlit\"]
  },
  \"style\": {
    \"type_hints\": true,
    \"docstrings\": \"google\",
    \"line_length\": 100,
    \"preserve_imperfections\": true
  },
  \"rules\": [
    \"Ask before making architectural changes\",
    \"Imperfection is intentional in lo-fi contexts\",
    \"Every rule-break needs emotional justification\",
    \"Interrogate before generate\"
  ]
}
---

FILE 3: CLAUDE.md
---
# DAiW - Digital Audio intelligent Workstation

## Philosophy
**Interrogate Before Generate** - This tool makes musicians braver, it doesn't replace creativity.

## What This Project Does
Translates psychological/emotional states into MIDI compositions through structured emotional interrogation.

## Tech Stack
- Python 3.11+
- music21 (music theory)
- librosa (audio analysis)
- mido (MIDI)
- Typer (CLI)
- Streamlit (UI)
- pytest (testing)

## Package Structure
```
music_brain/
├── models/          # Data models (EmotionalState, MusicalParameters)
├── data/            # JSON presets and rule-breaking database
├── groove/          # Rhythm and timing
├── structure/       # Song structure
├── harmony/         # Chord progressions
├── audio/           # Audio analysis
├── daw/             # DAW integration
└── utils/           # Helpers
```

## Current Focus
Kelly song: \"When I Found You Sleeping\"
- Grief + PTSD processing
- F-C-Am-Dm @ 82 BPM
- Misdirection technique (sounds like love until reveal)
- Lo-fi bedroom emo aesthetic

## Key Principle
Imperfection serves authenticity. Voice cracks, timing variations, and rough edges are features, not bugs.
---

FILE 4: .cursorrules
---
# DAiW Project Rules for Cursor

## Project Context
DAiW (Digital Audio intelligent Workstation) translates emotional states into MIDI.
Philosophy: \"Interrogate Before Generate\"

## Tech Stack
- Python 3.11+
- music21, librosa, mido, Typer, Streamlit
- pytest for testing

## Code Style
- Use type hints everywhere
- Google-style docstrings
- 100 char line length
- Preserve intentional imperfections

## Critical Rules
- NEVER smooth over rough edges - imperfection is intentional
- Every rule-break needs emotional justification
- Ask before architectural changes
- Test with pytest

## Current Project
Kelly song: F-C-Am-Dm @ 82 BPM
Aesthetic: Lo-fi bedroom emo
Technique: Misdirection (love surface, grief undertow)
---

Create all 4 files, then show me what you created."
```

---

## Step 3: Add the Main Code Files

Download these from Claude Chat outputs and copy manually, OR run:

```bash
# If you have the files downloaded to ~/Downloads:
cp ~/Downloads/emotional_mapping.py music_brain/models/
cp ~/Downloads/daiw_knowledge_base.json music_brain/data/presets.json
cp ~/Downloads/rule_breaking_database.json music_brain/data/rule_breaks.json
```

OR have Claude Code fetch and create them:

```bash
claude "Create music_brain/models/emotional_mapping.py with the full EmotionalState and MusicalParameters dataclasses, EMOTIONAL_PRESETS dict, EMOTION_MODIFIERS, INTERVAL_EMOTIONS, and helper functions. Include:

- Grief preset: 60-82 BPM, minor/dorian, behind beat, 30% dissonance, sparse
- Anxiety preset: 100-140 BPM, phrygian, ahead of beat, 60% dissonance, busy  
- Nostalgia preset: 70-90 BPM, mixolydian, behind beat, 25% dissonance
- PTSD intrusion modifier with register_spike, harmonic_rush, unresolved_dissonance
- Misdirection modifier for surface positive / undertow negative
- Interval emotions from minor 2nd (90% tension) to major 7th (55% tension)
- get_parameters_for_state() function
- get_interrogation_prompts() function

Use dataclasses and enums. Full production-ready code."
```

---

## Step 4: Create Tests

```bash
claude "Create tests/models/test_emotional_mapping.py with:

1. Test EmotionalState creation
2. Test MusicalParameters defaults
3. Test EMOTIONAL_PRESETS contains grief, anxiety, nostalgia, anger, calm
4. Test get_parameters_for_state returns MusicalParameters
5. Test grief preset has tempo 60-82
6. Test PTSD modifier exists in EMOTION_MODIFIERS

Use pytest. Run the tests after creating."
```

---

## Step 5: Update Package Init

```bash
claude "Update music_brain/__init__.py to import from models:

from music_brain.models import (
    EmotionalState,
    MusicalParameters,
    EMOTIONAL_PRESETS,
    get_parameters_for_state,
)

Add to __all__ list. Then run: python -c 'from music_brain import EmotionalState; print(EmotionalState)'"
```

---

## Step 6: Commit and Push

```bash
claude "Show me git status, then create a commit:
git add .
git commit -m 'Add emotional mapping module, presets, and AI collaboration config'
git push origin main

Show me the final structure with: tree -L 3 -I __pycache__"
```

---

## Final Structure Should Look Like:

```
DAiW-Music-Brain/
├── .claude/
│   └── settings.json
├── .cursorrules
├── CLAUDE.md
├── music_brain/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── emotional_mapping.py
│   ├── data/
│   │   ├── presets.json
│   │   └── rule_breaks.json
│   ├── groove/
│   ├── harmony/
│   └── ...
├── tests/
│   └── models/
│       └── test_emotional_mapping.py
├── docs/
│   └── research/
└── README.md
```

---

## Quick Verification

After everything:

```bash
cd DAiW-Music-Brain
python -c "
from music_brain.models import EmotionalState, EMOTIONAL_PRESETS, get_parameters_for_state

state = EmotionalState(primary_emotion='grief', has_intrusions=True)
params = get_parameters_for_state(state)
print(f'Grief + PTSD: {params.tempo_suggested} BPM, {params.timing_feel.value} beat')
"
```

Should output:
```
Grief + PTSD: 72 BPM, behind beat
```
