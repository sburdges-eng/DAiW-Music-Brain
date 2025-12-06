/**
 * PyBindings.cpp - Main pybind11 module definition for iDAW Bridge
 * 
 * Exposes C++ Harmony, Groove, and Diagnostics engines to Python
 * for high-performance music analysis in the DAiW-Music-Brain toolkit.
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>

#include "harmony/HarmonyEngine.h"

// MIDI constants
constexpr int DEFAULT_DURATION_TICKS = 480;  // One quarter note at 480 PPQ
constexpr int DEFAULT_CHANNEL = 0;
#include "groove/GrooveEngine.h"
#include "diagnostics/DiagnosticsEngine.h"
#include "MemoryManager.h"
#include "Version.h"

namespace py = pybind11;

// Forward declarations for submodule bindings
void init_harmony_bindings(py::module_& m);
void init_groove_bindings(py::module_& m);
void init_diagnostics_bindings(py::module_& m);

/**
 * Main module definition
 */
PYBIND11_MODULE(idaw_bridge, m) {
    m.doc() = R"pbdoc(
        iDAW Bridge - C++ Performance Core for DAiW-Music-Brain
        ========================================================
        
        This module provides high-performance C++ implementations of:
        - Harmony analysis (chord detection, key detection, progression analysis)
        - Groove extraction and application (timing, velocity, swing)
        - Diagnostics (progression diagnosis, rule-break identification)
        
        Usage:
            import idaw_bridge
            
            # Harmony
            result = idaw_bridge.diagnose_progression("F-C-Am-Dm")
            print(result['key'], result['issues'])
            
            # Groove
            groove = idaw_bridge.extract_groove(notes, ppq=480, tempo=120.0)
            humanized = idaw_bridge.humanize(notes, complexity=0.5, vulnerability=0.5)
    )pbdoc";
    
    // Version info
    m.attr("__version__") = IDAW_VERSION_STRING;
    m.attr("__platform__") = IDAW_PLATFORM_STRING;
    m.attr("__architecture__") = IDAW_ARCH_STRING;
    
    // Create submodules
    py::module_ harmony_m = m.def_submodule("harmony", "Harmony analysis module");
    py::module_ groove_m = m.def_submodule("groove", "Groove extraction and application module");
    py::module_ diagnostics_m = m.def_submodule("diagnostics", "Progression diagnostics module");
    
    // Initialize submodule bindings
    init_harmony_bindings(harmony_m);
    init_groove_bindings(groove_m);
    init_diagnostics_bindings(diagnostics_m);
    
    // ========================================================================
    // Top-level convenience functions
    // ========================================================================
    
    m.def("diagnose_progression", [](const std::string& progression) {
        auto& engine = iDAW::harmony::HarmonyEngine::getInstance();
        auto result = engine.diagnoseProgression(progression);
        
        py::dict output;
        output["key"] = result.detectedKey.toString();
        output["chords"] = result.chordNames;
        output["issues"] = result.issues;
        output["suggestions"] = result.suggestions;
        output["success"] = result.success;
        
        py::dict borrowed;
        for (const auto& [chord, source] : result.borrowedChords) {
            borrowed[py::str(chord)] = source;
        }
        output["borrowed_chords"] = borrowed;
        
        return output;
    }, py::arg("progression"),
    R"pbdoc(
        Diagnose a chord progression string.
        
        Args:
            progression: Chord progression (e.g., "F-C-Am-Dm")
        
        Returns:
            dict with 'key', 'chords', 'issues', 'suggestions', 'borrowed_chords'
    )pbdoc");
    
    m.def("detect_chord", [](const std::vector<int>& midi_notes) {
        auto& engine = iDAW::harmony::HarmonyEngine::getInstance();
        auto chord = engine.detectChord(midi_notes);
        
        py::dict output;
        output["name"] = chord.name();
        output["root"] = chord.root();
        output["quality"] = iDAW::harmony::qualityToString(chord.quality());
        output["valid"] = chord.isValid();
        
        return output;
    }, py::arg("midi_notes"),
    R"pbdoc(
        Detect chord from MIDI note numbers.
        
        Args:
            midi_notes: List of MIDI note numbers (e.g., [60, 64, 67] for C major)
        
        Returns:
            dict with 'name', 'root', 'quality', 'valid'
    )pbdoc");
    
    m.def("extract_groove", [](
        const std::vector<py::dict>& notes,
        int ppq,
        float tempo,
        int quantize_resolution,
        int ghost_threshold,
        int accent_threshold) {
        
        // Convert Python dicts to MidiNote structs
        std::vector<iDAW::groove::MidiNote> midiNotes;
        for (const auto& note : notes) {
            iDAW::groove::MidiNote mn;
            mn.pitch = note["pitch"].cast<int>();
            mn.velocity = note["velocity"].cast<int>();
            mn.startTick = note["start_tick"].cast<int>();
            mn.durationTicks = note.contains("duration_ticks") 
                ? note["duration_ticks"].cast<int>() : DEFAULT_DURATION_TICKS;
            mn.channel = note.contains("channel") ? note["channel"].cast<int>() : DEFAULT_CHANNEL;
            midiNotes.push_back(mn);
        }
        
        iDAW::groove::ExtractionSettings settings;
        settings.quantizeResolution = quantize_resolution;
        settings.ghostThreshold = ghost_threshold;
        settings.accentThreshold = accent_threshold;
        
        auto& engine = iDAW::groove::GrooveEngine::getInstance();
        auto groove = engine.extractGroove(midiNotes, ppq, tempo, settings);
        
        py::dict output;
        output["name"] = groove.name();
        output["swing_factor"] = groove.swingFactor();
        output["timing_deviations"] = groove.timingDeviations();
        output["velocity_curve"] = groove.velocityCurve();
        
        py::dict velStats;
        velStats["min"] = groove.velocityStats().min;
        velStats["max"] = groove.velocityStats().max;
        velStats["mean"] = groove.velocityStats().mean;
        velStats["ghost_count"] = groove.velocityStats().ghostCount;
        velStats["accent_count"] = groove.velocityStats().accentCount;
        output["velocity_stats"] = velStats;
        
        py::dict timeStats;
        timeStats["mean_deviation_ticks"] = groove.timingStats().meanDeviationTicks;
        timeStats["mean_deviation_ms"] = groove.timingStats().meanDeviationMs;
        timeStats["max_deviation_ticks"] = groove.timingStats().maxDeviationTicks;
        output["timing_stats"] = timeStats;
        
        return output;
    },
    py::arg("notes"),
    py::arg("ppq") = 480,
    py::arg("tempo") = 120.0f,
    py::arg("quantize_resolution") = 16,
    py::arg("ghost_threshold") = 40,
    py::arg("accent_threshold") = 100,
    R"pbdoc(
        Extract groove pattern from MIDI notes.
        
        Args:
            notes: List of note dicts with 'pitch', 'velocity', 'start_tick'
            ppq: Pulses per quarter note (default: 480)
            tempo: Tempo in BPM (default: 120.0)
            quantize_resolution: Grid resolution (default: 16 for 16th notes)
            ghost_threshold: Velocity below this is ghost note (default: 40)
            accent_threshold: Velocity above this is accent (default: 100)
        
        Returns:
            dict with groove template data
    )pbdoc");
    
    m.def("humanize", [](
        std::vector<py::dict>& notes,
        float complexity,
        float vulnerability,
        int ppq,
        int seed) {
        
        // Convert Python dicts to MidiNote structs
        std::vector<iDAW::groove::MidiNote> midiNotes;
        for (const auto& note : notes) {
            iDAW::groove::MidiNote mn;
            mn.pitch = note["pitch"].cast<int>();
            mn.velocity = note["velocity"].cast<int>();
            mn.startTick = note["start_tick"].cast<int>();
            mn.durationTicks = note.contains("duration_ticks") 
                ? note["duration_ticks"].cast<int>() : DEFAULT_DURATION_TICKS;
            mn.channel = note.contains("channel") ? note["channel"].cast<int>() : DEFAULT_CHANNEL;
            midiNotes.push_back(mn);
        }
        
        auto& engine = iDAW::groove::GrooveEngine::getInstance();
        engine.humanize(midiNotes, complexity, vulnerability, ppq, seed);
        
        // Convert back to Python dicts
        py::list output;
        for (const auto& mn : midiNotes) {
            py::dict note;
            note["pitch"] = mn.pitch;
            note["velocity"] = mn.velocity;
            note["start_tick"] = mn.startTick;
            note["duration_ticks"] = mn.durationTicks;
            note["channel"] = mn.channel;
            output.append(note);
        }
        
        return output;
    },
    py::arg("notes"),
    py::arg("complexity") = 0.5f,
    py::arg("vulnerability") = 0.5f,
    py::arg("ppq") = 480,
    py::arg("seed") = -1,
    R"pbdoc(
        Humanize MIDI notes by adding timing and velocity variations.
        
        Args:
            notes: List of note dicts with 'pitch', 'velocity', 'start_tick'
            complexity: Timing variation amount (0.0-1.0, default: 0.5)
            vulnerability: Velocity variation amount (0.0-1.0, default: 0.5)
            ppq: Pulses per quarter note (default: 480)
            seed: Random seed for reproducibility (-1 for random)
        
        Returns:
            List of humanized note dicts
    )pbdoc");
    
    m.def("get_genre_groove", [](const std::string& genre) {
        auto& engine = iDAW::groove::GrooveEngine::getInstance();
        auto groove = engine.getGenreTemplate(genre);
        
        py::dict output;
        output["name"] = groove.name();
        output["swing_factor"] = groove.swingFactor();
        output["timing_deviations"] = groove.timingDeviations();
        output["velocity_curve"] = groove.velocityCurve();
        output["tempo_bpm"] = groove.tempoBpm();
        
        return output;
    }, py::arg("genre"),
    R"pbdoc(
        Get built-in groove template for a genre.
        
        Args:
            genre: Genre name ('funk', 'jazz', 'rock', 'hiphop', 'lofi', 
                   'boombap', 'dilla', 'trap', 'straight')
        
        Returns:
            dict with groove template data
    )pbdoc");
    
    m.def("list_genre_presets", []() {
        auto& engine = iDAW::groove::GrooveEngine::getInstance();
        return engine.listGenrePresets();
    },
    R"pbdoc(
        List available genre groove presets.
        
        Returns:
            List of genre preset names
    )pbdoc");
    
    m.def("suggest_rule_breaks", [](const std::string& emotion) {
        auto& engine = iDAW::diagnostics::DiagnosticsEngine::getInstance();
        auto suggestions = engine.suggestRuleBreaks(emotion);
        
        py::list output;
        for (const auto& rb : suggestions) {
            py::dict item;
            item["category"] = iDAW::diagnostics::ruleBreakToString(rb.category);
            item["chord"] = rb.chordName;
            item["context"] = rb.context;
            item["emotional_effect"] = rb.emotionalEffect;
            item["justification"] = rb.justification;
            output.append(item);
        }
        
        return output;
    }, py::arg("emotion"),
    R"pbdoc(
        Suggest rule breaks for emotional effect.
        
        Args:
            emotion: Emotion to suggest for ('grief', 'anxiety', 'anger', 
                     'nostalgia', 'hope', etc.)
        
        Returns:
            List of rule break suggestions with emotional justifications
    )pbdoc");
    
    // ========================================================================
    // Memory management (for diagnostics)
    // ========================================================================
    
    m.def("is_audio_thread", []() {
        return iDAW::MemoryManager::getInstance().isAudioThread();
    }, "Check if current thread is registered as audio thread");
}
