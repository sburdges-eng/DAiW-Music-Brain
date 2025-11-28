# tests/test_engine_flow.py
from pathlib import Path
from music_brain.structure.comprehensive_engine import (
    TherapySession,
    render_plan_to_midi,
    AffectAnalyzer,
    select_kit_for_mood,
)


def test_affect_analyzer_detects_grief():
    analyzer = AffectAnalyzer()
    result = analyzer.analyze("I found her dead and I miss her so much")
    assert result.primary == "grief"
    assert result.intensity > 0


def test_affect_analyzer_detects_rage():
    analyzer = AffectAnalyzer()
    result = analyzer.analyze("I am furious he betrayed me I want to destroy everything")
    assert result.primary == "rage"


def test_affect_analyzer_neutral():
    analyzer = AffectAnalyzer()
    result = analyzer.analyze("hello world")
    assert result.primary == "neutral"


def test_session_process_input():
    session = TherapySession()
    mood = session.process_core_input("I feel broken and numb, floating through static")
    assert mood == "dissociation"
    assert session.state.suggested_mode == "locrian"


def test_session_generate_plan():
    session = TherapySession()
    session.process_core_input("I am furious he left and I cannot breathe")
    session.set_scales(motivation=8, chaos=0.7)
    plan = session.generate_plan()
    
    assert plan.length_bars in (32, 64)
    assert plan.tempo_bpm > 0
    assert len(plan.chord_symbols) > 0
    assert len(plan.tension_curve) == plan.length_bars


def test_engine_full_flow(tmp_path: Path):
    session = TherapySession()
    mood = session.process_core_input("I am furious he left and I cannot breathe")
    assert mood in ("rage", "fear", "defiance")

    session.set_scales(motivation=8, chaos=0.7)
    plan = session.generate_plan()

    out_path = tmp_path / "test_output.mid"
    midi_path = render_plan_to_midi(plan, str(out_path), vulnerability=0.3, seed=42)

    assert Path(midi_path).exists()
    assert plan.length_bars in (32, 64)


def test_kit_selection():
    assert select_kit_for_mood("grief") == "LoFi_Bedroom_Kit"
    assert select_kit_for_mood("rage") == "Industrial_Glitch_Kit"
    assert select_kit_for_mood("awe") == "Ambient_Shimmer_Kit"
    assert select_kit_for_mood("unknown") == "Standard_Kit"


def test_kelly_song_scenario():
    """Test the specific Kelly song emotional context."""
    session = TherapySession()
    
    # The core wound
    mood = session.process_core_input(
        "I found you sleeping and you were cold and the pills were everywhere"
    )
    
    assert mood == "grief"
    assert session.state.suggested_mode == "aeolian"
    
    session.set_scales(motivation=9, chaos=0.4)  # High motivation, controlled chaos
    plan = session.generate_plan()
    
    assert plan.structure_type == "climb"  # Grief gets slow build
    assert plan.tempo_bpm < 100  # Grief is slower
    assert plan.length_bars == 64  # High motivation = full length
