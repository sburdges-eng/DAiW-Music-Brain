/**
 * PyHarmony.cpp - pybind11 bindings for Harmony module
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "harmony/HarmonyEngine.h"
#include "harmony/Chord.h"
#include "harmony/Progression.h"

namespace py = pybind11;

void init_harmony_bindings(py::module_& m) {
    using namespace iDAW::harmony;
    
    // ChordQuality enum
    py::enum_<ChordQuality>(m, "ChordQuality")
        .value("Major", ChordQuality::Major)
        .value("Minor", ChordQuality::Minor)
        .value("Diminished", ChordQuality::Diminished)
        .value("Augmented", ChordQuality::Augmented)
        .value("Dominant7", ChordQuality::Dominant7)
        .value("Major7", ChordQuality::Major7)
        .value("Minor7", ChordQuality::Minor7)
        .value("HalfDim7", ChordQuality::HalfDim7)
        .value("Dim7", ChordQuality::Dim7)
        .value("Sus2", ChordQuality::Sus2)
        .value("Sus4", ChordQuality::Sus4)
        .value("Add9", ChordQuality::Add9)
        .value("Major6", ChordQuality::Major6)
        .value("Minor6", ChordQuality::Minor6)
        .value("Unknown", ChordQuality::Unknown);
    
    // Mode enum
    py::enum_<Mode>(m, "Mode")
        .value("Major", Mode::Major)
        .value("Minor", Mode::Minor)
        .value("Dorian", Mode::Dorian)
        .value("Phrygian", Mode::Phrygian)
        .value("Lydian", Mode::Lydian)
        .value("Mixolydian", Mode::Mixolydian)
        .value("Locrian", Mode::Locrian);
    
    // Key struct
    py::class_<Key>(m, "Key")
        .def(py::init<>())
        .def_readwrite("root", &Key::root)
        .def_readwrite("mode", &Key::mode)
        .def("to_string", &Key::toString)
        .def("__str__", &Key::toString)
        .def("__repr__", [](const Key& k) {
            return "<Key " + k.toString() + ">";
        });
    
    // Chord class
    py::class_<Chord>(m, "Chord")
        .def(py::init<>())
        .def(py::init<int, ChordQuality, int>(),
             py::arg("root"), py::arg("quality"), py::arg("bass") = -1)
        .def(py::init<const std::vector<int>&>(), py::arg("midi_notes"))
        .def_static("from_string", &Chord::fromString, py::arg("chord_str"),
            "Parse chord from string (e.g., 'Am7', 'F#dim')")
        .def_property_readonly("root", &Chord::root)
        .def_property_readonly("quality", &Chord::quality)
        .def_property_readonly("bass", &Chord::bass)
        .def_property_readonly("has_bass", &Chord::hasBass)
        .def_property_readonly("is_valid", &Chord::isValid)
        .def("name", &Chord::name, py::arg("use_flats") = false)
        .def("root_name", &Chord::rootName, py::arg("use_flats") = false)
        .def("intervals", &Chord::intervals)
        .def("has_interval", &Chord::hasInterval, py::arg("interval"))
        .def("midi_notes", &Chord::midiNotes, py::arg("octave") = 4)
        .def("__str__", [](const Chord& c) { return c.name(); })
        .def("__repr__", [](const Chord& c) {
            return "<Chord " + c.name() + ">";
        })
        .def("__eq__", &Chord::operator==)
        .def("__ne__", &Chord::operator!=);
    
    // Progression class
    py::class_<Progression>(m, "Progression")
        .def(py::init<>())
        .def(py::init<const std::vector<Chord>&>(), py::arg("chords"))
        .def_static("from_string", &Progression::fromString, py::arg("progression_str"),
            "Parse progression from string (e.g., 'F-C-Am-Dm')")
        .def_property_readonly("chords", &Progression::chords)
        .def_property_readonly("key", &Progression::key)
        .def_property_readonly("roman_numerals", &Progression::romanNumerals)
        .def("at", py::overload_cast<size_t>(&Progression::at, py::const_), py::arg("index"))
        .def("size", &Progression::size)
        .def("empty", &Progression::empty)
        .def("add_chord", &Progression::addChord, py::arg("chord"))
        .def("detect_key", &Progression::detectKey)
        .def("analyze", &Progression::analyze)
        .def("get_roman_numeral", &Progression::getRomanNumeral, py::arg("chord"))
        .def("identify_borrowed_chords", &Progression::identifyBorrowedChords)
        .def("is_diatonic", &Progression::isDiatonic, py::arg("chord"))
        .def("to_string", &Progression::toString)
        .def("__str__", &Progression::toString)
        .def("__len__", &Progression::size)
        .def("__getitem__", [](const Progression& p, size_t i) {
            if (i >= p.size()) throw py::index_error();
            return p.at(i);
        });
    
    // ReharmTechnique enum
    py::enum_<ReharmTechnique>(m, "ReharmTechnique")
        .value("TritoneSubstitution", ReharmTechnique::TritoneSubstitution)
        .value("ChromaticApproach", ReharmTechnique::ChromaticApproach)
        .value("SecondaryDominants", ReharmTechnique::SecondaryDominants)
        .value("DiminishedPassing", ReharmTechnique::DiminishedPassing)
        .value("BorrowedFromParallel", ReharmTechnique::BorrowedFromParallel)
        .value("PedalPoint", ReharmTechnique::PedalPoint)
        .value("SusChords", ReharmTechnique::SusChords)
        .value("Add9Extensions", ReharmTechnique::Add9Extensions)
        .value("ExtendedDominants", ReharmTechnique::ExtendedDominants)
        .value("ParallelMotion", ReharmTechnique::ParallelMotion)
        .value("QuartalVoicings", ReharmTechnique::QuartalVoicings);
    
    // ReharmSuggestion struct
    py::class_<ReharmSuggestion>(m, "ReharmSuggestion")
        .def(py::init<>())
        .def_readwrite("chords", &ReharmSuggestion::chords)
        .def_readwrite("technique", &ReharmSuggestion::technique)
        .def_readwrite("mood", &ReharmSuggestion::mood)
        .def_readwrite("description", &ReharmSuggestion::description);
    
    // DiagnosisResult struct
    py::class_<DiagnosisResult>(m, "DiagnosisResult")
        .def(py::init<>())
        .def_readonly("detected_key", &DiagnosisResult::detectedKey)
        .def_readonly("issues", &DiagnosisResult::issues)
        .def_readonly("suggestions", &DiagnosisResult::suggestions)
        .def_readonly("chord_names", &DiagnosisResult::chordNames)
        .def_readonly("borrowed_chords", &DiagnosisResult::borrowedChords)
        .def_readonly("success", &DiagnosisResult::success);
    
    // HarmonyEngine singleton access
    m.def("get_engine", []() -> HarmonyEngine& {
        return HarmonyEngine::getInstance();
    }, py::return_value_policy::reference,
    "Get the HarmonyEngine singleton instance");
    
    // Convenience functions
    m.def("parse_chord", &parseChordString, py::arg("chord_str"),
        "Parse a chord string into a Chord object");
    
    m.def("parse_progression", &parseProgressionString, py::arg("progression_str"),
        "Parse a progression string into a list of Chords");
    
    m.def("detect_chord", [](const std::vector<int>& notes) {
        return detectChord(notes);
    }, py::arg("midi_notes"),
    "Detect chord from MIDI note numbers");
    
    m.def("diagnose", [](const std::string& progression) {
        return HarmonyEngine::getInstance().diagnoseProgression(progression);
    }, py::arg("progression"),
    "Diagnose a chord progression string");
    
    m.def("generate_reharmonizations", [](
        const std::string& progression,
        const std::string& style,
        int count) {
        return HarmonyEngine::getInstance().generateReharmonizations(progression, style, count);
    },
    py::arg("progression"),
    py::arg("style") = "jazz",
    py::arg("count") = 3,
    "Generate reharmonization suggestions for a progression");
    
    // Utility functions
    m.def("quality_to_string", &qualityToString, py::arg("quality"),
        "Convert ChordQuality enum to string");
    
    m.def("mode_to_string", &modeToString, py::arg("mode"),
        "Convert Mode enum to string");
    
    m.def("get_scale_degrees", &getScaleDegrees, py::arg("mode"),
        "Get scale degrees (semitones from root) for a mode");
    
    m.def("midi_to_pitch_class", &midiToPitchClass, py::arg("midi_note"),
        "Convert MIDI note number to pitch class (0-11)");
    
    m.def("pitch_class_to_midi", &pitchClassToMidi,
        py::arg("pitch_class"), py::arg("octave") = 4,
        "Convert pitch class to MIDI note in given octave");
}
