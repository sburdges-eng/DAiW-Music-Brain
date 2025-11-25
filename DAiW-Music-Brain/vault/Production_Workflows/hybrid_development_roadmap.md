# Hybrid Development Roadmap: Python Brain + C++ Body

> Python is for Logic. C++ is for Audio. You are building a Logic Engine.

## The Core Insight

You are building a **Logic Engine** (Psychology → Harmony → MIDI). Python is the undisputed king of this domain. Trying to write text parsing, string manipulation, and high-level probability logic in C++ is a waste of life.

The eventual plugin will use a **"Brain in a Box"** architecture where Python does the thinking and C++ does the real-time work.

## Why C++ Would Kill You Right Now

| Task | Python | C++ |
|------|--------|-----|
| Text Processing | `text.split()` | 3 days writing a string splitter |
| UI Prototyping | `st.slider()` | Weeks fighting `lookAndFeel` classes |
| Probability/Matrices | `numpy`, `random` | Raw math or dependency manager hell |
| Iteration Speed | Change → Run | Change → Compile → Link → Run |

**Verdict:** Stay in Python until the Brain is stable.

## The Final Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Logic Pro                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              DAiW Plugin (C++/JUCE)                   │  │
│  │                                                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │  │
│  │  │ GUI         │  │ Audio Pass  │  │ MIDI Output  │  │  │
│  │  │ • Text area │  │ (untouched) │  │ (from Brain) │  │  │
│  │  │ • Chaos     │  │             │  │              │  │  │
│  │  │ • Generate  │  │             │  │              │  │  │
│  │  └─────────────┘  └─────────────┘  └──────────────┘  │  │
│  │         │                                    ▲        │  │
│  │         │ OSC /daiw/generate                 │        │  │
│  │         ▼                                    │        │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │              OSC Bridge (UDP 127.0.0.1)         │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ localhost
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 DAiW Brain (Python)                          │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Therapy     │  │ Harmony     │  │ Groove              │  │
│  │ Session     │→ │ Plan        │→ │ Humanization        │  │
│  │             │  │             │  │                     │  │
│  │ • Affect    │  │ • Chords    │  │ • Gaussian jitter   │  │
│  │ • Intent    │  │ • Key/Mode  │  │ • Velocity curves   │  │
│  │ • Wounds    │  │ • Tensions  │  │ • Drunken drummer   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                              │                               │
│                              ▼                               │
│                    ┌─────────────────┐                      │
│                    │ Note List (JSON)│                      │
│                    │ → OSC /daiw/result                     │
│                    └─────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

## Phase 1: Stabilize the Brain (Python-only)

**Status:** CURRENT PHASE

### Goals
- Freeze the public API
- Ensure programmatic callability (no CLI/UI dependency)
- Return serializable structures

### The Stable API

```python
def generate_session(
    text: str,
    motivation: str,
    chaos: float,        # 0.0 - 1.0
    vulnerability: float # 0.0 - 1.0
) -> dict:
    """
    Generate a complete musical response from emotional input.

    Returns:
        {
            "tempo": 120,
            "key": "F",
            "mode": "major",
            "time_sig": (4, 4),
            "notes": [
                {
                    "pitch": 60,        # MIDI note number
                    "start_ms": 0.0,    # Start time in milliseconds
                    "duration_ms": 500, # Duration in milliseconds
                    "velocity": 100     # 0-127
                },
                ...
            ],
            "harmony_plan": {...},      # Optional: full plan for debugging
            "affect_analysis": {...}    # Optional: emotional breakdown
        }
    """
```

### Checklist
- [ ] `generate_session()` works without UI
- [ ] Returns valid JSON-serializable dict
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Can be imported: `from music_brain import generate_session`

## Phase 2: Python OSC Server

### Goals
- Create standalone brain server
- Test communication without C++
- Validate message format

### File: `brain_server.py`

```python
"""
DAiW Brain Server - Listens for generation requests via OSC.

Run with: python brain_server.py
Listens on: 127.0.0.1:9000
Responds to: 127.0.0.1:9001
"""

from pythonosc import dispatcher, osc_server, udp_client
import json
import threading

# Import your brain
from music_brain import generate_session

class BrainServer:
    def __init__(self, listen_port=9000, reply_port=9001):
        self.listen_port = listen_port
        self.reply_client = udp_client.SimpleUDPClient("127.0.0.1", reply_port)

        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map("/daiw/generate", self.handle_generate)

    def handle_generate(self, address, *args):
        """
        Expected args: text, motivation, chaos, vulnerability
        """
        text = args[0] if len(args) > 0 else ""
        motivation = args[1] if len(args) > 1 else "exploration"
        chaos = args[2] if len(args) > 2 else 0.5
        vulnerability = args[3] if len(args) > 3 else 0.5

        # Call the brain
        result = generate_session(text, motivation, chaos, vulnerability)

        # Send response
        self.reply_client.send_message("/daiw/result", json.dumps(result))

    def start(self):
        server = osc_server.ThreadingOSCUDPServer(
            ("127.0.0.1", self.listen_port),
            self.dispatcher
        )
        print(f"Brain listening on port {self.listen_port}")
        server.serve_forever()

if __name__ == "__main__":
    BrainServer().start()
```

### Test Client (No C++ needed)

```python
"""Test the brain server without JUCE."""
from pythonosc import udp_client
import time

client = udp_client.SimpleUDPClient("127.0.0.1", 9000)
client.send_message("/daiw/generate", [
    "I lost someone I loved",  # text
    "grief",                    # motivation
    0.3,                        # chaos
    0.8                         # vulnerability
])
print("Sent generation request")
```

### Checklist
- [ ] `brain_server.py` starts without errors
- [ ] Test client can send messages
- [ ] Brain processes and responds
- [ ] Response is valid JSON

## Phase 3: JUCE Plugin Skeleton

### Goals
- Prove toolchain works
- Build minimal plugin shell
- Test in Logic Pro

### What the Skeleton Does
1. **Audio:** Passes through unchanged (no processing)
2. **UI:** Placeholder elements
   - Text area (disabled for now)
   - "Generate" button (does nothing yet)
   - "Chaos" slider (does nothing yet)
3. **MIDI:** Outputs a fixed test pattern on button press

### Verification Steps
1. Plugin builds as AU and VST3
2. Plugin appears in Logic Pro
3. Audio passes through without glitches
4. Test MIDI pattern plays when triggered

### Checklist
- [ ] JUCE installed and Projucer works
- [ ] Plugin compiles without errors
- [ ] AU validation passes
- [ ] Shows up in Logic Pro
- [ ] Audio passthrough works
- [ ] Fixed MIDI test works

## Phase 4: Wire OSC Bridge

### Goals
- Connect C++ and Python
- Real generation flow working
- DAiW is functional inside Logic

### JUCE Side

```cpp
// On Generate button click
void generateButtonClicked()
{
    juce::String text = textEditor.getText();
    float chaos = chaosSlider.getValue();
    float vulnerability = vulnerabilitySlider.getValue();

    juce::OSCMessage msg("/daiw/generate");
    msg.addString(text);
    msg.addString("exploration");  // motivation
    msg.addFloat32(chaos);
    msg.addFloat32(vulnerability);

    oscSender.send(msg);
}

// On receiving result
void oscMessageReceived(const juce::OSCMessage& msg) override
{
    if (msg.getAddressPattern() == "/daiw/result")
    {
        juce::String json = msg[0].getString();
        parseAndScheduleMidi(json);
    }
}
```

### The Complete Flow
1. User types in text area, adjusts knobs
2. User clicks "Generate"
3. Plugin sends OSC to Python brain
4. Python processes, returns note data
5. Plugin parses JSON into `MidiMessage` objects
6. Plugin schedules messages in `MidiBuffer`
7. Logic receives MIDI, plays instruments

### Checklist
- [ ] OSC sender/receiver work in JUCE
- [ ] Brain receives requests
- [ ] Brain responds with notes
- [ ] Plugin parses response
- [ ] MIDI plays in Logic
- [ ] End-to-end latency acceptable (<500ms)

## What Gets Ported to C++ (Later)

### Port if real-time needed:
- **Groove/humanization** — For real-time humanization of live MIDI input
- **Subset of Harmony** — For "play pad, get chords" real-time features

### Never port:
- NLP / therapy logic
- Lyric mirror
- Affect analysis
- High-level intent processing

### Porting strategy:
1. Take stable, well-tested math from Python
2. Re-implement as small, deterministic C++ functions
3. Leave heavy logic in Python

## Current Status

| Component | Status | File |
|-----------|--------|------|
| Comprehensive Engine | Gold Master | `comprehensive_engine.py` |
| Groove/Humanization | Working | `render_plan_to_midi` |
| UI (Streamlit) | Working | `app.py` |
| Native Wrapper | Working | `launcher.py` |
| PyInstaller Build | Working | `daiw.spec` |
| Brain Server | TODO | `brain_server.py` |
| JUCE Plugin | TODO | `cpp/DAiWBridge/` |

## Orders

1. **Stop planning. Start compiling.**
2. Inject finalized code into repo
3. Verify: `pytest tests/ -v`
4. Visualize: `python launcher.py`
5. Freeze: `pyinstaller daiw.spec`

**Go build your Creative Companion.**

## Tags

#roadmap #architecture #python #cpp #juce #osc #phases #engineering
