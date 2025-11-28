# Audio Cataloger Setup

A Python tool to scan and catalog your audio files with automatic key/tempo detection.

---

## What It Does

- Scans folders for audio files (WAV, AIFF, MP3, FLAC)
- Extracts metadata: duration, sample rate, channels
- Detects estimated BPM and key
- Saves to a searchable SQLite database
- Simple command-line search

---

## Requirements

- Python 3.9+ (comes with macOS)
- About 10 minutes to set up

---

## Installation

### Step 1: Create a Project Folder
```bash
mkdir -p ~/Music-Brain/audio-cataloger
cd ~/Music-Brain/audio-cataloger
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install librosa numpy soundfile
```

*Note: First install may take a few minutes*

### Step 4: Save the Script
Copy the `audio_cataloger.py` script (provided separately) to:
```
~/Music-Brain/audio-cataloger/audio_cataloger.py
```

---

## Usage

### Activate Environment (each session)
```bash
cd ~/Music-Brain/audio-cataloger
source venv/bin/activate
```

### Scan a Folder
```bash
python audio_cataloger.py scan ~/Music/Samples
```

### Search the Catalog
```bash
# Search by keyword
python audio_cataloger.py search kick

# Search by key
python audio_cataloger.py search --key Am

# Search by BPM range
python audio_cataloger.py search --bpm-min 118 --bpm-max 122

# Combine searches
python audio_cataloger.py search drum --key C --bpm-min 90
```

### List All Files
```bash
python audio_cataloger.py list
```

### Show Stats
```bash
python audio_cataloger.py stats
```

---

## Database Location

The catalog is saved to:
```
~/Music-Brain/audio-cataloger/audio_catalog.db
```

This is a SQLite database. You can:
- Back it up by copying the file
- View it with any SQLite browser
- Query it directly with SQL

---

## Integration with AI Assistant

Once cataloged, you can:
1. Export search results to markdown
2. Add to your Obsidian vault
3. Query through AnythingLLM

Example workflow:
```bash
# Export all samples in A minor to a file
python audio_cataloger.py search --key Am --export ~/Documents/Music-Brain-Vault/Samples-Library/am-samples.md
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `librosa` install fails | Try: `pip install --upgrade pip` then retry |
| Slow scanning | Normal for large libraries; BPM/key detection takes time |
| Wrong key detected | Detection is estimated; add manual override in vault notes |
| Permission denied | Check folder permissions |
| "No module named" | Make sure venv is activated |

---

## Limitations

- Key/BPM detection is *estimated* — not 100% accurate
- Works best on melodic/rhythmic content
- Very short samples (<1 sec) may not analyze well
- Large libraries take time to scan

---

## Future Enhancements

Potential additions:
- [ ] GUI interface
- [ ] Waveform thumbnails
- [ ] Similarity search
- [ ] Auto-tagging by content type
- [ ] Integration with Logic Pro

---

## Related
- [[AI Assistant Setup Guide]]
- [[../Samples-Library/Sample Library Index]]

