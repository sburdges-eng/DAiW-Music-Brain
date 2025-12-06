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

#ifdef IDAW_BUILDING_PYTHON_MODULE

#include "HarmonyCore.h"
#include "GrooveCore.h"
#include "DiagnosticsCore.h"
#include "OSCHandler.h"

/**
 * Expose C++ types to Python for bidirectional communication
 */
PYBIND11_MODULE(idaw_bridge, m) {
    m.doc() = "iDAW C++ Bridge - Exposes C++ types to Python for DAW/plugin integration";
    
    // ========================================================================
    // Original Bridge Types
    // ========================================================================
    
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
    
    // ========================================================================
    // Harmony Core Bindings
    // ========================================================================
    
    auto harmony = m.def_submodule("harmony", "Harmony analysis module");
    
    // ChordQuality enum
    py::enum_<iDAW::Harmony::ChordQuality>(harmony, "ChordQuality")
        .value("Unknown", iDAW::Harmony::ChordQuality::Unknown)
        .value("Major", iDAW::Harmony::ChordQuality::Major)
        .value("Minor", iDAW::Harmony::ChordQuality::Minor)
        .value("Diminished", iDAW::Harmony::ChordQuality::Diminished)
        .value("Augmented", iDAW::Harmony::ChordQuality::Augmented)
        .value("Dominant7", iDAW::Harmony::ChordQuality::Dominant7)
        .value("Major7", iDAW::Harmony::ChordQuality::Major7)
        .value("Minor7", iDAW::Harmony::ChordQuality::Minor7)
        .value("HalfDim7", iDAW::Harmony::ChordQuality::HalfDim7)
        .value("Dim7", iDAW::Harmony::ChordQuality::Dim7)
        .value("Sus2", iDAW::Harmony::ChordQuality::Sus2)
        .value("Sus4", iDAW::Harmony::ChordQuality::Sus4)
        .export_values();
    
    // Mode enum
    py::enum_<iDAW::Harmony::Mode>(harmony, "Mode")
        .value("Major", iDAW::Harmony::Mode::Major)
        .value("Minor", iDAW::Harmony::Mode::Minor)
        .value("Dorian", iDAW::Harmony::Mode::Dorian)
        .value("Phrygian", iDAW::Harmony::Mode::Phrygian)
        .value("Lydian", iDAW::Harmony::Mode::Lydian)
        .value("Mixolydian", iDAW::Harmony::Mode::Mixolydian)
        .value("Locrian", iDAW::Harmony::Mode::Locrian)
        .export_values();
    
    // Chord struct
    py::class_<iDAW::Harmony::Chord>(harmony, "Chord")
        .def(py::init<>())
        .def_readwrite("root", &iDAW::Harmony::Chord::root)
        .def_readwrite("quality", &iDAW::Harmony::Chord::quality)
        .def_readwrite("bass", &iDAW::Harmony::Chord::bass)
        .def_readwrite("start_tick", &iDAW::Harmony::Chord::startTick)
        .def_readwrite("duration_ticks", &iDAW::Harmony::Chord::durationTicks)
        .def_readwrite("confidence", &iDAW::Harmony::Chord::confidence)
        .def("is_valid", &iDAW::Harmony::Chord::isValid)
        .def("get_name", &iDAW::Harmony::Chord::getName)
        .def("__str__", &iDAW::Harmony::Chord::getName);
    
    // KeyResult struct
    py::class_<iDAW::Harmony::KeyResult>(harmony, "KeyResult")
        .def(py::init<>())
        .def_readwrite("key_root", &iDAW::Harmony::KeyResult::keyRoot)
        .def_readwrite("mode", &iDAW::Harmony::KeyResult::mode)
        .def_readwrite("confidence", &iDAW::Harmony::KeyResult::confidence)
        .def("get_name", &iDAW::Harmony::KeyResult::getName);
    
    // RomanNumeralResult struct
    py::class_<iDAW::Harmony::RomanNumeralResult>(harmony, "RomanNumeralResult")
        .def(py::init<>())
        .def_readwrite("numeral", &iDAW::Harmony::RomanNumeralResult::numeral)
        .def_readwrite("is_diatonic", &iDAW::Harmony::RomanNumeralResult::isDiatonic)
        .def_readwrite("borrowed_from", &iDAW::Harmony::RomanNumeralResult::borrowedFrom);
    
    // Harmony functions
    harmony.def("midi_to_pitch_class", &iDAW::Harmony::midiToPitchClass,
                "Convert MIDI note to pitch class (0-11)",
                py::arg("midi_note"));
    
    harmony.def("detect_chord_from_notes", [](py::array_t<uint8_t> notes) {
        auto buf = notes.request();
        return iDAW::Harmony::detectChordFromNotes(
            static_cast<uint8_t*>(buf.ptr), buf.size);
    }, "Detect chord from MIDI notes", py::arg("notes"));
    
    // ========================================================================
    // Groove Core Bindings
    // ========================================================================
    
    auto groove = m.def_submodule("groove", "Groove extraction and application module");
    
    // GenreGroove enum
    py::enum_<iDAW::Groove::GenreGroove>(groove, "GenreGroove")
        .value("Straight", iDAW::Groove::GenreGroove::Straight)
        .value("Funk", iDAW::Groove::GenreGroove::Funk)
        .value("Jazz", iDAW::Groove::GenreGroove::Jazz)
        .value("BoomBap", iDAW::Groove::GenreGroove::BoomBap)
        .value("Dilla", iDAW::Groove::GenreGroove::Dilla)
        .value("Trap", iDAW::Groove::GenreGroove::Trap)
        .value("Rock", iDAW::Groove::GenreGroove::Rock)
        .value("HipHop", iDAW::Groove::GenreGroove::HipHop)
        .value("LoFi", iDAW::Groove::GenreGroove::LoFi)
        .export_values();
    
    // NoteEvent struct
    py::class_<iDAW::Groove::NoteEvent>(groove, "NoteEvent")
        .def(py::init<>())
        .def_readwrite("pitch", &iDAW::Groove::NoteEvent::pitch)
        .def_readwrite("velocity", &iDAW::Groove::NoteEvent::velocity)
        .def_readwrite("channel", &iDAW::Groove::NoteEvent::channel)
        .def_readwrite("start_tick", &iDAW::Groove::NoteEvent::startTick)
        .def_readwrite("duration_ticks", &iDAW::Groove::NoteEvent::durationTicks)
        .def_readwrite("deviation_ticks", &iDAW::Groove::NoteEvent::deviationTicks)
        .def_readwrite("is_ghost", &iDAW::Groove::NoteEvent::isGhost)
        .def_readwrite("is_accent", &iDAW::Groove::NoteEvent::isAccent);
    
    // GenreGrooveParams struct
    py::class_<iDAW::Groove::GenreGrooveParams>(groove, "GenreGrooveParams")
        .def(py::init<>())
        .def_readwrite("swing_factor", &iDAW::Groove::GenreGrooveParams::swingFactor)
        .def_readwrite("kick_offset", &iDAW::Groove::GenreGrooveParams::kickOffset)
        .def_readwrite("snare_offset", &iDAW::Groove::GenreGrooveParams::snareOffset)
        .def_readwrite("hihat_offset", &iDAW::Groove::GenreGrooveParams::hihatOffset)
        .def_readwrite("velocity_variation", &iDAW::Groove::GenreGrooveParams::velocityVariation)
        .def_readwrite("timing_variation", &iDAW::Groove::GenreGrooveParams::timingVariation);
    
    // VelocityStats struct
    py::class_<iDAW::Groove::VelocityStats>(groove, "VelocityStats")
        .def(py::init<>())
        .def_readwrite("min", &iDAW::Groove::VelocityStats::min)
        .def_readwrite("max", &iDAW::Groove::VelocityStats::max)
        .def_readwrite("mean", &iDAW::Groove::VelocityStats::mean)
        .def_readwrite("std_dev", &iDAW::Groove::VelocityStats::stdDev)
        .def_readwrite("ghost_count", &iDAW::Groove::VelocityStats::ghostCount)
        .def_readwrite("accent_count", &iDAW::Groove::VelocityStats::accentCount);
    
    // TimingStats struct
    py::class_<iDAW::Groove::TimingStats>(groove, "TimingStats")
        .def(py::init<>())
        .def_readwrite("mean_deviation_ticks", &iDAW::Groove::TimingStats::meanDeviationTicks)
        .def_readwrite("mean_deviation_ms", &iDAW::Groove::TimingStats::meanDeviationMs)
        .def_readwrite("max_deviation_ticks", &iDAW::Groove::TimingStats::maxDeviationTicks)
        .def_readwrite("max_deviation_ms", &iDAW::Groove::TimingStats::maxDeviationMs);
    
    // Groove functions
    groove.def("get_genre_groove_params", &iDAW::Groove::getGenreGrooveParams,
               "Get groove parameters for a genre", py::arg("genre"));
    
    groove.def("calculate_timing_deviation", &iDAW::Groove::calculateTimingDeviation,
               "Calculate timing deviation from grid",
               py::arg("start_tick"), py::arg("ppq"), py::arg("grid_resolution"));
    
    // ========================================================================
    // Diagnostics Core Bindings
    // ========================================================================
    
    auto diagnostics = m.def_submodule("diagnostics", "Progression diagnostics module");
    
    // ParsedChord struct
    py::class_<iDAW::Diagnostics::ParsedChord>(diagnostics, "ParsedChord")
        .def(py::init<>())
        .def_readwrite("root_num", &iDAW::Diagnostics::ParsedChord::rootNum)
        .def_readwrite("quality", &iDAW::Diagnostics::ParsedChord::quality)
        .def_readwrite("bass_note", &iDAW::Diagnostics::ParsedChord::bassNote)
        .def("is_valid", &iDAW::Diagnostics::ParsedChord::isValid)
        .def("get_root", [](const iDAW::Diagnostics::ParsedChord& c) {
            return std::string(c.getRoot());
        })
        .def("get_original", [](const iDAW::Diagnostics::ParsedChord& c) {
            return std::string(c.getOriginal());
        });
    
    // DiagnosticIssue struct
    py::class_<iDAW::Diagnostics::DiagnosticIssue>(diagnostics, "DiagnosticIssue")
        .def(py::init<>())
        .def_readwrite("severity", &iDAW::Diagnostics::DiagnosticIssue::severity)
        .def_readwrite("chord_index", &iDAW::Diagnostics::DiagnosticIssue::chordIndex)
        .def("get_description", [](const iDAW::Diagnostics::DiagnosticIssue& i) {
            return std::string(i.getDescription());
        });
    
    // DiagnosticSuggestion struct
    py::class_<iDAW::Diagnostics::DiagnosticSuggestion>(diagnostics, "DiagnosticSuggestion")
        .def(py::init<>())
        .def("get_description", [](const iDAW::Diagnostics::DiagnosticSuggestion& s) {
            return std::string(s.getDescription());
        })
        .def("get_technique", [](const iDAW::Diagnostics::DiagnosticSuggestion& s) {
            return std::string(s.getTechnique());
        });
    
    // ProgressionDiagnosis struct
    py::class_<iDAW::Diagnostics::ProgressionDiagnosis>(diagnostics, "ProgressionDiagnosis")
        .def(py::init<>())
        .def_readwrite("key_root", &iDAW::Diagnostics::ProgressionDiagnosis::keyRoot)
        .def_readwrite("key_mode", &iDAW::Diagnostics::ProgressionDiagnosis::keyMode)
        .def_readwrite("key_confidence", &iDAW::Diagnostics::ProgressionDiagnosis::keyConfidence)
        .def_readwrite("chord_count", &iDAW::Diagnostics::ProgressionDiagnosis::chordCount)
        .def_readwrite("issue_count", &iDAW::Diagnostics::ProgressionDiagnosis::issueCount)
        .def_readwrite("suggestion_count", &iDAW::Diagnostics::ProgressionDiagnosis::suggestionCount)
        .def_readwrite("borrowed_chord_count", &iDAW::Diagnostics::ProgressionDiagnosis::borrowedChordCount)
        .def("get_key_name", &iDAW::Diagnostics::ProgressionDiagnosis::getKeyName);
    
    // ReharmonizationStyle enum
    py::enum_<iDAW::Diagnostics::ReharmonizationStyle>(diagnostics, "ReharmonizationStyle")
        .value("Jazz", iDAW::Diagnostics::ReharmonizationStyle::Jazz)
        .value("Pop", iDAW::Diagnostics::ReharmonizationStyle::Pop)
        .value("RnB", iDAW::Diagnostics::ReharmonizationStyle::RnB)
        .value("Classical", iDAW::Diagnostics::ReharmonizationStyle::Classical)
        .value("Experimental", iDAW::Diagnostics::ReharmonizationStyle::Experimental)
        .export_values();
    
    // Diagnostics functions
    diagnostics.def("parse_chord_string", &iDAW::Diagnostics::parseChordString,
                    "Parse a chord string (e.g., 'Am7', 'Cmaj7')",
                    py::arg("chord_str"));
    
    diagnostics.def("diagnose_progression", &iDAW::Diagnostics::diagnoseProgression,
                    "Diagnose a chord progression for harmonic issues",
                    py::arg("progression_str"));
    
    diagnostics.def("note_name_to_pitch_class", &iDAW::Diagnostics::noteNameToPitchClass,
                    "Convert note name to pitch class",
                    py::arg("name"));
    
    // ========================================================================
    // OSC Handler Bindings
    // ========================================================================
    
    auto osc = m.def_submodule("osc", "OSC communication module");
    
    // OSC Message
    py::class_<iDAW::OSC::Message>(osc, "Message")
        .def(py::init<>())
        .def("set_address", &iDAW::OSC::Message::setAddress)
        .def("get_address", [](const iDAW::OSC::Message& m) {
            return std::string(m.getAddress());
        })
        .def("set_float", &iDAW::OSC::Message::setFloat)
        .def("get_float", &iDAW::OSC::Message::getFloat)
        .def("set_int", &iDAW::OSC::Message::setInt)
        .def("get_int", &iDAW::OSC::Message::getInt)
        .def("is_valid", &iDAW::OSC::Message::isValid);
    
    // OSC Handler
    py::class_<iDAW::OSC::OSCHandler>(osc, "OSCHandler")
        .def(py::init<>())
        .def("is_initialized", &iDAW::OSC::OSCHandler::isInitialized)
        .def("send_float", &iDAW::OSC::OSCHandler::sendFloat)
        .def("send_int", &iDAW::OSC::OSCHandler::sendInt)
        .def("send_chaos", &iDAW::OSC::OSCHandler::sendChaos)
        .def("send_complexity", &iDAW::OSC::OSCHandler::sendComplexity)
        .def("send_tempo", &iDAW::OSC::OSCHandler::sendTempo)
        .def("send_play", &iDAW::OSC::OSCHandler::sendPlay)
        .def("send_stop", &iDAW::OSC::OSCHandler::sendStop)
        .def("send_note_on", &iDAW::OSC::OSCHandler::sendNoteOn)
        .def("send_note_off", &iDAW::OSC::OSCHandler::sendNoteOff)
        .def("send_cc", &iDAW::OSC::OSCHandler::sendCC)
        .def("is_outgoing_empty", &iDAW::OSC::OSCHandler::isOutgoingEmpty)
        .def("is_incoming_empty", &iDAW::OSC::OSCHandler::isIncomingEmpty);
    
    // Global OSC handler getter
    osc.def("get_handler", &iDAW::OSC::getHandler,
            py::return_value_policy::reference,
            "Get the global OSC handler instance");
    
    // Common OSC addresses as module attributes
    osc.attr("ADDRESS_PLAY") = std::string(iDAW::OSC::Address::PLAY);
    osc.attr("ADDRESS_STOP") = std::string(iDAW::OSC::Address::STOP);
    osc.attr("ADDRESS_TEMPO") = std::string(iDAW::OSC::Address::TEMPO);
    osc.attr("ADDRESS_IDAW_CHAOS") = std::string(iDAW::OSC::Address::IDAW_CHAOS);
    osc.attr("ADDRESS_IDAW_COMPLEXITY") = std::string(iDAW::OSC::Address::IDAW_COMPLEXITY);
    osc.attr("ADDRESS_IDAW_FLIP") = std::string(iDAW::OSC::Address::IDAW_FLIP);
    osc.attr("ADDRESS_MIDI_NOTE") = std::string(iDAW::OSC::Address::MIDI_NOTE);
    osc.attr("ADDRESS_MIDI_CC") = std::string(iDAW::OSC::Address::MIDI_CC);
}

#else
// When not building Python module, provide a stub
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
#endif
