# Guitar Recording Workflow

## Recording Options

### Option 1: Direct (DI)
```
Guitar → AudioBox iTwo (INST on) → Logic Pro
```
- Clean, flexible signal
- Add amp sim later (Neural Amp Modeler, Logic's stock amps)
- Good for re-amping

### Option 2: Mic'd Amp
```
Guitar → Amp → Mic → AudioBox iTwo → Logic Pro
```
- Captures real amp tone
- Needs good room/isolation
- Commit to sound

### Option 3: Amp + DI (Best of both)
```
Guitar → DI Box → AudioBox iTwo (clean track)
         ↓
        Amp → Mic → AudioBox iTwo (amp track)
```
- Record both simultaneously
- Flexibility to blend or re-amp

---

## AudioBox Settings for Guitar

### Direct Input
```
Input: 1/4" cable from guitar
48V: OFF
INST: ON
Gain: Set so loudest strumming peaks at -12dB
```

### Mic'd Amp
```
Input: XLR from mic
48V: ON if condenser, OFF if dynamic
INST: OFF
Gain: Peaks at -12dB
```

---

## Logic Pro Setup

### Track Setup
1. Create Audio Track (mono for DI, stereo for stereo mics)
2. Input: AudioBox Input 1 or 2
3. Enable "Input Monitoring" to hear yourself
4. Add amp sim if going direct

### Recommended Monitoring Chain (DI)
- Pedalboard or Amp Designer (for tone while playing)
- Keep CPU light

*Note: Record the DI clean, add amp sim after*

---

## Amp Sim Options (Free)

| Plugin | Style |
|--------|-------|
| Neural Amp Modeler | Profile-based, very realistic |
| Logic's Amp Designer | Good variety built-in |
| Logic's Pedalboard | Effects pedals |
| Ignite Amps Emissary | High gain metal |
| LePou Plugins | Classic amp tones |

---

## Double Tracking

For thick rhythm guitar:
1. Record first take (pan hard left)
2. Record second take (pan hard right)
3. Small variations = better width
4. Don't copy/paste — play it twice

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Thin DI sound | Normal — add amp sim |
| Buzzing/hum | Check cables, ground |
| Latency | Reduce buffer or use direct monitoring |
| Clipping on palm mutes | Reduce input gain |
| Phase issues (multi-mic) | Check phase, align waveforms |

---

## EQ Starting Points

| Frequency | Adjustment | Why |
|-----------|------------|-----|
| 80-100 Hz | Cut | Remove rumble |
| 200-400 Hz | Cut if muddy | Clarity |
| 800 Hz-1 kHz | Cut if honky | Remove nasal |
| 2-4 kHz | Boost for presence | Cut through mix |
| 6-8 kHz | Boost for clarity | Pick attack |

---

## Related
- [[Gear/PreSonus AudioBox iTwo]]
- [[Gear/Logic Pro Settings]]
- [[Mixing Workflow Checklist]]

