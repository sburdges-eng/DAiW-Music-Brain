---
title: DAiW Project Task Board
tags: [project, tasks, kanban, daiw]
category: Project_Management
created: 2025-11-25
updated: 2025-11-25
---

# DAiW / Vault Integration — Prioritized Task List

## ⭐ Critical — Immediate

- [x] Finalize repository structure as canonical source
- [x] Create chord.py, progression.py, sections.py modules
- [x] Build CLI scaffolding with all commands
- [x] Add rule_breaking_practical.md to Songwriting_Guides
- [x] Add rule_breaking_dataset.json to Data_Files
- [x] Create genre_pocket_maps.json
- [x] Implement RuleBreakingTeacher module
- [x] Implement SongInterrogator module
- [x] Create Git-ready repo structure
- [ ] Push to GitHub
- [ ] Import vault into AnythingLLM workspace

---

## ⬆️ High Priority — Enables System Growth

- [ ] Normalize imports + test all modules
- [ ] Move teaching MIDIs into `examples/midi/`
- [ ] Register CLI command `daiw teach rulebreaking`
- [ ] Test interactive teaching session output
- [ ] Tag documents with Dataview compliance
- [ ] Verify vault search behavior through AI retrieval
- [ ] Document new features in repository README
- [ ] Add unit tests for core modules

---

## ➡️ Normal Priority — Quality Expansion

- [ ] Add `daiw diagnose` CLI command (full implementation)
- [ ] Add `daiw reharm` CLI command (full implementation)
- [ ] Add `daiw play groove` CLI command scaffolding
- [ ] Build playback/preview function for MIDIs
- [ ] Generate DAW workflow script placement (Logic template)
- [ ] Ensure teaching dataset connects logically to CLI responses
- [ ] Create Dataview summary dashboard in Obsidian
- [ ] Add more progression templates

---

## ⬇️ Low Priority — Nice-to-Haves

- [ ] Convert rulebreaking guide into DAW project templates
- [ ] Auto-generate reharmonization MIDI examples
- [ ] Add Ableton workflow macros
- [ ] Add embedded chord diagrams + visuals to vault
- [ ] Expand dataset to multiple keys
- [ ] Add Spotify/Apple Music reference song list
- [ ] Create video tutorials

---

## 🔥 Major Builds — Future System Milestones

- [ ] Groove extractor engine (full audio analysis)
- [ ] Groove humanizer engine
- [ ] Automatic reharmonization model
- [ ] Full DAiW desktop GUI workstation (Electron/Tauri)
- [ ] DAW session exporter (Logic, Ableton, Pro Tools)
- [ ] Local LLM songwriting coach mode
- [ ] End-to-end "song doctor" pipeline
- [ ] MIDI playback in terminal

---

## ✅ Completed

- [x] Integrated vault into DAiW
- [x] Created YAML intelligence for rulebreaking doc
- [x] Built dataset + teaching scaffolding
- [x] Generated prioritized Obsidian task system
- [x] Created comprehensive Python package structure
- [x] Implemented groove extraction/application modules
- [x] Implemented chord analysis modules
- [x] Implemented section detection
- [x] Created "Interrogate Before Generate" system
- [x] Built genre pocket maps database

---

## Quick Stats

| Category | Count |
|----------|-------|
| Python modules | 15+ |
| JSON data files | 3 |
| Vault documents | 3 |
| CLI commands | 6 |

---

## Vision Reminder

> **Creative Companion, Not a Factory**

The tool shouldn't finish art for people — it should make them braver.

### Core Principles
1. **Interrogate Before Generate** — Ask about mood, intent, imagery first
2. **Rule-Breaking Engine** — Teach when and why to break norms
3. **Groove Trainer** — Help users learn timing, feel, pocket
4. **Emotional Arrangement** — Match harmony to lyrical meaning
5. **User-Guided Translation** — Help express the sound in their head

---

## Kanban View (for Obsidian Kanban Plugin)

```
%% kanban:settings
{"date-colors": true}
%%

## ⭐ Critical
- [ ] Push to GitHub
- [ ] Import to AnythingLLM

## ⬆️ High
- [ ] Test all modules
- [ ] Add unit tests

## ➡️ Normal
- [ ] Full CLI implementation
- [ ] Dataview dashboard

## ✅ Done
- [x] Repository structure
- [x] Core modules
- [x] Teaching system
- [x] Interrogator system
```

---

## Dataview Query (for automatic task tracking)

```dataview
TASK
FROM "vault"
WHERE !completed
GROUP BY priority
```
