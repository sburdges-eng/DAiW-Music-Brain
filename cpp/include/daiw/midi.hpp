/**
 * DAiW MIDI Processing Module
 *
 * Real-time safe MIDI event handling, sequencing, and processing.
 * Assigned to: Claude
 *
 * Features:
 * - Lock-free MIDI event queues
 * - MIDI file parsing (Standard MIDI File format)
 * - Real-time event scheduling
 * - MIDI clock sync
 * - Note tracking and voice management
 */

#pragma once

#include "daiw/types.hpp"
#include "daiw/lock_free_queue.hpp"
#include "daiw/memory_pool.hpp"

#include <vector>
#include <array>
#include <functional>
#include <cstring>

namespace daiw {
namespace midi {

// =============================================================================
// Constants
// =============================================================================

constexpr size_t MAX_MIDI_CHANNELS = 16;
constexpr size_t MAX_POLYPHONY = 128;
constexpr size_t DEFAULT_PPQ = 480;
constexpr size_t MIDI_QUEUE_SIZE = 4096;

// =============================================================================
// MIDI Message Helpers
// =============================================================================

/// Build a note on message
inline MidiEvent note_on(Tick timestamp, MidiChannel channel,
                         MidiNote note, MidiVelocity velocity) {
    return MidiEvent(timestamp, MidiMessageType::NoteOn, channel, note, velocity);
}

/// Build a note off message
inline MidiEvent note_off(Tick timestamp, MidiChannel channel,
                          MidiNote note, MidiVelocity velocity = 0) {
    return MidiEvent(timestamp, MidiMessageType::NoteOff, channel, note, velocity);
}

/// Build a control change message
inline MidiEvent control_change(Tick timestamp, MidiChannel channel,
                                uint8_t controller, uint8_t value) {
    return MidiEvent(timestamp, MidiMessageType::ControlChange, channel, controller, value);
}

/// Build a pitch bend message (14-bit value: 0-16383, center = 8192)
inline MidiEvent pitch_bend(Tick timestamp, MidiChannel channel, uint16_t value) {
    return MidiEvent(timestamp, MidiMessageType::PitchBend, channel,
                     value & 0x7F, (value >> 7) & 0x7F);
}

/// Build a program change message
inline MidiEvent program_change(Tick timestamp, MidiChannel channel, uint8_t program) {
    return MidiEvent(timestamp, MidiMessageType::ProgramChange, channel, program, 0);
}

// =============================================================================
// Note Tracker
// =============================================================================

/**
 * Tracks active notes per channel for proper note-off handling.
 * Real-time safe - no allocations after construction.
 */
class NoteTracker {
public:
    NoteTracker() {
        clear();
    }

    /// Record a note on
    void note_on(MidiChannel channel, MidiNote note, MidiVelocity velocity) {
        if (channel < MAX_MIDI_CHANNELS && note < MAX_POLYPHONY) {
            active_notes_[channel][note] = velocity;
            note_count_[channel]++;
        }
    }

    /// Record a note off
    void note_off(MidiChannel channel, MidiNote note) {
        if (channel < MAX_MIDI_CHANNELS && note < MAX_POLYPHONY) {
            if (active_notes_[channel][note] > 0) {
                active_notes_[channel][note] = 0;
                note_count_[channel]--;
            }
        }
    }

    /// Check if a note is active
    bool is_active(MidiChannel channel, MidiNote note) const {
        if (channel < MAX_MIDI_CHANNELS && note < MAX_POLYPHONY) {
            return active_notes_[channel][note] > 0;
        }
        return false;
    }

    /// Get velocity of active note (0 if not active)
    MidiVelocity get_velocity(MidiChannel channel, MidiNote note) const {
        if (channel < MAX_MIDI_CHANNELS && note < MAX_POLYPHONY) {
            return active_notes_[channel][note];
        }
        return 0;
    }

    /// Get count of active notes on channel
    size_t active_count(MidiChannel channel) const {
        if (channel < MAX_MIDI_CHANNELS) {
            return note_count_[channel];
        }
        return 0;
    }

    /// Get total active notes across all channels
    size_t total_active() const {
        size_t total = 0;
        for (size_t ch = 0; ch < MAX_MIDI_CHANNELS; ++ch) {
            total += note_count_[ch];
        }
        return total;
    }

    /// Clear all active notes
    void clear() {
        for (auto& channel : active_notes_) {
            channel.fill(0);
        }
        note_count_.fill(0);
    }

    /// Clear all notes on a specific channel
    void clear_channel(MidiChannel channel) {
        if (channel < MAX_MIDI_CHANNELS) {
            active_notes_[channel].fill(0);
            note_count_[channel] = 0;
        }
    }

    /// Generate note-off events for all active notes
    template<typename OutputIt>
    OutputIt all_notes_off(Tick timestamp, OutputIt out) const {
        for (MidiChannel ch = 0; ch < MAX_MIDI_CHANNELS; ++ch) {
            for (MidiNote note = 0; note < MAX_POLYPHONY; ++note) {
                if (active_notes_[ch][note] > 0) {
                    *out++ = note_off(timestamp, ch, note);
                }
            }
        }
        return out;
    }

private:
    std::array<std::array<MidiVelocity, MAX_POLYPHONY>, MAX_MIDI_CHANNELS> active_notes_;
    std::array<size_t, MAX_MIDI_CHANNELS> note_count_;
};

// =============================================================================
// MIDI Sequence
// =============================================================================

/**
 * A sequence of MIDI events with timing information.
 * Used for patterns, clips, and tracks.
 */
class Sequence {
public:
    Sequence(size_t ppq = DEFAULT_PPQ)
        : ppq_(ppq), length_ticks_(0) {}

    /// Add an event to the sequence
    void add_event(const MidiEvent& event) {
        events_.push_back(event);
        if (event.timestamp > length_ticks_) {
            length_ticks_ = event.timestamp;
        }
    }

    /// Sort events by timestamp
    void sort() {
        std::sort(events_.begin(), events_.end(),
            [](const MidiEvent& a, const MidiEvent& b) {
                return a.timestamp < b.timestamp;
            });
    }

    /// Get events in time range [start, end)
    template<typename OutputIt>
    OutputIt get_events_in_range(Tick start, Tick end, OutputIt out) const {
        for (const auto& event : events_) {
            if (event.timestamp >= start && event.timestamp < end) {
                *out++ = event;
            }
        }
        return out;
    }

    /// Clear all events
    void clear() {
        events_.clear();
        length_ticks_ = 0;
    }

    /// Get PPQ (pulses per quarter note)
    size_t ppq() const { return ppq_; }

    /// Set PPQ
    void set_ppq(size_t ppq) { ppq_ = ppq; }

    /// Get sequence length in ticks
    Tick length() const { return length_ticks_; }

    /// Set sequence length
    void set_length(Tick length) { length_ticks_ = length; }

    /// Get number of events
    size_t event_count() const { return events_.size(); }

    /// Get all events (const)
    const std::vector<MidiEvent>& events() const { return events_; }

    /// Get all events (mutable)
    std::vector<MidiEvent>& events() { return events_; }

    /// Transpose all notes by semitones
    void transpose(int semitones) {
        for (auto& event : events_) {
            if (event.type() == MidiMessageType::NoteOn ||
                event.type() == MidiMessageType::NoteOff) {
                int new_note = static_cast<int>(event.data1) + semitones;
                event.data1 = static_cast<uint8_t>(std::clamp(new_note, 0, 127));
            }
        }
    }

    /// Scale velocities by factor
    void scale_velocity(float factor) {
        for (auto& event : events_) {
            if (event.type() == MidiMessageType::NoteOn) {
                int new_vel = static_cast<int>(event.data2 * factor);
                event.data2 = static_cast<uint8_t>(std::clamp(new_vel, 1, 127));
            }
        }
    }

    /// Quantize events to grid
    void quantize(Tick grid_size, float strength = 1.0f) {
        for (auto& event : events_) {
            Tick nearest_grid = ((event.timestamp + grid_size / 2) / grid_size) * grid_size;
            Tick offset = nearest_grid - event.timestamp;
            event.timestamp += static_cast<Tick>(offset * strength);
        }
    }

private:
    std::vector<MidiEvent> events_;
    size_t ppq_;
    Tick length_ticks_;
};

// =============================================================================
// Real-Time MIDI Processor
// =============================================================================

/// Callback type for processed MIDI events
using MidiCallback = std::function<void(const MidiEvent&)>;

/**
 * Real-time MIDI event processor.
 * Handles event scheduling, filtering, and transformation.
 */
class Processor {
public:
    Processor()
        : input_queue_(MIDI_QUEUE_SIZE)
        , output_queue_(MIDI_QUEUE_SIZE)
        , transpose_(0)
        , velocity_scale_(1.0f)
        , channel_filter_(0xFFFF)  // All channels enabled
    {}

    /// Push event to input queue (thread-safe, RT-safe)
    bool push_event(const MidiEvent& event) {
        return input_queue_.push(event);
    }

    /// Process pending events (call from audio thread)
    void process(Tick current_tick) {
        MidiEvent event;
        while (input_queue_.pop(event)) {
            // Apply channel filter
            if (!is_channel_enabled(event.channel())) {
                continue;
            }

            // Apply transformations
            MidiEvent processed = transform(event);

            // Send to output
            output_queue_.push(processed);

            // Track notes
            if (processed.isNoteOn()) {
                tracker_.note_on(processed.channel(), processed.data1, processed.data2);
            } else if (processed.isNoteOff()) {
                tracker_.note_off(processed.channel(), processed.data1);
            }
        }
    }

    /// Pop processed event from output queue (thread-safe, RT-safe)
    bool pop_event(MidiEvent& event) {
        return output_queue_.pop(event);
    }

    /// Set transpose amount in semitones
    void set_transpose(int semitones) {
        transpose_ = semitones;
    }

    /// Set velocity scale factor
    void set_velocity_scale(float scale) {
        velocity_scale_ = scale;
    }

    /// Enable/disable a MIDI channel
    void set_channel_enabled(MidiChannel channel, bool enabled) {
        if (channel < MAX_MIDI_CHANNELS) {
            if (enabled) {
                channel_filter_ |= (1 << channel);
            } else {
                channel_filter_ &= ~(1 << channel);
            }
        }
    }

    /// Check if channel is enabled
    bool is_channel_enabled(MidiChannel channel) const {
        return channel < MAX_MIDI_CHANNELS && (channel_filter_ & (1 << channel));
    }

    /// Get note tracker
    const NoteTracker& tracker() const { return tracker_; }

    /// Panic - send all notes off
    void panic() {
        std::array<MidiEvent, MAX_POLYPHONY * MAX_MIDI_CHANNELS> off_events;
        auto end = tracker_.all_notes_off(0, off_events.begin());
        for (auto it = off_events.begin(); it != end; ++it) {
            output_queue_.push(*it);
        }
        tracker_.clear();
    }

private:
    MidiEvent transform(const MidiEvent& event) {
        MidiEvent result = event;

        // Apply transpose to note events
        if (event.type() == MidiMessageType::NoteOn ||
            event.type() == MidiMessageType::NoteOff) {
            int new_note = static_cast<int>(event.data1) + transpose_;
            result.data1 = static_cast<uint8_t>(std::clamp(new_note, 0, 127));

            // Apply velocity scaling to note on
            if (event.type() == MidiMessageType::NoteOn) {
                int new_vel = static_cast<int>(event.data2 * velocity_scale_);
                result.data2 = static_cast<uint8_t>(std::clamp(new_vel, 1, 127));
            }
        }

        return result;
    }

    SPSCQueue<MidiEvent> input_queue_;
    SPSCQueue<MidiEvent> output_queue_;
    NoteTracker tracker_;
    int transpose_;
    float velocity_scale_;
    uint16_t channel_filter_;
};

// =============================================================================
// MIDI Clock
// =============================================================================

/**
 * MIDI clock for tempo synchronization.
 * Generates MIDI clock messages (24 PPQN) and handles sync.
 */
class Clock {
public:
    Clock(double bpm = 120.0, size_t ppq = DEFAULT_PPQ)
        : bpm_(bpm)
        , ppq_(ppq)
        , position_ticks_(0)
        , is_playing_(false)
        , clock_counter_(0)
    {
        update_timing();
    }

    /// Set tempo in BPM
    void set_bpm(double bpm) {
        bpm_ = bpm;
        update_timing();
    }

    /// Get current BPM
    double bpm() const { return bpm_; }

    /// Start playback
    void start() {
        is_playing_ = true;
        position_ticks_ = 0;
        clock_counter_ = 0;
    }

    /// Stop playback
    void stop() {
        is_playing_ = false;
    }

    /// Continue playback from current position
    void continue_playback() {
        is_playing_ = true;
    }

    /// Check if playing
    bool is_playing() const { return is_playing_; }

    /// Get current position in ticks
    Tick position() const { return position_ticks_; }

    /// Set position in ticks
    void set_position(Tick ticks) {
        position_ticks_ = ticks;
    }

    /// Get position in beats
    double position_beats() const {
        return static_cast<double>(position_ticks_) / ppq_;
    }

    /// Get position in bars (assuming 4/4)
    double position_bars() const {
        return position_beats() / 4.0;
    }

    /// Advance clock by sample count
    /// Returns number of MIDI clock ticks that should be sent
    int advance(size_t sample_count, SampleRate sample_rate) {
        if (!is_playing_) return 0;

        double samples_per_tick = (60.0 * sample_rate) / (bpm_ * ppq_);
        double ticks_advanced = sample_count / samples_per_tick;

        Tick old_position = position_ticks_;
        position_ticks_ += static_cast<Tick>(ticks_advanced);

        // Calculate MIDI clock messages (24 PPQN)
        // MIDI clock divides quarter note into 24
        int clocks_per_tick = 24;
        int old_clock = (old_position * clocks_per_tick) / ppq_;
        int new_clock = (position_ticks_ * clocks_per_tick) / ppq_;

        return new_clock - old_clock;
    }

    /// Convert ticks to samples
    size_t ticks_to_samples(Tick ticks, SampleRate sample_rate) const {
        double samples_per_tick = (60.0 * sample_rate) / (bpm_ * ppq_);
        return static_cast<size_t>(ticks * samples_per_tick);
    }

    /// Convert samples to ticks
    Tick samples_to_ticks(size_t samples, SampleRate sample_rate) const {
        double samples_per_tick = (60.0 * sample_rate) / (bpm_ * ppq_);
        return static_cast<Tick>(samples / samples_per_tick);
    }

private:
    void update_timing() {
        // Pre-calculate timing values if needed
    }

    double bpm_;
    size_t ppq_;
    Tick position_ticks_;
    bool is_playing_;
    int clock_counter_;
};

// =============================================================================
// MIDI File Reader (SMF Format)
// =============================================================================

/**
 * Standard MIDI File (SMF) reader.
 * Parses .mid files into Sequence objects.
 */
class FileReader {
public:
    struct TrackInfo {
        std::string name;
        size_t event_count;
        MidiChannel channel;
    };

    /// Read MIDI file from buffer
    bool read(const uint8_t* data, size_t size) {
        if (size < 14) return false;  // Minimum header size

        // Check MThd header
        if (data[0] != 'M' || data[1] != 'T' || data[2] != 'h' || data[3] != 'd') {
            return false;
        }

        // Parse header
        size_t header_length = read_uint32_be(data + 4);
        format_ = read_uint16_be(data + 8);
        num_tracks_ = read_uint16_be(data + 10);
        ppq_ = read_uint16_be(data + 12);

        // Parse tracks
        size_t offset = 8 + header_length;
        sequences_.clear();
        track_info_.clear();

        for (uint16_t track = 0; track < num_tracks_ && offset < size; ++track) {
            if (!parse_track(data, size, offset)) {
                return false;
            }
        }

        return true;
    }

    /// Get number of tracks
    uint16_t num_tracks() const { return num_tracks_; }

    /// Get PPQ
    uint16_t ppq() const { return ppq_; }

    /// Get format (0, 1, or 2)
    uint16_t format() const { return format_; }

    /// Get sequence for track
    const Sequence* get_sequence(size_t track) const {
        if (track < sequences_.size()) {
            return &sequences_[track];
        }
        return nullptr;
    }

    /// Get track info
    const TrackInfo* get_track_info(size_t track) const {
        if (track < track_info_.size()) {
            return &track_info_[track];
        }
        return nullptr;
    }

private:
    static uint32_t read_uint32_be(const uint8_t* data) {
        return (data[0] << 24) | (data[1] << 16) | (data[2] << 8) | data[3];
    }

    static uint16_t read_uint16_be(const uint8_t* data) {
        return (data[0] << 8) | data[1];
    }

    static size_t read_variable_length(const uint8_t* data, size_t max_size, uint32_t& value) {
        value = 0;
        size_t bytes_read = 0;

        for (size_t i = 0; i < max_size && i < 4; ++i) {
            uint8_t byte = data[i];
            value = (value << 7) | (byte & 0x7F);
            bytes_read++;

            if (!(byte & 0x80)) break;
        }

        return bytes_read;
    }

    bool parse_track(const uint8_t* data, size_t size, size_t& offset) {
        // Check MTrk header
        if (offset + 8 > size) return false;
        if (data[offset] != 'M' || data[offset+1] != 'T' ||
            data[offset+2] != 'r' || data[offset+3] != 'k') {
            return false;
        }

        uint32_t track_length = read_uint32_be(data + offset + 4);
        offset += 8;

        Sequence seq(ppq_);
        TrackInfo info{"", 0, 0};
        Tick absolute_time = 0;
        uint8_t running_status = 0;

        size_t track_end = offset + track_length;
        while (offset < track_end && offset < size) {
            // Read delta time
            uint32_t delta;
            offset += read_variable_length(data + offset, track_end - offset, delta);
            absolute_time += delta;

            if (offset >= track_end) break;

            // Read event
            uint8_t status = data[offset];

            // Handle running status
            if (status < 0x80) {
                status = running_status;
            } else {
                offset++;
                if (status < 0xF0) {
                    running_status = status;
                }
            }

            // Parse event based on status
            uint8_t type = status & 0xF0;
            uint8_t channel = status & 0x0F;

            if (type == 0x80 || type == 0x90 || type == 0xA0 || type == 0xB0 || type == 0xE0) {
                // Two data bytes
                if (offset + 2 > track_end) break;
                uint8_t data1 = data[offset++];
                uint8_t data2 = data[offset++];

                MidiEvent event;
                event.timestamp = absolute_time;
                event.status = status;
                event.data1 = data1;
                event.data2 = data2;

                seq.add_event(event);
                info.event_count++;
                info.channel = channel;
            }
            else if (type == 0xC0 || type == 0xD0) {
                // One data byte
                if (offset + 1 > track_end) break;
                uint8_t data1 = data[offset++];

                MidiEvent event;
                event.timestamp = absolute_time;
                event.status = status;
                event.data1 = data1;
                event.data2 = 0;

                seq.add_event(event);
                info.event_count++;
            }
            else if (status == 0xFF) {
                // Meta event
                if (offset + 2 > track_end) break;
                uint8_t meta_type = data[offset++];
                uint32_t length;
                offset += read_variable_length(data + offset, track_end - offset, length);

                // Track name
                if (meta_type == 0x03 && length > 0 && offset + length <= track_end) {
                    info.name = std::string(reinterpret_cast<const char*>(data + offset), length);
                }

                offset += length;
            }
            else if (status == 0xF0 || status == 0xF7) {
                // SysEx
                uint32_t length;
                offset += read_variable_length(data + offset, track_end - offset, length);
                offset += length;
            }
        }

        seq.sort();
        sequences_.push_back(std::move(seq));
        track_info_.push_back(std::move(info));

        offset = track_end;
        return true;
    }

    uint16_t format_ = 0;
    uint16_t num_tracks_ = 0;
    uint16_t ppq_ = DEFAULT_PPQ;
    std::vector<Sequence> sequences_;
    std::vector<TrackInfo> track_info_;
};

} // namespace midi
} // namespace daiw
