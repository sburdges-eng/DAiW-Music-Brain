# Tags System

Consistent tagging makes your vault searchable and queryable.

---

## How to Use Tags

### In Frontmatter (Recommended)
```yaml
---
tags:
  - type/song
  - status/in-progress
  - genre/rock
---
```

### Inline
```markdown
This is about #mixing and #compression.
```

### Best Practice
Use frontmatter for structured tags, inline for ad-hoc connections.

---

## Tag Hierarchy

### By Type
What kind of note is this?

| Tag | Use For |
|-----|---------|
| `#type/song` | Song project notes |
| `#type/workflow` | Process documentation |
| `#type/gear` | Equipment notes |
| `#type/plugin` | Plugin reviews |
| `#type/reference` | Reference track analysis |
| `#type/session` | Recording session notes |
| `#type/practice` | Practice logs |
| `#type/project` | Non-song projects |
| `#type/learning` | Learning topics |
| `#type/collaboration` | Collaboration notes |
| `#type/sample-pack` | Sample pack reviews |
| `#type/sound-design` | Sound design patches |
| `#type/mix-notes` | Mix documentation |

---

### By Status
Where is this in the process?

| Tag | Meaning |
|-----|---------|
| `#status/idea` | Initial concept |
| `#status/planning` | Being planned |
| `#status/in-progress` | Actively working |
| `#status/recording` | In recording phase |
| `#status/mixing` | In mixing phase |
| `#status/mastering` | In mastering |
| `#status/review` | Awaiting feedback |
| `#status/complete` | Finished |
| `#status/on-hold` | Paused |
| `#status/archived` | Shelved/old |

---

### By Genre
Musical style/genre.

| Tag | Genre |
|-----|-------|
| `#genre/rock` | Rock |
| `#genre/pop` | Pop |
| `#genre/electronic` | Electronic/EDM |
| `#genre/ambient` | Ambient |
| `#genre/folk` | Folk/Acoustic |
| `#genre/jazz` | Jazz |
| `#genre/blues` | Blues |
| `#genre/country` | Country |
| `#genre/hip-hop` | Hip-Hop/Rap |
| `#genre/rnb` | R&B/Soul |
| `#genre/metal` | Metal |
| `#genre/classical` | Classical |
| `#genre/experimental` | Experimental |
| `#genre/lo-fi` | Lo-Fi |

---

### By Key
Musical key of the piece.

**Major Keys:**
`#key/C` `#key/Db` `#key/D` `#key/Eb` `#key/E` `#key/F` 
`#key/Gb` `#key/G` `#key/Ab` `#key/A` `#key/Bb` `#key/B`

**Minor Keys:**
`#key/Cm` `#key/Dbm` `#key/Dm` `#key/Ebm` `#key/Em` `#key/Fm`
`#key/Gbm` `#key/Gm` `#key/Abm` `#key/Am` `#key/Bbm` `#key/Bm`

---

### By Tempo Range
Approximate speed.

| Tag | BPM Range |
|-----|-----------|
| `#tempo/very-slow` | Under 60 BPM |
| `#tempo/slow` | 60-80 BPM |
| `#tempo/mid` | 80-120 BPM |
| `#tempo/fast` | 120-150 BPM |
| `#tempo/very-fast` | 150+ BPM |

---

### By Instrument
Primary instruments involved.

| Tag | Instrument |
|-----|------------|
| `#inst/guitar` | Guitar (any type) |
| `#inst/acoustic-guitar` | Acoustic guitar |
| `#inst/electric-guitar` | Electric guitar |
| `#inst/bass` | Bass guitar |
| `#inst/drums` | Drums/percussion |
| `#inst/keys` | Keyboard/piano |
| `#inst/synth` | Synthesizer |
| `#inst/vocals` | Vocals |
| `#inst/strings` | Strings |
| `#inst/brass` | Brass |
| `#inst/woodwinds` | Woodwinds |

---

### By Tool/DAW
Software or hardware used.

| Tag | Tool |
|-----|------|
| `#tool/logic-pro` | Logic Pro |
| `#tool/ableton` | Ableton Live |
| `#tool/pro-tools` | Pro Tools |
| `#tool/garageband` | GarageBand |
| `#tool/alchemy` | Logic's Alchemy synth |
| `#tool/vital` | Vital synth |

---

### By Priority
Importance level.

| Tag | Priority |
|-----|----------|
| `#priority/urgent` | Do immediately |
| `#priority/high` | Do soon |
| `#priority/medium` | Normal |
| `#priority/low` | When time permits |
| `#priority/someday` | Maybe later |

---

### By Mood/Vibe
Emotional quality.

| Tag | Mood |
|-----|------|
| `#mood/energetic` | High energy |
| `#mood/chill` | Relaxed |
| `#mood/dark` | Dark/moody |
| `#mood/happy` | Upbeat/positive |
| `#mood/sad` | Melancholic |
| `#mood/aggressive` | Intense |
| `#mood/dreamy` | Ethereal |
| `#mood/epic` | Grand/cinematic |

---

### Utility Tags

| Tag | Use |
|-----|-----|
| `#favorite` | Personal favorites |
| `#needs-review` | Needs attention |
| `#needs-info` | Missing information |
| `#example` | Example/template |
| `#reference` | Reference material |
| `#archive` | Archived/inactive |

---

## Tag Best Practices

### Do
- Use lowercase: `#type/song` not `#Type/Song`
- Use hyphens for multi-word: `#in-progress` not `#in_progress`
- Be consistent — pick one tag and stick with it
- Use hierarchy with `/` for organization
- Keep tags focused and specific

### Don't
- Over-tag (3-5 tags per note is usually enough)
- Create duplicate tags (`#rock` and `#genre/rock`)
- Use spaces in tags
- Make tags too specific (`#guitar-solo-in-bridge`)

---

## Searching by Tag

### In Obsidian
- Click any tag to see all notes with that tag
- Use search: `tag:#status/in-progress`
- Combine: `tag:#type/song tag:#status/mixing`

### In Dataview
```dataview
LIST
FROM #status/in-progress
```

```dataview
TABLE status, key
FROM #type/song AND #genre/rock
```

---

## Tag Maintenance

### Periodic Cleanup
- Review unused tags monthly
- Merge similar tags
- Update old tag schemes

### Finding Unused Tags
Use the "Tag Wrangler" community plugin to manage tags.

---

## Related
- [[Obsidian Templates Guide]]
- [[Dataview Queries Reference]]

