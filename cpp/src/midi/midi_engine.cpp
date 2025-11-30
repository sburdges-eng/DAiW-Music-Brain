/**
 * @file midi_engine.cpp
 * @brief MIDI event processing engine
 */

#include "daiw/types.hpp"
#include <vector>
#include <algorithm>

namespace daiw {
namespace midi {

/**
 * @brief MIDI event types
 */
enum class EventType {
    NoteOn,
    NoteOff,
    ControlChange,
    ProgramChange,
    PitchBend,
    Clock,
    Start,
    Stop
};

/**
 * @brief MIDI event structure
 */
struct MidiEvent {
    EventType type;
    TickCount tick;
    MidiChannel channel;
    uint8_t data1;
    uint8_t data2;
};

/**
 * @brief MIDI track container
 */
class MidiTrack {
public:
    void addEvent(const MidiEvent& event) {
        events_.push_back(event);
    }

    void sortByTime() {
        std::sort(events_.begin(), events_.end(),
                  [](const MidiEvent& a, const MidiEvent& b) {
                      return a.tick < b.tick;
                  });
    }

    const std::vector<MidiEvent>& getEvents() const { return events_; }
    std::vector<MidiEvent>& getEvents() { return events_; }

    void clear() { events_.clear(); }

private:
    std::vector<MidiEvent> events_;
};

/**
 * @brief MIDI engine for processing and playback
 */
class MidiEngine {
public:
    MidiEngine() = default;

    void setTempo(float bpm) { tempo_.bpm = bpm; }
    float getTempo() const { return tempo_.bpm; }

    void setPPQ(int ppq) { ppq_ = ppq; }
    int getPPQ() const { return ppq_; }

    TickCount msToTicks(float ms) const {
        float ticksPerMs = ppq_ * tempo_.bpm / 60000.0f;
        return static_cast<TickCount>(ms * ticksPerMs);
    }

    float ticksToMs(TickCount ticks) const {
        float ticksPerMs = ppq_ * tempo_.bpm / 60000.0f;
        return static_cast<float>(ticks) / ticksPerMs;
    }

private:
    Tempo tempo_;
    int ppq_ = DEFAULT_PPQ;
};

}  // namespace midi
}  // namespace daiw
