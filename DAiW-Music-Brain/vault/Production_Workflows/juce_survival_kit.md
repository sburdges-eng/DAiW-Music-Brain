# JUCE Survival Kit: The War Chest for Phase 3

> You don't need generic C++ lessons. You need the specific JUCE classes that act as limbs for your Python brain.

## The Holy Trinity Classes (Your Bridge)

These three classes are the exact mechanics to receive data from Python and turn it into sound inside the DAW.

### 1. The Listener: `juce::OSCReceiver`

**This is your ear.** It sits on a UDP port and waits for Python to send instructions.

```cpp
class DAiWPlugin : public juce::AudioProcessor,
                   private juce::OSCReceiver::Listener<juce::OSCReceiver::MessageLoopCallback>
{
public:
    DAiWPlugin()
    {
        // Listen on port 9001 for Python responses
        if (oscReceiver.connect(9001))
            oscReceiver.addListener(this);
    }

    void oscMessageReceived(const juce::OSCMessage& message) override
    {
        auto address = message.getAddressPattern().toString();

        if (address == "/daiw/notes")
        {
            // Parse JSON from Python
            juce::String json = message[0].getString();
            parseAndScheduleNotes(json);
        }
        else if (address == "/daiw/param")
        {
            // Python is ghost-turning a knob
            juce::String paramId = message[0].getString();
            float value = message[1].getFloat32();
            apvts.getParameter(paramId)->setValueNotifyingHost(value);
        }
    }

private:
    juce::OSCReceiver oscReceiver;
};
```

**Key Method:** `oscMessageReceived(const OSCMessage& message)`
- Triggers instantly when Python sends data
- Your code: "If address is `/daiw/notes`, parse the JSON arguments"

---

### 2. The Scheduler: `juce::MidiBuffer`

**This is your hands.** Python sends notes ("Play C3 at 1.2 seconds"). You can't play them "now" — you schedule them into the audio buffer.

```cpp
void processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages)
{
    // Merge any pending notes from Python
    {
        juce::ScopedLock lock(midiLock);
        for (const auto& event : pendingNotes)
        {
            // Calculate sample offset from milliseconds
            int sampleOffset = static_cast<int>(
                event.startMs * sampleRate / 1000.0
            );

            // Clamp to buffer size
            sampleOffset = juce::jmin(sampleOffset, buffer.getNumSamples() - 1);

            midiMessages.addEvent(
                juce::MidiMessage::noteOn(1, event.pitch, (juce::uint8)event.velocity),
                sampleOffset
            );

            // Schedule note off
            int noteOffSample = sampleOffset + static_cast<int>(
                event.durationMs * sampleRate / 1000.0
            );
            midiMessages.addEvent(
                juce::MidiMessage::noteOff(1, event.pitch),
                noteOffSample
            );
        }
        pendingNotes.clear();
    }
}
```

**Key Method:** `addEvent(const MidiMessage& message, int sampleOffset)`
- Places a note exactly `sampleOffset` samples into the future
- Ensures sample-accurate timing that Python can't physically achieve

---

### 3. The Brain Interface: `juce::AudioProcessorValueTreeState` (APVTS)

**This is your nervous system.** Manages every knob (Chaos, Vulnerability) and ensures they save/load correctly in Logic.

```cpp
class DAiWPlugin : public juce::AudioProcessor
{
public:
    DAiWPlugin()
        : apvts(*this, nullptr, "Parameters", createParameterLayout())
    {
    }

    static juce::AudioProcessorValueTreeState::ParameterLayout createParameterLayout()
    {
        std::vector<std::unique_ptr<juce::RangedAudioParameter>> params;

        params.push_back(std::make_unique<juce::AudioParameterFloat>(
            "chaos",           // ID (used in OSC: /daiw/param "chaos" 0.5)
            "Chaos",           // Display name
            0.0f, 1.0f,        // Range
            0.5f               // Default
        ));

        params.push_back(std::make_unique<juce::AudioParameterFloat>(
            "vulnerability",
            "Vulnerability",
            0.0f, 1.0f,
            0.3f
        ));

        params.push_back(std::make_unique<juce::AudioParameterChoice>(
            "motivation",
            "Motivation",
            juce::StringArray{"grief", "defiance", "hope", "longing", "rage"},
            0  // Default index
        ));

        return { params.begin(), params.end() };
    }

    // Python can ghost-turn knobs via OSC
    void setParameterFromOSC(const juce::String& paramId, float value)
    {
        if (auto* param = apvts.getParameter(paramId))
            param->setValueNotifyingHost(value);
    }

private:
    juce::AudioProcessorValueTreeState apvts;
};
```

**Key Method:** `getParameter("chaos")->setValueNotifyingHost(0.8f)`
- Allows Python (via OSC) to ghost-turn knobs in the plugin UI
- Updates sound engine safely, syncs with DAW automation

---

## DSP Toys (What Logic Can't Do)

When you want to process audio in ways Logic's scripter prohibits:

### `juce::dsp::Convolution`

Load custom Impulse Responses. Generate an IR in Python based on "Core Wound" (e.g., muddy distorted room reverb for "Grief").

```cpp
juce::dsp::Convolution convolution;

void prepareToPlay(double sampleRate, int samplesPerBlock) override
{
    juce::dsp::ProcessSpec spec;
    spec.sampleRate = sampleRate;
    spec.maximumBlockSize = samplesPerBlock;
    spec.numChannels = 2;

    convolution.prepare(spec);

    // Load IR from file (could be generated by Python)
    convolution.loadImpulseResponse(
        irFile,
        juce::dsp::Convolution::Stereo::yes,
        juce::dsp::Convolution::Trim::yes,
        0  // Size (0 = use file size)
    );
}
```

**Use Case:** Python generates IR based on affect → plugin loads it for emotional reverb.

### `juce::dsp::LadderFilter`

Modeled analog filter (Moog style). Map "Vulnerability" to resonance.

```cpp
juce::dsp::LadderFilter<float> ladderFilter;

void prepareToPlay(double sampleRate, int samplesPerBlock) override
{
    ladderFilter.prepare({sampleRate, (uint32)samplesPerBlock, 2});
    ladderFilter.setMode(juce::dsp::LadderFilterMode::LPF24);
}

void processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer&) override
{
    float vulnerability = *apvts.getRawParameterValue("vulnerability");

    // Map vulnerability to filter character
    // High vulnerability = more resonance, lower cutoff (muffled, internal)
    float cutoff = juce::jmap(vulnerability, 0.0f, 1.0f, 8000.0f, 800.0f);
    float resonance = juce::jmap(vulnerability, 0.0f, 1.0f, 0.1f, 0.8f);

    ladderFilter.setCutoffFrequencyHz(cutoff);
    ladderFilter.setResonance(resonance);

    juce::dsp::AudioBlock<float> block(buffer);
    ladderFilter.process(juce::dsp::ProcessContextReplacing<float>(block));
}
```

**Use Case:** Vulnerability score controls how "exposed" or "protected" the sound feels.

### `juce::dsp::Compressor`

Dynamic range control based on emotional state.

```cpp
juce::dsp::Compressor<float> compressor;

void updateCompressorFromAffect(float chaos)
{
    // High chaos = aggressive compression (pumping, squashed)
    // Low chaos = gentle, dynamic
    float ratio = juce::jmap(chaos, 0.0f, 1.0f, 2.0f, 20.0f);
    float attack = juce::jmap(chaos, 0.0f, 1.0f, 50.0f, 1.0f);  // ms

    compressor.setRatio(ratio);
    compressor.setAttack(attack);
}
```

---

## Rosetta Stone: Python ↔ C++

| Concept | Python (Brain) | C++ (Body) |
|---------|---------------|------------|
| **List** | `my_list = [1, 2, 3]` | `std::vector<int> myList = {1, 2, 3};` |
| **Dictionary** | `{"key": "value"}` | `std::map<String, String> myMap;` |
| **String** | `text = "hello"` | `juce::String text = "hello";` |
| **Print/Debug** | `print("debug")` | `DBG("debug");` |
| **JSON Parse** | `json.loads(s)` | `juce::JSON::parse(s)` |
| **Random** | `random.uniform(0, 1)` | `juce::Random::getSystemRandom().nextFloat()` |
| **File Read** | `open(path).read()` | `juce::File(path).loadFileAsString()` |
| **Sleep** | `time.sleep(1)` | `juce::Thread::sleep(1000);` |

---

## Learning Resources (No Fluff)

### Essential Videos

| Resource | Why It Matters |
|----------|---------------|
| **The Audio Programmer - OSC in JUCE** | Exact tutorial for Python ↔ JUCE communication |
| **MatKat Music - SimpleEQ Series** | Learn APVTS from scratch |
| **JUCE Examples/OscillatorDemo** | How to make sound without samples |

### Key Links

- **The Audio Programmer YouTube:** https://www.youtube.com/@TheAudioProgrammer
- **JUCE Tutorial 29 - OSC Messages:** Direct proof-of-concept for Brain in a Box
- **JUCE Forum:** https://forum.juce.com/
- **JUCE Documentation:** https://docs.juce.com/

### In Your JUCE Download

```
JUCE/
├── examples/
│   ├── Audio/
│   │   └── OscillatorDemo/     # Basic synth
│   ├── Plugins/
│   │   └── AudioPluginDemo/    # Full plugin template
│   └── Utilities/
│       └── OSCDemo/            # OSC sender/receiver example
```

---

## Quick Reference: OSC Message Flow

```
Python Brain                          C++ Plugin
─────────────                         ──────────
                                      oscReceiver.connect(9001)
                                              │
generate_session()                            │
       │                                      │
       ▼                                      │
{"notes": [...]}                              │
       │                                      │
oscClient.send("/daiw/notes", json) ────────► oscMessageReceived()
                                              │
                                              ▼
                                      parseAndScheduleNotes()
                                              │
                                              ▼
                                      midiBuffer.addEvent()
                                              │
                                              ▼
                                      Logic plays notes
```

---

## Bookmarks for Phase 3

1. **JUCE Tutorial 29 - Receiving OSC Messages**
   - Exact implementation of `OSCReceiver` for external control

2. **SimpleEQ Tutorial Series**
   - Complete APVTS walkthrough, parameter management

3. **JUCE AudioPluginDemo**
   - Starting template for AU/VST3 plugin

## Tags

#juce #cpp #osc #midi #dsp #phase3 #warChest #plugin
