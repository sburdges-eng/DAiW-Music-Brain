/**
 * PyGroove.cpp - pybind11 bindings for Groove module
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "groove/GrooveEngine.h"
#include "groove/GrooveTemplate.h"

namespace py = pybind11;

void init_groove_bindings(py::module_& m) {
    using namespace iDAW::groove;
    
    // GenrePreset enum
    py::enum_<GenrePreset>(m, "GenrePreset")
        .value("Funk", GenrePreset::Funk)
        .value("Jazz", GenrePreset::Jazz)
        .value("Rock", GenrePreset::Rock)
        .value("HipHop", GenrePreset::HipHop)
        .value("LoFi", GenrePreset::LoFi)
        .value("BoomBap", GenrePreset::BoomBap)
        .value("Dilla", GenrePreset::Dilla)
        .value("Trap", GenrePreset::Trap)
        .value("Straight", GenrePreset::Straight);
    
    // HumanizeStyle enum
    py::enum_<HumanizeStyle>(m, "HumanizeStyle")
        .value("Tight", HumanizeStyle::Tight)
        .value("Natural", HumanizeStyle::Natural)
        .value("Loose", HumanizeStyle::Loose)
        .value("Drunk", HumanizeStyle::Drunk)
        .value("Robot", HumanizeStyle::Robot);
    
    // NoteEvent struct
    py::class_<NoteEvent>(m, "NoteEvent")
        .def(py::init<>())
        .def_readwrite("pitch", &NoteEvent::pitch)
        .def_readwrite("velocity", &NoteEvent::velocity)
        .def_readwrite("start_tick", &NoteEvent::startTick)
        .def_readwrite("duration_ticks", &NoteEvent::durationTicks)
        .def_readwrite("channel", &NoteEvent::channel)
        .def_readwrite("deviation_ticks", &NoteEvent::deviationTicks)
        .def_readwrite("is_ghost", &NoteEvent::isGhost)
        .def_readwrite("is_accent", &NoteEvent::isAccent);
    
    // VelocityStats struct
    py::class_<VelocityStats>(m, "VelocityStats")
        .def(py::init<>())
        .def_readwrite("min", &VelocityStats::min)
        .def_readwrite("max", &VelocityStats::max)
        .def_readwrite("mean", &VelocityStats::mean)
        .def_readwrite("std_dev", &VelocityStats::stdDev)
        .def_readwrite("ghost_count", &VelocityStats::ghostCount)
        .def_readwrite("accent_count", &VelocityStats::accentCount);
    
    // TimingStats struct
    py::class_<TimingStats>(m, "TimingStats")
        .def(py::init<>())
        .def_readwrite("mean_deviation_ticks", &TimingStats::meanDeviationTicks)
        .def_readwrite("mean_deviation_ms", &TimingStats::meanDeviationMs)
        .def_readwrite("max_deviation_ticks", &TimingStats::maxDeviationTicks)
        .def_readwrite("max_deviation_ms", &TimingStats::maxDeviationMs)
        .def_readwrite("std_deviation_ticks", &TimingStats::stdDeviationTicks)
        .def_readwrite("std_deviation_ms", &TimingStats::stdDeviationMs);
    
    // GrooveTemplate class
    py::class_<GrooveTemplate>(m, "GrooveTemplate")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&>(),
             py::arg("name"), py::arg("source_file") = "")
        .def_property("name", &GrooveTemplate::name, &GrooveTemplate::setName)
        .def_property("source_file", &GrooveTemplate::sourceFile, &GrooveTemplate::setSourceFile)
        .def_property("ppq", &GrooveTemplate::ppq, &GrooveTemplate::setPpq)
        .def_property("tempo_bpm", &GrooveTemplate::tempoBpm, &GrooveTemplate::setTempoBpm)
        .def_property("swing_factor", &GrooveTemplate::swingFactor, &GrooveTemplate::setSwingFactor)
        .def_property("timing_deviations", 
            &GrooveTemplate::timingDeviations, &GrooveTemplate::setTimingDeviations)
        .def_property("velocity_curve", 
            &GrooveTemplate::velocityCurve, &GrooveTemplate::setVelocityCurve)
        .def_property_readonly("velocity_stats", &GrooveTemplate::velocityStats)
        .def_property_readonly("timing_stats", &GrooveTemplate::timingStats)
        .def_property_readonly("events", &GrooveTemplate::events)
        .def("add_event", &GrooveTemplate::addEvent, py::arg("event"))
        .def("is_valid", &GrooveTemplate::isValid)
        .def("to_map", &GrooveTemplate::toMap)
        .def_static("from_map", &GrooveTemplate::fromMap, py::arg("data"))
        .def("time_signature", &GrooveTemplate::timeSignature)
        .def("set_time_signature", &GrooveTemplate::setTimeSignature,
             py::arg("numerator"), py::arg("denominator"))
        .def("__repr__", [](const GrooveTemplate& g) {
            return "<GrooveTemplate '" + g.name() + "' swing=" + 
                   std::to_string(g.swingFactor()) + ">";
        });
    
    // MidiNote struct
    py::class_<MidiNote>(m, "MidiNote")
        .def(py::init<>())
        .def_readwrite("pitch", &MidiNote::pitch)
        .def_readwrite("velocity", &MidiNote::velocity)
        .def_readwrite("start_tick", &MidiNote::startTick)
        .def_readwrite("duration_ticks", &MidiNote::durationTicks)
        .def_readwrite("channel", &MidiNote::channel)
        .def("__repr__", [](const MidiNote& n) {
            return "<MidiNote pitch=" + std::to_string(n.pitch) + 
                   " vel=" + std::to_string(n.velocity) +
                   " tick=" + std::to_string(n.startTick) + ">";
        });
    
    // ExtractionSettings struct
    py::class_<ExtractionSettings>(m, "ExtractionSettings")
        .def(py::init<>())
        .def_readwrite("quantize_resolution", &ExtractionSettings::quantizeResolution)
        .def_readwrite("ghost_threshold", &ExtractionSettings::ghostThreshold)
        .def_readwrite("accent_threshold", &ExtractionSettings::accentThreshold)
        .def_readwrite("detect_swing", &ExtractionSettings::detectSwing)
        .def_readwrite("normalize_velocity", &ExtractionSettings::normalizeVelocity);
    
    // ApplicationSettings struct
    py::class_<ApplicationSettings>(m, "ApplicationSettings")
        .def(py::init<>())
        .def_readwrite("intensity", &ApplicationSettings::intensity)
        .def_readwrite("apply_timing", &ApplicationSettings::applyTiming)
        .def_readwrite("apply_velocity", &ApplicationSettings::applyVelocity)
        .def_readwrite("apply_swing", &ApplicationSettings::applySwing)
        .def_readwrite("preserve_ghosts", &ApplicationSettings::preserveGhosts);
    
    // GrooveEngine singleton access
    m.def("get_engine", []() -> GrooveEngine& {
        return GrooveEngine::getInstance();
    }, py::return_value_policy::reference,
    "Get the GrooveEngine singleton instance");
    
    // Convenience functions
    m.def("extract_groove", [](
        const std::vector<MidiNote>& notes,
        int ppq,
        float tempo,
        const ExtractionSettings& settings) {
        return GrooveEngine::getInstance().extractGroove(notes, ppq, tempo, settings);
    },
    py::arg("notes"),
    py::arg("ppq") = 480,
    py::arg("tempo") = 120.0f,
    py::arg("settings") = ExtractionSettings{},
    "Extract groove template from MIDI notes");
    
    m.def("apply_groove", [](
        std::vector<MidiNote>& notes,
        const GrooveTemplate& groove,
        int ppq,
        const ApplicationSettings& settings) {
        GrooveEngine::getInstance().applyGroove(notes, groove, ppq, settings);
    },
    py::arg("notes"),
    py::arg("groove"),
    py::arg("ppq") = 480,
    py::arg("settings") = ApplicationSettings{},
    "Apply groove template to MIDI notes (in-place)");
    
    m.def("humanize", [](
        std::vector<MidiNote>& notes,
        float complexity,
        float vulnerability,
        int ppq,
        int seed) {
        GrooveEngine::getInstance().humanize(notes, complexity, vulnerability, ppq, seed);
    },
    py::arg("notes"),
    py::arg("complexity") = 0.5f,
    py::arg("vulnerability") = 0.5f,
    py::arg("ppq") = 480,
    py::arg("seed") = -1,
    "Humanize MIDI notes by adding timing/velocity variations (in-place)");
    
    m.def("calculate_swing", [](const std::vector<MidiNote>& notes, int ppq) {
        return GrooveEngine::getInstance().calculateSwing(notes, ppq);
    },
    py::arg("notes"),
    py::arg("ppq") = 480,
    "Calculate swing factor from MIDI notes");
    
    m.def("quantize", [](std::vector<MidiNote>& notes, int ppq, int resolution) {
        GrooveEngine::getInstance().quantize(notes, ppq, resolution);
    },
    py::arg("notes"),
    py::arg("ppq") = 480,
    py::arg("resolution") = 16,
    "Quantize notes to grid (in-place)");
    
    m.def("get_genre_template", [](const std::string& genre) {
        return GrooveEngine::getInstance().getGenreTemplate(genre);
    }, py::arg("genre"),
    "Get built-in groove template for a genre");
    
    m.def("get_genre_template", [](GenrePreset preset) {
        return GrooveEngine::getInstance().getGenreTemplate(preset);
    }, py::arg("preset"),
    "Get built-in groove template for a genre preset");
    
    m.def("list_genre_presets", []() {
        return GrooveEngine::getInstance().listGenrePresets();
    }, "List available genre preset names");
    
    m.def("quick_humanize", &quickHumanize,
        py::arg("notes"),
        py::arg("style"),
        py::arg("ppq") = 480,
        "Quick humanization with style preset (in-place)");
    
    m.def("get_genre_preset_by_name", &getGenrePresetByName, py::arg("name"),
        "Get GenrePreset enum value from string name");
}
