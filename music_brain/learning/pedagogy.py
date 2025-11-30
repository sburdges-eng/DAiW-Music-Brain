"""
Pedagogy Module - AI teaching methodology and adaptive instruction.

Provides:
- TeachingStyle enum for different pedagogical approaches
- StudentProfile for tracking learner characteristics
- AdaptiveTeacher for personalized instruction
- PedagogyEngine for generating AI teaching prompts
- Prompt templates for AI-powered music education

Philosophy: "The best teacher adapts to the student, not the other way around."
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime
import random


class TeachingStyle(Enum):
    """Pedagogical approaches for music instruction."""
    # Traditional methods
    CLASSICAL = auto()          # Structured, notation-based, progressive
    SUZUKI = auto()             # Ear-first, parent involvement, repertoire-based
    KODALY = auto()             # Voice-based, solfege, rhythm syllables

    # Modern approaches
    CONTEMPORARY = auto()       # Popular music, chord charts, play-along
    PROJECT_BASED = auto()      # Learn by creating songs/projects
    GAMIFIED = auto()           # Points, levels, achievements

    # Adaptive methods
    SOCRATIC = auto()           # Question-based, discovery learning
    SCAFFOLDED = auto()         # Building blocks, gradual complexity
    MASTERY = auto()            # Perfect each skill before advancing

    # Specialized
    JAZZ_METHOD = auto()        # Improvisation-focused, aural tradition
    ORFF = auto()               # Movement, ensemble, percussion
    DALCROZE = auto()           # Eurhythmics, body movement, expression


class LearningPreference(Enum):
    """How a student prefers to learn."""
    VISUAL = auto()             # Diagrams, videos, sheet music
    AUDITORY = auto()           # Listening, ear training, recordings
    KINESTHETIC = auto()        # Hands-on, playing, movement
    READING = auto()            # Text explanations, theory
    SOCIAL = auto()             # Group learning, ensembles
    SOLITARY = auto()           # Self-paced, individual practice


@dataclass
class StudentProfile:
    """Profile of a music student for adaptive teaching."""
    id: str
    name: str

    # Learning characteristics
    age: int = 25
    experience_level: int = 1                   # 1-10
    learning_preferences: List[LearningPreference] = field(default_factory=list)
    preferred_styles: List[TeachingStyle] = field(default_factory=list)

    # Goals and motivation
    primary_goal: str = "personal_enjoyment"    # personal_enjoyment, performance, composition, etc.
    musical_interests: List[str] = field(default_factory=list)
    time_available_weekly_minutes: int = 300    # 5 hours default

    # Strengths and challenges
    strengths: List[str] = field(default_factory=list)
    challenges: List[str] = field(default_factory=list)
    learning_speed: str = "average"             # slow, average, fast

    # Practice habits
    practice_consistency: float = 0.7           # 0-1, how consistently they practice
    attention_span_minutes: int = 30
    prefers_structure: bool = True

    # Emotional factors
    performance_anxiety: bool = False
    perfectionism_level: str = "moderate"       # low, moderate, high
    frustration_tolerance: str = "moderate"     # low, moderate, high

    # Progress tracking
    lessons_completed: int = 0
    skills_mastered: List[str] = field(default_factory=list)
    current_repertoire: List[str] = field(default_factory=list)

    def get_ideal_lesson_duration(self) -> int:
        """Calculate ideal lesson duration based on profile."""
        base = self.attention_span_minutes
        if self.age < 10:
            return min(base, 20)
        if self.age < 15:
            return min(base, 30)
        return min(base, 60)

    def get_practice_session_length(self) -> int:
        """Suggest practice session length."""
        if self.experience_level <= 3:
            return min(20, self.attention_span_minutes)
        if self.experience_level <= 6:
            return min(30, self.attention_span_minutes)
        return min(45, self.attention_span_minutes)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "experience_level": self.experience_level,
            "learning_preferences": [p.name for p in self.learning_preferences],
            "preferred_styles": [s.name for s in self.preferred_styles],
            "primary_goal": self.primary_goal,
            "musical_interests": self.musical_interests,
            "time_available_weekly_minutes": self.time_available_weekly_minutes,
            "strengths": self.strengths,
            "challenges": self.challenges,
            "learning_speed": self.learning_speed,
            "practice_consistency": self.practice_consistency,
            "attention_span_minutes": self.attention_span_minutes,
            "prefers_structure": self.prefers_structure,
            "performance_anxiety": self.performance_anxiety,
            "perfectionism_level": self.perfectionism_level,
            "frustration_tolerance": self.frustration_tolerance,
            "lessons_completed": self.lessons_completed,
            "skills_mastered": self.skills_mastered,
            "current_repertoire": self.current_repertoire,
        }


class AdaptiveTeacher:
    """
    Adaptive teaching engine that adjusts to student needs.

    Generates personalized lesson content, exercises, and feedback.
    """

    def __init__(self, student: StudentProfile):
        self.student = student
        self.session_history: List[Dict[str, Any]] = []

    def select_teaching_style(self) -> TeachingStyle:
        """Select the most appropriate teaching style for the student."""
        if self.student.preferred_styles:
            return self.student.preferred_styles[0]

        # Default selection based on profile
        if self.student.age < 10:
            return TeachingStyle.SUZUKI
        if self.student.primary_goal == "improvisation":
            return TeachingStyle.JAZZ_METHOD
        if LearningPreference.KINESTHETIC in self.student.learning_preferences:
            return TeachingStyle.DALCROZE
        if self.student.prefers_structure:
            return TeachingStyle.MASTERY

        return TeachingStyle.CONTEMPORARY

    def generate_lesson_plan(
        self,
        topic: str,
        duration_minutes: int = 30,
        skill_level: int = None,
    ) -> Dict[str, Any]:
        """
        Generate a personalized lesson plan.

        Args:
            topic: What to teach (e.g., "major scales", "chord transitions")
            duration_minutes: Target lesson duration
            skill_level: Override skill level (uses student profile if not provided)

        Returns:
            Structured lesson plan
        """
        level = skill_level or self.student.experience_level
        style = self.select_teaching_style()
        attention = self.student.attention_span_minutes

        # Segment the lesson based on attention span
        segments = []
        remaining_time = duration_minutes

        # Warm-up (10-15% of lesson)
        warmup_time = max(3, int(duration_minutes * 0.12))
        segments.append({
            "type": "warmup",
            "duration_minutes": warmup_time,
            "description": self._generate_warmup(topic, level),
        })
        remaining_time -= warmup_time

        # Main instruction segments (break if longer than attention span)
        segment_length = min(attention // 2, 15)
        while remaining_time > segment_length + 5:  # Leave room for closing
            segments.append({
                "type": "instruction",
                "duration_minutes": segment_length,
                "description": f"Focused practice on {topic}",
            })
            remaining_time -= segment_length

            # Add variety/break if needed
            if remaining_time > 10:
                segments.append({
                    "type": "application",
                    "duration_minutes": 5,
                    "description": "Apply concept in musical context",
                })
                remaining_time -= 5

        # Closing/review
        segments.append({
            "type": "review",
            "duration_minutes": remaining_time,
            "description": "Review key points and set practice goals",
        })

        return {
            "topic": topic,
            "teaching_style": style.name,
            "total_duration_minutes": duration_minutes,
            "student_level": level,
            "segments": segments,
            "practice_assignment": self._generate_practice_assignment(topic, level),
            "success_criteria": self._generate_success_criteria(topic, level),
            "adaptations": self._get_adaptations(),
        }

    def _generate_warmup(self, topic: str, level: int) -> str:
        """Generate appropriate warmup activity."""
        warmups = {
            "scales": "Play familiar scales slowly, focusing on tone",
            "chords": "Strum or play through known chords with good form",
            "rhythm": "Clap or tap through basic rhythm patterns",
            "technique": "Finger exercises or stretches",
            "repertoire": "Play through a comfortable piece",
            "improvisation": "Free play in a comfortable key",
        }

        for key, value in warmups.items():
            if key in topic.lower():
                return value

        return "Light review of previously learned material"

    def _generate_practice_assignment(self, topic: str, level: int) -> Dict[str, Any]:
        """Generate a practice assignment."""
        session_length = self.student.get_practice_session_length()

        return {
            "daily_duration_minutes": session_length,
            "sessions_per_week": min(6, int(
                self.student.time_available_weekly_minutes / session_length
            )),
            "focus_areas": [
                {
                    "topic": topic,
                    "percentage": 40,
                    "instructions": f"Practice {topic} as demonstrated",
                },
                {
                    "topic": "review",
                    "percentage": 30,
                    "instructions": "Review previously learned material",
                },
                {
                    "topic": "free_play",
                    "percentage": 30,
                    "instructions": "Play music you enjoy for motivation",
                },
            ],
            "tips": self._get_practice_tips(),
        }

    def _get_practice_tips(self) -> List[str]:
        """Get personalized practice tips."""
        tips = []

        if self.student.frustration_tolerance == "low":
            tips.append("Take short breaks if you feel frustrated")
            tips.append("End on a success - play something you know well")

        if self.student.perfectionism_level == "high":
            tips.append("Progress over perfection - good enough is good enough")
            tips.append("Record yourself to hear improvement over time")

        if self.student.practice_consistency < 0.5:
            tips.append("Same time every day builds habits")
            tips.append("Even 10 minutes is valuable")

        if self.student.learning_speed == "slow":
            tips.append("Slow practice is fast learning")
            tips.append("Master small sections before moving on")

        # Default tips
        tips.extend([
            "Use a metronome for rhythm work",
            "Practice problem spots, not just the easy parts",
        ])

        return tips[:5]  # Limit to 5 tips

    def _generate_success_criteria(self, topic: str, level: int) -> List[str]:
        """Generate measurable success criteria."""
        criteria = [
            f"Can explain the concept of {topic} in your own words",
            f"Can demonstrate {topic} at a slow tempo without errors",
            f"Can identify common mistakes when practicing {topic}",
        ]

        if level >= 4:
            criteria.append(f"Can apply {topic} in a musical context")
        if level >= 7:
            criteria.append(f"Can teach {topic} to someone else")

        return criteria

    def _get_adaptations(self) -> List[str]:
        """Get adaptations based on student profile."""
        adaptations = []

        if self.student.performance_anxiety:
            adaptations.append("Practice performing for recordings before live audience")
            adaptations.append("Use relaxation techniques before playing")

        if self.student.age < 10:
            adaptations.append("Use games and stories to illustrate concepts")
            adaptations.append("Keep activities short and varied")

        if LearningPreference.VISUAL in self.student.learning_preferences:
            adaptations.append("Include diagrams, charts, and video demonstrations")

        if LearningPreference.AUDITORY in self.student.learning_preferences:
            adaptations.append("Emphasize listening examples and ear training")

        if LearningPreference.KINESTHETIC in self.student.learning_preferences:
            adaptations.append("Hands-on practice as soon as possible")
            adaptations.append("Use physical movement to reinforce concepts")

        return adaptations

    def generate_feedback(
        self,
        performance_notes: str,
        skill_demonstrated: str,
        success_level: float,  # 0-1
    ) -> Dict[str, Any]:
        """
        Generate personalized feedback on student performance.

        Args:
            performance_notes: Description of what the student did
            skill_demonstrated: Which skill was being practiced
            success_level: How well they did (0-1)

        Returns:
            Structured feedback with encouragement and improvement suggestions
        """
        feedback = {
            "skill": skill_demonstrated,
            "success_level": success_level,
            "praise": "",
            "constructive": [],
            "next_steps": [],
            "encouragement": "",
        }

        # Praise based on success level
        if success_level >= 0.9:
            feedback["praise"] = "Excellent work! You've really mastered this."
        elif success_level >= 0.7:
            feedback["praise"] = "Great progress! You're doing well with this."
        elif success_level >= 0.5:
            feedback["praise"] = "Good effort! You're making solid progress."
        else:
            feedback["praise"] = "You're working hard on this - that's what matters."

        # Adjust for perfectionism
        if self.student.perfectionism_level == "high" and success_level >= 0.7:
            feedback["encouragement"] = (
                "Remember: you don't need to be perfect. "
                "This level of skill is excellent for your stage."
            )
        elif self.student.frustration_tolerance == "low" and success_level < 0.5:
            feedback["encouragement"] = (
                "Every expert was once a beginner. "
                "This struggle is part of the learning process."
            )
        else:
            encouragements = [
                "Keep up the great work!",
                "Your dedication is paying off.",
                "You're building something great here.",
                "The journey is as important as the destination.",
            ]
            feedback["encouragement"] = random.choice(encouragements)

        # Constructive feedback
        if success_level < 0.9:
            feedback["constructive"] = [
                f"Focus on the specific areas where you felt uncertain",
                "Try practicing at a slower tempo",
                "Break the skill into smaller components",
            ]

        # Next steps
        if success_level >= 0.7:
            feedback["next_steps"] = [
                "Try increasing the tempo gradually",
                "Apply this skill in a new musical context",
                "Combine with previously learned skills",
            ]
        else:
            feedback["next_steps"] = [
                "Review the fundamentals of this skill",
                "Practice with focused attention on problem areas",
                "Consider breaking down into smaller steps",
            ]

        return feedback


class PedagogyEngine:
    """
    Engine for generating AI teaching prompts and content.

    Provides structured prompts for AI to act as a music teacher.
    """

    def __init__(self):
        self.templates = TEACHING_PROMPT_TEMPLATES

    def generate_ai_prompt(
        self,
        action: str,
        instrument: str,
        topic: str,
        student: Optional[StudentProfile] = None,
        difficulty: int = 5,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate a prompt for AI to perform a teaching action.

        Args:
            action: What the AI should do (explain, demonstrate, assess, etc.)
            instrument: The instrument being taught
            topic: The specific topic or skill
            student: Optional student profile for personalization
            difficulty: Difficulty level 1-10
            additional_context: Extra context to include

        Returns:
            A formatted prompt string for the AI
        """
        template = self.templates.get(action, self.templates["explain"])

        context_parts = [
            f"Instrument: {instrument}",
            f"Topic: {topic}",
            f"Difficulty Level: {difficulty}/10",
        ]

        if student:
            context_parts.extend([
                f"Student Age: {student.age}",
                f"Experience Level: {student.experience_level}/10",
                f"Learning Style: {', '.join(p.name for p in student.learning_preferences) or 'Not specified'}",
                f"Primary Goal: {student.primary_goal}",
            ])
            if student.challenges:
                context_parts.append(f"Known Challenges: {', '.join(student.challenges)}")
            if student.strengths:
                context_parts.append(f"Strengths: {', '.join(student.strengths)}")

        if additional_context:
            for key, value in additional_context.items():
                context_parts.append(f"{key}: {value}")

        context = "\n".join(context_parts)

        return template.format(
            instrument=instrument,
            topic=topic,
            difficulty=difficulty,
            context=context,
        )

    def generate_lesson_prompt(
        self,
        instrument: str,
        topic: str,
        student: StudentProfile,
        duration_minutes: int = 30,
    ) -> str:
        """Generate a comprehensive lesson prompt."""
        return f"""Design a {duration_minutes}-minute lesson plan for teaching {topic} on {instrument}.

STUDENT PROFILE:
{self._format_student_profile(student)}

LESSON REQUIREMENTS:
1. Include a warm-up activity (3-5 minutes)
2. Main instruction with clear explanations
3. Hands-on practice exercises
4. Application in a musical context
5. Summary and practice assignment

TEACHING APPROACH:
- Match the student's learning preferences
- Consider their challenges and adapt accordingly
- Build on their strengths
- Keep activities varied to maintain engagement
- Provide clear success criteria

FORMAT YOUR RESPONSE AS:
## Lesson Overview
[Brief summary]

## Warm-Up (X minutes)
[Activity description]

## Main Instruction (X minutes)
[Step-by-step teaching content]

## Practice Exercises
[Specific exercises with instructions]

## Musical Application
[How to apply the skill musically]

## Practice Assignment
[What to practice before next lesson]

## Success Criteria
[How to know when they've got it]
"""

    def generate_assessment_prompt(
        self,
        instrument: str,
        skill: str,
        student: StudentProfile,
        performance_description: str,
    ) -> str:
        """Generate a prompt for assessing student performance."""
        return f"""Assess this student's performance and provide personalized feedback.

INSTRUMENT: {instrument}
SKILL BEING ASSESSED: {skill}

STUDENT PROFILE:
{self._format_student_profile(student)}

PERFORMANCE DESCRIPTION:
{performance_description}

PROVIDE:
1. What they did well (be specific and encouraging)
2. Areas for improvement (constructive, not discouraging)
3. Specific exercises to address any issues
4. Encouragement appropriate to their personality
5. Clear next steps

Remember:
- If they have high perfectionism, reassure them about normal progress
- If they have low frustration tolerance, emphasize progress over perfection
- Match feedback to their learning preferences
- Be honest but kind
"""

    def generate_exercise_prompt(
        self,
        instrument: str,
        skill: str,
        difficulty: int,
        duration_minutes: int = 10,
    ) -> str:
        """Generate a prompt for creating a practice exercise."""
        return f"""Create a {duration_minutes}-minute practice exercise for {skill} on {instrument}.

DIFFICULTY: {difficulty}/10

THE EXERCISE SHOULD INCLUDE:
1. Clear objective (what the student will be able to do)
2. Step-by-step instructions
3. Tempo and dynamic markings if applicable
4. Common mistakes to avoid
5. How to know when it's done correctly
6. Variations for making it easier or harder

FORMAT:
## Exercise: [Name]
**Objective:** [What you'll achieve]
**Duration:** {duration_minutes} minutes
**Tempo:** [If applicable]

### Instructions
[Numbered steps]

### Common Mistakes
[What to avoid]

### Success Indicators
[How to know you got it]

### Variations
- Easier: [Modification]
- Harder: [Modification]
"""

    def _format_student_profile(self, student: StudentProfile) -> str:
        """Format student profile for inclusion in prompts."""
        lines = [
            f"- Age: {student.age}",
            f"- Experience Level: {student.experience_level}/10",
            f"- Learning Speed: {student.learning_speed}",
            f"- Attention Span: {student.attention_span_minutes} minutes",
            f"- Primary Goal: {student.primary_goal}",
        ]

        if student.learning_preferences:
            prefs = ", ".join(p.name.lower() for p in student.learning_preferences)
            lines.append(f"- Learning Preferences: {prefs}")

        if student.strengths:
            lines.append(f"- Strengths: {', '.join(student.strengths)}")

        if student.challenges:
            lines.append(f"- Challenges: {', '.join(student.challenges)}")

        if student.performance_anxiety:
            lines.append("- Has performance anxiety")

        lines.append(f"- Perfectionism: {student.perfectionism_level}")
        lines.append(f"- Frustration Tolerance: {student.frustration_tolerance}")

        return "\n".join(lines)


# Teaching prompt templates for different actions
TEACHING_PROMPT_TEMPLATES = {
    "explain": """Explain {topic} for {instrument} at difficulty level {difficulty}/10.

CONTEXT:
{context}

INSTRUCTIONS:
1. Start with WHY this topic matters for the student
2. Explain the concept in simple, clear terms
3. Use analogies appropriate to their age and experience
4. Provide step-by-step instructions
5. Include common mistakes to avoid
6. End with how this connects to their musical goals

Keep the explanation engaging and practical. Focus on understanding, not just information.""",

    "demonstrate": """Describe how to demonstrate {topic} for {instrument}.

CONTEXT:
{context}

PROVIDE:
1. What to show (the physical/auditory demonstration)
2. Key points to highlight while demonstrating
3. What to say during the demonstration
4. How to check student understanding
5. Follow-up activities for the student to try

Make the demonstration clear and memorable.""",

    "troubleshoot": """Help troubleshoot common problems with {topic} on {instrument}.

CONTEXT:
{context}

ADDRESS:
1. The most common mistakes students make
2. Why these mistakes happen
3. How to identify each problem
4. Specific corrections for each issue
5. Exercises to fix each problem
6. How to prevent the problems in the future

Be specific and practical.""",

    "motivate": """Generate motivational content for a student learning {topic} on {instrument}.

CONTEXT:
{context}

INCLUDE:
1. Encouragement appropriate to their level
2. Examples of what they'll be able to do with this skill
3. Stories or examples of progression
4. Reminder of their "why"
5. Practical next steps that feel achievable

Be genuine and avoid empty praise.""",

    "assess": """Create an assessment for {topic} on {instrument} at difficulty level {difficulty}/10.

CONTEXT:
{context}

DESIGN AN ASSESSMENT THAT:
1. Tests understanding of the concept
2. Tests practical execution
3. Has clear success criteria
4. Is appropriate for the student's level
5. Provides useful feedback
6. Feels encouraging, not stressful

Include both what to test and how to evaluate it.""",

    "practice_plan": """Create a practice plan for {topic} on {instrument}.

CONTEXT:
{context}

THE PLAN SHOULD INCLUDE:
1. Daily practice routine (specific activities and durations)
2. Weekly goals
3. How to track progress
4. Troubleshooting common issues
5. When to move on vs. when to keep practicing
6. How to keep practice interesting

Be specific and realistic.""",

    "song_suggestion": """Suggest songs for practicing {topic} on {instrument} at difficulty level {difficulty}/10.

CONTEXT:
{context}

FOR EACH SONG, PROVIDE:
1. Song title and artist
2. Why it's good for this skill
3. Specific parts that demonstrate the skill
4. Difficulty rating
5. Tips for learning it
6. What to focus on

Suggest 3-5 songs at varying difficulty within the range.""",
}


def generate_ai_teaching_prompt(
    action: str,
    instrument: str,
    topic: str,
    student: Optional[StudentProfile] = None,
    difficulty: int = 5,
    **kwargs,
) -> str:
    """
    Convenience function to generate AI teaching prompts.

    Args:
        action: What the AI should do (explain, demonstrate, assess, etc.)
        instrument: The instrument being taught
        topic: The specific topic or skill
        student: Optional student profile for personalization
        difficulty: Difficulty level 1-10
        **kwargs: Additional context

    Returns:
        A formatted prompt string for the AI
    """
    engine = PedagogyEngine()
    return engine.generate_ai_prompt(
        action=action,
        instrument=instrument,
        topic=topic,
        student=student,
        difficulty=difficulty,
        additional_context=kwargs if kwargs else None,
    )


# Pre-built teaching sequences for common topics
TEACHING_SEQUENCES = {
    "beginner_guitar_chords": [
        {"action": "explain", "topic": "why chords matter in guitar playing"},
        {"action": "demonstrate", "topic": "proper finger placement for G chord"},
        {"action": "practice_plan", "topic": "G chord practice routine"},
        {"action": "demonstrate", "topic": "proper finger placement for C chord"},
        {"action": "practice_plan", "topic": "C chord practice routine"},
        {"action": "explain", "topic": "transitioning between G and C chords"},
        {"action": "practice_plan", "topic": "chord transition practice"},
        {"action": "song_suggestion", "topic": "songs using G and C chords"},
    ],
    "beginner_piano_scales": [
        {"action": "explain", "topic": "what scales are and why they matter"},
        {"action": "demonstrate", "topic": "C major scale with correct fingering"},
        {"action": "practice_plan", "topic": "C major scale practice routine"},
        {"action": "troubleshoot", "topic": "common scale fingering mistakes"},
        {"action": "explain", "topic": "how scales relate to songs you play"},
        {"action": "practice_plan", "topic": "incorporating scales into daily practice"},
    ],
    "beginner_drum_beats": [
        {"action": "explain", "topic": "basic drum kit orientation"},
        {"action": "demonstrate", "topic": "basic rock beat"},
        {"action": "practice_plan", "topic": "rock beat practice with metronome"},
        {"action": "troubleshoot", "topic": "common timing issues in drum beats"},
        {"action": "explain", "topic": "adding hi-hat variations"},
        {"action": "song_suggestion", "topic": "songs with basic rock beats"},
    ],
}
