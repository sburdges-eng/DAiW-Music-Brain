# DAiW Examples

Quick-start examples for DAiW Music Brain.

## 5-Minute Quick Start

```bash
# Clone and install
git clone https://github.com/yourusername/DAiW-Music-Brain.git
cd DAiW-Music-Brain
pip install -e .

# Generate your first MIDI
python examples/basic_therapy_to_midi.py "I feel broken but still here" -v

# Output: output.mid
# Drag into your DAW and hit play
```

## Examples

| File | Description |
|------|-------------|
| `basic_therapy_to_midi.py` | Minimal script: text → MIDI |
| `audio_vault_workflow.md` | Full workflow with samples |

## basic_therapy_to_midi.py

Generate MIDI from emotional text input.

```bash
# Basic usage
python examples/basic_therapy_to_midi.py "I miss my grandmother"

# With options
python examples/basic_therapy_to_midi.py "I am furious" \
    --output rage.mid \
    --motivation 9 \
    --chaos 0.8 \
    --verbose
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `-o, --output` | Output MIDI path | `output.mid` |
| `-m, --motivation` | Motivation 1-10 (affects length) | 5 |
| `-c, --chaos` | Chaos 0.0-1.0 (affects complexity) | 0.5 |
| `-v, --verbose` | Show detailed analysis | off |

### Emotional Keywords

The engine recognizes these keywords:

| Emotion | Keywords |
|---------|----------|
| Grief | loss, gone, miss, dead, empty |
| Rage | angry, furious, hate, betrayed |
| Fear | scared, terrified, panic, trapped |
| Awe | wonder, beautiful, infinite, vast |
| Nostalgia | remember, childhood, memory, home |
| Dissociation | numb, nothing, floating, detached |
| Defiance | refuse, stand, strong, free |
| Tenderness | soft, gentle, hold, love, care |

## What Gets Generated

Based on your input, the engine produces:

1. **Chord Progression** - Mode selected by emotion
2. **Tempo** - Fast for rage/fear, slow for grief
3. **Length** - Based on motivation (16/32/64 bars)
4. **Tension Curve** - Verse/Chorus/Bridge dynamics

Example output structure for "I feel the loss":
- Mode: Aeolian (minor)
- Tempo: 70 BPM
- Length: 32 bars
- Structure: "climb" (slow build)

## Next Steps

After generating MIDI:

1. Open DAW (Logic, Ableton, FL Studio)
2. Import the MIDI file
3. Load an instrument (piano, pad, strings)
4. The tension curve is already in the velocities
5. Add drums that follow the emotional arc
