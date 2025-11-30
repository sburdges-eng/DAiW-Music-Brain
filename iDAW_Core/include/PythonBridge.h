/**
 * PythonBridge.h - pybind11 Integration for iDAW Dual Engine
 * 
 * This module initializes the embedded Python interpreter within Side B
 * and provides the call_iMIDI() function for C++ <-> Python communication.
 * 
 * Data Flow:
 *   User types text into Side B UI -> Async Queue -> Python Script
 *   Python script parses text against genres.json
 *   Python returns MIDI parameters -> Ring Buffer -> C++ Audio Engine
 */

#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

#include "MemoryManager.h"
#include <string>
#include <vector>
#include <map>
#include <optional>
#include <functional>
#include <mutex>
#include <future>
#include <fstream>
#include <regex>
#include <algorithm>

namespace py = pybind11;

namespace iDAW {

// =============================================================================
// INPUT SANITIZATION
// =============================================================================

/**
 * Sanitize user input to prevent injection attacks and ensure safety.
 * 
 * - Removes dangerous characters: ; { } ( )
 * - Truncates to maximum length (500 chars)
 * - Used before passing text to Python interpreter
 * 
 * @param input Raw user input string
 * @return Sanitized safe string
 */
inline std::string sanitizeInput(const std::string& input) {
    // Remove dangerous characters that could be used for injection
    std::string safe = std::regex_replace(input, std::regex("[;{}\\(\\)]"), "");
    
    // Also remove backticks, quotes that could escape strings
    safe = std::regex_replace(safe, std::regex("[`\"']"), "");
    
    // Remove potential escape sequences
    safe = std::regex_replace(safe, std::regex("\\\\"), "");
    
    // Truncate length to prevent buffer issues
    const size_t MAX_INPUT_LENGTH = 500;
    if (safe.length() > MAX_INPUT_LENGTH) {
        safe = safe.substr(0, MAX_INPUT_LENGTH);
    }
    
    // Trim whitespace
    auto start = safe.find_first_not_of(" \t\n\r");
    auto end = safe.find_last_not_of(" \t\n\r");
    if (start == std::string::npos) {
        return "";
    }
    safe = safe.substr(start, end - start + 1);
    
    return safe;
}

/**
 * Knob state structure - current values of Side B UI knobs
 */
struct KnobState {
    float grid;        // Grid resolution (4-32)
    float gate;        // Note gate (0.1-1.0)
    float swing;       // Swing amount (0.5-0.75)
    float chaos;       // Chaos/randomization (0-1)
    float complexity;  // Harmonic/rhythmic complexity (0-1)
    
    // Convert to Python dict
    py::dict toPyDict() const {
        py::dict d;
        d["grid"] = grid;
        d["gate"] = gate;
        d["swing"] = swing;
        d["chaos"] = chaos;
        d["complexity"] = complexity;
        return d;
    }
};

/**
 * MIDI Buffer result from Python
 */
struct MidiBuffer {
    std::vector<MidiEvent> events;
    float suggestedChaos;      // AI-suggested chaos value ("Ghost Hands")
    float suggestedComplexity; // AI-suggested complexity value ("Ghost Hands")
    std::string genre;         // Detected/applied genre
    bool success;
    std::string errorMessage;
};

/**
 * C Major Chord - Fail-safe when Python fails
 */
inline MidiBuffer createFailsafeMidiBuffer() {
    MidiBuffer buffer;
    buffer.success = false;
    buffer.errorMessage = "Python execution failed - using fail-safe";
    buffer.suggestedChaos = 0.5f;
    buffer.suggestedComplexity = 0.5f;
    buffer.genre = "fail_safe";
    
    // C Major chord: C4, E4, G4
    buffer.events = {
        {0x90, 60, 80, 0},     // Note On: C4, velocity 80
        {0x90, 64, 80, 0},     // Note On: E4, velocity 80
        {0x90, 67, 80, 0},     // Note On: G4, velocity 80
        {0x80, 60, 0, 480},    // Note Off: C4
        {0x80, 64, 0, 480},    // Note Off: E4
        {0x80, 67, 0, 480},    // Note Off: G4
    };
    
    return buffer;
}

/**
 * Callback type for "Ghost Hands" - UI knob updates from AI
 */
using GhostHandsCallback = std::function<void(float chaos, float complexity)>;

/**
 * PythonBridge - Manages embedded Python interpreter in Side B
 */
class PythonBridge {
public:
    /**
     * Get singleton instance
     */
    static PythonBridge& getInstance();
    
    // Non-copyable
    PythonBridge(const PythonBridge&) = delete;
    PythonBridge& operator=(const PythonBridge&) = delete;
    
    /**
     * Initialize the Python interpreter.
     * Must be called from Side B (non-audio) thread.
     * @param pythonPath Path to Python modules (music_brain package)
     * @param genresJsonPath Path to GenreDefinitions.json
     * @return true if initialization successful
     */
    bool initialize(const std::string& pythonPath, 
                    const std::string& genresJsonPath);
    
    /**
     * Shutdown the Python interpreter.
     * Call before application exit.
     */
    void shutdown();
    
    /**
     * Check if Python is initialized
     */
    bool isInitialized() const noexcept { return m_initialized; }
    
    /**
     * The main interface function: call_iMIDI
     * 
     * Takes current knob state and text prompt, passes to Python,
     * returns MIDI buffer with events and suggested knob values.
     * 
     * SAFETY: Wrapped in try-catch. Returns C Major chord on failure.
     * 
     * @param knobs Current UI knob values
     * @param textPrompt User text input
     * @return MidiBuffer with events and suggestions
     */
    MidiBuffer call_iMIDI(const KnobState& knobs, const std::string& textPrompt);
    
    /**
     * Async version of call_iMIDI for non-blocking UI
     */
    std::future<MidiBuffer> call_iMIDI_async(const KnobState& knobs, 
                                              const std::string& textPrompt);
    
    /**
     * Register callback for "Ghost Hands" knob updates
     */
    void setGhostHandsCallback(GhostHandsCallback callback);
    
    /**
     * Get the loaded genres map
     */
    const std::map<std::string, py::dict>& getGenres() const { return m_genres; }
    
    /**
     * Rejection Protocol: Track rejections and trigger innovation
     */
    void registerRejection();
    void resetRejectionCounter();
    int getRejectionCount() const { return m_rejectionCount; }
    bool shouldTriggerInnovation() const { return m_rejectionCount >= 3; }
    
private:
    PythonBridge();
    ~PythonBridge();
    
    bool loadGenresJson(const std::string& path);
    MidiBuffer parsePythonResult(const py::object& result);
    
    bool m_initialized = false;
    std::unique_ptr<py::scoped_interpreter> m_interpreter;
    py::module_ m_orchestratorModule;
    py::object m_pipeline;
    
    std::map<std::string, py::dict> m_genres;
    std::mutex m_pythonMutex;  // Python GIL helper
    
    GhostHandsCallback m_ghostHandsCallback;
    int m_rejectionCount = 0;
};

} // namespace iDAW


// ============================================================================
// PYBIND11 MODULE DEFINITION
// ============================================================================

/**
 * Expose C++ types to Python for bidirectional communication
 */
PYBIND11_MODULE(idaw_bridge, m) {
    m.doc() = "iDAW C++ Bridge - Exposes C++ types to Python";
    
    // Expose KnobState
    py::class_<iDAW::KnobState>(m, "KnobState")
        .def(py::init<>())
        .def_readwrite("grid", &iDAW::KnobState::grid)
        .def_readwrite("gate", &iDAW::KnobState::gate)
        .def_readwrite("swing", &iDAW::KnobState::swing)
        .def_readwrite("chaos", &iDAW::KnobState::chaos)
        .def_readwrite("complexity", &iDAW::KnobState::complexity);
    
    // Expose MidiEvent
    py::class_<iDAW::MidiEvent>(m, "MidiEvent")
        .def(py::init<>())
        .def_readwrite("status", &iDAW::MidiEvent::status)
        .def_readwrite("data1", &iDAW::MidiEvent::data1)
        .def_readwrite("data2", &iDAW::MidiEvent::data2)
        .def_readwrite("timestamp", &iDAW::MidiEvent::timestamp);
    
    // Expose MidiBuffer
    py::class_<iDAW::MidiBuffer>(m, "MidiBuffer")
        .def(py::init<>())
        .def_readwrite("events", &iDAW::MidiBuffer::events)
        .def_readwrite("suggested_chaos", &iDAW::MidiBuffer::suggestedChaos)
        .def_readwrite("suggested_complexity", &iDAW::MidiBuffer::suggestedComplexity)
        .def_readwrite("genre", &iDAW::MidiBuffer::genre)
        .def_readwrite("success", &iDAW::MidiBuffer::success)
        .def_readwrite("error_message", &iDAW::MidiBuffer::errorMessage);
    
    // Expose MemoryManager for diagnostics
    py::class_<iDAW::MemoryManager>(m, "MemoryManager")
        .def_static("get_instance", &iDAW::MemoryManager::getInstance,
                    py::return_value_policy::reference)
        .def("is_audio_thread", &iDAW::MemoryManager::isAudioThread);
}
