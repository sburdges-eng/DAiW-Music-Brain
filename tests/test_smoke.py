def test_smoke_imports():
    from music_brain.structure.comprehensive_engine import TherapySession
    from music_brain.groove.engine import apply_groove
    from music_brain.daw.logic import LogicProject

    assert TherapySession is not None
    assert callable(apply_groove)
    assert LogicProject is not None
