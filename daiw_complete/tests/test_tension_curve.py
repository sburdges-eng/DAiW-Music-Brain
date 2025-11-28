# tests/test_tension_curve.py
import numpy as np
from music_brain.structure.tension import generate_tension_curve, choose_structure_type_for_mood


def test_climb_curve_monotonic():
    curve = generate_tension_curve(32, "climb")
    assert len(curve) == 32
    # Should roughly increase
    assert curve[0] < curve[-1]


def test_constant_curve_flat():
    curve = generate_tension_curve(32, "constant")
    assert len(curve) == 32
    assert np.allclose(curve, curve[0])


def test_standard_has_shape():
    curve = generate_tension_curve(64, "standard")
    assert len(curve) == 64
    # Intro should be lower than chorus-ish area
    intro_avg = float(curve[0:8].mean())
    chorus_avg = float(curve[16:24].mean())
    assert chorus_avg > intro_avg


def test_empty_bars():
    curve = generate_tension_curve(0, "standard")
    assert len(curve) == 0


def test_short_song():
    curve = generate_tension_curve(8, "standard")
    assert len(curve) == 8


def test_mood_to_structure():
    assert choose_structure_type_for_mood("grief") == "climb"
    assert choose_structure_type_for_mood("rage") == "standard"
    assert choose_structure_type_for_mood("neutral") == "constant"
    assert choose_structure_type_for_mood("dissociation") == "climb"
