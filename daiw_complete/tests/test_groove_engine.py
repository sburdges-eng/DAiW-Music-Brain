# tests/test_groove_engine.py
import statistics
from music_brain.groove.engine import apply_groove, SAFE_DRIFT_LIMIT


def _make_grid_notes(count: int = 32):
    notes = []
    tick = 0
    for _ in range(count):
        notes.append(
            {
                "pitch": 60,
                "velocity": 90,
                "start_tick": tick,
                "duration_ticks": 120,
            }
        )
        tick += 120
    return notes


def test_low_complexity_is_tight():
    notes = _make_grid_notes()
    human = apply_groove(notes, complexity=0.0, vulnerability=0.5, seed=42)

    # With zero complexity, jitter should be near-zero
    diffs = [n["start_tick"] - o["start_tick"] for n, o in zip(human, notes)]
    assert all(abs(d) <= 1 for d in diffs)


def test_high_complexity_has_jitter_but_safe():
    notes = _make_grid_notes()
    human = apply_groove(notes, complexity=1.0, vulnerability=0.5, seed=42)

    # Dropout happens, so we can't zip directly - check each humanized note
    # against its likely original position
    original_ticks = {n["start_tick"] for n in notes}
    
    # At high complexity, either some notes dropped OR some have jitter
    has_dropout = len(human) < len(notes)
    has_jitter = any(n["start_tick"] not in original_ticks for n in human)
    assert has_dropout or has_jitter
    
    # Check that all jitter is within safe limits
    # Each note should be within SAFE_DRIFT_LIMIT of some original tick
    for h in human:
        closest_original = min(original_ticks, key=lambda x: abs(x - h["start_tick"]))
        assert abs(h["start_tick"] - closest_original) <= SAFE_DRIFT_LIMIT


def test_vulnerability_affects_velocity():
    notes = _make_grid_notes()

    low_vuln = apply_groove(notes, complexity=0.5, vulnerability=0.0, seed=42)
    high_vuln = apply_groove(notes, complexity=0.5, vulnerability=1.0, seed=42)

    low_mean = statistics.mean(n["velocity"] for n in low_vuln)
    high_mean = statistics.mean(n["velocity"] for n in high_vuln)

    # High vulnerability should be softer on average
    assert high_mean < low_mean


def test_seed_reproducibility():
    notes = _make_grid_notes()
    
    result1 = apply_groove(notes, complexity=0.7, vulnerability=0.5, seed=123)
    result2 = apply_groove(notes, complexity=0.7, vulnerability=0.5, seed=123)
    
    # Same seed should produce same results
    assert len(result1) == len(result2)
    for n1, n2 in zip(result1, result2):
        assert n1["start_tick"] == n2["start_tick"]
        assert n1["velocity"] == n2["velocity"]
