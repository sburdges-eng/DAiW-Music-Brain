# DAiW_Core - JUCE 8 Audio Plugin

## Phase 1: The Foundation

This is the native C++ audio processing core for DAiW, built with JUCE 8.

### AI Roles
- **AI-1: Primary Orchestrator** - Routes tasks, breaks down work, resolves conflicts
- **AI-2: Logic/Computation** - Code, math, structured operations (never touches creative output)
- **AI-3: Creative** - Music, text, reasoning, emotional/intent modeling
- **AI-4: Data/Memory/Validation** - Checks outputs, merges results, prevents hallucinations

### Directory Structure

```
DAiW_Core/
├── CMakeLists.txt           # Build configuration
├── Source/
│   ├── Core/                # Plugin processor & editor
│   │   ├── PluginProcessor.h/cpp
│   │   └── PluginEditor.h/cpp
│   ├── Memory/              # CRITICAL: Dual-allocator system
│   │   ├── MemoryManager.h/cpp
│   │   └── DAiW_Buffer.h/cpp
│   ├── UI/                  # Dual-view components
│   │   ├── MainComponent.h/cpp
│   │   ├── WorkStateComponent.h/cpp
│   │   ├── DreamStateComponent.h/cpp
│   │   ├── LookAndFeel_Metal.h/cpp
│   │   └── LookAndFeel_Blueprint.h/cpp
│   └── PythonBridge/        # C++/Python integration
│       ├── PythonBridge.h/cpp
│       └── PythonModule.cpp
```

### Memory Architecture (Critical)

The MemoryManager implements a dual-allocator system:

#### Side A: Iron Heap
- `std::pmr::monotonic_buffer_resource`
- Pre-allocated 4GB at startup
- **NO DEALLOCATION during runtime** (prevents fragmentation)
- Reset only between sessions
- Used for all audio processing buffers

#### Side B: Playground
- `std::pmr::synchronized_pool_resource`
- Thread-safe and expandable
- Can grow/shrink as needed
- Used for creative/experimental features

### Dual-View System

The UI has two states:

1. **Work State (Side A)**
   - Grey background with brushed metal aesthetic
   - Uses Iron Heap allocator
   - Production-focused, stable

2. **Dream State (Side B)**
   - Blue background with blueprint aesthetic
   - Uses Playground allocator
   - Creative/experimental, animated wobble

### Building

```bash
# Create build directory
mkdir build && cd build

# Configure with CMake
cmake .. -DCMAKE_BUILD_TYPE=Release

# Build
cmake --build . --config Release

# Or use Ninja for faster builds
cmake .. -GNinja -DCMAKE_BUILD_TYPE=Release
ninja
```

### Python Bridge

The `daiw_logic` Python module provides access to C++ infrastructure:

```python
import daiw_logic

# Get memory statistics
stats = daiw_logic.get_memory_stats()
print(f"Iron Heap: {stats['iron_heap_used']} / {stats['iron_heap_capacity']}")

# Allocate buffer
handle = daiw_logic.allocate_buffer(1024, "iron_heap")

# Check state
if daiw_logic.is_dream_state():
    print("Currently in Dream state")
```

### Dependencies

- JUCE 8.0.0
- pybind11 2.11.1
- C++20 compiler (GCC 10+, Clang 12+, MSVC 2022+)
- Python 3.9+ (for bridge)

### License

MIT License - See parent LICENSE file
