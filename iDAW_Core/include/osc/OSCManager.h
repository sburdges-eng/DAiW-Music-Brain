/**
 * OSCManager.h - OSC Communication for DAW Integration
 * 
 * Provides real-time safe OSC communication patterns:
 * - Async message queuing
 * - Lock-free parameter updates
 * - Standard DAW control mappings
 */

#pragma once

#include "../MemoryManager.h"
#include <string>
#include <functional>
#include <atomic>
#include <memory>
#include <map>

namespace iDAW {
namespace osc {

/**
 * OSC message types
 */
enum class OSCMessageType : uint8_t {
    Int,
    Float,
    String,
    Blob,
    True,
    False,
    Nil,
    Bundle
};

/**
 * OSC value union
 */
struct OSCValue {
    OSCMessageType type;
    union {
        int32_t intValue;
        float floatValue;
    };
    std::string stringValue;
    
    OSCValue() : type(OSCMessageType::Nil), intValue(0) {}
    explicit OSCValue(int32_t i) : type(OSCMessageType::Int), intValue(i) {}
    explicit OSCValue(float f) : type(OSCMessageType::Float), floatValue(f) {}
    explicit OSCValue(const std::string& s) : type(OSCMessageType::String), intValue(0), stringValue(s) {}
    explicit OSCValue(bool b) : type(b ? OSCMessageType::True : OSCMessageType::False), intValue(0) {}
};

/**
 * OSC message for queuing
 */
struct OSCMessage {
    std::string address;
    std::vector<OSCValue> args;
    uint64_t timestamp;  // For bundle ordering
    
    OSCMessage() : timestamp(0) {}
    OSCMessage(const std::string& addr) : address(addr), timestamp(0) {}
};

/**
 * OSC handler callback type
 */
using OSCHandler = std::function<void(const OSCMessage&)>;

/**
 * Standard DAW OSC addresses
 */
namespace addresses {
    // Transport
    constexpr const char* TRANSPORT_PLAY = "/transport/play";
    constexpr const char* TRANSPORT_STOP = "/transport/stop";
    constexpr const char* TRANSPORT_RECORD = "/transport/record";
    constexpr const char* TRANSPORT_TEMPO = "/transport/tempo";
    constexpr const char* TRANSPORT_POSITION = "/transport/position";
    
    // Track control
    constexpr const char* TRACK_VOLUME = "/track/%d/volume";
    constexpr const char* TRACK_PAN = "/track/%d/pan";
    constexpr const char* TRACK_MUTE = "/track/%d/mute";
    constexpr const char* TRACK_SOLO = "/track/%d/solo";
    
    // iDAW specific
    constexpr const char* IDAW_INTENT = "/idaw/intent";
    constexpr const char* IDAW_HARMONY = "/idaw/harmony/analyze";
    constexpr const char* IDAW_GROOVE = "/idaw/groove/apply";
    constexpr const char* IDAW_DIAGNOSE = "/idaw/diagnose";
    constexpr const char* IDAW_GHOST_HANDS = "/idaw/ghost_hands";
    constexpr const char* IDAW_KNOB = "/idaw/knob/%s";
}

/**
 * OSC connection status
 */
enum class ConnectionStatus : uint8_t {
    Disconnected,
    Connecting,
    Connected,
    Error
};

/**
 * OSCManager - Thread-safe OSC communication
 * 
 * Uses lock-free queues for real-time safe message passing.
 */
class OSCManager {
public:
    /**
     * Get singleton instance
     */
    static OSCManager& getInstance();
    
    // Non-copyable
    OSCManager(const OSCManager&) = delete;
    OSCManager& operator=(const OSCManager&) = delete;
    
    /**
     * Initialize OSC server
     * @param receivePort Port to listen on
     * @param sendPort Port to send to
     * @param sendHost Host to send to (default: localhost)
     * @return true if initialization successful
     */
    bool initialize(
        int receivePort = 8000,
        int sendPort = 9000,
        const std::string& sendHost = "127.0.0.1");
    
    /**
     * Shutdown OSC server
     */
    void shutdown();
    
    /**
     * Check if OSC is initialized
     */
    bool isInitialized() const noexcept { return m_initialized.load(); }
    
    /**
     * Get connection status
     */
    ConnectionStatus getStatus() const noexcept { return m_status.load(); }
    
    /**
     * Send OSC message (thread-safe, non-blocking)
     */
    bool send(const OSCMessage& message);
    
    /**
     * Send simple float message
     */
    bool sendFloat(const std::string& address, float value);
    
    /**
     * Send simple int message
     */
    bool sendInt(const std::string& address, int32_t value);
    
    /**
     * Send simple string message
     */
    bool sendString(const std::string& address, const std::string& value);
    
    /**
     * Register handler for OSC address
     */
    void registerHandler(const std::string& address, OSCHandler handler);
    
    /**
     * Unregister handler for OSC address
     */
    void unregisterHandler(const std::string& address);
    
    /**
     * Process pending incoming messages (call from main/UI thread)
     */
    void processIncoming();
    
    /**
     * Flush pending outgoing messages (call from network thread)
     */
    void flushOutgoing();
    
    /**
     * Get last error message
     */
    std::string getLastError() const { return m_lastError; }
    
private:
    OSCManager();
    ~OSCManager();
    
    std::atomic<bool> m_initialized{false};
    std::atomic<ConnectionStatus> m_status{ConnectionStatus::Disconnected};
    
    // Lock-free queues for thread-safe message passing
    LockFreeRingBuffer<OSCMessage, 256> m_incomingQueue;
    LockFreeRingBuffer<OSCMessage, 256> m_outgoingQueue;
    
    // Handler registry (protected by mutex, accessed from main thread only)
    std::map<std::string, OSCHandler> m_handlers;
    
    std::string m_lastError;
    
    // Network resources (opaque pointer to avoid liblo dependency in header)
    struct NetworkImpl;
    std::unique_ptr<NetworkImpl> m_network;
};

/**
 * RAII helper for OSC initialization
 */
class ScopedOSC {
public:
    ScopedOSC(int receivePort = 8000, int sendPort = 9000) {
        m_success = OSCManager::getInstance().initialize(receivePort, sendPort);
    }
    
    ~ScopedOSC() {
        if (m_success) {
            OSCManager::getInstance().shutdown();
        }
    }
    
    bool isValid() const { return m_success; }
    operator bool() const { return m_success; }
    
private:
    bool m_success;
};

} // namespace osc
} // namespace iDAW
