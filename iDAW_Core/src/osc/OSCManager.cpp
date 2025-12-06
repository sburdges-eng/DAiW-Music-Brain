/**
 * OSCManager.cpp - Implementation of OSC Communication Manager
 */

#include "osc/OSCManager.h"
#include <chrono>

#ifdef IDAW_HAS_OSC
#include <lo/lo.h>
#endif

namespace iDAW {
namespace osc {

// ============================================================================
// Network Implementation (liblo wrapper)
// ============================================================================

struct OSCManager::NetworkImpl {
#ifdef IDAW_HAS_OSC
    lo_server_thread server = nullptr;
    lo_address destination = nullptr;
#endif
    int receivePort = 8000;
    int sendPort = 9000;
    std::string sendHost = "127.0.0.1";
};

// ============================================================================
// OSCManager Implementation
// ============================================================================

OSCManager& OSCManager::getInstance() {
    static OSCManager instance;
    return instance;
}

OSCManager::OSCManager() 
    : m_network(std::make_unique<NetworkImpl>()) {}

OSCManager::~OSCManager() {
    shutdown();
}

bool OSCManager::initialize(
    int receivePort,
    int sendPort,
    const std::string& sendHost) {
    
    if (m_initialized.load()) {
        return true;  // Already initialized
    }
    
    m_network->receivePort = receivePort;
    m_network->sendPort = sendPort;
    m_network->sendHost = sendHost;
    
#ifdef IDAW_HAS_OSC
    m_status.store(ConnectionStatus::Connecting);
    
    // Create server thread
    std::string portStr = std::to_string(receivePort);
    m_network->server = lo_server_thread_new(portStr.c_str(), 
        [](int num, const char* msg, const char* where) {
            // Error handler
        });
    
    if (!m_network->server) {
        m_lastError = "Failed to create OSC server on port " + portStr;
        m_status.store(ConnectionStatus::Error);
        return false;
    }
    
    // Add generic handler for all messages
    lo_server_thread_add_method(m_network->server, nullptr, nullptr,
        [](const char* path, const char* types, lo_arg** argv, int argc,
           lo_message msg, void* userData) -> int {
            
            OSCManager* manager = static_cast<OSCManager*>(userData);
            
            OSCMessage oscMsg;
            oscMsg.address = path;
            oscMsg.timestamp = std::chrono::duration_cast<std::chrono::microseconds>(
                std::chrono::system_clock::now().time_since_epoch()).count();
            
            // Parse arguments
            for (int i = 0; i < argc; i++) {
                switch (types[i]) {
                    case 'i':
                        oscMsg.args.push_back(OSCValue(argv[i]->i));
                        break;
                    case 'f':
                        oscMsg.args.push_back(OSCValue(argv[i]->f));
                        break;
                    case 's':
                        oscMsg.args.push_back(OSCValue(std::string(&argv[i]->s)));
                        break;
                    case 'T':
                        oscMsg.args.push_back(OSCValue(true));
                        break;
                    case 'F':
                        oscMsg.args.push_back(OSCValue(false));
                        break;
                }
            }
            
            // Queue message for processing
            manager->m_incomingQueue.tryPush(oscMsg);
            
            return 0;
        }, this);
    
    // Start server thread
    lo_server_thread_start(m_network->server);
    
    // Create destination address
    m_network->destination = lo_address_new(
        sendHost.c_str(), 
        std::to_string(sendPort).c_str());
    
    if (!m_network->destination) {
        m_lastError = "Failed to create OSC destination";
        lo_server_thread_free(m_network->server);
        m_network->server = nullptr;
        m_status.store(ConnectionStatus::Error);
        return false;
    }
    
    m_status.store(ConnectionStatus::Connected);
    m_initialized.store(true);
    return true;
    
#else
    // OSC not available - store configuration but operate in stub mode
    m_status.store(ConnectionStatus::Connected);
    m_initialized.store(true);
    return true;
#endif
}

void OSCManager::shutdown() {
    if (!m_initialized.load()) {
        return;
    }
    
#ifdef IDAW_HAS_OSC
    if (m_network->server) {
        lo_server_thread_stop(m_network->server);
        lo_server_thread_free(m_network->server);
        m_network->server = nullptr;
    }
    
    if (m_network->destination) {
        lo_address_free(m_network->destination);
        m_network->destination = nullptr;
    }
#endif
    
    m_handlers.clear();
    m_status.store(ConnectionStatus::Disconnected);
    m_initialized.store(false);
}

bool OSCManager::send(const OSCMessage& message) {
    if (!m_initialized.load()) {
        return false;
    }
    
    return m_outgoingQueue.tryPush(message);
}

bool OSCManager::sendFloat(const std::string& address, float value) {
    OSCMessage msg(address);
    msg.args.push_back(OSCValue(value));
    return send(msg);
}

bool OSCManager::sendInt(const std::string& address, int32_t value) {
    OSCMessage msg(address);
    msg.args.push_back(OSCValue(value));
    return send(msg);
}

bool OSCManager::sendString(const std::string& address, const std::string& value) {
    OSCMessage msg(address);
    msg.args.push_back(OSCValue(value));
    return send(msg);
}

void OSCManager::registerHandler(const std::string& address, OSCHandler handler) {
    m_handlers[address] = std::move(handler);
}

void OSCManager::unregisterHandler(const std::string& address) {
    m_handlers.erase(address);
}

void OSCManager::processIncoming() {
    OSCMessage msg;
    while (m_incomingQueue.tryPop(msg)) {
        // Try exact match first
        auto it = m_handlers.find(msg.address);
        if (it != m_handlers.end()) {
            it->second(msg);
        }
        
        // Try wildcard handlers
        // Simple implementation: check for handlers that end with /*
        for (const auto& [pattern, handler] : m_handlers) {
            if (pattern.back() == '*') {
                std::string prefix = pattern.substr(0, pattern.length() - 1);
                if (msg.address.compare(0, prefix.length(), prefix) == 0) {
                    handler(msg);
                }
            }
        }
    }
}

void OSCManager::flushOutgoing() {
#ifdef IDAW_HAS_OSC
    if (!m_network->destination) {
        return;
    }
    
    OSCMessage msg;
    while (m_outgoingQueue.tryPop(msg)) {
        // Build type string
        std::string types;
        for (const auto& arg : msg.args) {
            switch (arg.type) {
                case OSCMessageType::Int:    types += 'i'; break;
                case OSCMessageType::Float:  types += 'f'; break;
                case OSCMessageType::String: types += 's'; break;
                case OSCMessageType::True:   types += 'T'; break;
                case OSCMessageType::False:  types += 'F'; break;
                case OSCMessageType::Nil:    types += 'N'; break;
                default: break;
            }
        }
        
        // Create and send message
        lo_message loMsg = lo_message_new();
        
        for (const auto& arg : msg.args) {
            switch (arg.type) {
                case OSCMessageType::Int:
                    lo_message_add_int32(loMsg, arg.intValue);
                    break;
                case OSCMessageType::Float:
                    lo_message_add_float(loMsg, arg.floatValue);
                    break;
                case OSCMessageType::String:
                    lo_message_add_string(loMsg, arg.stringValue.c_str());
                    break;
                case OSCMessageType::True:
                    lo_message_add_true(loMsg);
                    break;
                case OSCMessageType::False:
                    lo_message_add_false(loMsg);
                    break;
                case OSCMessageType::Nil:
                    lo_message_add_nil(loMsg);
                    break;
                default:
                    break;
            }
        }
        
        lo_send_message(m_network->destination, msg.address.c_str(), loMsg);
        lo_message_free(loMsg);
    }
#else
    // Stub mode: just drain the queue
    OSCMessage msg;
    while (m_outgoingQueue.tryPop(msg)) {
        // Discarded
    }
#endif
}

} // namespace osc
} // namespace iDAW
