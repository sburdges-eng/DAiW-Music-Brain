# PreSonus AudioBox iTwo

## Overview

- **Type:** USB 2.0 Audio Interface
- **Inputs:** 2 combo XLR/TRS
- **Outputs:** 2 TRS (Main), Headphone
- **Phantom Power:** 48V (both channels)
- **Sample Rates:** Up to 96 kHz
- **Bit Depth:** 24-bit

---

## Front Panel

```
[INPUT 1]     [INPUT 2]     [MIXER]     [PHONES]     [MAIN]
   Gain          Gain      Input/DAW    HP Volume   Main Volume
   
[48V] - Phantom Power Switch (affects both inputs)
[INST 1] [INST 2] - Hi-Z switches for guitar/bass
```

---

## Connections

### Inputs
- **Combo Jacks (1 & 2):** Accept XLR (mic) or 1/4" TRS (line/instrument)
- **INST Switch:** Engage for guitar/bass direct
- **48V:** Enable for condenser microphones

### Outputs
- **Main Outs:** 1/4" TRS balanced to monitors
- **Headphone:** 1/4" TRS stereo

### USB
- USB 2.0 to computer (bus powered)

---

## Optimal Settings

### For Recording Vocals
```
Input: XLR (condenser mic)
48V: ON
INST: OFF
Gain: Loudest part peaks at -12dB in Logic
Mixer: Center or slightly toward Input
```

### For Recording Guitar (Direct)
```
Input: 1/4" from guitar
48V: OFF
INST: ON
Gain: Set for -12dB peaks
Mixer: Center
```

### For Recording Guitar (Amp + Mic)
```
Input: XLR from mic
48V: ON if condenser, OFF if dynamic
INST: OFF
Gain: Set for -12dB peaks
Mixer: Center
```

---

## Logic Pro Audio Settings

### Audio Preferences
```
Output Device: PreSonus AudioBox iTwo
Input Device: PreSonus AudioBox iTwo
Sample Rate: 48000 Hz (or 44100 for CD projects)
Buffer Size: 128 samples (recording) / 256-512 (mixing)
```

### I/O Labels (customize in Audio Preferences)
```
Input 1: Mic/DI 1
Input 2: Mic/DI 2
Output 1-2: Monitors
```

---

## Latency Management

| Buffer Size | Latency | Use Case |
|-------------|---------|----------|
| 32 samples | ~3ms | Not recommended (CPU heavy) |
| 64 samples | ~5ms | Recording if CPU allows |
| 128 samples | ~8ms | Recording (recommended) |
| 256 samples | ~15ms | Mixing with plugins |
| 512 samples | ~25ms | Heavy mixing sessions |
| 1024 samples | ~45ms | Mixing only |

*If you hear latency while recording, use the MIXER knob to blend direct input*

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No sound | Check MAIN knob, Logic output settings |
| No input | Check gain, 48V if condenser, INST if guitar |
| Crackling/pops | Increase buffer size |
| Latency | Decrease buffer size or use direct monitoring |
| Not recognized | Reinstall Universal Control, try different USB port |

---

## Software

- **Universal Control:** PreSonus driver/control panel
- Download: https://www.presonus.com/products/audiobox-itwo

---

## Related
- [[Logic Pro Settings]]
- [[Vocal Recording Workflow]]

