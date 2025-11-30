/**
 * PythonBridge.cpp - Implementation of Python Bridge for iDAW
 */

#include "PythonBridge.h"
#include <fstream>
#include <sstream>
#include <nlohmann/json.hpp>  // For JSON parsing

using json = nlohmann::json;

namespace iDAW {

// ============================================================================
// PythonBridge Implementation
// ============================================================================

PythonBridge& PythonBridge::getInstance() {
    static PythonBridge instance;
    return instance;
}

PythonBridge::PythonBridge() = default;

PythonBridge::~PythonBridge() {
    shutdown();
}

bool PythonBridge::initialize(const std::string& pythonPath,
                               const std::string& genresJsonPath) {
    // Ensure we're not on audio thread
    MemoryManager::getInstance().assertNotAudioThread();
    
    std::lock_guard<std::mutex> lock(m_pythonMutex);
    
    if (m_initialized) {
        return true;  // Already initialized
    }
    
    try {
        // Initialize Python interpreter in Side B memory context
        m_interpreter = std::make_unique<py::scoped_interpreter>();
        
        // Add music_brain path to Python path
        py::module_::import("sys").attr("path").attr("insert")(0, pythonPath);
        
        // Import the orchestrator module
        m_orchestratorModule = py::module_::import("music_brain.orchestrator");
        
        // Create pipeline for processing
        auto Pipeline = m_orchestratorModule.attr("Pipeline");
        auto IntentProcessor = py::module_::import(
            "music_brain.orchestrator.processors").attr("IntentProcessor");
        auto HarmonyProcessor = py::module_::import(
            "music_brain.orchestrator.processors").attr("HarmonyProcessor");
        auto GrooveProcessor = py::module_::import(
            "music_brain.orchestrator.processors").attr("GrooveProcessor");
        
        m_pipeline = Pipeline("idaw_pipeline");
        m_pipeline.attr("add_stage")("intent", IntentProcessor());
        m_pipeline.attr("add_stage")("harmony", HarmonyProcessor());
        m_pipeline.attr("add_stage")("groove", GrooveProcessor());
        
        // Load genres JSON
        if (!loadGenresJson(genresJsonPath)) {
            return false;
        }
        
        m_initialized = true;
        return true;
        
    } catch (const py::error_already_set& e) {
        // Python exception
        m_initialized = false;
        return false;
    } catch (const std::exception& e) {
        m_initialized = false;
        return false;
    }
}

void PythonBridge::shutdown() {
    std::lock_guard<std::mutex> lock(m_pythonMutex);
    
    if (!m_initialized) return;
    
    m_pipeline = py::none();
    m_orchestratorModule = py::none();
    m_genres.clear();
    m_interpreter.reset();
    m_initialized = false;
}

bool PythonBridge::loadGenresJson(const std::string& path) {
    try {
        std::ifstream file(path);
        if (!file.is_open()) {
            return false;
        }
        
        json genresData;
        file >> genresData;
        
        // Convert to Python dicts and store
        for (auto& [name, data] : genresData["genres"].items()) {
            py::dict genreDict;
            // Convert JSON to Python dict recursively
            std::function<py::object(const json&)> jsonToPy = [&](const json& j) -> py::object {
                if (j.is_null()) return py::none();
                if (j.is_boolean()) return py::bool_(j.get<bool>());
                if (j.is_number_integer()) return py::int_(j.get<int>());
                if (j.is_number_float()) return py::float_(j.get<double>());
                if (j.is_string()) return py::str(j.get<std::string>());
                if (j.is_array()) {
                    py::list list;
                    for (const auto& item : j) {
                        list.append(jsonToPy(item));
                    }
                    return list;
                }
                if (j.is_object()) {
                    py::dict dict;
                    for (auto& [k, v] : j.items()) {
                        dict[py::str(k)] = jsonToPy(v);
                    }
                    return dict;
                }
                return py::none();
            };
            
            m_genres[name] = jsonToPy(data).cast<py::dict>();
        }
        
        return true;
        
    } catch (const std::exception& e) {
        return false;
    }
}

MidiBuffer PythonBridge::call_iMIDI(const KnobState& knobs,
                                     const std::string& textPrompt) {
    // SAFETY: Entire Python call wrapped in try-catch
    try {
        // Ensure not on audio thread
        MemoryManager::getInstance().assertNotAudioThread();
        
        std::lock_guard<std::mutex> lock(m_pythonMutex);
        
        if (!m_initialized) {
            return createFailsafeMidiBuffer();
        }
        
        // SAFETY: Sanitize user input before passing to Python
        std::string safePrompt = sanitizeInput(textPrompt);
        if (safePrompt.empty()) {
            // Empty prompt after sanitization - use default
            safePrompt = "create music";
        }
        
        // Acquire GIL for Python operations
        py::gil_scoped_acquire gil;
        
        // Prepare input data
        py::dict inputData;
        inputData["text_prompt"] = safePrompt;  // Use sanitized input
        inputData["knobs"] = knobs.toPyDict();
        inputData["genres"] = py::dict();  // Pass available genres
        for (const auto& [name, data] : m_genres) {
            inputData["genres"][py::str(name)] = data;
        }
        
        // Check for innovation protocol
        if (shouldTriggerInnovation()) {
            inputData["trigger_innovation"] = true;
            resetRejectionCounter();
        }
        
        // Create orchestrator and execute pipeline
        auto AIOrchestrator = m_orchestratorModule.attr("AIOrchestrator");
        auto orchestrator = AIOrchestrator();
        
        // Execute asynchronously using asyncio
        auto asyncio = py::module_::import("asyncio");
        auto loop = asyncio.attr("new_event_loop")();
        auto result = loop.attr("run_until_complete")(
            orchestrator.attr("execute")(m_pipeline, inputData)
        );
        loop.attr("close")();
        
        // Parse result
        MidiBuffer buffer = parsePythonResult(result);
        
        // Trigger Ghost Hands callback if we have suggested values
        if (buffer.success && m_ghostHandsCallback) {
            m_ghostHandsCallback(buffer.suggestedChaos, buffer.suggestedComplexity);
        }
        
        return buffer;
        
    } catch (const py::error_already_set& e) {
        // Python exception - return fail-safe C Major chord
        MidiBuffer failsafe = createFailsafeMidiBuffer();
        failsafe.errorMessage = std::string("Python error: ") + e.what();
        return failsafe;
        
    } catch (const std::exception& e) {
        // C++ exception - return fail-safe C Major chord
        MidiBuffer failsafe = createFailsafeMidiBuffer();
        failsafe.errorMessage = std::string("C++ error: ") + e.what();
        return failsafe;
    }
}

std::future<MidiBuffer> PythonBridge::call_iMIDI_async(const KnobState& knobs,
                                                        const std::string& textPrompt) {
    return std::async(std::launch::async, [this, knobs, textPrompt]() {
        return call_iMIDI(knobs, textPrompt);
    });
}

MidiBuffer PythonBridge::parsePythonResult(const py::object& result) {
    MidiBuffer buffer;
    
    try {
        // Check if execution was successful
        buffer.success = result.attr("success").cast<bool>();
        
        if (!buffer.success) {
            buffer.errorMessage = result.attr("error").cast<std::string>();
            return createFailsafeMidiBuffer();
        }
        
        // Get final output
        auto finalOutput = result.attr("final_output");
        
        // Extract MIDI events if present
        if (py::hasattr(finalOutput, "midi_events")) {
            auto events = finalOutput.attr("midi_events").cast<py::list>();
            for (const auto& evt : events) {
                MidiEvent midiEvent;
                midiEvent.status = evt.attr("status").cast<uint8_t>();
                midiEvent.data1 = evt.attr("data1").cast<uint8_t>();
                midiEvent.data2 = evt.attr("data2").cast<uint8_t>();
                midiEvent.timestamp = evt.attr("timestamp").cast<uint32_t>();
                buffer.events.push_back(midiEvent);
            }
        }
        
        // Extract Ghost Hands suggestions from context
        auto context = result.attr("context");
        if (context && !context.is_none()) {
            auto sharedData = context.attr("shared_data").cast<py::dict>();
            
            if (sharedData.contains("suggested_chaos")) {
                buffer.suggestedChaos = sharedData["suggested_chaos"].cast<float>();
            }
            if (sharedData.contains("suggested_complexity")) {
                buffer.suggestedComplexity = sharedData["suggested_complexity"].cast<float>();
            }
            if (sharedData.contains("genre")) {
                buffer.genre = sharedData["genre"].cast<std::string>();
            }
        }
        
        // If no MIDI events generated, use the harmony/groove data
        if (buffer.events.empty()) {
            // Generate basic MIDI from harmony output
            auto harmony = context.attr("get_shared")("harmony");
            if (harmony && !harmony.is_none()) {
                // Create placeholder MIDI based on chord progression
                // This would be expanded to full MIDI generation
                buffer = createFailsafeMidiBuffer();
                buffer.success = true;
                buffer.errorMessage = "";
            }
        }
        
        return buffer;
        
    } catch (const std::exception& e) {
        return createFailsafeMidiBuffer();
    }
}

void PythonBridge::setGhostHandsCallback(GhostHandsCallback callback) {
    m_ghostHandsCallback = std::move(callback);
}

void PythonBridge::registerRejection() {
    m_rejectionCount++;
}

void PythonBridge::resetRejectionCounter() {
    m_rejectionCount = 0;
}

} // namespace iDAW
