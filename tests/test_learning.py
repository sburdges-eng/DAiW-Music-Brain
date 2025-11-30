"""
Tests for the Learning Module.

Tests curriculum structures, resource fetching, instruments database,
and pedagogy engine functionality.
"""

import pytest
from pathlib import Path
import json
import tempfile


class TestCurriculumModule:
    """Tests for curriculum.py."""

    def test_difficulty_level_enum(self):
        """Test DifficultyLevel enum properties."""
        from music_brain.learning.curriculum import DifficultyLevel

        # Test all levels exist
        assert len(DifficultyLevel) == 10

        # Test specific level properties
        beginner = DifficultyLevel.BEGINNER
        assert beginner.value == 3
        assert beginner.name_friendly == "Beginner"
        assert beginner.tier == "Beginner"

        intermediate = DifficultyLevel.INTERMEDIATE
        assert intermediate.value == 5
        assert intermediate.tier == "Intermediate"

        expert = DifficultyLevel.EXPERT
        assert expert.value == 10
        assert expert.tier == "Expert"

    def test_difficulty_level_can_attempt(self):
        """Test can_attempt method for difficulty progression."""
        from music_brain.learning.curriculum import DifficultyLevel

        beginner = DifficultyLevel.BEGINNER
        intermediate = DifficultyLevel.INTERMEDIATE

        # Can attempt up to 2 levels above
        assert beginner.can_attempt(DifficultyLevel.BEGINNER)
        assert beginner.can_attempt(DifficultyLevel.EARLY_INTERMEDIATE)
        assert beginner.can_attempt(DifficultyLevel.INTERMEDIATE)
        assert not beginner.can_attempt(DifficultyLevel.ADVANCED)

    def test_skill_category_enum(self):
        """Test SkillCategory enum."""
        from music_brain.learning.curriculum import SkillCategory

        # Should have all main categories
        assert SkillCategory.TECHNIQUE
        assert SkillCategory.RHYTHM
        assert SkillCategory.HARMONY
        assert SkillCategory.IMPROVISATION
        assert SkillCategory.PRACTICE_HABITS

    def test_learning_objective_creation(self):
        """Test LearningObjective dataclass."""
        from music_brain.learning.curriculum import (
            LearningObjective, SkillCategory, DifficultyLevel
        )

        obj = LearningObjective(
            id="test-001",
            title="Learn C Major Scale",
            description="Master the C major scale in first position",
            skill_category=SkillCategory.SCALES,
            difficulty=DifficultyLevel.BEGINNER,
            success_criteria=["Play at 60 BPM", "No wrong notes"],
        )

        assert obj.id == "test-001"
        assert obj.skill_category == SkillCategory.SCALES
        assert len(obj.success_criteria) == 2

    def test_learning_objective_serialization(self):
        """Test LearningObjective to_dict and from_dict."""
        from music_brain.learning.curriculum import (
            LearningObjective, SkillCategory, DifficultyLevel
        )

        original = LearningObjective(
            id="test-002",
            title="Test Objective",
            description="Test description",
            skill_category=SkillCategory.RHYTHM,
            difficulty=DifficultyLevel.INTERMEDIATE,
        )

        # Serialize and deserialize
        data = original.to_dict()
        restored = LearningObjective.from_dict(data)

        assert restored.id == original.id
        assert restored.title == original.title
        assert restored.skill_category == original.skill_category
        assert restored.difficulty == original.difficulty

    def test_lesson_creation(self):
        """Test Lesson dataclass."""
        from music_brain.learning.curriculum import Lesson, DifficultyLevel

        lesson = Lesson(
            id="lesson-001",
            title="First Chords",
            description="Learn your first guitar chords",
            difficulty=DifficultyLevel.ABSOLUTE_BEGINNER,
            estimated_duration_minutes=30,
        )

        assert lesson.id == "lesson-001"
        assert lesson.estimated_duration_minutes == 30

    def test_module_properties(self):
        """Test Module computed properties."""
        from music_brain.learning.curriculum import Module, Lesson, DifficultyLevel

        lesson1 = Lesson(
            id="l1", title="L1", description="D1",
            difficulty=DifficultyLevel.BEGINNER,
            estimated_duration_minutes=20,
        )
        lesson2 = Lesson(
            id="l2", title="L2", description="D2",
            difficulty=DifficultyLevel.BEGINNER,
            estimated_duration_minutes=30,
        )

        module = Module(
            id="m1",
            title="Module 1",
            description="First module",
            difficulty_range=(1, 3),
            lessons=[lesson1, lesson2],
        )

        assert module.lesson_count == 2
        assert module.total_duration_minutes == 50

    def test_curriculum_builder(self):
        """Test CurriculumBuilder fluent API."""
        from music_brain.learning.curriculum import (
            CurriculumBuilder, DifficultyLevel, SkillCategory
        )

        curriculum = (
            CurriculumBuilder("guitar")
            .start_module(
                "basics",
                "Guitar Basics",
                "Learn the fundamentals",
                (1, 3),
            )
            .add_lesson(
                "holding",
                "Holding the Guitar",
                "How to hold your instrument",
                DifficultyLevel.ABSOLUTE_BEGINNER,
            )
            .add_objective(
                "posture",
                "Correct Posture",
                "Maintain good posture while playing",
                SkillCategory.POSTURE,
            )
            .add_exercise(
                "5-minute hold",
                "Hold the guitar correctly for 5 minutes",
            )
            .finish_module()
            .build(
                "guitar-101",
                "Guitar 101",
                "Complete beginner guitar course",
            )
        )

        assert curriculum.id == "guitar-101"
        assert curriculum.instrument == "guitar"
        assert len(curriculum.modules) == 1
        assert curriculum.total_lessons == 1

    def test_curriculum_save_load(self):
        """Test Curriculum save and load functionality."""
        from music_brain.learning.curriculum import (
            CurriculumBuilder, DifficultyLevel
        )

        original = (
            CurriculumBuilder("piano")
            .start_module("m1", "Module 1", "Desc", (1, 3))
            .add_lesson("l1", "Lesson 1", "Desc", DifficultyLevel.BEGINNER)
            .finish_module()
            .build("piano-101", "Piano 101", "Piano course")
        )

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            original.save(f.name)

            from music_brain.learning.curriculum import Curriculum
            loaded = Curriculum.load(f.name)

            assert loaded.id == original.id
            assert loaded.instrument == original.instrument
            assert len(loaded.modules) == len(original.modules)

    def test_learning_path(self):
        """Test LearningPath tracking."""
        from music_brain.learning.curriculum import LearningPath, DifficultyLevel

        path = LearningPath(
            id="path-001",
            student_id="student-001",
            curriculum_id="guitar-101",
        )

        # Record practice
        path.record_practice(30)
        assert path.total_practice_minutes == 30
        assert path.session_count == 1
        assert path.streak_days == 1

        # Complete objectives
        path.complete_objective("obj-001")
        path.complete_lesson("lesson-001")
        assert "obj-001" in path.completed_objective_ids
        assert "lesson-001" in path.completed_lesson_ids

        # Level up
        assert path.current_level == DifficultyLevel.ABSOLUTE_BEGINNER
        path.level_up()
        assert path.current_level == DifficultyLevel.EARLY_BEGINNER


class TestResourcesModule:
    """Tests for resources.py."""

    def test_resource_type_enum(self):
        """Test ResourceType enum."""
        from music_brain.learning.resources import ResourceType

        assert ResourceType.ARTICLE
        assert ResourceType.VIDEO
        assert ResourceType.INTERACTIVE
        assert ResourceType.SHEET_MUSIC

    def test_learning_resource_creation(self):
        """Test LearningResource dataclass."""
        from music_brain.learning.resources import LearningResource, ResourceType

        resource = LearningResource(
            id="res-001",
            url="https://example.com/lesson",
            title="Test Lesson",
            resource_type=ResourceType.VIDEO,
            source_name="TestSource",
            instrument="guitar",
            difficulty_estimate=3,
        )

        assert resource.id == "res-001"
        assert resource.instrument == "guitar"
        assert resource.difficulty_estimate == 3

    def test_learning_resource_serialization(self):
        """Test LearningResource to_dict and from_dict."""
        from music_brain.learning.resources import LearningResource, ResourceType

        original = LearningResource(
            id="res-002",
            url="https://example.com",
            title="Test",
            resource_type=ResourceType.ARTICLE,
            source_name="Test",
        )

        data = original.to_dict()
        restored = LearningResource.from_dict(data)

        assert restored.id == original.id
        assert restored.resource_type == original.resource_type

    def test_known_sources_exist(self):
        """Test that KNOWN_SOURCES contains expected sources."""
        from music_brain.learning.resources import KNOWN_SOURCES

        # Should have major sources
        assert "justinguitar" in KNOWN_SOURCES
        assert "drumeo" in KNOWN_SOURCES
        assert "pianote" in KNOWN_SOURCES

        # Each source should have required fields
        for source_id, source in KNOWN_SOURCES.items():
            assert "name" in source
            assert "base_url" in source
            assert "instruments" in source
            assert "content_types" in source

    def test_resource_fetcher_get_sources(self):
        """Test ResourceFetcher.get_sources_for_instrument."""
        from music_brain.learning.resources import ResourceFetcher

        fetcher = ResourceFetcher()

        # Guitar should have multiple sources
        guitar_sources = fetcher.get_sources_for_instrument("guitar")
        assert len(guitar_sources) > 0
        assert any("guitar" in s["id"].lower() or
                   "guitar" in str(s.get("instruments", [])).lower()
                   for s in guitar_sources)

        # Drums should have sources
        drum_sources = fetcher.get_sources_for_instrument("drums")
        assert len(drum_sources) > 0

    def test_resource_fetcher_search_query(self):
        """Test ResourceFetcher.build_search_query."""
        from music_brain.learning.resources import ResourceFetcher

        fetcher = ResourceFetcher()

        query = fetcher.build_search_query(
            instrument="guitar",
            difficulty=3,
            skill_focus="chords",
            topic="barre chords",
        )

        assert query["instrument"] == "guitar"
        assert query["difficulty"] == 3
        assert "beginner" in query["difficulty_terms"]
        assert "search_string" in query

    def test_get_recommended_sources(self):
        """Test get_recommended_sources function."""
        from music_brain.learning.resources import get_recommended_sources

        sources = get_recommended_sources("piano", difficulty=1, limit=3)

        assert len(sources) <= 3
        for source in sources:
            assert "name" in source
            assert "base_url" in source

    def test_generate_learning_plan(self):
        """Test generate_learning_plan function."""
        from music_brain.learning.resources import generate_learning_plan

        plan = generate_learning_plan(
            instrument="guitar",
            current_level=1,
            target_level=5,
            weekly_hours=5.0,
        )

        assert plan["instrument"] == "guitar"
        assert plan["current_level"] == 1
        assert plan["target_level"] == 5
        assert len(plan["phases"]) == 5  # Levels 1-5


class TestInstrumentsModule:
    """Tests for instruments.py."""

    def test_instrument_family_enum(self):
        """Test InstrumentFamily enum."""
        from music_brain.learning.instruments import InstrumentFamily

        assert InstrumentFamily.STRINGS
        assert InstrumentFamily.WOODWINDS
        assert InstrumentFamily.BRASS
        assert InstrumentFamily.PERCUSSION
        assert InstrumentFamily.KEYBOARD
        assert InstrumentFamily.ELECTRONIC
        assert InstrumentFamily.VOICE
        assert InstrumentFamily.FRETTED

    def test_instruments_database_exists(self):
        """Test that INSTRUMENTS contains expected instruments."""
        from music_brain.learning.instruments import INSTRUMENTS

        # Core instruments should exist
        assert "piano" in INSTRUMENTS
        assert "acoustic_guitar" in INSTRUMENTS
        assert "electric_guitar" in INSTRUMENTS
        assert "drums" in INSTRUMENTS
        assert "bass" in INSTRUMENTS
        assert "voice" in INSTRUMENTS

    def test_instrument_properties(self):
        """Test Instrument dataclass properties."""
        from music_brain.learning.instruments import INSTRUMENTS

        piano = INSTRUMENTS["piano"]

        assert piano.name == "Piano"
        assert piano.beginner_friendly is True
        assert piano.days_to_first_song > 0
        assert len(piano.common_challenges) > 0
        assert len(piano.first_skills) > 0
        assert len(piano.practice_tips) > 0
        assert len(piano.primary_genres) > 0

    def test_get_instrument_by_id(self):
        """Test get_instrument function."""
        from music_brain.learning.instruments import get_instrument

        # By ID
        guitar = get_instrument("acoustic_guitar")
        assert guitar is not None
        assert guitar.name == "Acoustic Guitar"

        # By alias
        guitar2 = get_instrument("guitar")
        assert guitar2 is not None

        # Unknown
        unknown = get_instrument("theremin")
        assert unknown is None

    def test_get_instruments_by_family(self):
        """Test get_instruments_by_family function."""
        from music_brain.learning.instruments import (
            get_instruments_by_family, InstrumentFamily
        )

        fretted = get_instruments_by_family(InstrumentFamily.FRETTED)
        assert len(fretted) > 0
        assert any(i.id == "acoustic_guitar" for i in fretted)
        assert any(i.id == "bass" for i in fretted)

    def test_get_beginner_instruments(self):
        """Test get_beginner_instruments function."""
        from music_brain.learning.instruments import get_beginner_instruments

        beginners = get_beginner_instruments()

        assert len(beginners) > 0
        for inst in beginners:
            assert inst.beginner_friendly is True

        # Should be sorted by days_to_first_song
        days = [i.days_to_first_song for i in beginners]
        assert days == sorted(days)

    def test_suggest_instrument(self):
        """Test suggest_instrument function."""
        from music_brain.learning.instruments import suggest_instrument

        suggestions = suggest_instrument(
            age=25,
            physical_ability="normal",
            goals=["songwriting"],
            budget_usd=500,
        )

        assert len(suggestions) > 0
        for s in suggestions:
            assert "instrument" in s
            assert "score" in s
            assert "reasons" in s


class TestPedagogyModule:
    """Tests for pedagogy.py."""

    def test_teaching_style_enum(self):
        """Test TeachingStyle enum."""
        from music_brain.learning.pedagogy import TeachingStyle

        assert TeachingStyle.CLASSICAL
        assert TeachingStyle.SUZUKI
        assert TeachingStyle.CONTEMPORARY
        assert TeachingStyle.MASTERY
        assert TeachingStyle.JAZZ_METHOD

    def test_learning_preference_enum(self):
        """Test LearningPreference enum."""
        from music_brain.learning.pedagogy import LearningPreference

        assert LearningPreference.VISUAL
        assert LearningPreference.AUDITORY
        assert LearningPreference.KINESTHETIC
        assert LearningPreference.READING

    def test_student_profile_creation(self):
        """Test StudentProfile dataclass."""
        from music_brain.learning.pedagogy import (
            StudentProfile, LearningPreference
        )

        student = StudentProfile(
            id="student-001",
            name="Test Student",
            age=30,
            experience_level=3,
            learning_preferences=[LearningPreference.VISUAL],
            primary_goal="performance",
        )

        assert student.id == "student-001"
        assert student.age == 30
        assert student.experience_level == 3

    def test_student_profile_ideal_lesson_duration(self):
        """Test StudentProfile.get_ideal_lesson_duration."""
        from music_brain.learning.pedagogy import StudentProfile

        # Child
        child = StudentProfile(id="c1", name="Child", age=8, attention_span_minutes=30)
        assert child.get_ideal_lesson_duration() <= 20

        # Adult
        adult = StudentProfile(id="a1", name="Adult", age=30, attention_span_minutes=60)
        assert adult.get_ideal_lesson_duration() <= 60

    def test_adaptive_teacher_select_style(self):
        """Test AdaptiveTeacher.select_teaching_style."""
        from music_brain.learning.pedagogy import (
            AdaptiveTeacher, StudentProfile, TeachingStyle
        )

        # Child should get Suzuki
        child = StudentProfile(id="c1", name="Child", age=7)
        teacher = AdaptiveTeacher(child)
        assert teacher.select_teaching_style() == TeachingStyle.SUZUKI

        # Adult with structure preference should get Mastery
        adult = StudentProfile(id="a1", name="Adult", age=30, prefers_structure=True)
        teacher2 = AdaptiveTeacher(adult)
        # Default for structured adult is MASTERY or CONTEMPORARY

    def test_adaptive_teacher_generate_lesson_plan(self):
        """Test AdaptiveTeacher.generate_lesson_plan."""
        from music_brain.learning.pedagogy import AdaptiveTeacher, StudentProfile

        student = StudentProfile(id="s1", name="Student", age=25)
        teacher = AdaptiveTeacher(student)

        plan = teacher.generate_lesson_plan("major scales", duration_minutes=30)

        assert plan["topic"] == "major scales"
        assert plan["total_duration_minutes"] == 30
        assert "segments" in plan
        assert "practice_assignment" in plan
        assert "success_criteria" in plan

    def test_adaptive_teacher_generate_feedback(self):
        """Test AdaptiveTeacher.generate_feedback."""
        from music_brain.learning.pedagogy import AdaptiveTeacher, StudentProfile

        student = StudentProfile(id="s1", name="Student", age=25)
        teacher = AdaptiveTeacher(student)

        feedback = teacher.generate_feedback(
            performance_notes="Played C major scale at 60 BPM",
            skill_demonstrated="C major scale",
            success_level=0.8,
        )

        assert feedback["skill"] == "C major scale"
        assert feedback["success_level"] == 0.8
        assert "praise" in feedback
        assert "encouragement" in feedback

    def test_pedagogy_engine_generate_prompt(self):
        """Test PedagogyEngine.generate_ai_prompt."""
        from music_brain.learning.pedagogy import PedagogyEngine

        engine = PedagogyEngine()

        prompt = engine.generate_ai_prompt(
            action="explain",
            instrument="guitar",
            topic="barre chords",
            difficulty=5,
        )

        assert "guitar" in prompt
        assert "barre chords" in prompt
        assert "Difficulty" in prompt

    def test_generate_ai_teaching_prompt_function(self):
        """Test the convenience function."""
        from music_brain.learning.pedagogy import generate_ai_teaching_prompt

        prompt = generate_ai_teaching_prompt(
            action="demonstrate",
            instrument="piano",
            topic="scales",
            difficulty=3,
        )

        assert "piano" in prompt
        assert "scales" in prompt
        assert "demonstrate" in prompt.lower()

    def test_teaching_prompt_templates_exist(self):
        """Test that all expected templates exist."""
        from music_brain.learning.pedagogy import TEACHING_PROMPT_TEMPLATES

        expected_actions = [
            "explain", "demonstrate", "troubleshoot",
            "motivate", "assess", "practice_plan", "song_suggestion"
        ]

        for action in expected_actions:
            assert action in TEACHING_PROMPT_TEMPLATES


class TestModuleIntegration:
    """Integration tests for the learning module."""

    def test_full_curriculum_creation_flow(self):
        """Test creating a complete curriculum from scratch."""
        from music_brain.learning import (
            CurriculumBuilder, DifficultyLevel, SkillCategory,
            get_instrument, get_recommended_sources,
        )

        # Get instrument info
        guitar = get_instrument("acoustic_guitar")
        assert guitar is not None

        # Get sources
        sources = get_recommended_sources("guitar", difficulty=1)
        assert len(sources) > 0

        # Build curriculum
        curriculum = (
            CurriculumBuilder("acoustic_guitar")
            .start_module(
                "basics",
                "Guitar Basics",
                "Learn the fundamentals of acoustic guitar",
                (1, 3),
                [SkillCategory.TECHNIQUE, SkillCategory.POSTURE],
            )
            .add_lesson(
                "holding",
                "Holding the Guitar",
                guitar.first_skills[0] if guitar.first_skills else "Holding",
                DifficultyLevel.ABSOLUTE_BEGINNER,
                duration_minutes=20,
            )
            .add_objective(
                "posture-obj",
                "Correct Posture",
                "Maintain correct posture",
                SkillCategory.POSTURE,
                ["Comfortable seated position", "Relaxed shoulders"],
            )
            .add_resource(
                sources[0]["base_url"] if sources else "https://example.com",
                sources[0]["name"] if sources else "Example",
                "video",
            )
            .finish_module()
            .build(
                "guitar-101",
                "Guitar 101",
                "Complete beginner acoustic guitar curriculum",
            )
        )

        assert curriculum.instrument == "acoustic_guitar"
        assert curriculum.total_lessons == 1
        assert len(curriculum.modules[0].lessons[0].external_resources) == 1

    def test_learning_path_with_curriculum(self):
        """Test using a learning path with a curriculum."""
        from music_brain.learning import (
            CurriculumBuilder, Curriculum, LearningPath, DifficultyLevel
        )

        # Create simple curriculum
        curriculum = (
            CurriculumBuilder("piano")
            .start_module("m1", "Module 1", "Desc", (1, 3))
            .add_lesson("l1", "Lesson 1", "Desc", DifficultyLevel.BEGINNER)
            .finish_module()
            .start_module("m2", "Module 2", "Desc", (3, 5))
            .add_lesson("l2", "Lesson 2", "Desc", DifficultyLevel.INTERMEDIATE)
            .finish_module()
            .build("piano-101", "Piano 101", "Piano course")
        )

        # Create learning path
        path = LearningPath(
            id="path-001",
            student_id="student-001",
            curriculum_id=curriculum.id,
        )

        # Get available modules at beginner level
        available = curriculum.get_modules_for_level(DifficultyLevel.BEGINNER)
        assert len(available) >= 1

        # Complete first module
        path.complete_module("m1")
        path.complete_lesson("l1")

        # Get next modules
        next_modules = curriculum.get_next_modules(path.completed_module_ids)
        assert "m2" in [m.id for m in next_modules]

    def test_adaptive_teaching_with_student_profile(self):
        """Test adaptive teaching based on student profile."""
        from music_brain.learning import (
            StudentProfile, AdaptiveTeacher, LearningPreference
        )

        # Create detailed student profile
        student = StudentProfile(
            id="detailed-student",
            name="Detailed Student",
            age=16,
            experience_level=2,
            learning_preferences=[
                LearningPreference.VISUAL,
                LearningPreference.KINESTHETIC,
            ],
            primary_goal="play in a band",
            challenges=["reading music", "timing"],
            frustration_tolerance="low",
            performance_anxiety=True,
        )

        teacher = AdaptiveTeacher(student)

        # Generate lesson
        plan = teacher.generate_lesson_plan(
            "basic strumming",
            duration_minutes=25,
        )

        # Should have adaptations for the student
        assert "adaptations" in plan
        assert len(plan["adaptations"]) > 0

        # Generate feedback
        feedback = teacher.generate_feedback(
            "Struggled with chord changes",
            "chord transitions",
            success_level=0.4,
        )

        # Should have encouraging feedback for low frustration tolerance
        assert "encouragement" in feedback
        assert len(feedback["encouragement"]) > 0


class TestImports:
    """Test that all imports work correctly."""

    def test_import_curriculum(self):
        """Test importing from curriculum module."""
        from music_brain.learning.curriculum import (
            DifficultyLevel, SkillCategory, LearningObjective,
            Lesson, Module, Curriculum, LearningPath, CurriculumBuilder,
        )

    def test_import_resources(self):
        """Test importing from resources module."""
        from music_brain.learning.resources import (
            ResourceType, LearningResource, ResourceFetcher,
            ResourceCache, KNOWN_SOURCES,
        )

    def test_import_instruments(self):
        """Test importing from instruments module."""
        from music_brain.learning.instruments import (
            InstrumentFamily, Instrument, INSTRUMENTS,
            get_instrument, get_instruments_by_family, get_beginner_instruments,
        )

    def test_import_pedagogy(self):
        """Test importing from pedagogy module."""
        from music_brain.learning.pedagogy import (
            TeachingStyle, StudentProfile, LearningPreference,
            AdaptiveTeacher, PedagogyEngine, generate_ai_teaching_prompt,
        )

    def test_import_from_package(self):
        """Test importing from the main package."""
        from music_brain.learning import (
            # Curriculum
            DifficultyLevel, SkillCategory, Curriculum, LearningPath, CurriculumBuilder,
            # Resources
            ResourceType, LearningResource, ResourceFetcher, KNOWN_SOURCES,
            # Instruments
            InstrumentFamily, Instrument, INSTRUMENTS, get_instrument,
            # Pedagogy
            TeachingStyle, StudentProfile, AdaptiveTeacher, generate_ai_teaching_prompt,
        )
