/**
 * @file bindings.cpp
 * @brief Main pybind11 bindings entry point
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "daiw/types.hpp"

namespace py = pybind11;

// Forward declarations for submodule bindings
void init_groove_bindings(py::module_& m);
void init_harmony_bindings(py::module_& m);

PYBIND11_MODULE(daiw_logic, m) {
    m.doc() = "DAiW C++ Core - Python Bindings";

    // Version info
    m.attr("__version__") = daiw::Version::string();

    // Core types
    py::class_<daiw::NoteEvent>(m, "NoteEvent")
        .def(py::init<>())
        .def_readwrite("pitch", &daiw::NoteEvent::pitch)
        .def_readwrite("velocity", &daiw::NoteEvent::velocity)
        .def_readwrite("start_tick", &daiw::NoteEvent::startTick)
        .def_readwrite("duration_ticks", &daiw::NoteEvent::durationTicks)
        .def_readwrite("channel", &daiw::NoteEvent::channel)
        .def("end_tick", &daiw::NoteEvent::endTick);

    py::class_<daiw::GrooveSettings>(m, "GrooveSettings")
        .def(py::init<>())
        .def_readwrite("swing", &daiw::GrooveSettings::swing)
        .def_readwrite("push_pull", &daiw::GrooveSettings::pushPull)
        .def_readwrite("humanization", &daiw::GrooveSettings::humanization)
        .def_readwrite("velocity_var", &daiw::GrooveSettings::velocityVar);

    py::class_<daiw::TimeSignature>(m, "TimeSignature")
        .def(py::init<>())
        .def_readwrite("numerator", &daiw::TimeSignature::numerator)
        .def_readwrite("denominator", &daiw::TimeSignature::denominator)
        .def("beats_per_bar", &daiw::TimeSignature::beatsPerBar)
        .def("ticks_per_bar", &daiw::TimeSignature::ticksPerBar);

    py::class_<daiw::Tempo>(m, "Tempo")
        .def(py::init<>())
        .def_readwrite("bpm", &daiw::Tempo::bpm)
        .def("samples_per_beat", &daiw::Tempo::samplesPerBeat)
        .def("ms_per_beat", &daiw::Tempo::msPerBeat);

    // Initialize submodules
    init_groove_bindings(m);
    init_harmony_bindings(m);
}
