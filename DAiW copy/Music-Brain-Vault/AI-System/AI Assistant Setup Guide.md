# AI Assistant Setup Guide

Complete setup for your local AI assistant using Ollama + AnythingLLM on M4 Mac.

---

## Overview

This system lets you chat with your Music Brain vault locally — no cloud, no subscription, 100% private.

**Components:**
1. **Ollama** — Runs AI models locally on your Mac
2. **Llama 3** — The AI model (free, open source)
3. **AnythingLLM** — Chat interface that reads your vault

---

## Part 1: Install Ollama

### Step 1: Download Ollama
1. Go to: https://ollama.com
2. Click "Download for macOS"
3. Open the downloaded file
4. Drag Ollama to Applications

### Step 2: Start Ollama
1. Open Ollama from Applications
2. It will appear in your menu bar (llama icon)
3. Ollama now runs in the background

### Step 3: Download a Model
Open Terminal and run:
```bash
ollama pull llama3
```

This downloads Llama 3 (about 4GB). Wait for it to complete.

### Step 4: Test It
In Terminal:
```bash
ollama run llama3
```

Type a question. If it responds, Ollama is working. Type `/bye` to exit.

---

## Part 2: Install AnythingLLM

### Step 1: Download
1. Go to: https://anythingllm.com
2. Click "Download"
3. Select macOS (Apple Silicon)
4. Open the downloaded .dmg
5. Drag to Applications

### Step 2: First Launch
1. Open AnythingLLM
2. If macOS blocks it: System Settings → Privacy & Security → "Open Anyway"

### Step 3: Configure LLM Provider
1. Click Settings (gear icon)
2. Go to "LLM Preference"
3. Select "Ollama"
4. Model: `llama3`
5. Ollama Base URL: `http://localhost:11434` (default)
6. Save

### Step 4: Configure Embedder
1. Still in Settings
2. Go to "Embedding Preference"
3. Select "Ollama"
4. Embedding Model: `nomic-embed-text`
5. Save

If you don't have the embedding model yet:
```bash
ollama pull nomic-embed-text
```

---

## Part 3: Connect Your Vault

### Step 1: Create a Workspace
1. In AnythingLLM, click "+ New Workspace"
2. Name it: "Music Brain"

### Step 2: Upload Your Vault
1. Click on your Music Brain workspace
2. Click the upload icon (📁)
3. Select "Upload Folder"
4. Navigate to your Obsidian vault (e.g., `~/Documents/Music-Brain-Vault`)
5. Select and upload

### Step 3: Process Documents
1. AnythingLLM will process all markdown files
2. This creates "embeddings" — searchable chunks of your content
3. Wait for processing to complete

---

## Part 4: Start Chatting

### Example Queries
Try asking:
- "What are the different types of reverb?"
- "Summarize my mixing workflow checklist"
- "What compression settings should I try for vocals?"
- "What key is Kelly in the Water in?"
- "Explain gain staging"

### Tips for Better Results
- Be specific in your questions
- Reference note names when possible
- Ask follow-up questions

---

## Updating Your Knowledge

When you add new notes to Obsidian:

1. Open AnythingLLM
2. Go to your Music Brain workspace
3. Click upload icon
4. Re-upload the vault folder (or just new files)
5. AnythingLLM will process new content

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Ollama not responding | Make sure Ollama is running (check menu bar) |
| Model download fails | Check internet, try `ollama pull llama3` again |
| AnythingLLM won't open | Right-click → Open, or allow in Security settings |
| Slow responses | Normal for first query; M4 handles it well |
| "No documents" error | Re-upload vault folder |
| Answers not using your notes | Check that documents were processed (green check) |

---

## Advanced: Custom System Prompt

For better music-focused responses, set a custom system prompt:

1. Settings → Workspace Settings
2. Find "System Prompt"
3. Paste:

```
You are a music production assistant with deep knowledge of:
- Music theory and composition
- Audio recording and engineering
- Mixing and mastering
- Logic Pro and DAW workflows
- Synthesis and sound design

When answering questions, draw from the user's personal notes and knowledge base. Be practical and specific. Reference their documented workflows, gear settings, and song projects when relevant.

Speak as a knowledgeable collaborator, not a textbook. Be concise but thorough.
```

---

## Alternative Models

If Llama 3 feels slow or you want to experiment:

```bash
# Smaller/faster
ollama pull llama3:8b-instruct-q4_K_M

# Larger/smarter (needs more RAM)
ollama pull llama3:70b

# Good for coding/technical
ollama pull codellama

# Mistral (alternative family)
ollama pull mistral
```

---

## Hardware Notes

Your M4 Mac is well-suited for local AI:
- Unified memory = efficient model loading
- Neural Engine = faster inference
- Recommended: 16GB+ RAM for best experience
- Models run entirely on-device

---

## Related
- [[Audio Cataloger Setup]]
- [[../README]]

