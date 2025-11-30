# Audio Vault & Kits Documentation

The Audio Vault is DAiW's sample organization system. This document explains the folder structure, kit definitions, and how to extend it.

## Overview

The Audio Vault provides:
- Standardized folder structure for samples
- Kit definition files for mood-based sample selection
- Integration with the therapy engine for emotionally-driven production

## Folder Structure

```
audio_vault/
├── raw/                        # Unprocessed samples (your originals)
│   ├── drums/
│   │   ├── kicks/
│   │   ├── snares/
│   │   ├── hats/
│   │   ├── cymbals/
│   │   ├── toms/
│   │   └── percussion/
│   ├── synths/
│   │   ├── leads/
│   │   ├── pads/
│   │   ├── bass/
│   │   └── textures/
│   ├── fx/
│   │   ├── risers/
│   │   ├── impacts/
│   │   └── atmospheres/
│   └── one_shots/
│
├── refined/                    # Processed samples (normalized, trimmed)
│   └── (same structure as raw/)
│
└── kits/                       # Kit definition JSON files
    ├── lofi_bedroom.json
    ├── industrial_glitch.json
    ├── jazz_brushes.json
    ├── ambient_drift.json
    └── defiant_punk.json
```

## Configuration

### Environment Variable

Set the Audio Vault path via environment variable:

```bash
export DAIW_AUDIO_VAULT_PATH="/path/to/your/audio_vault"
```

If not set, defaults to:
- `~/Music/AudioVault` (macOS/Linux)
- `%USERPROFILE%\Music\AudioVault` (Windows)
- Or `./audio_vault` relative to the repo

### Programmatic Access

```python
from music_brain.config import get_audio_vault_path

vault_path = get_audio_vault_path()
```

## Kit Definition Format

Kits are JSON files that define:
- Which samples to use
- Processing parameters
- Mood associations

### Example: `lofi_bedroom.json`

```json
{
  "name": "Lo-Fi Bedroom",
  "description": "Warm, dusty, intimate production style",
  "moods": ["grief", "nostalgia", "tenderness"],
  "tempo_range": [60, 90],

  "samples": {
    "kick": {
      "path": "drums/kicks/vinyl_thump.wav",
      "velocity_curve": "soft",
      "processing": {
        "saturation": 0.3,
        "lowpass_hz": 8000
      }
    },
    "snare": {
      "path": "drums/snares/tape_crack.wav",
      "velocity_curve": "natural",
      "processing": {
        "reverb_wet": 0.2
      }
    },
    "hat": {
      "path": "drums/hats/dusty_hat.wav",
      "velocity_curve": "ghost_heavy"
    }
  },

  "global_processing": {
    "vinyl_noise": true,
    "tape_wobble": 0.1,
    "bitcrush": 12
  }
}
```

### Kit Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Display name |
| `description` | string | What this kit sounds like |
| `moods` | array | Which emotions this kit suits |
| `tempo_range` | array | [min, max] BPM this kit works best at |
| `samples` | object | Sample definitions by type |
| `global_processing` | object | Effects applied to entire kit |

### Sample Definition Fields

| Field | Type | Description |
|-------|------|-------------|
| `path` | string | Relative path within vault |
| `velocity_curve` | string | "soft", "natural", "hard", "ghost_heavy" |
| `processing` | object | Per-sample effects |

## Mood-to-Kit Mapping

The therapy engine suggests kits based on detected affect:

| Primary Affect | Suggested Kits |
|---------------|----------------|
| grief | lofi_bedroom, ambient_drift |
| rage | industrial_glitch, defiant_punk |
| fear | industrial_glitch, ambient_drift |
| awe | ambient_drift |
| nostalgia | lofi_bedroom, jazz_brushes |
| dissociation | ambient_drift, lofi_bedroom |
| defiance | defiant_punk, industrial_glitch |
| tenderness | lofi_bedroom, jazz_brushes |

### Programmatic Selection

```python
from music_brain.audio.kits import select_kit_for_mood

# Returns kit definition dict
kit = select_kit_for_mood("grief")
print(kit["name"])  # "Lo-Fi Bedroom"
```

## Adding a New Kit

1. Create the JSON file in `audio_vault/kits/`:

```json
{
  "name": "My Custom Kit",
  "description": "Description of the sound",
  "moods": ["rage", "defiance"],
  "tempo_range": [100, 140],
  "samples": {
    "kick": {"path": "drums/kicks/my_kick.wav"},
    "snare": {"path": "drums/snares/my_snare.wav"},
    "hat": {"path": "drums/hats/my_hat.wav"}
  }
}
```

2. Place your samples in the corresponding paths under `refined/`

3. The kit will be automatically discovered on next run

## Processing Pipeline

When samples are loaded:

1. **Load** - Read from `refined/` (or fall back to `raw/`)
2. **Normalize** - Peak normalize to -1dB
3. **Apply Kit Processing** - Per-sample effects
4. **Apply Global Processing** - Kit-wide effects
5. **Velocity Scaling** - Apply velocity curve

## Best Practices

### Sample Organization

- Keep `raw/` as your archive (unchanged originals)
- Process into `refined/` for production use
- Name samples descriptively: `808_sub_clean.wav`, `vinyl_crack_snare.wav`

### Kit Design

- One kit per emotional "world"
- Don't make kits too specific (e.g., "sad_tuesday_kit")
- Include at minimum: kick, snare, hat
- Test at the kit's tempo_range extremes

### Path Conventions

- Use forward slashes even on Windows
- Paths are relative to `audio_vault/refined/`
- No leading slash

## Troubleshooting

### "Sample not found"

1. Check the path in your kit JSON
2. Ensure the file exists in `refined/` (or `raw/` as fallback)
3. Verify `DAIW_AUDIO_VAULT_PATH` is set correctly

### Kit not appearing in selection

1. Ensure JSON is valid (use a linter)
2. Check that `moods` array includes valid mood names
3. Restart the application to reload kits

### Samples sound wrong

1. Verify sample rate (44.1kHz or 48kHz recommended)
2. Check bit depth (16-bit or 24-bit)
3. Ensure samples are mono or stereo (not surround)
