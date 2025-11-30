/**
 * DAiW Logic Bridge - Python/JUCE Integration
 *
 * Bridges the Python music_brain modules with the C++ JUCE plugin.
 * Uses pybind11 embedded interpreter.
 */

#pragma once

#include <pybind11/embed.h>
#include <pybind11/stl.h>
#include <juce_core/juce_core.h>

#include <string>
#include <memory>
#include <mutex>

namespace py = pybind11;

namespace daiw {
namespace bridge {

/**
 * LogicBridge - Manages Python interpreter and module access.
 *
 * Thread-safe singleton that initializes the Python interpreter once
 * and provides access to DAiW Python modules from C++.
 */
class LogicBridge {
public:
    static LogicBridge& getInstance() {
        static LogicBridge instance;
        return instance;
    }

    // Delete copy/move
    LogicBridge(const LogicBridge&) = delete;
    LogicBridge& operator=(const LogicBridge&) = delete;

    /**
     * Initialize the Python interpreter and load modules.
     * Call once at plugin startup.
     */
    void initialize() {
        std::lock_guard<std::mutex> lock(mutex_);

        if (initialized_) return;

        // 1. Start the Interpreter
        py::initialize_interpreter();

        // 2. Locate the "Resources" folder relative to the Executable
        auto appDir = juce::File::getSpecialLocation(
            juce::File::currentExecutableFile
        ).getParentDirectory();

        // On macOS, we might be inside Contents/MacOS, so go up to Resources
        #if JUCE_MAC
            auto scriptsDir = appDir.getParentDirectory()
                                    .getChildFile("Resources")
                                    .getChildFile("scripts");
        #elif JUCE_WINDOWS
            auto scriptsDir = appDir.getChildFile("resources")
                                    .getChildFile("scripts");
        #else
            auto scriptsDir = appDir.getChildFile("resources")
                                    .getChildFile("scripts");
        #endif

        // 3. INJECT into sys.path
        py::module::import("sys")
            .attr("path")
            .attr("append")(scriptsDir.getFullPathName().toStdString());

        // Also add the music_brain package path
        auto musicBrainDir = scriptsDir.getParentDirectory()
                                       .getChildFile("music_brain");
        if (musicBrainDir.exists()) {
            py::module::import("sys")
                .attr("path")
                .attr("append")(musicBrainDir.getFullPathName().toStdString());
        }

        // 4. Now we can safely import
        try {
            mainModule_ = py::module::import("daiw_logic");
            intentModule_ = py::module::import("music_brain.session.intent_schema");
            grooveModule_ = py::module::import("music_brain.groove.humanizer");
            harmonyModule_ = py::module::import("music_brain.structure.chord");

            initialized_ = true;
            DBG("DAiW Python Bridge initialized successfully");

        } catch (py::error_already_set& e) {
            DBG("PYTHON INITIALIZATION ERROR: " << e.what());
            initialized_ = false;
        }
    }

    /**
     * Shutdown the Python interpreter.
     * Call once at plugin shutdown.
     */
    void shutdown() {
        std::lock_guard<std::mutex> lock(mutex_);

        if (!initialized_) return;

        mainModule_ = py::none();
        intentModule_ = py::none();
        grooveModule_ = py::none();
        harmonyModule_ = py::none();

        py::finalize_interpreter();
        initialized_ = false;

        DBG("DAiW Python Bridge shutdown");
    }

    bool isInitialized() const { return initialized_; }

    // ==========================================================================
    // Intent System Access
    // ==========================================================================

    /**
     * Create a new song intent from Phase 0 data.
     */
    py::object createIntent(const std::string& coreEvent,
                            const std::string& coreResistance,
                            const std::string& coreLonging) {
        std::lock_guard<std::mutex> lock(mutex_);

        if (!initialized_) return py::none();

        try {
            auto SongRoot = intentModule_.attr("SongRoot");
            return SongRoot(
                py::arg("core_event") = coreEvent,
                py::arg("core_resistance") = coreResistance,
                py::arg("core_longing") = coreLonging
            );
        } catch (py::error_already_set& e) {
            DBG("Python error creating intent: " << e.what());
            return py::none();
        }
    }

    // ==========================================================================
    // Groove System Access
    // ==========================================================================

    /**
     * Humanize MIDI notes using Python humanizer.
     */
    py::object humanizeMidi(py::list notes,
                           const std::string& style = "tight_pocket",
                           float intensity = 1.0f) {
        std::lock_guard<std::mutex> lock(mutex_);

        if (!initialized_) return py::none();

        try {
            auto humanize_midi = grooveModule_.attr("humanize_midi");
            return humanize_midi(notes, style, intensity);
        } catch (py::error_already_set& e) {
            DBG("Python error humanizing MIDI: " << e.what());
            return py::none();
        }
    }

    // ==========================================================================
    // Harmony Analysis Access
    // ==========================================================================

    /**
     * Analyze a chord progression string.
     */
    py::object analyzeProgression(const std::string& progression) {
        std::lock_guard<std::mutex> lock(mutex_);

        if (!initialized_) return py::none();

        try {
            auto diagnose = harmonyModule_.attr("diagnose_progression");
            return diagnose(progression);
        } catch (py::error_already_set& e) {
            DBG("Python error analyzing progression: " << e.what());
            return py::none();
        }
    }

    /**
     * Execute arbitrary Python code (for advanced use).
     */
    py::object execute(const std::string& code) {
        std::lock_guard<std::mutex> lock(mutex_);

        if (!initialized_) return py::none();

        try {
            return py::eval(code);
        } catch (py::error_already_set& e) {
            DBG("Python execution error: " << e.what());
            return py::none();
        }
    }

private:
    LogicBridge() : initialized_(false) {}

    ~LogicBridge() {
        if (initialized_) {
            shutdown();
        }
    }

    std::mutex mutex_;
    bool initialized_;

    py::object mainModule_;
    py::object intentModule_;
    py::object grooveModule_;
    py::object harmonyModule_;
};

// =============================================================================
// RAII Guard for Python GIL
// =============================================================================

/**
 * Acquires the Python GIL for the duration of its scope.
 * Use when calling Python from non-main threads.
 */
class GILGuard {
public:
    GILGuard() : state_(PyGILState_Ensure()) {}
    ~GILGuard() { PyGILState_Release(state_); }

    GILGuard(const GILGuard&) = delete;
    GILGuard& operator=(const GILGuard&) = delete;

private:
    PyGILState_STATE state_;
};

} // namespace bridge
} // namespace daiw
