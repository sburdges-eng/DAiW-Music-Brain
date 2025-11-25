# OSC Bridge: Python ↔ C++ Communication

> OSC is the invisible wire connecting the Brain (Python) to the Body (C++).

## What is OSC?

**Open Sound Control (OSC)** is a protocol for sending structured data over a network (typically UDP). It's designed for real-time music/multimedia applications.

### Why OSC?

| Alternative | Problem |
|-------------|---------|
| HTTP/REST | Too slow, connection overhead |
| WebSockets | Overkill for local communication |
| Shared memory | Complex, platform-specific |
| Files | Way too slow |
| **OSC** | Fast, simple, made for audio |

## The DAiW OSC Architecture

```
┌─────────────────────────────────────────┐
│         C++ Plugin (JUCE)               │
│                                         │
│  OSC Sender ──────────► Port 9000       │
│                              │          │
│  OSC Receiver ◄────────── Port 9001     │
│                              ▲          │
└──────────────────────────────┼──────────┘
                               │
                          UDP (localhost)
                               │
┌──────────────────────────────┼──────────┐
│         Python (DAiW Brain)  │          │
│                              ▼          │
│  OSC Server ◄────────── Port 9000       │
│                                         │
│  OSC Client ──────────► Port 9001       │
│                                         │
└─────────────────────────────────────────┘
```

## Python Side

### Installation

```bash
pip install python-osc
```

### OSC Server (Receive from Plugin)

```python
"""DAiW OSC Server - receives commands from C++ plugin."""

from pythonosc import dispatcher, osc_server
import threading

class DAiWOSCServer:
    def __init__(self, host="127.0.0.1", port=9000):
        self.host = host
        self.port = port
        self.dispatcher = dispatcher.Dispatcher()
        self._setup_handlers()

    def _setup_handlers(self):
        """Register OSC message handlers."""
        self.dispatcher.map("/daiw/generate", self._handle_generate)
        self.dispatcher.map("/daiw/set_intent", self._handle_set_intent)
        self.dispatcher.map("/daiw/ping", self._handle_ping)

    def _handle_generate(self, address, chaos: float, vulnerability: float):
        """Handle generation request from plugin."""
        print(f"Generate request: chaos={chaos}, vulnerability={vulnerability}")
        # Process intent and generate harmony
        # Send MIDI back via OSC client

    def _handle_set_intent(self, address, intent_json: str):
        """Handle intent update from plugin."""
        import json
        intent = json.loads(intent_json)
        print(f"Intent updated: {intent}")

    def _handle_ping(self, address):
        """Health check."""
        print("Ping received from plugin")

    def start(self):
        """Start the OSC server in a background thread."""
        self.server = osc_server.ThreadingOSCUDPServer(
            (self.host, self.port),
            self.dispatcher
        )
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        print(f"OSC Server listening on {self.host}:{self.port}")

    def stop(self):
        """Stop the server."""
        self.server.shutdown()


if __name__ == "__main__":
    server = DAiWOSCServer()
    server.start()
    input("Press Enter to stop...\n")
    server.stop()
```

### OSC Client (Send to Plugin)

```python
"""DAiW OSC Client - sends data to C++ plugin."""

from pythonosc import udp_client

class DAiWOSCClient:
    def __init__(self, host="127.0.0.1", port=9001):
        self.client = udp_client.SimpleUDPClient(host, port)

    def send_midi_note(self, note: int, velocity: int, duration_ms: int):
        """Send a MIDI note to the plugin."""
        self.client.send_message("/daiw/midi/note", [note, velocity, duration_ms])

    def send_chord(self, notes: list, velocity: int, duration_ms: int):
        """Send a chord (multiple notes)."""
        # OSC supports variable-length arguments
        self.client.send_message("/daiw/midi/chord", notes + [velocity, duration_ms])

    def send_progression(self, progression_json: str):
        """Send a complete progression as JSON."""
        self.client.send_message("/daiw/progression", [progression_json])

    def send_status(self, status: str):
        """Send status update."""
        self.client.send_message("/daiw/status", [status])


# Usage example
if __name__ == "__main__":
    client = DAiWOSCClient()

    # Send a C major chord
    client.send_chord([60, 64, 67], velocity=100, duration_ms=500)

    # Send status
    client.send_status("Generation complete")
```

## C++ Side (JUCE)

### OSC Sender (Send to Python)

```cpp
// In PluginProcessor.h
#include <juce_osc/juce_osc.h>

class DAiWBridgeAudioProcessor : public juce::AudioProcessor
{
private:
    juce::OSCSender oscSender;
    bool oscConnected = false;

public:
    void connectToPython()
    {
        oscConnected = oscSender.connect("127.0.0.1", 9000);
        if (oscConnected)
            DBG("Connected to Python OSC server");
    }

    void requestGeneration()
    {
        if (!oscConnected) return;

        float chaos = *parameters.getRawParameterValue("chaos");
        float vulnerability = *parameters.getRawParameterValue("vulnerability");

        juce::OSCMessage msg("/daiw/generate");
        msg.addFloat32(chaos);
        msg.addFloat32(vulnerability);
        oscSender.send(msg);
    }

    void sendIntent(const juce::String& intentJson)
    {
        if (!oscConnected) return;

        juce::OSCMessage msg("/daiw/set_intent");
        msg.addString(intentJson);
        oscSender.send(msg);
    }

    void ping()
    {
        if (!oscConnected) return;
        oscSender.send(juce::OSCMessage("/daiw/ping"));
    }
};
```

### OSC Receiver (Receive from Python)

```cpp
// In PluginProcessor.h
class DAiWBridgeAudioProcessor : public juce::AudioProcessor,
                                  private juce::OSCReceiver::Listener<
                                      juce::OSCReceiver::MessageLoopCallback>
{
private:
    juce::OSCReceiver oscReceiver;
    juce::MidiBuffer pendingMidi;
    juce::CriticalSection midiLock;

public:
    void setupOSCReceiver()
    {
        if (oscReceiver.connect(9001))
        {
            oscReceiver.addListener(this);
            DBG("OSC Receiver listening on port 9001");
        }
    }

    void oscMessageReceived(const juce::OSCMessage& message) override
    {
        auto address = message.getAddressPattern().toString();

        if (address == "/daiw/midi/note")
        {
            int note = message[0].getInt32();
            int velocity = message[1].getInt32();
            int durationMs = message[2].getInt32();

            // Thread-safe MIDI buffer access
            juce::ScopedLock lock(midiLock);
            pendingMidi.addEvent(
                juce::MidiMessage::noteOn(1, note, (juce::uint8)velocity),
                0
            );
        }
        else if (address == "/daiw/midi/chord")
        {
            // Parse chord notes
            juce::ScopedLock lock(midiLock);
            int numNotes = message.size() - 2; // Last two are velocity and duration
            int velocity = message[numNotes].getInt32();

            for (int i = 0; i < numNotes; ++i)
            {
                int note = message[i].getInt32();
                pendingMidi.addEvent(
                    juce::MidiMessage::noteOn(1, note, (juce::uint8)velocity),
                    0
                );
            }
        }
        else if (address == "/daiw/status")
        {
            juce::String status = message[0].getString();
            DBG("Python status: " + status);
        }
    }

    void processBlock(juce::AudioBuffer<float>& buffer,
                      juce::MidiBuffer& midiMessages) override
    {
        // Merge pending MIDI from Python
        {
            juce::ScopedLock lock(midiLock);
            midiMessages.addEvents(pendingMidi, 0, buffer.getNumSamples(), 0);
            pendingMidi.clear();
        }

        // Audio passthrough (or processing)
    }
};
```

## OSC Message Protocol

### Plugin → Python

| Address | Arguments | Description |
|---------|-----------|-------------|
| `/daiw/generate` | float chaos, float vulnerability | Request generation |
| `/daiw/set_intent` | string json | Update full intent |
| `/daiw/ping` | (none) | Health check |
| `/daiw/param` | string name, float value | Parameter change |

### Python → Plugin

| Address | Arguments | Description |
|---------|-----------|-------------|
| `/daiw/midi/note` | int note, int velocity, int duration_ms | Single note |
| `/daiw/midi/chord` | int[] notes, int velocity, int duration_ms | Chord |
| `/daiw/progression` | string json | Full progression data |
| `/daiw/status` | string message | Status update |
| `/daiw/pong` | (none) | Ping response |

## Threading Considerations

### Python
- OSC server runs in daemon thread
- Main thread handles intent processing
- Use `threading.Lock` for shared state

### C++
- OSC messages arrive on message thread (NOT audio thread)
- Use `juce::CriticalSection` for MIDI buffer access
- NEVER block in `processBlock()`

```cpp
// WRONG - blocks audio thread
void processBlock(...) {
    oscSender.send(...);  // Network I/O on audio thread!
}

// RIGHT - queue for later
void processBlock(...) {
    if (shouldSendUpdate) {
        // Set flag, send from timer callback or message thread
        needsOSCUpdate = true;
    }
}
```

## Debugging OSC

### Python - Log all messages

```python
def log_all(address, *args):
    print(f"OSC: {address} -> {args}")

dispatcher.set_default_handler(log_all)
```

### Monitor with external tool

```bash
# Install oscdump (part of liblo-tools)
brew install liblo  # macOS
sudo apt install liblo-tools  # Linux

# Monitor port 9000
oscdump 9000
```

### Test from command line

```bash
# Install oscsend
oscsend localhost 9000 /daiw/ping

oscsend localhost 9000 /daiw/generate ff 0.5 0.3
```

## Tags

#osc #bridge #python #cpp #communication #midi #realtime
