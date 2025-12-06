# iDAW C++ Core - Phase 3 Architecture

## Overview

The iDAW C++ Core provides high-performance implementations of the DAiW-Music-Brain analysis engines:
- **HarmonyEngine**: Chord detection, key detection, progression analysis
- **GrooveEngine**: Timing extraction, velocity patterns, swing analysis
- **DiagnosticsEngine**: Rule-break identification, emotional character analysis

These C++ modules are designed for:
1. **Real-time DAW plugin use** (VST3/AU via JUCE)
2. **High-performance Python extension** (via pybind11)
3. **OSC-based communication** with external applications

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Python (music_brain)                        │
│                                                                     │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │
│   │   groove/   │  │  structure/ │  │   session/  │               │
│   │ extractor   │  │   chord     │  │  intent_    │               │
│   │ applicator  │  │progression  │  │  processor  │               │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘               │
│          │                │                │                        │
│          └────────────────┼────────────────┘                        │
│                           │                                         │
│                    ┌──────▼──────┐                                  │
│                    │ idaw_bridge │  ← pybind11 module               │
│                    └──────┬──────┘                                  │
└───────────────────────────┼─────────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────────┐
│                     C++ (iDAW_Core)                                 │
│                           │                                         │
│    ┌──────────────────────┼──────────────────────────┐              │
│    │                      ▼                          │              │
│    │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│              │
│    │  │  Harmony    │ │   Groove    │ │ Diagnostics ││              │
│    │  │   Engine    │ │   Engine    │ │   Engine    ││              │
│    │  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘│              │
│    │         │               │               │       │              │
│    │         └───────────────┼───────────────┘       │              │
│    │                         │                       │              │
│    │                   MemoryManager                 │              │
│    │        (Side A: RT-safe / Side B: Dynamic)      │              │
│    └─────────────────────────────────────────────────┘              │
│                              │                                      │
│    ┌─────────────────────────┼─────────────────────────────────┐    │
│    │                         ▼                                 │    │
│    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │    │
│    │  │ OSCManager  │  │ PythonBridge│  │ JUCE Plugin │       │    │
│    │  │   (liblo)   │  │  (pybind11) │  │ (VST3/AU)   │       │    │
│    │  └─────────────┘  └─────────────┘  └─────────────┘       │    │
│    │                    Integration Layer                      │    │
│    └───────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
iDAW_Core/
├── CMakeLists.txt              # Main CMake configuration
├── include/
│   ├── harmony/
│   │   ├── Chord.h             # Chord representation
│   │   ├── Progression.h       # Progression analysis
│   │   └── HarmonyEngine.h     # Main harmony interface
│   ├── groove/
│   │   ├── GrooveTemplate.h    # Groove pattern storage
│   │   └── GrooveEngine.h      # Groove extraction/application
│   ├── diagnostics/
│   │   └── DiagnosticsEngine.h # Progression diagnostics
│   ├── osc/
│   │   └── OSCManager.h        # OSC communication
│   ├── MemoryManager.h         # Dual-heap memory system
│   ├── PythonBridge.h          # Python interop
│   ├── SafetyUtils.h           # DSP safety utilities
│   └── Version.h               # Version information
├── src/
│   ├── harmony/
│   │   └── HarmonyEngine.cpp
│   ├── groove/
│   │   └── GrooveEngine.cpp
│   ├── diagnostics/
│   │   └── DiagnosticsEngine.cpp
│   ├── osc/
│   │   └── OSCManager.cpp
│   ├── bindings/
│   │   ├── PyBindings.cpp      # Main pybind11 module
│   │   ├── PyHarmony.cpp       # Harmony bindings
│   │   ├── PyGroove.cpp        # Groove bindings
│   │   └── PyDiagnostics.cpp   # Diagnostics bindings
│   ├── MemoryManager.cpp
│   └── PythonBridge.cpp
├── tests/
│   ├── test_harmony.cpp
│   ├── test_groove.cpp
│   ├── test_diagnostics.cpp
│   ├── test_memory_manager.cpp
│   └── test_ring_buffer.cpp
└── plugins/                    # JUCE plugin targets (future)
```

## Building

### Prerequisites

- CMake 3.18+
- C++17 compatible compiler (GCC 9+, Clang 10+, MSVC 2019+)
- Python 3.9+ (for pybind11 bindings)
- Optional: liblo (for OSC support)

### Build Commands

```bash
# Configure
cd iDAW_Core
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release

# Build
cmake --build . --parallel

# Run tests
ctest --output-on-failure

# Install Python module
cmake --install . --prefix ../..
```

### CMake Options

| Option | Default | Description |
|--------|---------|-------------|
| `IDAW_BUILD_TESTS` | ON | Build unit tests |
| `IDAW_BUILD_PYTHON_BINDINGS` | ON | Build pybind11 Python module |
| `IDAW_BUILD_JUCE_PLUGIN` | OFF | Build JUCE VST3/AU plugins |
| `IDAW_USE_OSC` | ON | Enable OSC communication |
| `IDAW_ENABLE_SANITIZERS` | OFF | Enable address/UB sanitizers |

## Usage

### Python (via idaw_bridge)

```python
import idaw_bridge

# Diagnose a progression
result = idaw_bridge.diagnose_progression("F-C-Am-Dm")
print(f"Key: {result['key']}")
print(f"Issues: {result['issues']}")
print(f"Borrowed chords: {result['borrowed_chords']}")

# Detect chord from MIDI notes
chord = idaw_bridge.detect_chord([60, 64, 67])  # C major
print(f"Chord: {chord['name']}")

# Extract groove from notes
notes = [
    {"pitch": 36, "velocity": 100, "start_tick": 0},
    {"pitch": 38, "velocity": 110, "start_tick": 480},
]
groove = idaw_bridge.extract_groove(notes, ppq=480, tempo=120.0)
print(f"Swing: {groove['swing_factor']}")

# Humanize notes
humanized = idaw_bridge.humanize(notes, complexity=0.5, vulnerability=0.5)

# Get genre groove template
funk = idaw_bridge.get_genre_groove("funk")
print(f"Funk swing: {funk['swing_factor']}")

# Suggest rule breaks for emotion
suggestions = idaw_bridge.suggest_rule_breaks("grief")
for s in suggestions:
    print(f"- {s['category']}: {s['emotional_effect']}")
```

### C++ Direct Usage

```cpp
#include "harmony/HarmonyEngine.h"
#include "groove/GrooveEngine.h"
#include "diagnostics/DiagnosticsEngine.h"

using namespace iDAW;

// Harmony analysis
auto& harmony = harmony::HarmonyEngine::getInstance();
auto result = harmony.diagnoseProgression("F-C-Am-Dm");
std::cout << "Key: " << result.detectedKey.toString() << std::endl;

// Groove extraction
auto& groove = groove::GrooveEngine::getInstance();
std::vector<groove::MidiNote> notes = {...};
auto template = groove.extractGroove(notes, 480, 120.0f);
std::cout << "Swing: " << template.swingFactor() << std::endl;

// Diagnostics
auto& diag = diagnostics::DiagnosticsEngine::getInstance();
auto ruleBreaks = diag.suggestRuleBreaks("grief");
```

## Memory Architecture

The iDAW Core uses a **Dual-Heap** memory system:

### Side A (Work State)
- **4GB pre-allocated monotonic buffer**
- Thread-safe, lock-free allocation
- NO deallocation during runtime
- Used for real-time audio processing

### Side B (Dream State)
- **Dynamic synchronized pool**
- Supports allocation AND deallocation
- May block - never use from audio thread
- Used for AI/UI operations

### Ring Buffer
- Lock-free SPSC queue for MIDI events
- 4096 event capacity
- Real-time safe producer/consumer pattern

## Threading Model

```
┌──────────────────────────────────────────────────────────────────┐
│                          Audio Thread                            │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Side A Memory Only                                        │  │
│  │  - Monotonic allocation                                    │  │
│  │  - Ring buffer consumer                                    │  │
│  │  - No blocking operations                                  │  │
│  │  - No Python calls                                         │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                              │
                         Ring Buffer
                         (Lock-Free)
                              │
┌──────────────────────────────────────────────────────────────────┐
│                          UI/AI Thread                            │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Side B Memory                                             │  │
│  │  - Dynamic allocation                                      │  │
│  │  - Ring buffer producer                                    │  │
│  │  - Python bridge operations                                │  │
│  │  - OSC message handling                                    │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

## OSC Addresses

### Standard DAW Control
- `/transport/play`, `/transport/stop`, `/transport/record`
- `/transport/tempo` (float)
- `/track/{n}/volume`, `/track/{n}/pan`, `/track/{n}/mute`

### iDAW Specific
- `/idaw/intent` - Process song intent
- `/idaw/harmony/analyze` - Analyze chord progression
- `/idaw/groove/apply` - Apply groove template
- `/idaw/diagnose` - Get progression diagnostics
- `/idaw/ghost_hands` - Receive AI knob suggestions
- `/idaw/knob/{name}` - Knob state updates

## Real-Time Safety Guidelines

1. **Never allocate in audio thread** - Use Side A pre-allocated memory
2. **Never lock in audio thread** - Use lock-free data structures
3. **Never call Python from audio thread** - Use ring buffer for communication
4. **Always validate parameters** - Use SafetyUtils.h functions
5. **Disable denormals** - Call `Safety::disableDenormals()` at thread start

## Phase 3 Migration Status

- [x] CMake build system
- [x] Core headers (Chord, Progression, GrooveTemplate)
- [x] HarmonyEngine implementation
- [x] GrooveEngine implementation
- [x] DiagnosticsEngine implementation
- [x] pybind11 bindings
- [x] OSC communication layer
- [x] Unit tests
- [ ] Python module integration
- [ ] JUCE plugin targets
- [ ] Performance benchmarks
- [ ] Documentation updates

## Philosophy

> "The tool shouldn't finish art for people. It should make them braver."

The C++ core preserves the emotional intent system while providing:
- **Professional-grade performance** for DAW integration
- **Real-time safe operation** for plugin deployment
- **Seamless Python interop** for flexible "brain" logic
