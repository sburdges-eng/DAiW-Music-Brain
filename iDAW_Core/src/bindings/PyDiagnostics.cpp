/**
 * PyDiagnostics.cpp - pybind11 bindings for Diagnostics module
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "diagnostics/DiagnosticsEngine.h"

namespace py = pybind11;

void init_diagnostics_bindings(py::module_& m) {
    using namespace iDAW::diagnostics;
    
    // RuleBreakCategory enum
    py::enum_<RuleBreakCategory>(m, "RuleBreakCategory")
        .value("HarmonyModalInterchange", RuleBreakCategory::HarmonyModalInterchange)
        .value("HarmonyParallelMotion", RuleBreakCategory::HarmonyParallelMotion)
        .value("HarmonyAvoidTonicResolution", RuleBreakCategory::HarmonyAvoidTonicResolution)
        .value("HarmonyUnresolvedDissonance", RuleBreakCategory::HarmonyUnresolvedDissonance)
        .value("HarmonyNonFunctional", RuleBreakCategory::HarmonyNonFunctional)
        .value("RhythmConstantDisplacement", RuleBreakCategory::RhythmConstantDisplacement)
        .value("RhythmTempoFluctuation", RuleBreakCategory::RhythmTempoFluctuation)
        .value("RhythmMeterAmbiguity", RuleBreakCategory::RhythmMeterAmbiguity)
        .value("ArrangementBuriedVocals", RuleBreakCategory::ArrangementBuriedVocals)
        .value("ArrangementExtremeDynamics", RuleBreakCategory::ArrangementExtremeDynamics)
        .value("ProductionPitchImperfection", RuleBreakCategory::ProductionPitchImperfection)
        .value("ProductionExcessiveMud", RuleBreakCategory::ProductionExcessiveMud)
        .value("ProductionLoFiAesthetics", RuleBreakCategory::ProductionLoFiAesthetics);
    
    // RuleBreak struct
    py::class_<RuleBreak>(m, "RuleBreak")
        .def(py::init<>())
        .def_readwrite("category", &RuleBreak::category)
        .def_readwrite("chord_name", &RuleBreak::chordName)
        .def_readwrite("context", &RuleBreak::context)
        .def_readwrite("emotional_effect", &RuleBreak::emotionalEffect)
        .def_readwrite("justification", &RuleBreak::justification)
        .def("to_string", &RuleBreak::toString)
        .def("__str__", &RuleBreak::toString)
        .def("__repr__", [](const RuleBreak& rb) {
            return "<RuleBreak " + ruleBreakToString(rb.category) + 
                   " at " + rb.chordName + ">";
        });
    
    // DiagnosticIssue struct
    py::class_<DiagnosticIssue>(m, "DiagnosticIssue")
        .def(py::init<>())
        .def_readwrite("description", &DiagnosticIssue::description)
        .def_readwrite("chord_involved", &DiagnosticIssue::chordInvolved)
        .def_readwrite("chord_index", &DiagnosticIssue::chordIndex)
        .def_readwrite("is_warning", &DiagnosticIssue::isWarning)
        .def_readwrite("rule_break", &DiagnosticIssue::ruleBreak)
        .def("__str__", [](const DiagnosticIssue& i) {
            return i.description;
        })
        .def("__repr__", [](const DiagnosticIssue& i) {
            return "<DiagnosticIssue '" + i.description + "'>";
        });
    
    // DiagnosticSuggestion struct
    py::class_<DiagnosticSuggestion>(m, "DiagnosticSuggestion")
        .def(py::init<>())
        .def_readwrite("description", &DiagnosticSuggestion::description)
        .def_readwrite("rationale", &DiagnosticSuggestion::rationale)
        .def_readwrite("priority", &DiagnosticSuggestion::priority)
        .def("__str__", [](const DiagnosticSuggestion& s) {
            return s.description;
        })
        .def("__repr__", [](const DiagnosticSuggestion& s) {
            return "<DiagnosticSuggestion priority=" + std::to_string(s.priority) + 
                   " '" + s.description + "'>";
        });
    
    // DiagnosticReport struct
    py::class_<DiagnosticReport>(m, "DiagnosticReport")
        .def(py::init<>())
        .def_readonly("detected_key", &DiagnosticReport::detectedKey)
        .def_readonly("chord_names", &DiagnosticReport::chordNames)
        .def_readonly("roman_numerals", &DiagnosticReport::romanNumerals)
        .def_readonly("issues", &DiagnosticReport::issues)
        .def_readonly("suggestions", &DiagnosticReport::suggestions)
        .def_readonly("rule_breaks", &DiagnosticReport::ruleBreaks)
        .def_readonly("borrowed_chords", &DiagnosticReport::borrowedChords)
        .def_readonly("emotional_character", &DiagnosticReport::emotionalCharacter)
        .def_readonly("harmony_complexity", &DiagnosticReport::harmonyComplexity)
        .def_readonly("has_resolution", &DiagnosticReport::hasResolution)
        .def_readonly("success", &DiagnosticReport::success)
        .def_readonly("error_message", &DiagnosticReport::errorMessage)
        .def("to_dict", [](const DiagnosticReport& r) {
            py::dict d;
            d["key"] = r.detectedKey.toString();
            d["chords"] = r.chordNames;
            d["roman_numerals"] = r.romanNumerals;
            
            py::list issues;
            for (const auto& issue : r.issues) {
                py::dict i;
                i["description"] = issue.description;
                i["chord"] = issue.chordInvolved;
                i["index"] = issue.chordIndex;
                i["is_warning"] = issue.isWarning;
                issues.append(i);
            }
            d["issues"] = issues;
            
            py::list suggestions;
            for (const auto& sug : r.suggestions) {
                py::dict s;
                s["description"] = sug.description;
                s["rationale"] = sug.rationale;
                s["priority"] = sug.priority;
                suggestions.append(s);
            }
            d["suggestions"] = suggestions;
            
            py::list ruleBreaks;
            for (const auto& rb : r.ruleBreaks) {
                py::dict b;
                b["category"] = ruleBreakToString(rb.category);
                b["chord"] = rb.chordName;
                b["context"] = rb.context;
                b["emotional_effect"] = rb.emotionalEffect;
                b["justification"] = rb.justification;
                ruleBreaks.append(b);
            }
            d["rule_breaks"] = ruleBreaks;
            
            py::dict borrowed;
            for (const auto& [chord, source] : r.borrowedChords) {
                borrowed[py::str(chord)] = source;
            }
            d["borrowed_chords"] = borrowed;
            
            d["emotional_character"] = r.emotionalCharacter;
            d["harmony_complexity"] = r.harmonyComplexity;
            d["has_resolution"] = r.hasResolution;
            d["success"] = r.success;
            d["error_message"] = r.errorMessage;
            
            return d;
        })
        .def("__repr__", [](const DiagnosticReport& r) {
            return "<DiagnosticReport key=" + r.detectedKey.toString() + 
                   " issues=" + std::to_string(r.issues.size()) + 
                   " rule_breaks=" + std::to_string(r.ruleBreaks.size()) + ">";
        });
    
    // DiagnosticsEngine singleton access
    m.def("get_engine", []() -> DiagnosticsEngine& {
        return DiagnosticsEngine::getInstance();
    }, py::return_value_policy::reference,
    "Get the DiagnosticsEngine singleton instance");
    
    // Convenience functions
    m.def("diagnose", [](const std::string& progression) {
        return DiagnosticsEngine::getInstance().diagnose(progression);
    }, py::arg("progression"),
    "Diagnose a chord progression string");
    
    m.def("diagnose_progression", [](const iDAW::harmony::Progression& progression) {
        return DiagnosticsEngine::getInstance().diagnose(progression);
    }, py::arg("progression"),
    "Diagnose a Progression object");
    
    m.def("identify_rule_breaks", [](
        const iDAW::harmony::Progression& progression,
        const iDAW::harmony::Key& key) {
        return DiagnosticsEngine::getInstance().identifyRuleBreaks(progression, key);
    },
    py::arg("progression"),
    py::arg("key"),
    "Identify rule breaks in a progression");
    
    m.def("get_emotional_character", [](
        const iDAW::harmony::Progression& progression,
        const iDAW::harmony::Key& key) {
        return DiagnosticsEngine::getInstance().getEmotionalCharacter(progression, key);
    },
    py::arg("progression"),
    py::arg("key"),
    "Get emotional character description for a progression");
    
    m.def("calculate_complexity", [](const iDAW::harmony::Progression& progression) {
        return DiagnosticsEngine::getInstance().calculateComplexity(progression);
    }, py::arg("progression"),
    "Calculate harmonic complexity score (0.0-1.0)");
    
    m.def("has_resolution", [](
        const iDAW::harmony::Progression& progression,
        const iDAW::harmony::Key& key) {
        return DiagnosticsEngine::getInstance().hasResolution(progression, key);
    },
    py::arg("progression"),
    py::arg("key"),
    "Check if progression has proper resolution");
    
    m.def("suggest_rule_breaks", [](const std::string& emotion) {
        return DiagnosticsEngine::getInstance().suggestRuleBreaks(emotion);
    }, py::arg("emotion"),
    "Suggest rule breaks for emotional effect");
    
    // Utility function
    m.def("rule_break_to_string", &ruleBreakToString, py::arg("category"),
        "Convert RuleBreakCategory to string");
}
