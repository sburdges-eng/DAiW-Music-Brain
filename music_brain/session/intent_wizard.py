"""
Interactive Song Intent Wizard

A guided interrogation system that helps artists discover their emotional intent
through branching questions. Implements the "Interrogate Before Generate" philosophy.

Assigned to: ChatGPT

Features:
- Branching question trees based on emotional responses
- Progressive deepening from surface to core intent
- Adaptive follow-up questions
- Intent validation and completeness scoring
- Export to CompleteSongIntent schema
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any, Tuple
from enum import Enum
import json
from pathlib import Path


class QuestionCategory(Enum):
    """Categories of questions in the intent discovery process."""
    SURFACE = "surface"           # Initial exploration
    EMOTIONAL = "emotional"       # Feeling identification
    RESISTANCE = "resistance"     # What's hard to say
    LONGING = "longing"           # What you want to feel
    STAKES = "stakes"             # What's at risk
    TRANSFORMATION = "transformation"  # Desired change
    TECHNICAL = "technical"       # Genre/style preferences


class ResponseType(Enum):
    """Types of responses expected."""
    FREE_TEXT = "free_text"
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    SCALE = "scale"               # 1-10 or similar
    BOOLEAN = "boolean"


@dataclass
class Choice:
    """A choice option for single/multiple choice questions."""
    id: str
    text: str
    leads_to: Optional[str] = None  # Question ID to branch to
    tags: List[str] = field(default_factory=list)  # Tags for analysis


@dataclass
class Question:
    """A single question in the wizard."""
    id: str
    text: str
    category: QuestionCategory
    response_type: ResponseType

    # For choice-based questions
    choices: List[Choice] = field(default_factory=list)

    # For scale questions
    scale_min: int = 1
    scale_max: int = 10
    scale_labels: Dict[int, str] = field(default_factory=dict)

    # Navigation
    next_question: Optional[str] = None  # Default next question
    conditional_next: Dict[str, str] = field(default_factory=dict)  # Response -> next question

    # Metadata
    required: bool = True
    help_text: Optional[str] = None
    example_answers: List[str] = field(default_factory=list)

    # Mapping to intent schema
    maps_to: Optional[str] = None  # Field in CompleteSongIntent


@dataclass
class WizardResponse:
    """A user's response to a question."""
    question_id: str
    response: Any  # Could be string, list, int, bool
    timestamp: str = ""


@dataclass
class WizardSession:
    """A complete wizard session."""
    session_id: str
    responses: List[WizardResponse] = field(default_factory=list)
    current_question_id: Optional[str] = None
    started_at: str = ""
    completed_at: Optional[str] = None
    completeness_score: float = 0.0

    def get_response(self, question_id: str) -> Optional[WizardResponse]:
        """Get response for a specific question."""
        for r in self.responses:
            if r.question_id == question_id:
                return r
        return None


class IntentWizard:
    """
    The main wizard engine that guides artists through intent discovery.

    The wizard uses branching questions to progressively deepen understanding
    of the artist's emotional intent before any technical decisions are made.
    """

    def __init__(self):
        self.questions: Dict[str, Question] = {}
        self.start_question_id: Optional[str] = None
        self._build_question_tree()

    def _build_question_tree(self):
        """Build the default question tree."""

        # =====================================================================
        # SURFACE QUESTIONS - Initial Exploration
        # =====================================================================

        self._add_question(Question(
            id="start",
            text="What's the situation that made you need to write this song?",
            category=QuestionCategory.SURFACE,
            response_type=ResponseType.FREE_TEXT,
            help_text="Don't overthink it. Just describe what happened or what's on your mind.",
            example_answers=[
                "I just went through a breakup",
                "I'm feeling stuck in my career",
                "I witnessed something beautiful today",
                "I can't stop thinking about someone"
            ],
            maps_to="core_event",
            next_question="surface_who"
        ))
        self.start_question_id = "start"

        self._add_question(Question(
            id="surface_who",
            text="Is this about a specific person, yourself, or something more abstract?",
            category=QuestionCategory.SURFACE,
            response_type=ResponseType.SINGLE_CHOICE,
            choices=[
                Choice("specific_person", "A specific person", leads_to="person_relationship"),
                Choice("myself", "Myself / My own journey", leads_to="self_what"),
                Choice("abstract", "Something abstract (society, time, life)", leads_to="abstract_what"),
                Choice("unclear", "I'm not sure yet", leads_to="unclear_explore")
            ],
            maps_to="subject_focus"
        ))

        # Person branch
        self._add_question(Question(
            id="person_relationship",
            text="What's your relationship to this person?",
            category=QuestionCategory.SURFACE,
            response_type=ResponseType.SINGLE_CHOICE,
            choices=[
                Choice("romantic_current", "Current romantic partner"),
                Choice("romantic_ex", "Ex-partner / Lost love"),
                Choice("family", "Family member"),
                Choice("friend", "Friend"),
                Choice("stranger", "Stranger / Someone I barely know"),
                Choice("self_past", "A past version of myself")
            ],
            next_question="emotional_primary"
        ))

        # Self branch
        self._add_question(Question(
            id="self_what",
            text="What aspect of yourself are you exploring?",
            category=QuestionCategory.SURFACE,
            response_type=ResponseType.SINGLE_CHOICE,
            choices=[
                Choice("growth", "Personal growth / Change"),
                Choice("struggle", "Internal struggle / Conflict"),
                Choice("identity", "Identity / Who I am"),
                Choice("dreams", "Dreams / Aspirations"),
                Choice("regrets", "Regrets / Past mistakes"),
                Choice("celebration", "Celebration / Self-love")
            ],
            next_question="emotional_primary"
        ))

        # Abstract branch
        self._add_question(Question(
            id="abstract_what",
            text="What concept or theme are you drawn to?",
            category=QuestionCategory.SURFACE,
            response_type=ResponseType.SINGLE_CHOICE,
            choices=[
                Choice("time", "Time / Mortality"),
                Choice("society", "Society / The world"),
                Choice("nature", "Nature / The universe"),
                Choice("spirituality", "Spirituality / Faith"),
                Choice("freedom", "Freedom / Escape"),
                Choice("connection", "Human connection")
            ],
            next_question="emotional_primary"
        ))

        # Unclear branch - help them find it
        self._add_question(Question(
            id="unclear_explore",
            text="That's okay. Let's try this: If this song could change one thing about how you feel right now, what would it be?",
            category=QuestionCategory.SURFACE,
            response_type=ResponseType.FREE_TEXT,
            help_text="There's no wrong answer. Just say what comes to mind.",
            next_question="emotional_primary"
        ))

        # =====================================================================
        # EMOTIONAL QUESTIONS - Feeling Identification
        # =====================================================================

        self._add_question(Question(
            id="emotional_primary",
            text="What's the PRIMARY emotion you want listeners to feel?",
            category=QuestionCategory.EMOTIONAL,
            response_type=ResponseType.SINGLE_CHOICE,
            choices=[
                Choice("sadness", "Sadness / Melancholy", tags=["dark", "slow"]),
                Choice("anger", "Anger / Frustration", tags=["intense", "aggressive"]),
                Choice("joy", "Joy / Euphoria", tags=["bright", "energetic"]),
                Choice("longing", "Longing / Yearning", tags=["bittersweet", "slow"]),
                Choice("peace", "Peace / Calm", tags=["soft", "minimal"]),
                Choice("defiance", "Defiance / Rebellion", tags=["intense", "driving"]),
                Choice("confusion", "Confusion / Uncertainty", tags=["complex", "atmospheric"]),
                Choice("hope", "Hope / Anticipation", tags=["building", "bright"]),
                Choice("nostalgia", "Nostalgia / Memory", tags=["warm", "bittersweet"])
            ],
            maps_to="mood_primary",
            next_question="emotional_secondary"
        ))

        self._add_question(Question(
            id="emotional_secondary",
            text="Is there a SECONDARY emotion that conflicts with or complicates the first?",
            category=QuestionCategory.EMOTIONAL,
            response_type=ResponseType.SINGLE_CHOICE,
            choices=[
                Choice("none", "No, it's pure / uncomplicated"),
                Choice("anger_beneath_sadness", "Anger beneath the sadness"),
                Choice("sadness_beneath_anger", "Sadness beneath the anger"),
                Choice("hope_despite_pain", "Hope despite the pain"),
                Choice("fear_beneath_defiance", "Fear beneath the defiance"),
                Choice("guilt_with_joy", "Guilt mixed with joy"),
                Choice("relief_with_grief", "Relief mixed with grief"),
                Choice("love_with_resentment", "Love mixed with resentment")
            ],
            maps_to="mood_secondary_tension",
            next_question="emotional_tension"
        ))

        self._add_question(Question(
            id="emotional_tension",
            text="How much internal tension/conflict is in this song?",
            category=QuestionCategory.EMOTIONAL,
            response_type=ResponseType.SCALE,
            scale_min=1,
            scale_max=10,
            scale_labels={
                1: "Pure, uncomplicated emotion",
                5: "Some inner conflict",
                10: "Completely torn apart"
            },
            maps_to="mood_secondary_tension_scale",
            next_question="resistance_intro"
        ))

        # =====================================================================
        # RESISTANCE QUESTIONS - What's Hard to Say
        # =====================================================================

        self._add_question(Question(
            id="resistance_intro",
            text="Now let's go deeper. What's the thing you're AFRAID to say in this song?",
            category=QuestionCategory.RESISTANCE,
            response_type=ResponseType.FREE_TEXT,
            help_text="The part that makes you uncomfortable. The truth you've been dancing around.",
            example_answers=[
                "That I was partly to blame",
                "That I actually miss them",
                "That I don't know who I am anymore",
                "That I want something I shouldn't want"
            ],
            maps_to="core_resistance",
            next_question="resistance_why"
        ))

        self._add_question(Question(
            id="resistance_why",
            text="Why is it hard to say that?",
            category=QuestionCategory.RESISTANCE,
            response_type=ResponseType.SINGLE_CHOICE,
            choices=[
                Choice("vulnerability", "It makes me too vulnerable"),
                Choice("shame", "I'm ashamed of it"),
                Choice("hurt_others", "It might hurt someone"),
                Choice("admit_truth", "It means admitting something I don't want to"),
                Choice("permanence", "Saying it makes it real"),
                Choice("dont_know", "I honestly don't know")
            ],
            next_question="vulnerability_level"
        ))

        self._add_question(Question(
            id="vulnerability_level",
            text="How vulnerable are you willing to be in this song?",
            category=QuestionCategory.RESISTANCE,
            response_type=ResponseType.SINGLE_CHOICE,
            choices=[
                Choice("low", "Keep some distance - hint at it", leads_to="longing_what"),
                Choice("medium", "Open up, but maintain some armor", leads_to="longing_what"),
                Choice("high", "Completely raw and exposed", leads_to="longing_what")
            ],
            maps_to="vulnerability_scale"
        ))

        # =====================================================================
        # LONGING QUESTIONS - What You Want to Feel
        # =====================================================================

        self._add_question(Question(
            id="longing_what",
            text="What do you WISH you could feel instead of what you're feeling now?",
            category=QuestionCategory.LONGING,
            response_type=ResponseType.FREE_TEXT,
            help_text="Not what you think you should feel - what you actually long for.",
            example_answers=[
                "Peace",
                "To feel nothing at all",
                "To feel that intensity again",
                "To feel certain about something",
                "To feel free"
            ],
            maps_to="core_longing",
            next_question="longing_attainable"
        ))

        self._add_question(Question(
            id="longing_attainable",
            text="Does it feel like that's actually possible to achieve?",
            category=QuestionCategory.LONGING,
            response_type=ResponseType.SINGLE_CHOICE,
            choices=[
                Choice("yes", "Yes, I'm working toward it"),
                Choice("maybe", "Maybe, someday"),
                Choice("no", "No, it's lost forever"),
                Choice("unknown", "I don't know")
            ],
            next_question="stakes_what"
        ))

        # =====================================================================
        # STAKES QUESTIONS - What's at Risk
        # =====================================================================

        self._add_question(Question(
            id="stakes_what",
            text="What's at stake if you DON'T write this song?",
            category=QuestionCategory.STAKES,
            response_type=ResponseType.SINGLE_CHOICE,
            choices=[
                Choice("nothing", "Nothing really - it's just creative expression"),
                Choice("sanity", "My sanity - I need to get this out"),
                Choice("relationship", "A relationship - I need to say this"),
                Choice("identity", "My sense of self - I need to understand"),
                Choice("closure", "Closure - I need to process this"),
                Choice("legacy", "My legacy - this needs to exist")
            ],
            maps_to="core_stakes",
            next_question="stakes_audience"
        ))

        self._add_question(Question(
            id="stakes_audience",
            text="Who NEEDS to hear this song?",
            category=QuestionCategory.STAKES,
            response_type=ResponseType.SINGLE_CHOICE,
            choices=[
                Choice("me", "Just me - it's personal processing"),
                Choice("them", "Them - the person it's about"),
                Choice("people_like_me", "People going through the same thing"),
                Choice("everyone", "Everyone - it's a universal truth"),
                Choice("future_me", "Future me - to remember this moment")
            ],
            next_question="transformation_before"
        ))

        # =====================================================================
        # TRANSFORMATION QUESTIONS - Desired Change
        # =====================================================================

        self._add_question(Question(
            id="transformation_before",
            text="How do you feel RIGHT NOW, before writing this song?",
            category=QuestionCategory.TRANSFORMATION,
            response_type=ResponseType.FREE_TEXT,
            help_text="Don't filter. Just name the feeling state you're in.",
            next_question="transformation_after"
        ))

        self._add_question(Question(
            id="transformation_after",
            text="How do you want to feel AFTER writing/singing this song?",
            category=QuestionCategory.TRANSFORMATION,
            response_type=ResponseType.FREE_TEXT,
            maps_to="core_transformation",
            help_text="This is the emotional destination. Where are you trying to get to?",
            next_question="transformation_arc"
        ))

        self._add_question(Question(
            id="transformation_arc",
            text="What shape should the song's emotional journey take?",
            category=QuestionCategory.TRANSFORMATION,
            response_type=ResponseType.SINGLE_CHOICE,
            choices=[
                Choice("climb", "Climb to Climax - Building intensity to a peak"),
                Choice("reveal", "Slow Reveal - Gradually uncovering the truth"),
                Choice("repetitive", "Repetitive Despair - Stuck in a loop"),
                Choice("release", "Tension and Release - Build up, then let go"),
                Choice("descent", "Descent - Spiraling downward"),
                Choice("acceptance", "Journey to Acceptance - Fighting, then surrendering"),
                Choice("defiant", "Defiant Stand - Standing your ground throughout")
            ],
            maps_to="narrative_arc",
            next_question="technical_genre"
        ))

        # =====================================================================
        # TECHNICAL QUESTIONS - Genre/Style (Only After Emotional Clarity)
        # =====================================================================

        self._add_question(Question(
            id="technical_genre",
            text="Now that we understand the emotion - what genre feels right?",
            category=QuestionCategory.TECHNICAL,
            response_type=ResponseType.SINGLE_CHOICE,
            help_text="Based on everything you've said, what sonic world should this live in?",
            choices=[
                Choice("pop", "Pop - Accessible, hooky, universal"),
                Choice("rock", "Rock - Raw, powerful, guitar-driven"),
                Choice("hiphop", "Hip-Hop/R&B - Rhythmic, honest, groove-based"),
                Choice("electronic", "Electronic - Atmospheric, textured, modern"),
                Choice("folk", "Folk/Acoustic - Intimate, storytelling, stripped"),
                Choice("indie", "Indie - Alternative, artistic, unconventional"),
                Choice("soul", "Soul/Gospel - Emotional, vocal-forward, spiritual"),
                Choice("country", "Country - Narrative, heartfelt, traditional"),
                Choice("ambient", "Ambient - Spacious, meditative, textural")
            ],
            maps_to="technical_genre",
            next_question="technical_energy"
        ))

        self._add_question(Question(
            id="technical_energy",
            text="What energy level fits this emotion?",
            category=QuestionCategory.TECHNICAL,
            response_type=ResponseType.SCALE,
            scale_min=1,
            scale_max=10,
            scale_labels={
                1: "Whisper quiet, minimal",
                5: "Medium energy, steady",
                10: "Full intensity, explosive"
            },
            maps_to="technical_energy",
            next_question="technical_rule_break"
        ))

        self._add_question(Question(
            id="technical_rule_break",
            text="Is there a musical 'rule' that should be broken to serve this emotion?",
            category=QuestionCategory.TECHNICAL,
            response_type=ResponseType.SINGLE_CHOICE,
            choices=[
                Choice("none", "No - keep it conventional"),
                Choice("harmony", "Harmony - Avoid resolution, use dissonance"),
                Choice("rhythm", "Rhythm - Play off the grid, asymmetric"),
                Choice("arrangement", "Arrangement - Bury vocals, extreme dynamics"),
                Choice("production", "Production - Lo-fi, imperfect, raw"),
                Choice("structure", "Structure - No chorus, unconventional form"),
                Choice("not_sure", "Not sure - suggest something")
            ],
            maps_to="technical_rule_to_break",
            next_question="final_summary"
        ))

        self._add_question(Question(
            id="final_summary",
            text="One last thing: In one sentence, what is this song really about?",
            category=QuestionCategory.SURFACE,
            response_type=ResponseType.FREE_TEXT,
            help_text="Not the story - the truth underneath the story.",
            example_answers=[
                "It's about admitting I was wrong",
                "It's about letting go of who I thought I'd be",
                "It's about choosing myself for the first time",
                "It's about grief disguised as anger"
            ],
            maps_to="core_truth",
            next_question=None  # End of wizard
        ))

    def _add_question(self, question: Question):
        """Add a question to the wizard."""
        self.questions[question.id] = question

    def start_session(self, session_id: str) -> WizardSession:
        """Start a new wizard session."""
        from datetime import datetime
        session = WizardSession(
            session_id=session_id,
            current_question_id=self.start_question_id,
            started_at=datetime.now().isoformat()
        )
        return session

    def get_current_question(self, session: WizardSession) -> Optional[Question]:
        """Get the current question for a session."""
        if session.current_question_id:
            return self.questions.get(session.current_question_id)
        return None

    def answer_question(self, session: WizardSession, response: Any) -> Optional[Question]:
        """
        Record an answer and advance to the next question.
        Returns the next question, or None if wizard is complete.
        """
        from datetime import datetime

        current = self.get_current_question(session)
        if not current:
            return None

        # Record the response
        session.responses.append(WizardResponse(
            question_id=current.id,
            response=response,
            timestamp=datetime.now().isoformat()
        ))

        # Determine next question
        next_id = current.next_question

        # Check for choice-based branching
        if current.response_type == ResponseType.SINGLE_CHOICE:
            for choice in current.choices:
                if choice.id == response and choice.leads_to:
                    next_id = choice.leads_to
                    break

        # Check conditional next
        if str(response) in current.conditional_next:
            next_id = current.conditional_next[str(response)]

        # Update session
        session.current_question_id = next_id

        if next_id is None:
            # Wizard complete
            session.completed_at = datetime.now().isoformat()
            session.completeness_score = self._calculate_completeness(session)

        return self.questions.get(next_id) if next_id else None

    def _calculate_completeness(self, session: WizardSession) -> float:
        """Calculate how complete the intent discovery is."""
        # Check coverage of each category
        category_coverage = {cat: 0 for cat in QuestionCategory}
        category_required = {cat: 0 for cat in QuestionCategory}

        for response in session.responses:
            question = self.questions.get(response.question_id)
            if question:
                category_coverage[question.category] += 1

        for question in self.questions.values():
            if question.required:
                category_required[question.category] += 1

        # Core categories that must be covered
        core_categories = [
            QuestionCategory.EMOTIONAL,
            QuestionCategory.RESISTANCE,
            QuestionCategory.LONGING,
            QuestionCategory.TRANSFORMATION
        ]

        score = 0.0
        for cat in core_categories:
            if category_coverage[cat] > 0:
                score += 0.25

        return min(1.0, score)

    def export_to_intent(self, session: WizardSession) -> Dict[str, Any]:
        """Export wizard responses to a CompleteSongIntent-compatible dict."""
        intent = {
            "phase0_root": {},
            "phase1_intent": {},
            "phase2_technical": {},
            "metadata": {
                "wizard_session_id": session.session_id,
                "completeness_score": session.completeness_score,
                "started_at": session.started_at,
                "completed_at": session.completed_at
            }
        }

        # Map responses to intent fields
        for response in session.responses:
            question = self.questions.get(response.question_id)
            if question and question.maps_to:
                field = question.maps_to
                value = response.response

                # Categorize the field
                if field.startswith("core_"):
                    intent["phase0_root"][field] = value
                elif field.startswith("mood_") or field.startswith("vulnerability") or field.startswith("narrative"):
                    intent["phase1_intent"][field] = value
                elif field.startswith("technical_"):
                    intent["phase2_technical"][field] = value

        return intent

    def get_progress(self, session: WizardSession) -> Dict[str, Any]:
        """Get progress information for the session."""
        answered_categories = set()
        for response in session.responses:
            question = self.questions.get(response.question_id)
            if question:
                answered_categories.add(question.category)

        return {
            "questions_answered": len(session.responses),
            "categories_covered": [c.value for c in answered_categories],
            "completeness_score": self._calculate_completeness(session),
            "is_complete": session.current_question_id is None
        }


# =============================================================================
# CLI Interface
# =============================================================================

def run_wizard_cli():
    """Run the wizard in CLI mode."""
    import uuid

    wizard = IntentWizard()
    session = wizard.start_session(str(uuid.uuid4())[:8])

    print("\n" + "=" * 60)
    print("  SONG INTENT WIZARD")
    print("  Discover what you really need to say")
    print("=" * 60 + "\n")

    while True:
        question = wizard.get_current_question(session)
        if not question:
            break

        print(f"\n[{question.category.value.upper()}]")
        print(f"\n{question.text}\n")

        if question.help_text:
            print(f"  💡 {question.help_text}\n")

        if question.example_answers:
            print("  Examples:")
            for ex in question.example_answers[:3]:
                print(f"    - {ex}")
            print()

        # Get response based on type
        if question.response_type == ResponseType.FREE_TEXT:
            response = input("Your answer: ").strip()

        elif question.response_type == ResponseType.SINGLE_CHOICE:
            for i, choice in enumerate(question.choices, 1):
                print(f"  {i}. {choice.text}")
            while True:
                try:
                    choice_num = int(input("\nEnter number: "))
                    if 1 <= choice_num <= len(question.choices):
                        response = question.choices[choice_num - 1].id
                        break
                    print("Invalid choice, try again.")
                except ValueError:
                    print("Please enter a number.")

        elif question.response_type == ResponseType.SCALE:
            labels = question.scale_labels
            if labels:
                for val, label in sorted(labels.items()):
                    print(f"  {val}: {label}")
            while True:
                try:
                    response = int(input(f"\nEnter {question.scale_min}-{question.scale_max}: "))
                    if question.scale_min <= response <= question.scale_max:
                        break
                    print(f"Please enter a number between {question.scale_min} and {question.scale_max}.")
                except ValueError:
                    print("Please enter a number.")

        elif question.response_type == ResponseType.BOOLEAN:
            response = input("(y/n): ").strip().lower() == 'y'

        else:
            response = input("Your answer: ").strip()

        wizard.answer_question(session, response)

    # Show results
    print("\n" + "=" * 60)
    print("  WIZARD COMPLETE")
    print("=" * 60)

    intent = wizard.export_to_intent(session)
    progress = wizard.get_progress(session)

    print(f"\nCompleteness: {progress['completeness_score'] * 100:.0f}%")
    print(f"Questions answered: {progress['questions_answered']}")
    print(f"\nCategories covered: {', '.join(progress['categories_covered'])}")

    print("\n--- EXPORTED INTENT ---\n")
    print(json.dumps(intent, indent=2))

    return intent


# Export public API
__all__ = [
    'QuestionCategory',
    'ResponseType',
    'Choice',
    'Question',
    'WizardResponse',
    'WizardSession',
    'IntentWizard',
    'run_wizard_cli'
]


if __name__ == "__main__":
    run_wizard_cli()
