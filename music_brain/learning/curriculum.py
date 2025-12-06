"""
Curriculum System - Structured learning paths with incremental difficulty.

Provides:
- DifficultyLevel enum with 10 granular levels
- SkillCategory for organizing abilities
- Lesson, Module, and Curriculum structures
- LearningPath for personalized progression
- CurriculumBuilder for creating custom curricula

Philosophy: "Small steps, consistently applied, create mastery."
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Set
from datetime import datetime, timedelta
import json


class DifficultyLevel(Enum):
    """
    10-level difficulty scale for granular progression.

    Each level represents approximately 50-100 hours of practice.
    """
    # Beginner Tier (0-300 hours)
    ABSOLUTE_BEGINNER = 1      # Never touched the instrument
    EARLY_BEGINNER = 2         # Learning to hold/position correctly
    BEGINNER = 3               # Basic notes/chords, simple rhythms

    # Intermediate Tier (300-1000 hours)
    EARLY_INTERMEDIATE = 4     # Simple songs, basic technique
    INTERMEDIATE = 5           # Full songs, developing style
    LATE_INTERMEDIATE = 6      # Complex pieces, theory understanding

    # Advanced Tier (1000-3000 hours)
    EARLY_ADVANCED = 7         # Improvisation, composition basics
    ADVANCED = 8               # Complex improvisation, arranging
    LATE_ADVANCED = 9          # Professional-level execution

    # Mastery Tier (3000+ hours)
    EXPERT = 10                # Teaching-level mastery

    @property
    def name_friendly(self) -> str:
        """Human-readable name."""
        names = {
            1: "Absolute Beginner",
            2: "Early Beginner",
            3: "Beginner",
            4: "Early Intermediate",
            5: "Intermediate",
            6: "Late Intermediate",
            7: "Early Advanced",
            8: "Advanced",
            9: "Late Advanced",
            10: "Expert/Master",
        }
        return names.get(self.value, "Unknown")

    @property
    def estimated_hours(self) -> tuple:
        """Estimated practice hours to reach this level."""
        hours = {
            1: (0, 0),
            2: (10, 50),
            3: (50, 150),
            4: (150, 300),
            5: (300, 500),
            6: (500, 1000),
            7: (1000, 1500),
            8: (1500, 2500),
            9: (2500, 4000),
            10: (4000, 10000),
        }
        return hours.get(self.value, (0, 0))

    @property
    def tier(self) -> str:
        """Get the tier name for this level."""
        if self.value <= 3:
            return "Beginner"
        elif self.value <= 6:
            return "Intermediate"
        elif self.value <= 9:
            return "Advanced"
        return "Expert"

    def can_attempt(self, target_level: 'DifficultyLevel') -> bool:
        """Check if student at this level can attempt target level content."""
        # Allow attempting content up to 2 levels above current
        return target_level.value <= self.value + 2


class SkillCategory(Enum):
    """Categories of musical skills."""
    # Technical Skills
    TECHNIQUE = auto()          # Physical execution, dexterity
    POSTURE = auto()            # Body position, ergonomics
    TONE = auto()               # Sound production quality
    ARTICULATION = auto()       # Note attacks, releases
    DYNAMICS = auto()           # Volume control, expression

    # Rhythmic Skills
    RHYTHM = auto()             # Basic timing, pulse
    GROOVE = auto()             # Feel, pocket, swing
    TEMPO = auto()              # Speed control, consistency
    SUBDIVISION = auto()        # Note value precision
    POLYRHYTHM = auto()         # Multiple rhythms simultaneously

    # Melodic/Harmonic Skills
    MELODY = auto()             # Single-line playing
    HARMONY = auto()            # Chords, voice leading
    SCALES = auto()             # Scale knowledge and execution
    ARPEGGIOS = auto()          # Broken chords
    INTERVALS = auto()          # Distance between notes

    # Musical Understanding
    THEORY = auto()             # Music theory knowledge
    EAR_TRAINING = auto()       # Listening and identification
    SIGHT_READING = auto()      # Reading notation
    IMPROVISATION = auto()      # Spontaneous creation
    COMPOSITION = auto()        # Structured creation

    # Performance Skills
    REPERTOIRE = auto()         # Song knowledge
    MEMORIZATION = auto()       # Playing without notation
    STAGE_PRESENCE = auto()     # Performance confidence
    ENSEMBLE = auto()           # Playing with others

    # Meta Skills
    PRACTICE_HABITS = auto()    # Effective practice techniques
    SELF_ASSESSMENT = auto()    # Identifying weaknesses
    GOAL_SETTING = auto()       # Progress planning


@dataclass
class LearningObjective:
    """A specific, measurable learning goal."""
    id: str
    title: str
    description: str
    skill_category: SkillCategory
    difficulty: DifficultyLevel

    # Success criteria
    success_criteria: List[str] = field(default_factory=list)
    assessment_method: str = "self-assessment"

    # Prerequisites
    prerequisite_ids: List[str] = field(default_factory=list)

    # Time estimates
    estimated_practice_minutes: int = 30
    suggested_sessions: int = 5

    # Tags for searchability
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "skill_category": self.skill_category.name,
            "difficulty": self.difficulty.value,
            "success_criteria": self.success_criteria,
            "assessment_method": self.assessment_method,
            "prerequisite_ids": self.prerequisite_ids,
            "estimated_practice_minutes": self.estimated_practice_minutes,
            "suggested_sessions": self.suggested_sessions,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningObjective':
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            skill_category=SkillCategory[data["skill_category"]],
            difficulty=DifficultyLevel(data["difficulty"]),
            success_criteria=data.get("success_criteria", []),
            assessment_method=data.get("assessment_method", "self-assessment"),
            prerequisite_ids=data.get("prerequisite_ids", []),
            estimated_practice_minutes=data.get("estimated_practice_minutes", 30),
            suggested_sessions=data.get("suggested_sessions", 5),
            tags=data.get("tags", []),
        )


@dataclass
class Lesson:
    """A single lesson within a module."""
    id: str
    title: str
    description: str
    difficulty: DifficultyLevel

    # Content
    objectives: List[LearningObjective] = field(default_factory=list)
    content_sections: List[Dict[str, str]] = field(default_factory=list)
    exercises: List[Dict[str, Any]] = field(default_factory=list)

    # Media references
    video_urls: List[str] = field(default_factory=list)
    audio_urls: List[str] = field(default_factory=list)
    sheet_music_urls: List[str] = field(default_factory=list)

    # External resources
    external_resources: List[Dict[str, str]] = field(default_factory=list)

    # Timing
    estimated_duration_minutes: int = 30
    practice_routine: Optional[Dict[str, Any]] = None

    # Metadata
    author: str = "DAiW Learning Module"
    source_url: Optional[str] = None
    last_updated: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty.value,
            "objectives": [obj.to_dict() for obj in self.objectives],
            "content_sections": self.content_sections,
            "exercises": self.exercises,
            "video_urls": self.video_urls,
            "audio_urls": self.audio_urls,
            "sheet_music_urls": self.sheet_music_urls,
            "external_resources": self.external_resources,
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "practice_routine": self.practice_routine,
            "author": self.author,
            "source_url": self.source_url,
            "last_updated": self.last_updated,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Lesson':
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            difficulty=DifficultyLevel(data["difficulty"]),
            objectives=[LearningObjective.from_dict(o) for o in data.get("objectives", [])],
            content_sections=data.get("content_sections", []),
            exercises=data.get("exercises", []),
            video_urls=data.get("video_urls", []),
            audio_urls=data.get("audio_urls", []),
            sheet_music_urls=data.get("sheet_music_urls", []),
            external_resources=data.get("external_resources", []),
            estimated_duration_minutes=data.get("estimated_duration_minutes", 30),
            practice_routine=data.get("practice_routine"),
            author=data.get("author", "DAiW Learning Module"),
            source_url=data.get("source_url"),
            last_updated=data.get("last_updated"),
        )


@dataclass
class Module:
    """A collection of related lessons forming a unit of study."""
    id: str
    title: str
    description: str
    difficulty_range: tuple  # (min_level, max_level)

    # Content
    lessons: List[Lesson] = field(default_factory=list)
    skill_focus: List[SkillCategory] = field(default_factory=list)

    # Prerequisites
    prerequisite_module_ids: List[str] = field(default_factory=list)

    # Completion criteria
    required_lesson_ids: List[str] = field(default_factory=list)
    passing_score: float = 0.7  # 70% of objectives met

    # Metadata
    tags: List[str] = field(default_factory=list)

    @property
    def total_duration_minutes(self) -> int:
        return sum(lesson.estimated_duration_minutes for lesson in self.lessons)

    @property
    def lesson_count(self) -> int:
        return len(self.lessons)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "difficulty_range": list(self.difficulty_range),
            "lessons": [lesson.to_dict() for lesson in self.lessons],
            "skill_focus": [s.name for s in self.skill_focus],
            "prerequisite_module_ids": self.prerequisite_module_ids,
            "required_lesson_ids": self.required_lesson_ids,
            "passing_score": self.passing_score,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Module':
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            difficulty_range=tuple(data["difficulty_range"]),
            lessons=[Lesson.from_dict(l) for l in data.get("lessons", [])],
            skill_focus=[SkillCategory[s] for s in data.get("skill_focus", [])],
            prerequisite_module_ids=data.get("prerequisite_module_ids", []),
            required_lesson_ids=data.get("required_lesson_ids", []),
            passing_score=data.get("passing_score", 0.7),
            tags=data.get("tags", []),
        )


@dataclass
class Curriculum:
    """A complete curriculum for an instrument or skill area."""
    id: str
    title: str
    description: str
    instrument: str

    # Structure
    modules: List[Module] = field(default_factory=list)

    # Difficulty coverage
    min_difficulty: DifficultyLevel = DifficultyLevel.ABSOLUTE_BEGINNER
    max_difficulty: DifficultyLevel = DifficultyLevel.EXPERT

    # Metadata
    version: str = "1.0.0"
    author: str = "DAiW Learning Module"
    created_date: Optional[str] = None
    last_updated: Optional[str] = None
    source_urls: List[str] = field(default_factory=list)

    @property
    def total_lessons(self) -> int:
        return sum(module.lesson_count for module in self.modules)

    @property
    def total_duration_hours(self) -> float:
        minutes = sum(module.total_duration_minutes for module in self.modules)
        return minutes / 60

    def get_modules_for_level(self, level: DifficultyLevel) -> List[Module]:
        """Get modules appropriate for a given difficulty level."""
        return [
            m for m in self.modules
            if m.difficulty_range[0] <= level.value <= m.difficulty_range[1]
        ]

    def get_next_modules(self, completed_module_ids: Set[str]) -> List[Module]:
        """Get modules available based on completed prerequisites."""
        available = []
        for module in self.modules:
            if module.id in completed_module_ids:
                continue
            prereqs_met = all(
                pid in completed_module_ids
                for pid in module.prerequisite_module_ids
            )
            if prereqs_met:
                available.append(module)
        return available

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "instrument": self.instrument,
            "modules": [m.to_dict() for m in self.modules],
            "min_difficulty": self.min_difficulty.value,
            "max_difficulty": self.max_difficulty.value,
            "version": self.version,
            "author": self.author,
            "created_date": self.created_date,
            "last_updated": self.last_updated,
            "source_urls": self.source_urls,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Curriculum':
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            instrument=data["instrument"],
            modules=[Module.from_dict(m) for m in data.get("modules", [])],
            min_difficulty=DifficultyLevel(data.get("min_difficulty", 1)),
            max_difficulty=DifficultyLevel(data.get("max_difficulty", 10)),
            version=data.get("version", "1.0.0"),
            author=data.get("author", "DAiW Learning Module"),
            created_date=data.get("created_date"),
            last_updated=data.get("last_updated"),
            source_urls=data.get("source_urls", []),
        )

    def save(self, filepath: str) -> None:
        """Save curriculum to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> 'Curriculum':
        """Load curriculum from JSON file."""
        with open(filepath, 'r') as f:
            return cls.from_dict(json.load(f))


@dataclass
class LearningPath:
    """A personalized learning journey for a student."""
    id: str
    student_id: str
    curriculum_id: str

    # Current state
    current_level: DifficultyLevel = DifficultyLevel.ABSOLUTE_BEGINNER
    completed_lesson_ids: Set[str] = field(default_factory=set)
    completed_module_ids: Set[str] = field(default_factory=set)
    completed_objective_ids: Set[str] = field(default_factory=set)

    # Progress tracking
    total_practice_minutes: int = 0
    session_count: int = 0
    streak_days: int = 0
    last_practice_date: Optional[str] = None

    # Goals
    target_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    weekly_practice_goal_minutes: int = 300  # 5 hours/week default

    # Adaptive learning data
    strong_skills: List[SkillCategory] = field(default_factory=list)
    weak_skills: List[SkillCategory] = field(default_factory=list)
    preferred_content_types: List[str] = field(default_factory=list)

    @property
    def progress_percentage(self) -> float:
        """Calculate overall progress toward target level."""
        current = self.current_level.value
        target = self.target_level.value
        start = DifficultyLevel.ABSOLUTE_BEGINNER.value

        if target <= start:
            return 100.0

        return min(100.0, ((current - start) / (target - start)) * 100)

    def record_practice(self, minutes: int) -> None:
        """Record a practice session."""
        self.total_practice_minutes += minutes
        self.session_count += 1
        today = datetime.now().strftime("%Y-%m-%d")

        if self.last_practice_date:
            last = datetime.strptime(self.last_practice_date, "%Y-%m-%d")
            diff = (datetime.now() - last).days
            if diff == 1:
                self.streak_days += 1
            elif diff > 1:
                self.streak_days = 1
        else:
            self.streak_days = 1

        self.last_practice_date = today

    def complete_lesson(self, lesson_id: str) -> None:
        """Mark a lesson as completed."""
        self.completed_lesson_ids.add(lesson_id)

    def complete_module(self, module_id: str) -> None:
        """Mark a module as completed."""
        self.completed_module_ids.add(module_id)

    def complete_objective(self, objective_id: str) -> None:
        """Mark an objective as completed."""
        self.completed_objective_ids.add(objective_id)

    def level_up(self) -> bool:
        """Attempt to increase the current level."""
        if self.current_level.value < 10:
            self.current_level = DifficultyLevel(self.current_level.value + 1)
            return True
        return False

    def get_recommended_focus(self) -> List[SkillCategory]:
        """Get skills that need the most attention."""
        if self.weak_skills:
            return self.weak_skills[:3]
        # Default focus areas for beginners
        return [
            SkillCategory.TECHNIQUE,
            SkillCategory.RHYTHM,
            SkillCategory.PRACTICE_HABITS,
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "student_id": self.student_id,
            "curriculum_id": self.curriculum_id,
            "current_level": self.current_level.value,
            "completed_lesson_ids": list(self.completed_lesson_ids),
            "completed_module_ids": list(self.completed_module_ids),
            "completed_objective_ids": list(self.completed_objective_ids),
            "total_practice_minutes": self.total_practice_minutes,
            "session_count": self.session_count,
            "streak_days": self.streak_days,
            "last_practice_date": self.last_practice_date,
            "target_level": self.target_level.value,
            "weekly_practice_goal_minutes": self.weekly_practice_goal_minutes,
            "strong_skills": [s.name for s in self.strong_skills],
            "weak_skills": [s.name for s in self.weak_skills],
            "preferred_content_types": self.preferred_content_types,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningPath':
        path = cls(
            id=data["id"],
            student_id=data["student_id"],
            curriculum_id=data["curriculum_id"],
        )
        path.current_level = DifficultyLevel(data.get("current_level", 1))
        path.completed_lesson_ids = set(data.get("completed_lesson_ids", []))
        path.completed_module_ids = set(data.get("completed_module_ids", []))
        path.completed_objective_ids = set(data.get("completed_objective_ids", []))
        path.total_practice_minutes = data.get("total_practice_minutes", 0)
        path.session_count = data.get("session_count", 0)
        path.streak_days = data.get("streak_days", 0)
        path.last_practice_date = data.get("last_practice_date")
        path.target_level = DifficultyLevel(data.get("target_level", 5))
        path.weekly_practice_goal_minutes = data.get("weekly_practice_goal_minutes", 300)
        path.strong_skills = [SkillCategory[s] for s in data.get("strong_skills", [])]
        path.weak_skills = [SkillCategory[s] for s in data.get("weak_skills", [])]
        path.preferred_content_types = data.get("preferred_content_types", [])
        return path


class CurriculumBuilder:
    """Builder for creating curricula from fetched resources."""

    def __init__(self, instrument: str):
        self.instrument = instrument
        self.modules: List[Module] = []
        self.current_module: Optional[Module] = None
        self.current_lesson: Optional[Lesson] = None

    def start_module(
        self,
        module_id: str,
        title: str,
        description: str,
        difficulty_range: tuple,
        skill_focus: Optional[List[SkillCategory]] = None,
    ) -> 'CurriculumBuilder':
        """Start building a new module."""
        self.current_module = Module(
            id=module_id,
            title=title,
            description=description,
            difficulty_range=difficulty_range,
            skill_focus=skill_focus or [],
        )
        return self

    def add_lesson(
        self,
        lesson_id: str,
        title: str,
        description: str,
        difficulty: DifficultyLevel,
        duration_minutes: int = 30,
    ) -> 'CurriculumBuilder':
        """Add a lesson to the current module."""
        if not self.current_module:
            raise ValueError("Must start a module before adding lessons")

        self.current_lesson = Lesson(
            id=lesson_id,
            title=title,
            description=description,
            difficulty=difficulty,
            estimated_duration_minutes=duration_minutes,
        )
        self.current_module.lessons.append(self.current_lesson)
        return self

    def add_objective(
        self,
        objective_id: str,
        title: str,
        description: str,
        skill_category: SkillCategory,
        success_criteria: Optional[List[str]] = None,
    ) -> 'CurriculumBuilder':
        """Add an objective to the current lesson."""
        if not self.current_lesson:
            raise ValueError("Must add a lesson before adding objectives")

        objective = LearningObjective(
            id=objective_id,
            title=title,
            description=description,
            skill_category=skill_category,
            difficulty=self.current_lesson.difficulty,
            success_criteria=success_criteria or [],
        )
        self.current_lesson.objectives.append(objective)
        return self

    def add_exercise(
        self,
        title: str,
        instructions: str,
        duration_minutes: int = 5,
        repetitions: Optional[int] = None,
        tempo_bpm: Optional[int] = None,
    ) -> 'CurriculumBuilder':
        """Add an exercise to the current lesson."""
        if not self.current_lesson:
            raise ValueError("Must add a lesson before adding exercises")

        exercise = {
            "title": title,
            "instructions": instructions,
            "duration_minutes": duration_minutes,
        }
        if repetitions:
            exercise["repetitions"] = repetitions
        if tempo_bpm:
            exercise["tempo_bpm"] = tempo_bpm

        self.current_lesson.exercises.append(exercise)
        return self

    def add_resource(
        self,
        url: str,
        title: str,
        resource_type: str = "article",
    ) -> 'CurriculumBuilder':
        """Add an external resource to the current lesson."""
        if not self.current_lesson:
            raise ValueError("Must add a lesson before adding resources")

        self.current_lesson.external_resources.append({
            "url": url,
            "title": title,
            "type": resource_type,
        })
        return self

    def finish_module(self) -> 'CurriculumBuilder':
        """Finish the current module and add it to the list."""
        if self.current_module:
            self.modules.append(self.current_module)
            self.current_module = None
            self.current_lesson = None
        return self

    def build(
        self,
        curriculum_id: str,
        title: str,
        description: str,
    ) -> Curriculum:
        """Build and return the complete curriculum."""
        # Make sure any open module is finished
        self.finish_module()

        # Determine difficulty range from modules
        if self.modules:
            min_diff = min(m.difficulty_range[0] for m in self.modules)
            max_diff = max(m.difficulty_range[1] for m in self.modules)
        else:
            min_diff, max_diff = 1, 10

        return Curriculum(
            id=curriculum_id,
            title=title,
            description=description,
            instrument=self.instrument,
            modules=self.modules,
            min_difficulty=DifficultyLevel(min_diff),
            max_difficulty=DifficultyLevel(max_diff),
            created_date=datetime.now().strftime("%Y-%m-%d"),
            last_updated=datetime.now().strftime("%Y-%m-%d"),
        )


# Pre-built skill progressions for common patterns
SKILL_PROGRESSIONS = {
    "rhythm_foundation": [
        (DifficultyLevel.ABSOLUTE_BEGINNER, [SkillCategory.RHYTHM]),
        (DifficultyLevel.BEGINNER, [SkillCategory.TEMPO, SkillCategory.SUBDIVISION]),
        (DifficultyLevel.INTERMEDIATE, [SkillCategory.GROOVE]),
        (DifficultyLevel.ADVANCED, [SkillCategory.POLYRHYTHM]),
    ],
    "melodic_development": [
        (DifficultyLevel.BEGINNER, [SkillCategory.MELODY]),
        (DifficultyLevel.EARLY_INTERMEDIATE, [SkillCategory.SCALES]),
        (DifficultyLevel.INTERMEDIATE, [SkillCategory.INTERVALS, SkillCategory.ARPEGGIOS]),
        (DifficultyLevel.ADVANCED, [SkillCategory.IMPROVISATION]),
    ],
    "harmonic_mastery": [
        (DifficultyLevel.EARLY_INTERMEDIATE, [SkillCategory.HARMONY]),
        (DifficultyLevel.INTERMEDIATE, [SkillCategory.THEORY]),
        (DifficultyLevel.LATE_INTERMEDIATE, [SkillCategory.EAR_TRAINING]),
        (DifficultyLevel.ADVANCED, [SkillCategory.COMPOSITION]),
    ],
}
