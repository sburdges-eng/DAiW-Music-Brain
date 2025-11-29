/**
 * DAiW MIDI Engine Implementation
 *
 * Real-time MIDI processing, sequencing, and clock sync.
 */

#include "daiw/midi.hpp"
#include "daiw/core.hpp"

#include <algorithm>

namespace daiw {
namespace midi {

// =============================================================================
// MIDI Utilities
// =============================================================================

const char* message_type_name(MidiMessageType type) {
    switch (type) {
        case MidiMessageType::NoteOff: return "NoteOff";
        case MidiMessageType::NoteOn: return "NoteOn";
        case MidiMessageType::PolyPressure: return "PolyPressure";
        case MidiMessageType::ControlChange: return "ControlChange";
        case MidiMessageType::ProgramChange: return "ProgramChange";
        case MidiMessageType::ChannelPressure: return "ChannelPressure";
        case MidiMessageType::PitchBend: return "PitchBend";
        case MidiMessageType::System: return "System";
        default: return "Unknown";
    }
}

// =============================================================================
// Common Controller Numbers
// =============================================================================

namespace cc {
    constexpr uint8_t MODULATION = 1;
    constexpr uint8_t BREATH = 2;
    constexpr uint8_t VOLUME = 7;
    constexpr uint8_t PAN = 10;
    constexpr uint8_t EXPRESSION = 11;
    constexpr uint8_t SUSTAIN = 64;
    constexpr uint8_t PORTAMENTO = 65;
    constexpr uint8_t SOSTENUTO = 66;
    constexpr uint8_t SOFT = 67;
    constexpr uint8_t LEGATO = 68;
    constexpr uint8_t ALL_SOUND_OFF = 120;
    constexpr uint8_t RESET_CONTROLLERS = 121;
    constexpr uint8_t LOCAL_CONTROL = 122;
    constexpr uint8_t ALL_NOTES_OFF = 123;
} // namespace cc

// =============================================================================
// MIDI Event Stream Processing
// =============================================================================

/**
 * Process a raw MIDI byte stream and extract events.
 * Handles running status.
 */
class MidiParser {
public:
    MidiParser() : running_status_(0), expected_bytes_(0), current_event_{} {}

    /**
     * Feed a byte to the parser.
     * @return true if a complete event is ready
     */
    bool feed(uint8_t byte, MidiEvent& out_event) {
        // Status byte?
        if (byte & 0x80) {
            // System real-time messages (single byte, don't affect running status)
            if (byte >= 0xF8) {
                out_event.status = byte;
                out_event.data1 = 0;
                out_event.data2 = 0;
                out_event.timestamp = 0;
                return true;
            }

            // New status byte
            running_status_ = byte;
            buffer_pos_ = 0;

            // Determine expected data bytes
            uint8_t type = byte & 0xF0;
            if (type == 0xC0 || type == 0xD0) {
                expected_bytes_ = 1;  // Program change, channel pressure
            } else if (byte == 0xF1 || byte == 0xF3) {
                expected_bytes_ = 1;  // MTC quarter frame, song select
            } else if (byte == 0xF2) {
                expected_bytes_ = 2;  // Song position
            } else if (byte >= 0xF4) {
                expected_bytes_ = 0;  // System common (undefined, tune request, etc.)
                out_event.status = byte;
                out_event.data1 = 0;
                out_event.data2 = 0;
                out_event.timestamp = 0;
                return true;
            } else {
                expected_bytes_ = 2;  // Note, CC, pitch bend, etc.
            }
            return false;
        }

        // Data byte
        if (running_status_ == 0) {
            return false;  // No status yet, ignore
        }

        buffer_[buffer_pos_++] = byte;

        if (buffer_pos_ >= expected_bytes_) {
            out_event.status = running_status_;
            out_event.data1 = buffer_[0];
            out_event.data2 = (expected_bytes_ > 1) ? buffer_[1] : 0;
            out_event.timestamp = 0;
            buffer_pos_ = 0;
            return true;
        }

        return false;
    }

    void reset() {
        running_status_ = 0;
        expected_bytes_ = 0;
        buffer_pos_ = 0;
    }

private:
    uint8_t running_status_;
    uint8_t expected_bytes_;
    uint8_t buffer_[2];
    size_t buffer_pos_ = 0;
    MidiEvent current_event_;
};

// =============================================================================
// MIDI Output Formatting
// =============================================================================

/**
 * Convert MIDI events to raw byte stream.
 */
class MidiFormatter {
public:
    /**
     * Format an event to bytes.
     * @return Number of bytes written (1-3)
     */
    size_t format(const MidiEvent& event, uint8_t* out, bool use_running_status = true) {
        size_t bytes_written = 0;

        // Check if we need to send status byte
        bool need_status = !use_running_status ||
                           event.status != last_status_ ||
                           (event.status & 0xF0) >= 0xF0;  // Always send system messages

        if (need_status) {
            out[bytes_written++] = event.status;
            last_status_ = event.status;
        }

        // Data bytes
        uint8_t type = event.status & 0xF0;
        if (type == 0xC0 || type == 0xD0) {
            out[bytes_written++] = event.data1 & 0x7F;
        } else if (type != 0xF0 || event.status == 0xF2) {
            out[bytes_written++] = event.data1 & 0x7F;
            if (type != 0xF1 && type != 0xF3) {
                out[bytes_written++] = event.data2 & 0x7F;
            }
        }

        return bytes_written;
    }

    void reset() {
        last_status_ = 0;
    }

private:
    uint8_t last_status_ = 0;
};

// =============================================================================
// Tempo Conversion Utilities
// =============================================================================

namespace tempo {

/**
 * Convert BPM to microseconds per quarter note.
 */
uint32_t bpm_to_uspqn(double bpm) {
    return static_cast<uint32_t>(60000000.0 / bpm);
}

/**
 * Convert microseconds per quarter note to BPM.
 */
double uspqn_to_bpm(uint32_t uspqn) {
    return 60000000.0 / uspqn;
}

/**
 * Convert ticks to milliseconds.
 */
double ticks_to_ms(Tick ticks, double bpm, size_t ppq) {
    double ms_per_beat = 60000.0 / bpm;
    return (static_cast<double>(ticks) / ppq) * ms_per_beat;
}

/**
 * Convert milliseconds to ticks.
 */
Tick ms_to_ticks(double ms, double bpm, size_t ppq) {
    double ms_per_beat = 60000.0 / bpm;
    return static_cast<Tick>((ms / ms_per_beat) * ppq);
}

/**
 * Convert ticks to samples.
 */
size_t ticks_to_samples(Tick ticks, double bpm, size_t ppq, SampleRate sample_rate) {
    double seconds_per_tick = 60.0 / (bpm * ppq);
    return static_cast<size_t>(ticks * seconds_per_tick * sample_rate);
}

/**
 * Convert samples to ticks.
 */
Tick samples_to_ticks(size_t samples, double bpm, size_t ppq, SampleRate sample_rate) {
    double ticks_per_sample = (bpm * ppq) / (60.0 * sample_rate);
    return static_cast<Tick>(samples * ticks_per_sample);
}

} // namespace tempo

} // namespace midi
} // namespace daiw
