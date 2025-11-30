# DAiW Scripts

Helper scripts for common DAiW workflows.

## Available Scripts

### generate_demo_samples.py

Creates a demo AudioVault structure with placeholder audio files for testing.

```bash
# Generate demo vault at default location (~/Music/AudioVault)
python scripts/generate_demo_samples.py

# Generate at custom location
python scripts/generate_demo_samples.py /path/to/my/vault
```

This creates:
- Sample files organized by category (Drums/Kicks, Drums/Snares, etc.)
- A demo kit JSON file
- Output directory for generated MIDI

### build_logic_kit.py

Build Logic Pro X compatible sample kit from AudioVault.

```bash
# Basic kit
python scripts/build_logic_kit.py "My Kit"

# Mood-based kit
python scripts/build_logic_kit.py "Grief Kit" --mood grief

# With genre tag
python scripts/build_logic_kit.py "Punk Drums" --mood rage --genre punk

# Custom vault location
python scripts/build_logic_kit.py "My Kit" --vault /path/to/vault
```

Options:
- `--mood`: grief, rage, nostalgia, defiance, hope, anxiety, peace
- `--genre`: Any genre tag for organization
- `--vault`: Custom AudioVault path
- `--output`: Custom output file path

### quick_session.py

Run a complete therapy-to-MIDI session from the command line.

```bash
# Basic session
python scripts/quick_session.py "I feel lost in the darkness"

# With parameters
python scripts/quick_session.py -m 10 -c 3 "Ready to fight back"

# Custom output
python scripts/quick_session.py -o my_track.mid "Something needs to change"
```

Options:
- `-m, --motivation`: 1-10 (affects song length)
- `-c, --chaos`: 1-10 (affects tempo stability)
- `-v, --vulnerability`: 0-1 (affects dynamics)
- `-o, --output`: Output MIDI file path

## Setup

Make sure you're in the project directory with the package installed:

```bash
cd DAiW-Music-Brain
pip install -e .
```

Or add the parent directory to your Python path:

```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/DAiW-Music-Brain"
```

## Environment Variables

- `DAIW_AUDIO_VAULT_PATH`: Default AudioVault location
- `DAIW_SEED`: Random seed for reproducible output

## Typical Workflow

1. **Set up AudioVault** (first time only):
   ```bash
   python scripts/generate_demo_samples.py
   ```

2. **Create a mood-based kit**:
   ```bash
   python scripts/build_logic_kit.py "Session Kit" --mood grief
   ```

3. **Run a therapy session**:
   ```bash
   python scripts/quick_session.py "What I need to say"
   ```

4. **Import to DAW**:
   - Drag the generated MIDI into your DAW
   - Load the recommended kit or your own sounds
   - The tension curve is baked into velocities
