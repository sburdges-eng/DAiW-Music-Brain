# JUCE Getting Started Guide

> You don't need to learn "C++" broadly (which takes 10 years). You need **Audio C++**.

## What is JUCE?

JUCE (Jules' Utility Class Extensions) is the industry standard framework for building audio plugins. Most plugins you own are built with it:

- Neural DSP (Archetype series)
- Arturia (V Collection)
- Valhalla (VintageVerb, Supermassive)
- FabFilter (Pro-Q, Pro-L)
- Xfer (Serum)

## Why JUCE?

| Feature | Benefit |
|---------|---------|
| Cross-platform | Write once, export to Mac/Windows |
| Multi-format | VST3, AU, AAX from same code |
| Built-in UI | JUCE handles graphics, knobs, sliders |
| Audio engine | Handles buffer management, sample rates |
| MIDI support | Full MIDI I/O built in |
| Large community | Extensive tutorials, forums, examples |

## Installation

### 1. Download JUCE

```bash
# Option A: Download from website
# https://juce.com/get-juce/download

# Option B: Clone from GitHub
git clone https://github.com/juce-framework/JUCE.git
```

### 2. Install Projucer

Projucer is JUCE's project management tool. It generates IDE projects (Xcode, Visual Studio).

```
JUCE/extras/Projucer/Builds/MacOSX/build/Debug/Projucer.app
```

Or download pre-built from juce.com.

### 3. Set Up Build Tools

**macOS:**
```bash
# Install Xcode from App Store
xcode-select --install
```

**Windows:**
- Install Visual Studio 2019/2022 with C++ workload

**Linux:**
```bash
sudo apt-get install build-essential libfreetype6-dev libx11-dev \
  libxinerama-dev libxrandr-dev libxcursor-dev mesa-common-dev \
  libasound2-dev freeglut3-dev libxcomposite-dev libcurl4-openssl-dev
```

## Your First Plugin (Audio Passthrough)

### Step 1: Create Project in Projucer

1. Open Projucer
2. File → New Project → Audio Plug-In
3. Name: `DAiWBridge`
4. Select formats: VST3, AU (macOS), Standalone
5. Save to `DAiW-Music-Brain/cpp/`

### Step 2: Understand the Structure

```
DAiWBridge/
├── Source/
│   ├── PluginProcessor.h    # Audio processing (the "brain")
│   ├── PluginProcessor.cpp
│   ├── PluginEditor.h       # UI (the "face")
│   └── PluginEditor.cpp
├── DAiWBridge.jucer         # Projucer project file
└── Builds/
    ├── MacOSX/              # Xcode project
    └── VisualStudio2022/    # VS project
```

### Step 3: The Audio Callback

This is where real-time audio happens. **44,100 times per second.**

```cpp
// PluginProcessor.cpp
void DAiWBridgeAudioProcessor::processBlock(
    juce::AudioBuffer<float>& buffer,
    juce::MidiBuffer& midiMessages)
{
    // This runs on the audio thread
    // NEVER allocate memory here
    // NEVER lock mutexes here
    // NEVER do I/O here

    // Simple passthrough (do nothing = audio passes through)
    // Later: add processing here
}
```

### Step 4: Build and Test

**macOS:**
```bash
cd DAiWBridge/Builds/MacOSX
xcodebuild -configuration Release
```

**Plugin location:**
```
~/Library/Audio/Plug-Ins/VST3/DAiWBridge.vst3
~/Library/Audio/Plug-Ins/Components/DAiWBridge.component
```

## Key JUCE Concepts

### AudioProcessor

The core class. Handles:
- Audio I/O
- MIDI I/O
- State saving/loading
- Parameter management

```cpp
class DAiWBridgeAudioProcessor : public juce::AudioProcessor
{
public:
    void prepareToPlay(double sampleRate, int samplesPerBlock) override;
    void processBlock(juce::AudioBuffer<float>&, juce::MidiBuffer&) override;
    void releaseResources() override;
};
```

### AudioProcessorEditor

The UI class. Handles:
- Drawing
- User interaction
- Parameter display

```cpp
class DAiWBridgeAudioProcessorEditor : public juce::AudioProcessorEditor
{
public:
    void paint(juce::Graphics& g) override;
    void resized() override;

private:
    juce::Slider chaosKnob;
    juce::TextButton generateButton;
};
```

### Parameters

Use `AudioProcessorValueTreeState` for DAW-automatable parameters:

```cpp
// In PluginProcessor.h
juce::AudioProcessorValueTreeState parameters;

// In constructor
parameters(*this, nullptr, "Parameters",
{
    std::make_unique<juce::AudioParameterFloat>(
        "chaos",      // ID
        "Chaos",      // Name
        0.0f,         // Min
        1.0f,         // Max
        0.5f          // Default
    ),
    std::make_unique<juce::AudioParameterFloat>(
        "vulnerability",
        "Vulnerability",
        0.0f,
        1.0f,
        0.3f
    )
})
```

## JUCE + OSC (Connecting to Python)

### Add OSC Module

In Projucer, enable the `juce_osc` module.

### Send Message to Python

```cpp
#include <juce_osc/juce_osc.h>

class DAiWBridgeAudioProcessor : public juce::AudioProcessor
{
private:
    juce::OSCSender oscSender;

public:
    void connectToPython()
    {
        oscSender.connect("127.0.0.1", 9000);
    }

    void requestGeneration(float chaos, float vulnerability)
    {
        juce::OSCMessage msg("/daiw/generate");
        msg.addFloat32(chaos);
        msg.addFloat32(vulnerability);
        oscSender.send(msg);
    }
};
```

### Receive MIDI from Python

```cpp
class DAiWBridgeAudioProcessor : public juce::AudioProcessor,
                                  public juce::OSCReceiver::Listener<>
{
private:
    juce::OSCReceiver oscReceiver;
    juce::MidiBuffer incomingMidi;

public:
    void setupOSC()
    {
        oscReceiver.connect(9001);
        oscReceiver.addListener(this);
    }

    void oscMessageReceived(const juce::OSCMessage& msg) override
    {
        if (msg.getAddressPattern() == "/daiw/midi")
        {
            // Parse MIDI data from message
            int note = msg[0].getInt32();
            int velocity = msg[1].getInt32();
            // Add to buffer (thread-safe)
        }
    }
};
```

## Resources

### Official
- JUCE Documentation: https://docs.juce.com/
- JUCE Tutorials: https://juce.com/learn/tutorials
- JUCE Forum: https://forum.juce.com/

### Tutorials
- The Audio Programmer (YouTube): https://www.youtube.com/@TheAudioProgrammer
- JUCE Tutorial Series by Akash Murthy
- "Getting Started with JUCE" (official)

### Books
- "The Audio Programming Book" (Boulanger, Lazzarini)
- "Designing Audio Effect Plugins in C++" (Pirkle)

### Example Projects
- JUCE examples: `JUCE/examples/`
- Plugin Examples: `JUCE/examples/Plugins/`

## Development Cycle (C++)

```
Change code → Build → Test in DAW → Repeat
```

```bash
# 1. Make changes in Xcode/VS
# 2. Build (Cmd+B / Ctrl+B)
# 3. Restart DAW or rescan plugins
# 4. Test
```

**Tip:** Use Standalone build for faster iteration (no DAW restart needed).

## Next Steps

1. **Build passthrough plugin** - Verify your toolchain works
2. **Add a knob** - Learn UI basics
3. **Add OSC** - Connect to Python
4. **Send MIDI** - Trigger notes from Python
5. **Audio analysis** - FFT, transient detection

## Tags

#juce #cpp #plugin #audio #tutorial #setup
