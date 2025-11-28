# Dataview Queries Reference

Copy-paste ready queries for your Music Brain vault.

---

## Installation

1. Settings → Community Plugins → Browse
2. Search "Dataview"
3. Install and Enable
4. Settings → Dataview → Enable JavaScript Queries (optional)

---

## Query Types

| Type | Use Case |
|------|----------|
| `TABLE` | Display data in columns |
| `LIST` | Simple bullet list |
| `TASK` | Show tasks/checkboxes |
| `CALENDAR` | Calendar view by date |

---

## Songs Queries

### All Songs
```dataview
TABLE status, key, bpm, genre
FROM "Songs"
WHERE type = "song"
SORT file.mtime DESC
```

### Songs In Progress
```dataview
TABLE key, bpm, file.mtime AS "Last Modified"
FROM "Songs"
WHERE status = "in-progress"
SORT file.mtime DESC
```

### Songs by Status
```dataview
TABLE WITHOUT ID
  status AS "Status",
  length(rows) AS "Count",
  rows.file.link AS "Songs"
FROM "Songs"
WHERE type = "song"
GROUP BY status
```

### Songs by Key
```dataview
TABLE WITHOUT ID
  key AS "Key",
  length(rows) AS "Count"
FROM "Songs"
WHERE key
GROUP BY key
SORT length(rows) DESC
```

### Songs Missing Info
```dataview
LIST
FROM "Songs"
WHERE type = "song" AND (!key OR !bpm)
```

### Recently Modified Songs
```dataview
TABLE file.mtime AS "Modified", status
FROM "Songs"
SORT file.mtime DESC
LIMIT 10
```

---

## Gear Queries

### All Gear
```dataview
TABLE category, manufacturer
FROM "Gear"
WHERE type = "gear"
SORT category
```

### Plugins by Category
```dataview
TABLE WITHOUT ID
  category AS "Category",
  rows.file.link AS "Plugins"
FROM "Gear"
WHERE type = "plugin"
GROUP BY category
```

### Plugins by Rating
```dataview
TABLE rating, category, developer
FROM "Gear"
WHERE type = "plugin" AND rating
SORT rating DESC
```

---

## Workflow Queries

### All Workflows
```dataview
LIST
FROM "Workflows"
WHERE type = "workflow"
SORT file.name
```

### Workflows with Tasks
```dataview
TASK
FROM "Workflows"
WHERE !completed
```

---

## Session Queries

### Recent Sessions
```dataview
TABLE date, project, duration_hours
FROM ""
WHERE type = "session"
SORT date DESC
LIMIT 10
```

### Sessions by Project
```dataview
TABLE WITHOUT ID
  project AS "Project",
  length(rows) AS "Sessions",
  sum(rows.duration_hours) AS "Total Hours"
FROM ""
WHERE type = "session"
GROUP BY project
```

### Total Recording Time
```dataview
TABLE WITHOUT ID
  sum(rows.duration_hours) AS "Total Hours"
FROM ""
WHERE type = "session"
```

---

## Practice Log Queries

### Recent Practice
```dataview
TABLE date, duration_minutes, instrument, focus
FROM ""
WHERE type = "practice"
SORT date DESC
LIMIT 7
```

### Practice Time This Week
```dataview
TABLE WITHOUT ID
  sum(rows.duration_minutes) AS "Total Minutes This Week"
FROM ""
WHERE type = "practice" AND date >= date(today) - dur(7 days)
```

### Practice by Instrument
```dataview
TABLE WITHOUT ID
  instrument AS "Instrument",
  length(rows) AS "Sessions",
  sum(rows.duration_minutes) AS "Total Minutes"
FROM ""
WHERE type = "practice"
GROUP BY instrument
```

---

## Project Queries

### Active Projects
```dataview
TABLE status, priority, due_date
FROM "Projects"
WHERE type = "project" AND status != "complete"
SORT priority DESC
```

### Overdue Projects
```dataview
TABLE due_date, priority
FROM "Projects"
WHERE type = "project" AND due_date < date(today) AND status != "complete"
SORT due_date
```

### Projects by Status
```dataview
TABLE WITHOUT ID
  status AS "Status",
  length(rows) AS "Count"
FROM "Projects"
WHERE type = "project"
GROUP BY status
```

---

## Tag Queries

### All Notes with Tag
```dataview
LIST
FROM #status/in-progress
```

### Count by Tag
```dataview
TABLE WITHOUT ID
  length(rows) AS "Count"
FROM #type/song
```

---

## Learning Queries

### Topics by Confidence
```dataview
TABLE confidence, category
FROM ""
WHERE type = "learning"
SORT confidence ASC
```

### Topics to Review
```dataview
LIST
FROM ""
WHERE type = "learning" AND confidence < 3
```

---

## Reference Track Queries

### All References
```dataview
TABLE artist, genre, bpm, key
FROM ""
WHERE type = "reference"
SORT artist
```

### References by Genre
```dataview
TABLE WITHOUT ID
  genre AS "Genre",
  rows.file.link AS "Tracks"
FROM ""
WHERE type = "reference"
GROUP BY genre
```

---

## Sample Pack Queries

### All Sample Packs
```dataview
TABLE developer, rating, price
FROM ""
WHERE type = "sample-pack"
SORT rating DESC
```

### Top Rated Packs
```dataview
TABLE developer, genre
FROM ""
WHERE type = "sample-pack" AND rating >= 4
SORT rating DESC
```

---

## Collaboration Queries

### Active Collaborations
```dataview
TABLE collaborator, project, status
FROM ""
WHERE type = "collaboration" AND status = "active"
```

---

## Dashboard Queries

### Quick Stats Dashboard
```dataview
TABLE WITHOUT ID
  "Songs" AS "Type",
  length(filter(file.lists, (x) => x)) AS "Count"
FROM "Songs"
WHERE type = "song"
```

### Activity Summary
```dataview
TABLE WITHOUT ID
  dateformat(file.mtime, "yyyy-MM-dd") AS "Date",
  file.link AS "Note",
  file.folder AS "Folder"
FROM ""
SORT file.mtime DESC
LIMIT 15
```

---

## Advanced Queries

### Notes Modified Today
```dataview
LIST
FROM ""
WHERE file.mday = date(today)
```

### Notes Created This Month
```dataview
LIST
FROM ""
WHERE file.cday >= date(today) - dur(30 days)
SORT file.cday DESC
```

### Orphan Notes (No Links)
```dataview
LIST
FROM ""
WHERE length(file.inlinks) = 0 AND length(file.outlinks) = 0
```

### Most Linked Notes
```dataview
TABLE length(file.inlinks) AS "Incoming Links"
FROM ""
SORT length(file.inlinks) DESC
LIMIT 10
```

---

## Inline Queries

Use these within regular text:

### Count Songs
```
I have `= length(filter(dv.pages('"Songs"'), (p) => p.type = "song"))` songs in my vault.
```

### Today's Date
```
Today is `= date(today)`.
```

### Days Until Due
```
`= dateformat(this.due_date, "yyyy-MM-dd")` - `= (this.due_date - date(today)).days` days away
```

---

## Query Syntax Reference

### FROM Clause
```
FROM "Folder"              - specific folder
FROM #tag                  - notes with tag
FROM [[Note]]              - linked from note
FROM ""                    - all notes
```

### WHERE Clause
```
WHERE field = "value"      - exact match
WHERE field != "value"     - not equal
WHERE contains(field, "x") - contains text
WHERE field > 100          - comparison
WHERE field                - field exists
WHERE !field               - field doesn't exist
WHERE field AND field2     - multiple conditions
WHERE field OR field2      - either condition
```

### SORT Clause
```
SORT field                 - ascending
SORT field DESC            - descending
SORT field ASC             - explicit ascending
```

### Other
```
LIMIT 10                   - max results
FLATTEN field              - expand arrays
GROUP BY field             - group results
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No results | Check folder path spelling |
| Property not showing | Ensure frontmatter is valid YAML |
| Dates not working | Use format: `YYYY-MM-DD` |
| Query errors | Check syntax, commas, quotes |

---

## Related
- [[Obsidian Templates Guide]]
- [[Tags System]]

