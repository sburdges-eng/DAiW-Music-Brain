# Penta-Core Integration

## Overview

This document describes the integration between DAiW-Music-Brain (Python) and [penta-core](https://github.com/sburdges-eng/penta-core) (C++/JUCE).

The integration follows DAiW-Music-Brain's core philosophy of **"Interrogate Before Generate"** - ensuring that emotional intent drives technical decisions throughout the integration.

### Architecture: Brain in a Box

```
┌─────────────────────────────────────────────────────────────────┐
│                         DAW (Logic, Ableton, etc.)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │               C++ Plugin (penta-core / JUCE)             │   │
│  │                                                         │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │   │
│  │  │   Side A    │    │   Bridge    │    │   Side B    │ │   │
│  │  │  Audio DSP  │◄───│   Layer     │───►│  UI/Logic   │ │   │
│  │  │ (Realtime)  │    │ (pybind11/  │    │  (Python)   │ │   │
│  │  │             │    │    OSC)     │    │             │ │   │
│  │  └─────────────┘    └──────┬──────┘    └─────────────┘ │   │
│  │                            │                           │   │
│  └────────────────────────────┼───────────────────────────┘   │
│                               │                               │
└───────────────────────────────┼───────────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   DAiW-Music-Brain    │
                    │   (Python Package)    │
                    │                       │
                    │  • Intent Processing  │
                    │  • Emotional Analysis │
                    │  • Chord Diagnosis    │
                    │  • Groove Templates   │
                    └───────────────────────┘
```

### Philosophy Alignment

- **Emotional intent first**: Any data exchange with penta-core should preserve and respect the emotional context established in Phase 0 (Core Wound/Desire)
- **Rule-breaking with justification**: When technical constraints from penta-core conflict with emotional intent, the integration should support intentional rule-breaking with proper justification
- **Teaching over automation**: The integration should expose learning opportunities, not just automate away complexity

---

## Phase 3 Integration Points

> **Reference**: [Issue #14 - DAW-ready C++ Migration & Bridge Layer](https://github.com/sburdges-eng/DAiW-Music-Brain/issues/14)

### Bridge Layer Options

| Bridge Type | Use Case | Latency | Complexity |
|-------------|----------|---------|------------|
| **pybind11** | Direct Python/C++ interop | Low | Medium |
| **OSC** | Real-time audio-safe messaging | Very Low | Low |
| **Hybrid** | Data via pybind11, signals via OSC | Optimal | High |

### Recommended: Hybrid Approach

```python
from music_brain.integrations import CppBridge, OSCBridge, CppBridgeConfig, BridgeType

# Configure hybrid bridge
config = CppBridgeConfig(
    bridge_type=BridgeType.HYBRID,
    osc_send_port=9001,      # Python → C++
    osc_receive_port=9000,   # C++ → Python
)

# pybind11 for heavy data (intents, progressions)
cpp_bridge = CppBridge(config=config)

# OSC for real-time signals (MIDI triggers, param updates)
osc_bridge = OSCBridge(config=config)
```

---

## API Interface Points

### High-Level Integration API

The `PentaCoreIntegration` class provides a simplified interface:

```python
from music_brain.integrations import PentaCoreIntegration, PentaCoreConfig

config = PentaCoreConfig(
    endpoint_url="http://localhost:8000",
    timeout_seconds=30,
)

integration = PentaCoreIntegration(config=config)

# Connect and send data
if integration.connect():
    result = integration.send_intent(complete_song_intent)
    suggestions = integration.receive_suggestions()
```

### Outbound (DAiW-Music-Brain → Penta-Core)

| Interface | Description | Data Type |
|-----------|-------------|-----------|
| `send_intent` | Share song intent/emotional context | `CompleteSongIntent` |
| `send_groove` | Share extracted groove templates | `GrooveTemplate` |
| `send_analysis` | Share chord progression analysis | `ProgressionDiagnosis` |

### Inbound (Penta-Core → DAiW-Music-Brain)

| Interface | Description | Data Type |
|-----------|-------------|-----------|
| `receive_feedback` | Receive processing feedback | `dict` |
| `receive_suggestions` | Receive creative suggestions | `list[str]` |

---

## C++/pybind11 Bridge Layer

### Python-Side Interface

The `CppBridge` class mirrors the C++ `PythonBridge` class:

```python
from music_brain.integrations import CppBridge, KnobState, MidiBuffer

bridge = CppBridge()

# Initialize with paths to music_brain and genre definitions
bridge.initialize(
    python_path="/path/to/music_brain",
    genres_json_path="/path/to/genres.json"
)

# Call into C++ for MIDI generation
knobs = KnobState(
    grid=16.0,
    gate=0.8,
    swing=0.55,
    chaos=0.5,
    complexity=0.6
)

result: MidiBuffer = bridge.call_imidi(knobs, "sad piano with rain feeling")

# Check result
if result.success:
    for event in result.events:
        print(f"MIDI: {event.status} {event.data1} {event.data2}")
```

### C++-Side Interface (iDAW_Core/include/PythonBridge.h)

The C++ side exposes these structures via pybind11:

```cpp
PYBIND11_MODULE(idaw_bridge, m) {
    // KnobState - UI control values
    py::class_<iDAW::KnobState>(m, "KnobState")
        .def(py::init<>())
        .def_readwrite("grid", &iDAW::KnobState::grid)
        .def_readwrite("gate", &iDAW::KnobState::gate)
        .def_readwrite("swing", &iDAW::KnobState::swing)
        .def_readwrite("chaos", &iDAW::KnobState::chaos)
        .def_readwrite("complexity", &iDAW::KnobState::complexity);

    // MidiEvent - individual MIDI message
    py::class_<iDAW::MidiEvent>(m, "MidiEvent")
        .def(py::init<>())
        .def_readwrite("status", &iDAW::MidiEvent::status)
        .def_readwrite("data1", &iDAW::MidiEvent::data1)
        .def_readwrite("data2", &iDAW::MidiEvent::data2)
        .def_readwrite("timestamp", &iDAW::MidiEvent::timestamp);

    // MidiBuffer - collection of events with metadata
    py::class_<iDAW::MidiBuffer>(m, "MidiBuffer")
        .def(py::init<>())
        .def_readwrite("events", &iDAW::MidiBuffer::events)
        .def_readwrite("suggested_chaos", &iDAW::MidiBuffer::suggestedChaos)
        .def_readwrite("suggested_complexity", &iDAW::MidiBuffer::suggestedComplexity);
}
```

### Ghost Hands Feature

The C++ layer can suggest UI knob adjustments based on AI analysis:

```python
def on_ghost_hands(chaos: float, complexity: float):
    """Called when C++ suggests new knob values."""
    print(f"AI suggests: chaos={chaos:.2f}, complexity={complexity:.2f}")
    # Update UI knobs with animation

bridge.set_ghost_hands_callback(on_ghost_hands)
```

### Rejection Protocol

Track user rejections to trigger innovation mode:

```python
# User rejects generated content
bridge.register_rejection()

# After 3 rejections, trigger innovation
if bridge.should_trigger_innovation():
    print("Triggering innovation mode...")
    bridge.reset_rejection_counter()
```

---

## OSC Communication Layer

### Protocol Overview

OSC (Open Sound Control) provides real-time, audio-thread-safe messaging:

```
┌─────────────────────┐          UDP          ┌─────────────────────┐
│   C++ Plugin        │                       │   Python Brain      │
│                     │                       │                     │
│  OSC Sender ────────┼───► Port 9000 ───────►│  OSC Server        │
│                     │                       │                     │
│  OSC Receiver ◄─────┼───◄ Port 9001 ◄──────┼  OSC Client        │
│                     │                       │                     │
└─────────────────────┘                       └─────────────────────┘
```

### Message Protocol

#### Plugin → Python (Port 9000)

| Address | Arguments | Description |
|---------|-----------|-------------|
| `/daiw/generate` | `float chaos, float vulnerability` | Request generation |
| `/daiw/set_intent` | `string json` | Update full intent |
| `/daiw/ping` | (none) | Health check |
| `/daiw/param` | `string name, float value` | Parameter change |

#### Python → Plugin (Port 9001)

| Address | Arguments | Description |
|---------|-----------|-------------|
| `/daiw/midi/note` | `int note, int velocity, int duration_ms` | Single note |
| `/daiw/midi/chord` | `int[] notes, int velocity, int duration_ms` | Chord |
| `/daiw/progression` | `string json` | Full progression data |
| `/daiw/status` | `string message` | Status update |
| `/daiw/pong` | (none) | Ping response |

### Python OSC Implementation

```python
from music_brain.integrations import OSCBridge, CppBridgeConfig, BridgeType

config = CppBridgeConfig(
    bridge_type=BridgeType.OSC,
    osc_host="127.0.0.1",
    osc_send_port=9001,
    osc_receive_port=9000,
)

osc = OSCBridge(config=config)

# Register handlers for incoming messages
def on_generate(chaos: float, vulnerability: float):
    print(f"Generate request: chaos={chaos}, vulnerability={vulnerability}")
    # Process and return MIDI

osc.register_handler("/daiw/generate", on_generate)

# Start server
osc.start()

# Send MIDI to plugin
osc.send_midi_note(60, 100, 500)  # C4, velocity 100, 500ms
osc.send_chord([60, 64, 67], 80, 1000)  # C major chord
```

---

## Threading Considerations

### Audio Thread Safety

**CRITICAL**: Never block the audio thread (processBlock in C++).

```
┌───────────────────────────────────────────────────────────────┐
│                        AUDIO THREAD                           │
│  • Runs 44,100+ times per second                             │
│  • NEVER allocate memory                                      │
│  • NEVER lock mutexes                                         │
│  • NEVER do I/O                                               │
│  • NEVER call Python directly                                 │
└───────────────────────────────────────────────────────────────┘
                              ▲
                              │ Lock-free queue
                              ▼
┌───────────────────────────────────────────────────────────────┐
│                       MESSAGE THREAD                          │
│  • Handles OSC messages                                       │
│  • Can call Python (with GIL)                                 │
│  • Queues MIDI events for audio thread                        │
└───────────────────────────────────────────────────────────────┘
```

### GIL Management in pybind11

```cpp
// When calling Python from C++
{
    py::gil_scoped_acquire gil;  // Acquire Python GIL
    // ... call Python functions ...
}  // GIL automatically released

// When running C++ that might take long
{
    py::gil_scoped_release release;  // Release GIL
    // ... long-running C++ code ...
}  // GIL automatically reacquired
```

### Thread-Safe MIDI Buffer

```cpp
class DAiWPlugin {
private:
    juce::MidiBuffer pendingMidi;
    juce::CriticalSection midiLock;

public:
    // Called from message thread (OSC handler)
    void scheduleNote(int note, int velocity) {
        juce::ScopedLock lock(midiLock);
        pendingMidi.addEvent(
            juce::MidiMessage::noteOn(1, note, (uint8)velocity), 0
        );
    }

    // Called from audio thread
    void processBlock(..., juce::MidiBuffer& midiMessages) {
        juce::ScopedLock lock(midiLock);
        midiMessages.addEvents(pendingMidi, 0, buffer.getNumSamples(), 0);
        pendingMidi.clear();
    }
};
```

---

## CMake/JUCE Build System

### Project Structure

```
penta-core/
├── CMakeLists.txt              # Main CMake configuration
├── cmake/
│   ├── FindJUCE.cmake          # JUCE finder module
│   └── pybind11.cmake          # pybind11 configuration
├── src/
│   ├── core/                   # Core library (libdaiw-core)
│   ├── midi/                   # MIDI engine
│   ├── dsp/                    # DSP processing
│   ├── harmony/                # Harmony analysis (from music_brain)
│   ├── groove/                 # Groove templates (from music_brain)
│   ├── plugin/
│   │   ├── vst3/              # VST3 plugin
│   │   └── au/                # Audio Unit plugin
│   └── python/                 # pybind11 bindings
└── tests/
```

### CMakeLists.txt Example

```cmake
cmake_minimum_required(VERSION 3.20)
project(PentaCore VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find dependencies
find_package(JUCE CONFIG REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# Core library
add_library(daiw-core
    src/core/types.cpp
    src/core/intent.cpp
)

# Python bridge
pybind11_add_module(idaw_bridge
    src/python/bridge.cpp
)
target_link_libraries(idaw_bridge PRIVATE daiw-core)

# VST3 Plugin
juce_add_plugin(DAiWBridge
    VERSION 1.0.0
    COMPANY_NAME "DAiW"
    PLUGIN_MANUFACTURER_CODE Daiw
    PLUGIN_CODE Dbrg
    FORMATS VST3 AU Standalone
    PRODUCT_NAME "DAiW Bridge"
)

target_link_libraries(DAiWBridge
    PRIVATE
        daiw-core
        juce::juce_audio_utils
        juce::juce_osc
)
```

### Building with pybind11

```bash
# Configure
cmake -B build -DCMAKE_BUILD_TYPE=Release \
    -DJUCE_DIR=/path/to/JUCE \
    -Dpybind11_DIR=/path/to/pybind11

# Build
cmake --build build --config Release

# Install Python module
pip install build/idaw_bridge*.so
```

---

## Data Flow

### Typical Integration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      DAiW-Music-Brain (Python)                  │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  Phase 0:   │───►│  Phase 1:   │───►│  Phase 2:   │         │
│  │ Core Intent │    │ Emotional   │    │ Technical   │         │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘         │
│         │                  │                  │                 │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
    ┌───────────────────────────────────────────────┐
    │              CppBridge / OSCBridge            │
    │         (pybind11 + OSC communication)        │
    └─────────────────────┬─────────────────────────┘
                          │
                          ▼
    ┌───────────────────────────────────────────────┐
    │              penta-core (C++/JUCE)            │
    │                                               │
    │  • Real-time MIDI generation                  │
    │  • Audio DSP processing                       │
    │  • DAW plugin hosting                         │
    └───────────────────────────────────────────────┘
```

### Data Format

Data exchange uses JSON serialization compatible with DAiW-Music-Brain's existing `to_dict()` / `from_dict()` patterns:

```python
from music_brain.integrations import PentaCoreIntegration, MidiBuffer, KnobState

# Serialize for transmission
knobs = KnobState(chaos=0.7, complexity=0.5)
knobs_json = json.dumps(knobs.to_dict())

# Deserialize response
response = MidiBuffer.from_dict(json.loads(response_json))
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PENTA_CORE_URL` | Penta-core service endpoint | `None` |
| `PENTA_CORE_API_KEY` | API authentication key | `None` |
| `PENTA_CORE_TIMEOUT` | Request timeout in seconds | `30` |
| `DAIW_OSC_SEND_PORT` | OSC send port (Python → C++) | `9001` |
| `DAIW_OSC_RECV_PORT` | OSC receive port (C++ → Python) | `9000` |

### Optional Dependencies

Install penta-core integration dependencies:

```bash
# Basic integration
pip install idaw[penta-core]

# With OSC support
pip install idaw[penta-core] python-osc
```

---

## Implementation Status

### Completed

- [x] High-level `PentaCoreIntegration` class
- [x] `PentaCoreConfig` dataclass with serialization
- [x] `CppBridge` stub with interface signatures
- [x] `CppBridgeConfig` for bridge configuration
- [x] `OSCBridge` stub for real-time communication
- [x] Data structures: `MidiEvent`, `MidiBuffer`, `KnobState`
- [x] Bridge type and threading mode enums
- [x] Ghost Hands callback support
- [x] Rejection protocol implementation

### Future Work

- [ ] Implement actual pybind11 bindings when C++ module is ready
- [ ] Implement OSC server/client using python-osc
- [ ] Define concrete API contracts with penta-core team
- [ ] Implement authentication and secure communication
- [ ] Add retry logic and error handling
- [ ] Create integration tests with mock penta-core responses
- [ ] Document versioning and compatibility requirements
- [ ] CMake integration for building Python bindings

---

## Related Documentation

- [DAiW Integration Guide](../INTEGRATION_GUIDE.md)
- [OSC Bridge Documentation](../../DAiW-Music-Brain/vault/Production_Workflows/osc_bridge_python_cpp.md)
- [JUCE Getting Started](../../DAiW-Music-Brain/vault/Production_Workflows/juce_getting_started.md)
- [JUCE Survival Kit](../../DAiW-Music-Brain/vault/Production_Workflows/juce_survival_kit.md)
- [C++ Planner](../../mcp_workstation/cpp_planner.py)
- [PythonBridge.h](../../iDAW_Core/include/PythonBridge.h)
- [PythonBridge.cpp](../../iDAW_Core/src/PythonBridge.cpp)
- [Penta-Core Repository](https://github.com/sburdges-eng/penta-core)

---

## References

### Phase 3 Issue

See [Issue #14 - DAW-ready C++ Migration & Bridge Layer](https://github.com/sburdges-eng/DAiW-Music-Brain/issues/14) for the complete Phase 3 roadmap including:

- Incremental C++ port of core modules (harmony, groove, diagnostics)
- pybind11 bridge for Python/DAW interoperability
- CMake/JUCE production targets
- Real-time safe threading and OSC communication patterns
