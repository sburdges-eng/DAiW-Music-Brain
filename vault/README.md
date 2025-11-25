# Music Brain Vault

An Obsidian-compatible knowledge base for music production, songwriting, and creative theory.

## Setup

1. Open Obsidian
2. Create new vault or open existing
3. Copy contents of this `vault/` directory into your vault
4. Enable recommended plugins (see below)

## Recommended Obsidian Plugins

### Core
- **Dataview** — Query-based document views
- **Templater** — Advanced templates
- **Kanban** — Task board visualization

### Optional
- **Calendar** — Date-based navigation
- **Excalidraw** — Visual diagrams
- **Obsidian Git** — Version control

## Directory Structure

```
vault/
├── Songwriting_Guides/    # Practical songwriting references
│   ├── rule_breaking_masterpieces.md
│   └── rule_breaking_practical.md
├── Theory_Reference/      # Deep music theory
├── Production_Workflows/  # DAW-specific techniques
├── Templates/             # Reusable templates
│   └── DAiW_Task_Board.md
└── Data_Files/           # JSON datasets
```

## Tags System

| Tag | Usage |
|-----|-------|
| `#songwriting` | Songwriting guides |
| `#harmony` | Chord/harmonic content |
| `#production` | Production techniques |
| `#borrowed-chords` | Modal mixture content |
| `#emotional-mapping` | Emotion → music mapping |
| `#rhythm` | Timing and groove |
| `#ai-priority` | High priority for AI embedding |

## AI Integration

This vault is optimized for use with:
- **AnythingLLM** — Local AI chat with vault content
- **DAiW CLI** — Command-line music tools

### AnythingLLM Setup
1. Install AnythingLLM
2. Create new workspace
3. Upload vault directory
4. Documents with `ai_priority: high` in frontmatter are prioritized

## Dataview Queries

### All Songwriting Guides
```dataview
TABLE tags, updated
FROM "Songwriting_Guides"
SORT updated DESC
```

### High-Priority AI Documents
```dataview
LIST
FROM ""
WHERE ai_priority = "high"
```

### Tasks by Priority
```dataview
TASK
WHERE !completed
GROUP BY priority
```

## Philosophy

> "The wrong note played with conviction is the right note."

This vault exists to help musicians:
1. Understand WHY rules exist
2. Know WHEN to break them
3. Connect theory to EMOTION
4. Create music that FEELS right, not just sounds "correct"

## Related

- [DAiW Python Package](../README.md)
- [Rule-Breaking Masterpieces](Songwriting_Guides/rule_breaking_masterpieces.md)
- [Practical Guide](Songwriting_Guides/rule_breaking_practical.md)
