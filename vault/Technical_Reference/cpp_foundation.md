# C++ Foundation

> Real-time audio safety architecture for professional DAW development.

## Overview

The C++ foundation provides the low-level infrastructure needed for professional audio software. All code is designed for **real-time safety** - no allocations, no locks, no syscalls in the audio thread.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    DAiW C++ Core                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   core.hpp   │  │  types.hpp   │  │  simd.hpp    │  │
│  │  RT Safety   │  │  Basic Types │  │  SIMD DSP    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │memory_pool   │  │lock_free_q   │  │ring_buffer   │  │
│  │  Allocator   │  │ SPSC/MPSC    │  │   Streaming  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  midi.hpp    │  │ harmony.hpp  │  │ audio_io.hpp │  │
│  │MIDI Process  │  │Chord/Key Det │  │ Device Mgmt  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Real-Time Safety Rules

### The Golden Rules
1. **No allocations** in audio thread (use pre-allocated pools)
2. **No locks** (use lock-free data structures)
3. **No syscalls** (no file I/O, no console output)
4. **No exceptions** (use error codes or std::expected)
5. **Bounded execution time** (no unbounded loops)

### RT-Safe Annotation
```cpp
// Mark functions as real-time safe
void process(float* buffer, size_t n) DAIW_RT_SAFE;

// Compile-time enforcement
#define DAIW_RT_SAFE [[clang::annotate("rt_safe")]]
```

## Core Components

### Memory Pool (`memory_pool.hpp`)
Lock-free memory allocator for real-time use.

```cpp
daiw::MemoryPool<MidiEvent, 1024> event_pool;

// Allocate (RT-safe)
MidiEvent* event = event_pool.allocate();

// Deallocate (RT-safe)
event_pool.deallocate(event);
```

### Lock-Free Queues (`lock_free_queue.hpp`)

#### SPSC Queue (Single Producer, Single Consumer)
```cpp
daiw::SPSCQueue<MidiEvent> midi_queue(1024);

// Producer thread
midi_queue.push(event);

// Consumer thread (audio callback)
MidiEvent event;
if (midi_queue.pop(event)) {
    // Process event
}
```

#### MPSC Queue (Multiple Producers, Single Consumer)
```cpp
daiw::MPSCQueue<Command> command_queue(256);

// Multiple UI threads can push
command_queue.push(command);

// Single audio thread pops
Command cmd;
while (command_queue.pop(cmd)) {
    process(cmd);
}
```

### Ring Buffer (`ring_buffer.hpp`)
For audio streaming between threads.

```cpp
daiw::RingBuffer<float> audio_buffer(8192);

// Write from disk thread
audio_buffer.write(samples, count);

// Read from audio thread
audio_buffer.read(output, block_size);
```

### SIMD DSP (`simd.hpp`)
Optimized audio processing primitives.

```cpp
// Apply gain (auto-vectorized)
daiw::simd::apply_gain(buffer, size, 0.5f);

// Mix buffers
daiw::simd::mix_buffers(dst, src, size);

// Find peak
float peak = daiw::simd::find_peak(buffer, size);

// Supports: SSE4.2, AVX2, AVX-512, ARM NEON
```

## MIDI Processing (`midi.hpp`)

### Note Tracker
```cpp
daiw::midi::NoteTracker tracker;

// Track notes
tracker.note_on(channel, note, velocity);
tracker.note_off(channel, note);

// Query
bool active = tracker.is_active(channel, note);
size_t count = tracker.active_count(channel);
```

### MIDI Sequence
```cpp
daiw::midi::Sequence seq(480);  // PPQ

seq.add_event(note_on(0, 0, 60, 100));
seq.add_event(note_off(480, 0, 60));
seq.sort();
seq.transpose(5);
seq.quantize(120);  // 16th notes
```

### MIDI Clock
```cpp
daiw::midi::Clock clock(120.0, 480);

clock.start();
int clocks = clock.advance(block_size, sample_rate);
double beats = clock.position_beats();
```

## Harmony Analysis (`harmony.hpp`)

### Chord Detection
```cpp
daiw::harmony::ChordDetector detector;
auto result = detector.detect_from_notes(notes);

std::cout << result.chord.name();      // "Cmaj7"
std::cout << result.confidence;        // 0.95
```

### Key Detection
```cpp
daiw::harmony::KeyDetector detector;
detector.accumulate(note, weight);
auto key = detector.detect_accumulated();

std::cout << key.scale.root;   // NoteName::C
std::cout << key.is_minor;     // false
```

### Roman Numeral Analysis
```cpp
daiw::harmony::RomanNumeralAnalyzer analyzer;
auto analysis = analyzer.analyze(chord, key);

std::cout << analysis.numeral;    // "IV"
std::cout << analysis.function;   // "subdominant"
```

## Audio I/O (`audio_io.hpp`)

### Audio Callback
```cpp
class MyProcessor : public daiw::audio_io::AudioCallback {
    void process(const float* const* input,
                 float** output,
                 BlockSize samples,
                 const ProcessContext& ctx) override {
        // RT-safe processing here
    }
};
```

### Audio Buffer
```cpp
daiw::audio_io::AudioBuffer buffer(2, 512);  // stereo, 512 samples

buffer.clear();
buffer.apply_gain(0.5f);
float peak = buffer.peak_level();
```

## Build System

### CMake Configuration
```bash
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . -j8
```

### Dependencies (via CPM)
- **JUCE** - Audio plugin framework
- **fmt** - Modern formatting
- **spdlog** - Fast logging
- **Catch2** - Testing framework

### Compiler Options
- C++20 required
- Strict warnings enabled
- Sanitizers available (ASan, UBSan, TSan)

## File Reference

| Header | Purpose | RT-Safe |
|--------|---------|---------|
| `core.hpp` | RT-safety macros, assertions | ✅ |
| `types.hpp` | MidiEvent, GroovePoint, ProcessContext | ✅ |
| `memory_pool.hpp` | Lock-free allocator | ✅ |
| `lock_free_queue.hpp` | SPSC/MPSC queues | ✅ |
| `ring_buffer.hpp` | Audio streaming buffer | ✅ |
| `simd.hpp` | SIMD-optimized DSP | ✅ |
| `midi.hpp` | MIDI processing | ✅ |
| `harmony.hpp` | Chord/key analysis | ⚠️ (some allocations) |
| `audio_io.hpp` | Device management | ❌ (setup only) |

## Related

- [[mcp_multi_ai_workstation]] - The multi-AI system that designed this
- [[neural_groove_humanization]] - Python humanization (will be ported)
