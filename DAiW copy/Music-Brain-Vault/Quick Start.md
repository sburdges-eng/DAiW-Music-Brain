# Quick Start Guide

Get your Music Brain system running in 30 minutes.

---

## Step 1: Set Up Obsidian (5 min)

1. **Download Obsidian** — https://obsidian.md (free)
2. **Open this folder as a vault**
   - Open Obsidian
   - Click "Open folder as vault"
   - Select this `Music-Brain-Vault` folder
3. **Trust the vault** when prompted

You can now browse all your notes!

---

## Step 2: Install Plugins (5 min)

In Obsidian:
1. Settings (⚙️) → Community Plugins
2. Turn off "Restricted mode"
3. Browse and install:
   - **Dataview** — query notes like a database
   - **Templater** — templates for new notes
4. Enable both plugins

---

## Step 3: Install Ollama (5 min)

1. Download from https://ollama.com
2. Install and open (appears in menu bar)
3. Open Terminal and run:
```bash
ollama pull llama3
ollama pull nomic-embed-text
```

Wait for downloads to complete.

---

## Step 4: Install AnythingLLM (10 min)

1. Download from https://anythingllm.com
2. Install and open
3. Configure:
   - LLM: Ollama → llama3
   - Embedder: Ollama → nomic-embed-text
4. Create workspace "Music Brain"
5. Upload this vault folder

---

## Step 5: Test It (5 min)

Ask your AI:
- "What are the different types of reverb?"
- "Summarize the mixing workflow checklist"
- "Explain compression ratios"

---

## Optional: Audio Cataloger

See [[AI-System/Audio Cataloger Setup]] for scanning your sample library.

---

## You're Done!

Start documenting:
- Add notes about your songs
- Document your workflows
- Catalog your samples
- Ask your AI assistant questions

---

## Folder Overview

| Folder | Purpose |
|--------|---------|
| Songs/ | Your song projects |
| Workflows/ | Production checklists |
| Gear/ | Equipment settings |
| Theory/ | Reference materials |
| Samples-Library/ | Sound catalog |
| AI-System/ | Setup guides & tools |

---

## Need Help?

- Check [[AI-System/AI Assistant Setup Guide]] for detailed instructions
- Obsidian docs: https://help.obsidian.md
- AnythingLLM docs: https://docs.anythingllm.com

