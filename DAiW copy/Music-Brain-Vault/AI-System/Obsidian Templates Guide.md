# Obsidian Templates Guide

Complete guide to creating and using templates in your Music Brain vault.

---

## Why Templates Matter

Templates save time and ensure consistency. Instead of starting from scratch, you:
- Capture the same information every time
- Don't forget important fields
- Build a queryable database of notes
- Maintain consistent structure across your vault

---

## Two Template Systems

### 1. Core Templates (Built-in)
- Simple variable replacement
- No plugin required
- Limited functionality

### 2. Templater Plugin (Recommended)
- Dynamic dates, prompts, logic
- JavaScript support
- Much more powerful

**This guide focuses on Templater** — install it first.

---

## Installing Templater

1. Settings → Community Plugins
2. Turn off Restricted Mode
3. Browse → Search "Templater"
4. Install and Enable
5. Configure:
   - Template folder: `Templates` (or `.templates` in each folder)
   - Trigger on new file: ON
   - Folder Templates: Set defaults per folder

---

## Template Basics

### Frontmatter (Properties)

Every template should start with YAML frontmatter:

```yaml
---
title: "{{title}}"
created: {{date}}
modified: {{date}}
tags:
  - tag1
  - tag2
type: note-type
status: draft
---
```

Frontmatter enables:
- Dataview queries
- Filtering and sorting
- Metadata display
- Graph view filtering

### Templater Variables

| Variable | Output | Example |
|----------|--------|---------|
| `<% tp.date.now() %>` | Current date | 2025-01-15 |
| `<% tp.date.now("YYYY-MM-DD HH:mm") %>` | Date + time | 2025-01-15 14:30 |
| `<% tp.file.title %>` | File name | My Song |
| `<% tp.file.folder() %>` | Current folder | Songs |
| `<% tp.file.cursor() %>` | Cursor position | (places cursor here) |
| `<% tp.system.prompt("Question?") %>` | User prompt | (asks user) |
| `<% tp.file.creation_date() %>` | File created | 2025-01-15 |

### Common Date Formats

| Format | Output |
|--------|--------|
| `YYYY-MM-DD` | 2025-01-15 |
| `YYYY-MM-DD HH:mm` | 2025-01-15 14:30 |
| `dddd, MMMM Do YYYY` | Wednesday, January 15th 2025 |
| `YYYY-[W]WW` | 2025-W03 |
| `MMMM YYYY` | January 2025 |

---

## Template Structure Best Practices

### 1. Start with Frontmatter
```yaml
---
title: "<% tp.file.title %>"
created: <% tp.date.now("YYYY-MM-DD") %>
type: song
status: idea
---
```

### 2. Use Clear Sections
```markdown
## Overview
Key information at a glance

## Details
Expanded information

## Notes
Freeform notes

## Related
Links to other notes
```

### 3. Include Tables for Structured Data
```markdown
| Parameter | Value | Notes |
|-----------|-------|-------|
| | | |
```

### 4. Add Checklists for Processes
```markdown
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3
```

### 5. Use Callouts for Important Info
```markdown
> [!tip] Pro Tip
> Important information here

> [!warning] Watch Out
> Common mistake to avoid

> [!info] Note
> Additional context
```

### 6. End with Related Links
```markdown
## Related
- [[Related Note 1]]
- [[Related Note 2]]
```

---

## Frontmatter Field Types

### Text Fields
```yaml
title: "My Song Title"
artist: "Artist Name"
genre: "Rock"
```

### Date Fields
```yaml
created: 2025-01-15
due: 2025-02-01
```

### Number Fields
```yaml
bpm: 120
duration: 245
rating: 4
```

### Boolean Fields
```yaml
published: true
favorite: false
```

### List Fields
```yaml
tags:
  - rock
  - guitar
  - demo
collaborators:
  - John
  - Jane
```

### Nested Fields
```yaml
audio:
  sample_rate: 48000
  bit_depth: 24
  format: wav
```

---

## Tags Strategy

### Hierarchical Tags
```
#status/idea
#status/in-progress
#status/mixing
#status/complete

#genre/rock
#genre/electronic
#genre/ambient

#type/song
#type/workflow
#type/gear
#type/reference
```

### How to Use
- In frontmatter: `tags: [status/idea, genre/rock]`
- Inline: `#status/idea`
- Both work for searching

---

## Dataview Queries

Dataview lets you query your notes like a database.

### Basic Table
```dataview
TABLE status, bpm, key
FROM "Songs"
SORT file.mtime DESC
```

### Filtered List
```dataview
LIST
FROM #status/in-progress
WHERE type = "song"
```

### Task Query
```dataview
TASK
FROM "Workflows"
WHERE !completed
```

### Group By
```dataview
TABLE rows.file.link AS "Songs"
FROM "Songs"
GROUP BY status
```

### With Calculations
```dataview
TABLE 
  length(rows) AS "Count",
  round(average(rows.bpm)) AS "Avg BPM"
FROM "Songs"
WHERE bpm
GROUP BY genre
```

---

## Linking Strategies

### Direct Links
```markdown
See [[Other Note]] for details.
```

### Aliased Links
```markdown
Check the [[Mixing Workflow Checklist|mixing checklist]].
```

### Block Links
```markdown
Reference this specific section: [[Note#Section]]
```

### Embedded Content
```markdown
![[Other Note]] — embeds entire note
![[Other Note#Section]] — embeds section
![[image.png]] — embeds image
```

---

## Folder Organization

### Option 1: By Type
```
/Songs
/Workflows  
/Gear
/Theory
/Projects
```

### Option 2: By Status
```
/Inbox
/Active
/Archive
```

### Option 3: Hybrid (Recommended)
```
/Songs (by type)
  /Active (by status within)
  /Archive
/Workflows
/Gear
/Reference
```

### Template Locations
- Global: `/Templates/` folder
- Local: `.templates/` in each folder

---

## Advanced Templater Features

### User Prompts
```markdown
Genre: <% tp.system.prompt("What genre?") %>
BPM: <% tp.system.prompt("BPM?") %>
```

### Suggester (Dropdown)
```markdown
Status: <% tp.system.suggester(["idea", "in-progress", "mixing", "complete"], ["idea", "in-progress", "mixing", "complete"]) %>
```

### Conditional Content
```markdown
<%* if (tp.file.folder() === "Songs") { %>
This is a song note.
<%* } else { %>
This is not a song.
<%* } %>
```

### Auto-move Files
```markdown
<%* await tp.file.move("/Songs/" + tp.file.title) %>
```

### Include Other Templates
```markdown
<% tp.file.include("[[Templates/Header]]") %>
```

---

## Template Triggers

### Folder Templates
Set default template per folder:
1. Templater Settings → Folder Templates
2. Add folder path and template

Example:
- `/Songs` → `Song Template`
- `/Workflows` → `Workflow Template`

### Hotkeys
Assign hotkey to insert template:
1. Settings → Hotkeys
2. Search "Templater: Insert template"
3. Assign key (e.g., `Cmd+Shift+T`)

### Command Palette
- `Cmd+P` → "Templater: Insert template"
- Or: "Templater: Create new note from template"

---

## Troubleshooting Templates

| Issue | Solution |
|-------|----------|
| Variables not replacing | Check Templater is enabled |
| Frontmatter not parsing | Ensure `---` on own lines |
| Date format wrong | Check moment.js format string |
| Template not found | Check template folder setting |
| Cursor not placing | Use `<% tp.file.cursor() %>` |

---

## Related
- [[Dataview Queries Reference]]
- [[Tags System]]
- [[Songs/.templates/Song Template]]
- [[Workflows/.templates/Workflow Template]]

