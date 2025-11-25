import pytest

from music_brain.structure.comprehensive_engine import (
    AffectAnalyzer,
    TherapySession,
    AffectResult,
)


@pytest.fixture
def analyzer():
    return AffectAnalyzer()


@pytest.mark.parametrize(
    "keyword, expected_affect",
    [
        ("dead", "grief"),
        ("mourning", "grief"),
        ("loss", "grief"),
        ("furious", "rage"),
        ("burn", "rage"),
        ("revenge", "rage"),
        ("god", "awe"),
        ("infinite", "awe"),
        ("remember", "nostalgia"),
        ("childhood", "nostalgia"),
        ("panic", "fear"),
        ("trapped", "fear"),
        ("numb", "dissociation"),
        ("nothing", "dissociation"),
        ("refuse", "defiance"),
        ("strong", "defiance"),
        ("gentle", "tenderness"),  # will fall back to neutral in current map
        ("chaos", "confusion"),
        ("why", "confusion"),
    ],
)
def test_affect_analyzer_keywords(analyzer, keyword, expected_affect):
    result = analyzer.analyze(f"I feel {keyword} today")
    assert isinstance(result, AffectResult)
    assert result.scores.get(expected_affect, 0.0) >= 1.0


def test_affect_analyzer_empty_input(analyzer):
    result = analyzer.analyze("")
    assert result.primary == "neutral"
    assert result.intensity == 0.0


def test_affect_analyzer_mixed_emotions(analyzer):
    result = analyzer.analyze("I am furious that he is dead")
    assert result.scores["rage"] > 0
    assert result.scores["grief"] > 0
    assert result.secondary is not None


@pytest.fixture
def session():
    return TherapySession()


@pytest.mark.parametrize(
    "input_text, expected_mode",
    [
        ("I am furious", "phrygian"),
        ("So beautiful", "lydian"),
        ("I feel numb", "locrian"),
        ("I miss him", "aeolian"),
        ("I refuse", "mixolydian"),
        ("   ", "ionian"),
    ],
)
def test_process_core_input_mode_mapping(session, input_text, expected_mode):
    mood = session.process_core_input(input_text)
    assert session.state.suggested_mode == expected_mode
    assert isinstance(mood, str)


@pytest.mark.parametrize(
    "motivation, expected_bars",
    [
        (1, 16),
        (3, 16),
        (4, 32),
        (7, 32),
        (8, 64),
        (10, 64),
    ],
)
def test_plan_generation_length(session, motivation, expected_bars):
    session.process_core_input("test input")
    session.set_scales(motivation, 0.5)
    plan = session.generate_plan()
    assert plan.length_bars == expected_bars


def test_chaos_modulates_tempo(session):
    session.process_core_input("I feel nothing")  # dissociation → base 70
    session.set_scales(5, 0.0)
    low = session.generate_plan()
    session.set_scales(5, 1.0)
    high = session.generate_plan()
    assert low.tempo_bpm != high.tempo_bpm
