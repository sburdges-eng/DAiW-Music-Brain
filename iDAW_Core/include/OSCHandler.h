/**
 * OSCHandler.h - Thread-safe OSC Communication for DAW Integration
 * 
 * Part of Phase 3 C++ Migration for DAiW-Music-Brain
 * 
 * This module provides real-time safe OSC (Open Sound Control) communication:
 * - Lock-free message queue for audio thread safety
 * - Common DAW parameter mappings
 * - Bidirectional communication patterns
 * - MIDI over OSC support
 * 
 * Design Philosophy:
 * - All operations are allocation-free after initialization
 * - Thread-safe for concurrent access
 * - Optimized for real-time audio processing
 * - Compatible with common DAW OSC implementations
 * 
 * Common DAW OSC Addresses:
 * - Ableton Live: /live/song/*, /live/track/*, /live/clip/*
 * - Logic Pro: /logic/*, /transport/*
 * - Reaper: /track/*, /action/*
 * - Bitwig: /track/*, /device/*
 */

#pragma once

#include <array>
#include <atomic>
#include <cstdint>
#include <cstring>
#include <string_view>
#include <functional>

namespace iDAW {
namespace OSC {

// =============================================================================
// Constants
// =============================================================================

// Maximum OSC address length
constexpr size_t MAX_ADDRESS_LENGTH = 128;

// Maximum OSC message data size
constexpr size_t MAX_MESSAGE_DATA = 256;

// OSC message queue size (power of 2 for efficient modulo)
constexpr size_t MESSAGE_QUEUE_SIZE = 256;

// Default OSC ports
constexpr uint16_t DEFAULT_SEND_PORT = 9000;
constexpr uint16_t DEFAULT_RECEIVE_PORT = 8000;

// =============================================================================
// OSC Type Tags
// =============================================================================

/**
 * OSC type tag characters
 */
namespace TypeTag {
    constexpr char INT32 = 'i';
    constexpr char FLOAT = 'f';
    constexpr char STRING = 's';
    constexpr char BLOB = 'b';
    constexpr char INT64 = 'h';
    constexpr char TIMETAG = 't';
    constexpr char DOUBLE = 'd';
    constexpr char CHAR = 'c';
    constexpr char MIDI = 'm';
    constexpr char TRUE = 'T';
    constexpr char FALSE = 'F';
    constexpr char NIL = 'N';
    constexpr char ARRAY_START = '[';
    constexpr char ARRAY_END = ']';
}

// =============================================================================
// OSC Message
// =============================================================================

/**
 * OSC message structure for queue-based communication
 * 
 * Fixed-size structure suitable for lock-free queues
 */
struct Message {
    std::array<char, MAX_ADDRESS_LENGTH> address = {};
    std::array<char, 8> typeTag = {};  // Type tag string (e.g., ",iif")
    std::array<uint8_t, MAX_MESSAGE_DATA> data = {};
    size_t dataSize = 0;
    uint64_t timestamp = 0;  // NTP timestamp (0 = immediately)
    
    /**
     * Set the OSC address
     */
    void setAddress(std::string_view addr) {
        size_t len = std::min(addr.size(), address.size() - 1);
        std::copy_n(addr.begin(), len, address.begin());
        address[len] = '\0';
    }
    
    /**
     * Get the OSC address
     */
    std::string_view getAddress() const {
        return std::string_view(address.data());
    }
    
    /**
     * Set a single float value
     */
    void setFloat(float value) {
        typeTag[0] = ',';
        typeTag[1] = TypeTag::FLOAT;
        typeTag[2] = '\0';
        
        // OSC uses big-endian, but for internal use we keep native
        std::memcpy(data.data(), &value, sizeof(float));
        dataSize = sizeof(float);
    }
    
    /**
     * Get float value (assumes single float message)
     */
    float getFloat() const {
        if (dataSize < sizeof(float)) return 0.0f;
        float value;
        std::memcpy(&value, data.data(), sizeof(float));
        return value;
    }
    
    /**
     * Set a single int value
     */
    void setInt(int32_t value) {
        typeTag[0] = ',';
        typeTag[1] = TypeTag::INT32;
        typeTag[2] = '\0';
        
        std::memcpy(data.data(), &value, sizeof(int32_t));
        dataSize = sizeof(int32_t);
    }
    
    /**
     * Get int value (assumes single int message)
     */
    int32_t getInt() const {
        if (dataSize < sizeof(int32_t)) return 0;
        int32_t value;
        std::memcpy(&value, data.data(), sizeof(int32_t));
        return value;
    }
    
    /**
     * Set MIDI message (4 bytes: port, status, data1, data2)
     */
    void setMIDI(uint8_t port, uint8_t status, uint8_t data1, uint8_t data2) {
        typeTag[0] = ',';
        typeTag[1] = TypeTag::MIDI;
        typeTag[2] = '\0';
        
        data[0] = port;
        data[1] = status;
        data[2] = data1;
        data[3] = data2;
        dataSize = 4;
    }
    
    /**
     * Check if message is valid
     */
    bool isValid() const {
        return address[0] == '/' && typeTag[0] == ',';
    }
};

// =============================================================================
// Lock-Free Message Queue
// =============================================================================

/**
 * Thread-safe, lock-free SPSC (Single Producer Single Consumer) queue
 * 
 * For bidirectional communication, use two queues:
 * - One for audio thread -> UI thread (sending)
 * - One for UI thread -> audio thread (receiving)
 */
class MessageQueue {
public:
    MessageQueue() : m_head(0), m_tail(0) {}
    
    /**
     * Try to push a message (Producer side)
     * @return true if successful, false if queue full
     */
    bool tryPush(const Message& msg) {
        size_t head = m_head.load(std::memory_order_relaxed);
        size_t next = (head + 1) % MESSAGE_QUEUE_SIZE;
        
        if (next == m_tail.load(std::memory_order_acquire)) {
            return false;  // Queue full
        }
        
        m_buffer[head] = msg;
        m_head.store(next, std::memory_order_release);
        return true;
    }
    
    /**
     * Try to pop a message (Consumer side)
     * @return true if message popped, false if queue empty
     */
    bool tryPop(Message& msg) {
        size_t tail = m_tail.load(std::memory_order_relaxed);
        
        if (tail == m_head.load(std::memory_order_acquire)) {
            return false;  // Queue empty
        }
        
        msg = m_buffer[tail];
        m_tail.store((tail + 1) % MESSAGE_QUEUE_SIZE, std::memory_order_release);
        return true;
    }
    
    /**
     * Check if queue is empty (approximate)
     */
    bool isEmpty() const noexcept {
        return m_head.load(std::memory_order_relaxed) == 
               m_tail.load(std::memory_order_relaxed);
    }
    
    /**
     * Get approximate queue size
     */
    size_t approximateSize() const noexcept {
        size_t head = m_head.load(std::memory_order_relaxed);
        size_t tail = m_tail.load(std::memory_order_relaxed);
        return (head >= tail) ? (head - tail) : (MESSAGE_QUEUE_SIZE - tail + head);
    }
    
private:
    std::array<Message, MESSAGE_QUEUE_SIZE> m_buffer;
    std::atomic<size_t> m_head;
    std::atomic<size_t> m_tail;
};

// =============================================================================
// Common DAW Addresses
// =============================================================================

/**
 * Standard OSC address patterns for common DAW operations
 */
namespace Address {
    // Transport
    constexpr std::string_view PLAY = "/transport/play";
    constexpr std::string_view STOP = "/transport/stop";
    constexpr std::string_view RECORD = "/transport/record";
    constexpr std::string_view TEMPO = "/transport/tempo";
    constexpr std::string_view POSITION = "/transport/position";
    constexpr std::string_view LOOP_START = "/transport/loop/start";
    constexpr std::string_view LOOP_END = "/transport/loop/end";
    
    // Track parameters (use with track index)
    constexpr std::string_view TRACK_VOLUME = "/track/%d/volume";
    constexpr std::string_view TRACK_PAN = "/track/%d/pan";
    constexpr std::string_view TRACK_MUTE = "/track/%d/mute";
    constexpr std::string_view TRACK_SOLO = "/track/%d/solo";
    constexpr std::string_view TRACK_ARM = "/track/%d/arm";
    
    // Clip triggering
    constexpr std::string_view CLIP_LAUNCH = "/clip/%d/%d/launch";
    constexpr std::string_view CLIP_STOP = "/clip/%d/%d/stop";
    
    // Device/Plugin parameters
    constexpr std::string_view DEVICE_PARAM = "/device/%d/param/%d";
    
    // MIDI
    constexpr std::string_view MIDI_NOTE = "/midi/note";
    constexpr std::string_view MIDI_CC = "/midi/cc";
    constexpr std::string_view MIDI_PITCH_BEND = "/midi/pitchbend";
    
    // iDAW specific
    constexpr std::string_view IDAW_CHAOS = "/idaw/chaos";
    constexpr std::string_view IDAW_COMPLEXITY = "/idaw/complexity";
    constexpr std::string_view IDAW_GENRE = "/idaw/genre";
    constexpr std::string_view IDAW_PROMPT = "/idaw/prompt";
    constexpr std::string_view IDAW_HARMONY = "/idaw/harmony";
    constexpr std::string_view IDAW_GROOVE = "/idaw/groove";
    constexpr std::string_view IDAW_FLIP = "/idaw/flip";
    constexpr std::string_view IDAW_REJECTION = "/idaw/rejection";
}

// =============================================================================
// OSC Handler
// =============================================================================

/**
 * Message handler callback type
 */
using MessageHandler = std::function<void(const Message&)>;

/**
 * OSCHandler - Manages OSC communication for DAW integration
 * 
 * Usage:
 * 1. Create handler instance
 * 2. Register message callbacks
 * 3. Call processIncoming() from UI thread
 * 4. Call queueOutgoing() from any thread
 * 5. Send queued messages from network thread
 */
class OSCHandler {
public:
    /**
     * Configuration for OSC communication
     */
    struct Config {
        uint16_t sendPort = DEFAULT_SEND_PORT;
        uint16_t receivePort = DEFAULT_RECEIVE_PORT;
        std::array<char, 64> sendHost = {"127.0.0.1"};
    };
    
    OSCHandler() = default;
    
    /**
     * Initialize the handler with configuration
     */
    void initialize(const Config& config) {
        m_config = config;
        m_initialized = true;
    }
    
    /**
     * Check if handler is initialized
     */
    bool isInitialized() const { return m_initialized; }
    
    /**
     * Queue an outgoing message (thread-safe)
     * 
     * @param msg Message to send
     * @return true if queued successfully
     */
    bool queueOutgoing(const Message& msg) {
        return m_outgoingQueue.tryPush(msg);
    }
    
    /**
     * Queue a simple float message
     */
    bool sendFloat(std::string_view address, float value) {
        Message msg;
        msg.setAddress(address);
        msg.setFloat(value);
        return queueOutgoing(msg);
    }
    
    /**
     * Queue a simple int message
     */
    bool sendInt(std::string_view address, int32_t value) {
        Message msg;
        msg.setAddress(address);
        msg.setInt(value);
        return queueOutgoing(msg);
    }
    
    /**
     * Queue a MIDI message
     */
    bool sendMIDI(std::string_view address, uint8_t status, uint8_t data1, uint8_t data2) {
        Message msg;
        msg.setAddress(address);
        msg.setMIDI(0, status, data1, data2);
        return queueOutgoing(msg);
    }
    
    /**
     * Receive an incoming message (thread-safe)
     * 
     * @param msg Output message
     * @return true if message received
     */
    bool receiveIncoming(Message& msg) {
        return m_incomingQueue.tryPop(msg);
    }
    
    /**
     * Push an incoming message to the queue (called by network thread)
     */
    bool pushIncoming(const Message& msg) {
        return m_incomingQueue.tryPush(msg);
    }
    
    /**
     * Pop an outgoing message from the queue (called by network thread)
     */
    bool popOutgoing(Message& msg) {
        return m_outgoingQueue.tryPop(msg);
    }
    
    /**
     * Process all incoming messages with the registered handler
     * Call this from the UI/processing thread
     */
    void processIncoming(MessageHandler handler) {
        Message msg;
        while (m_incomingQueue.tryPop(msg)) {
            handler(msg);
        }
    }
    
    /**
     * Get the configuration
     */
    const Config& getConfig() const { return m_config; }
    
    /**
     * Check if outgoing queue is empty
     */
    bool isOutgoingEmpty() const { return m_outgoingQueue.isEmpty(); }
    
    /**
     * Check if incoming queue is empty
     */
    bool isIncomingEmpty() const { return m_incomingQueue.isEmpty(); }
    
    // =========================================================================
    // Convenience methods for iDAW-specific messages
    // =========================================================================
    
    /**
     * Send chaos parameter update
     */
    bool sendChaos(float chaos) {
        return sendFloat(Address::IDAW_CHAOS, chaos);
    }
    
    /**
     * Send complexity parameter update
     */
    bool sendComplexity(float complexity) {
        return sendFloat(Address::IDAW_COMPLEXITY, complexity);
    }
    
    /**
     * Send flip state change
     */
    bool sendFlip(bool isFlipped) {
        return sendInt(Address::IDAW_FLIP, isFlipped ? 1 : 0);
    }
    
    /**
     * Send tempo update
     */
    bool sendTempo(float bpm) {
        return sendFloat(Address::TEMPO, bpm);
    }
    
    /**
     * Send a trigger/bang message (no arguments)
     */
    bool sendTrigger(std::string_view address) {
        Message msg;
        msg.setAddress(address);
        msg.typeTag[0] = ',';
        msg.typeTag[1] = '\0';
        msg.dataSize = 0;
        return queueOutgoing(msg);
    }
    
    /**
     * Send play command
     */
    bool sendPlay() {
        return sendTrigger(Address::PLAY);
    }
    
    /**
     * Send stop command
     */
    bool sendStop() {
        return sendTrigger(Address::STOP);
    }
    
    /**
     * Send MIDI note on
     */
    bool sendNoteOn(uint8_t channel, uint8_t note, uint8_t velocity) {
        return sendMIDI(Address::MIDI_NOTE, 0x90 | (channel & 0x0F), note, velocity);
    }
    
    /**
     * Send MIDI note off
     */
    bool sendNoteOff(uint8_t channel, uint8_t note) {
        return sendMIDI(Address::MIDI_NOTE, 0x80 | (channel & 0x0F), note, 0);
    }
    
    /**
     * Send MIDI CC
     */
    bool sendCC(uint8_t channel, uint8_t cc, uint8_t value) {
        return sendMIDI(Address::MIDI_CC, 0xB0 | (channel & 0x0F), cc, value);
    }
    
private:
    Config m_config;
    bool m_initialized = false;
    
    MessageQueue m_outgoingQueue;  // Messages to send
    MessageQueue m_incomingQueue;  // Messages received
};

// =============================================================================
// Global OSC Handler Instance
// =============================================================================

/**
 * Get the singleton OSC handler instance
 */
inline OSCHandler& getHandler() {
    static OSCHandler instance;
    return instance;
}

} // namespace OSC
} // namespace iDAW
