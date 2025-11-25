# Audio Vault Workflow

Step-by-step guide to using DAiW with your own audio samples.

## Overview

The Audio Vault is where DAiW stores and organizes audio samples for kit-based production. This workflow shows how to go from raw samples to a complete track.

## Prerequisites

```bash
# Install DAiW with audio support
pip install -e .[audio]
```

## Folder Structure

```
audio_vault/
├── raw/                    # Your unprocessed samples
│   ├── drums/
│   │   ├── kicks/
│   │   ├── snares/
│   │   ├── hats/
│   │   └── percussion/
│   ├── synths/
│   └── fx/
├── refined/                # Processed/normalized samples
│   └── (same structure)
└── kits/                   # Kit definition files
    ├── lofi_bedroom.json
    ├── industrial_glitch.json
    └── jazz_brushes.json
```

## Step 1: Organize Raw Samples

Put your raw samples in the appropriate folders:

```bash
# Example structure
audio_vault/raw/drums/kicks/808_sub.wav
audio_vault/raw/drums/snares/vinyl_crack.wav
audio_vault/raw/drums/hats/dusty_hat.wav
```

## Step 2: Generate MIDI from Emotion

Use the therapy engine to create emotionally-driven MIDI:

```bash
# Generate MIDI based on emotional input
python examples/basic_therapy_to_midi.py "I feel lost and disconnected" \
    --motivation 4 \
    --chaos 0.3 \
    --output grief_session.mid
```

This creates MIDI with:
- **Low motivation (4)**: Shorter piece (32 bars)
- **Low chaos (0.3)**: More structured, less chaotic
- **"lost and disconnected"**: Triggers grief/dissociation affect → "climb" tension curve

## Step 3: Load in Your DAW

### Logic Pro
1. Create new project at the tempo shown in output (e.g., 70 BPM for grief)
2. Drag `grief_session.mid` onto the arrangement
3. Create a software instrument track
4. Load a pad or piano

### Ableton Live
1. Drag MIDI file into arrangement view
2. Load instrument on the track
3. Adjust clip to match project tempo

### FL Studio
1. Import MIDI via File > Import > MIDI File
2. Route to desired instrument

## Step 4: Layer with Your Kit

Once you have the MIDI playing:

1. Create a drum track
2. Load samples from your `audio_vault/refined/` folder
3. Program drums that complement the emotional arc

### Suggested kits by mood:

| Mood | Kit Style | Characteristics |
|------|-----------|-----------------|
| Grief | Lo-fi Bedroom | Vinyl crackle, soft hits, room verb |
| Rage | Industrial Glitch | Distorted, clipped, aggressive |
| Awe | Ambient Pads | Long decays, shimmering textures |
| Nostalgia | Vintage Analog | Warm, slightly detuned |

## Step 5: Use Tension Curve for Dynamics

The generated MIDI already has tension curves baked in:

- **Bars 1-16 (Verse)**: Quieter velocities (~54-63)
- **Bars 16-32 (Chorus)**: Louder (~99)
- **Bars 48-60 (Bridge)**: Peak energy (~108-135)
- **Bars 60+ (Outro)**: Collapse (~45)

Match your drum programming to these dynamics for cohesive feel.

## Example: Complete Session

```bash
# 1. Generate the emotional MIDI
python examples/basic_therapy_to_midi.py \
    "I remember when things were simpler" \
    --motivation 6 \
    --chaos 0.4 \
    --verbose \
    --output nostalgia_track.mid

# 2. The output tells you:
#    - Detected affect: nostalgia
#    - Mode: dorian
#    - Tempo: ~100 BPM
#    - Structure: constant (loop/mantra style)

# 3. In your DAW:
#    - Set project to 100 BPM
#    - Import nostalgia_track.mid
#    - Load a Rhodes or Wurlitzer
#    - Add your vintage drum kit
#    - Mix to taste
```

## Tips

1. **Don't fight the mood**: If the engine suggests aeolian (minor), lean into it
2. **Use the tension curve**: The quiet parts are quiet for a reason
3. **Layer intentionally**: Each layer should serve the emotional narrative
4. **Imperfection is a feature**: The humanization in the MIDI is intentional

## Troubleshooting

### MIDI sounds robotic
- Increase chaos tolerance to add more variation
- The groove humanization is subtle; give it headroom

### Output too short/long
- Adjust motivation scale (1-3 = 16 bars, 4-7 = 32 bars, 8-10 = 64 bars)

### Wrong emotional tone
- Check the keywords in your input text
- Use explicit emotion words: "grief", "rage", "fear", "numb", "tender"
