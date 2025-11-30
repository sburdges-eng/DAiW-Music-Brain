# DAiW Roadmap

> Externalized planning to prevent the README from becoming a fantasy novel.

## Current Version: v0.2.x

### Stabilization & Infrastructure

- [x] Core therapy-to-MIDI pipeline
- [x] Tension curve module for emotional contour
- [x] GitHub Actions CI (test, lint, type-check)
- [x] Release workflow for packaging
- [x] Examples folder with quick-start scripts
- [x] Central configuration module
- [x] Domain-specific exceptions
- [ ] Fix pre-existing test failures in bridge integration
- [ ] Improve error messages in render pipeline
- [ ] Add seed control to all random operations

### Documentation

- [x] Audio Vault documentation
- [x] Privacy & Data section
- [x] 5-minute quick start guide
- [ ] API reference (sphinx or mkdocs)
- [ ] Video tutorial: text → MIDI → DAW

---

## v0.3.x: Enhanced Structure Engine

### Structural Intelligence

- [ ] Multi-section arrangement generation (intro, verse, chorus, bridge, outro)
- [ ] Melodic fragment generation from chord progressions
- [ ] Bass line generation with groove integration
- [ ] Drum pattern generation tied to tension curves

### Reference Track Analysis

- [ ] Extract "DNA" from reference tracks (tempo, key, energy curve)
- [ ] Match generated output to reference characteristics
- [ ] A/B comparison tools

### Improved Affect Analysis

- [ ] Expand keyword vocabulary
- [ ] Add sentiment analysis fallback (optional dependency)
- [ ] Multi-language support

---

## v0.4.x: Real-Time Integration

### OSC Bridge

- [ ] OSC server for real-time parameter control
- [ ] Bidirectional communication with DAWs
- [ ] MIDI clock sync

### JUCE Plugin (Experimental)

- [ ] C++ JUCE plugin skeleton
- [ ] Python ↔ JUCE communication layer
- [ ] VST3/AU/AAX builds

### Live Performance Mode

- [ ] Real-time tension curve following
- [ ] MIDI input processing
- [ ] Low-latency generation

---

## v0.5.x: Audio Layer

### Audio Vault Integration

- [ ] Kit selection based on mood
- [ ] Sample processing pipeline
- [ ] Audio export (not just MIDI)

### Audio Analysis

- [ ] Stem separation integration
- [ ] Spectral analysis for mood detection
- [ ] BPM and key detection from audio

---

## Future / Exploratory

### LLM Integration (Optional)

- [ ] Natural language intent parsing
- [ ] Lyric generation assistance
- [ ] Conversational interrogation mode

### Collaboration Features

- [ ] Session export/import
- [ ] Intent sharing format
- [ ] Version control for musical ideas

### DAW-Specific Plugins

- [ ] Logic Pro MIDI FX
- [ ] Ableton Max for Live device
- [ ] FL Studio plugin

---

## Not Planned

The following are explicitly **not** in scope:

- Cloud services or remote processing
- Subscription models
- Telemetry or analytics
- "Finish the song for you" features
- Replacing human creativity

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) (when it exists) for how to help.

Priority areas for contribution:
1. Test coverage
2. Documentation
3. New groove templates
4. Bug fixes

---

## Philosophy Reminder

> "The tool shouldn't finish art for people. It should make them braver."

Every feature should ask: "Does this help the artist explore, or does it replace their exploration?"
