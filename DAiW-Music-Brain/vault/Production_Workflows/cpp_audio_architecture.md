# C++ Audio Architecture for DAiW

> This is the pivot point where you stop writing a Script and start building an Engine.

## The Hybrid Model

DAiW uses a **Brain/Body split**:

| Component | Language | Role |
|-----------|----------|------|
| **Brain** | Python | Therapy logic, NLP, harmony generation, intent processing |
| **Body** | C++ | Real-time audio, plugin UI, DAW integration |

```
┌─────────────────────────────────────────────────────────┐
│                    Logic Pro / DAW                       │
│  ┌─────────────────────────────────────────────────┐    │
│  │           DAiW Plugin (C++/JUCE)                │    │
│  │  ┌─────────┐  ┌──────────┐  ┌──────────────┐   │    │
│  │  │ UI/Knobs│  │Audio Pass│  │ OSC Client   │   │    │
│  │  └─────────┘  └──────────┘  └──────┬───────┘   │    │
│  └────────────────────────────────────┼───────────┘    │
└───────────────────────────────────────┼────────────────┘
                                        │ OSC (UDP)
                                        ▼
                    ┌───────────────────────────────┐
                    │      DAiW Brain (Python)      │
                    │  ┌─────────┐  ┌───────────┐   │
                    │  │ Intent  │  │ Harmony   │   │
                    │  │ Schema  │  │ Generator │   │
                    │  └─────────┘  └───────────┘   │
                    │  ┌─────────┐  ┌───────────┐   │
                    │  │ Therapy │  │ Groove    │   │
                    │  │ Engine  │  │ Engine    │   │
                    │  └─────────┘  └───────────┘   │
                    └───────────────────────────────┘
```

## Why Python Cannot Do Real-Time Audio

### 1. The Garbage Collector Problem

**Audio Reality:** CPU must deliver 128 samples every **2.9 milliseconds**. Miss by 0.0001ms = crackle/pop.

**Python Problem:** Garbage Collector pauses program for **5-20ms** periodically.

**Result:** 20ms pause = catastrophic audio glitch.

**C++ Solution:** Manual memory management. You decide when to clean up (never during audio callback).

### 2. The GIL (Global Interpreter Lock)

**Audio Reality:** Plugins need dedicated high-priority audio thread.

**Python Problem:** Only one thread runs at a time. If Python is processing therapy text, audio thread blocks.

**C++ Solution:** True multi-threading. UI on Core 1, Audio on Core 2, never block each other.

### 3. Pointer Indirection (Speed)

**The Math:** Volume change = multiply 44,100 numbers per second.

| Language | Operation |
|----------|-----------|
| Python | Check type → Check permissions → Read → Multiply |
| C++ | Direct memory access → Multiply |

**Result:** C++ is **50-100x faster** for raw loop math.

## The C++ Arsenal

### 1. JUCE (Framework)

**What:** Industry standard. 95% of plugins (Neural DSP, Arturia, Valhalla) use JUCE.

**Why:**
- Handles Mac/Windows/VST/AU/AAX export from one codebase
- Manipulates raw audio samples 44,100 times/second
- Logic's Scripter only handles MIDI; JUCE handles audio

**Links:**
- https://juce.com/
- https://docs.juce.com/

### 2. DSP Libraries (Maximilian / Gamma)

**What:** Pre-built audio math. Oscillators, filters, delays, FFTs.

**Why:**
- Writing a high-pass filter from scratch = complex calculus
- With library: `filter.cutoff = 500;`
- Build weird filters that react to Vulnerability variable

**Links:**
- Maximilian: https://github.com/micknoise/Maximilian
- Gamma: https://github.com/LancePutnam/Gamma

### 3. OSC (Open Sound Control)

**What:** Protocol for sending data over local network (UDP).

**Why:**
- Logic cannot talk to Python natively
- OSC is the invisible wire connecting Brain (Python) to Body (C++)
- Low latency, flexible message format

**Links:**
- liblo (C++): https://github.com/radarsat1/liblo
- python-osc: https://github.com/attwad/python-osc

## The Data Flow

```
User clicks "Generate" in C++ plugin
        │
        ▼
Plugin sends OSC message to Python
        │
        ▼
Python processes intent → generates harmony
        │
        ▼
Python sends MIDI data back via OSC
        │
        ▼
Plugin receives MIDI → plays notes in DAW
```

## What Lives Where

### Python (Brain) - Keep Building Here
- Intent schema and processing
- Therapy/emotional analysis
- Harmony generation algorithms
- Groove template logic
- NLP and text processing
- Rule-breaking engine

### C++ (Body) - Build Later
- Audio passthrough (no glitches)
- Plugin UI (knobs, buttons)
- OSC client/server
- Real-time parameter automation
- Audio analysis (FFT, transient detection)
- Direct DAW integration

## Development Strategy

1. **Now:** Keep building Python Brain. It's perfect for logic/AI.
2. **Soon:** Learn JUCE basics. Build a simple passthrough plugin.
3. **Later:** Add OSC bridge between Python and C++ plugin.
4. **Future:** Move performance-critical audio processing to C++.

## Tags

#architecture #cpp #juce #audio #realtime #osc
