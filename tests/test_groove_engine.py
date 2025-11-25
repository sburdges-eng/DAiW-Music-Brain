import pytest

from music_brain.groove.engine import apply_groove, SAFE_DRIFT_LIMIT


@pytest.fixture
def basic_events():
    return [
        {"start_tick": 0, "velocity": 80, "pitch": 60, "duration_ticks": 480},
        {"start_tick": 240, "velocity": 80, "pitch": 62, "duration_ticks": 480},
        {"start_tick": 480, "velocity": 80, "pitch": 64, "duration_ticks": 480},
        {"start_tick": 720, "velocity": 80, "pitch": 65, "duration_ticks": 480},
    ]


def test_groove_no_chaos_no_vulnerability(basic_events):
    processed = apply_groove(basic_events, complexity=0.0, vulnerability=0.0)
    for orig, new in zip(basic_events, processed):
        assert abs(orig["start_tick"] - new["start_tick"]) <= 2
        assert new["velocity"] >= orig["velocity"]


def test_groove_high_complexity_jitter(basic_events):
    processed = apply_groove(basic_events, complexity=1.0, vulnerability=0.0)
    drifted = False
    for orig, new in zip(basic_events, processed):
        diff = abs(orig["start_tick"] - new["start_tick"])
        assert diff <= SAFE_DRIFT_LIMIT
        if diff > 0:
            drifted = True
    assert drifted


def test_groove_high_vulnerability_dynamics(basic_events):
    processed = apply_groove(basic_events, complexity=0.0, vulnerability=1.0)
    for new in processed:
        assert new["velocity"] < 80
        assert new["velocity"] > 0
