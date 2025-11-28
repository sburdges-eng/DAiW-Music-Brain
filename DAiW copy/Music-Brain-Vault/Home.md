# 🎵 Music Brain Dashboard

> Your command center for music production.

---

## Quick Actions

| Action | Link |
|--------|------|
| ➕ New Song | [[Templates/Song Template]] |
| 📝 Session Notes | [[Templates/Session Notes Template]] |
| 🎯 Weekly Review | [[Templates/Weekly Review Template]] |
| 🎸 Practice Log | [[Templates/Daily Practice Log Template]] |

---

## 🎼 Songs Overview

### In Progress
```dataview
TABLE WITHOUT ID
  file.link AS "Song",
  status AS "Status",
  key AS "Key",
  bpm AS "BPM"
FROM "Songs"
WHERE type = "song" AND (status = "in-progress" OR status = "mixing" OR status = "recording")
SORT file.mtime DESC
```

### Recently Updated
```dataview
TABLE WITHOUT ID
  file.link AS "Song",
  dateformat(file.mtime, "MMM dd") AS "Modified"
FROM "Songs"
WHERE type = "song"
SORT file.mtime DESC
LIMIT 5
```

### By Status
```dataview
TABLE WITHOUT ID
  status AS "Status",
  length(rows) AS "Count"
FROM "Songs"
WHERE type = "song"
GROUP BY status
```

---

## 📋 Active Projects

```dataview
TABLE WITHOUT ID
  file.link AS "Project",
  status AS "Status",
  priority AS "Priority",
  due_date AS "Due"
FROM "Projects"
WHERE type = "project" AND status != "complete" AND status != "archived"
SORT priority DESC
```

---

## 📅 Recent Activity

```dataview
TABLE WITHOUT ID
  file.link AS "Note",
  file.folder AS "Folder",
  dateformat(file.mtime, "MMM dd HH:mm") AS "Modified"
FROM ""
WHERE file.name != "Home"
SORT file.mtime DESC
LIMIT 10
```

---

## ✅ Open Tasks

```dataview
TASK
FROM "Songs" OR "Projects" OR "Workflows"
WHERE !completed
LIMIT 15
```

---

## 📊 Stats

### Song Count by Status
```dataview
TABLE WITHOUT ID
  status AS "Status",
  length(rows) AS "Songs"
FROM "Songs"
WHERE type = "song"
GROUP BY status
```

### Content Overview
| Type | Count |
|------|-------|
| Songs | `$= dv.pages('"Songs"').where(p => p.type == "song").length` |
| Workflows | `$= dv.pages('"Workflows"').length` |
| Gear Notes | `$= dv.pages('"Gear"').length` |

---

## 🔗 Quick Links

### Workflows
- [[Workflows/Vocal Recording Workflow]]
- [[Workflows/Guitar Recording Workflow]]
- [[Workflows/Mixing Workflow Checklist]]
- [[Workflows/Mastering Checklist]]

### Gear
- [[Gear/PreSonus AudioBox iTwo]]
- [[Gear/Logic Pro Settings]]
- [[Gear/Free Plugins Reference]]

### Reference
- [[Theory/Music Theory Vocabulary]]
- [[Theory/Audio Recording Vocabulary]]

### System
- [[AI-System/AI Assistant Setup Guide]]
- [[AI-System/Obsidian Templates Guide]]
- [[AI-System/Dataview Queries Reference]]
- [[AI-System/Tags System]]

---

## 📁 Folder Navigation

| Folder | Description |
|--------|-------------|
| [[Songs/]] | Song projects |
| [[Workflows/]] | Process documentation |
| [[Gear/]] | Equipment & plugins |
| [[Theory/]] | Reference materials |
| [[Samples-Library/]] | Sample catalog |
| [[Projects/]] | Non-song projects |
| [[Templates/]] | Note templates |
| [[AI-System/]] | System docs & tools |

---

## 🎯 This Week's Focus

*Edit this section manually each week:*

### Priority #1


### Priority #2


### Priority #3


---

## 💡 Capture Box

*Quick ideas — move to proper notes later:*

- 
- 
- 

---

*Last updated: `= date(today)`*

