"""
Song Interrogator - Interrogate Before Generate

The philosophy: Don't just generate music. Ask questions first.
Understand the emotional intent, the vulnerability, the story.

This module implements the "Creative Companion, Not a Factory" approach:
- Ask about mood, intent, imagery, vulnerability
- Challenge assumptions
- Teach theory in context
- Adapt to emotional intent and genre expectations
- Help translate the sound in someone's head

The tool shouldn't finish art for people - it should make them braver.
"""

from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import random


class SongPhase(Enum):
    """Phases of songwriting interrogation."""
    INTENT = "intent"
    EMOTION = "emotion"
    STORY = "story"
    SOUND = "sound"
    STRUCTURE = "structure"
    LYRICS = "lyrics"
    PRODUCTION = "production"


@dataclass
class SongContext:
    """
    Accumulated context about a song being developed.
    
    Built up through interrogation, used to guide generation.
    """
    # Core intent
    title: str = ""
    core_emotion: str = ""
    emotional_arc: List[str] = field(default_factory=list)  # How emotion changes
    
    # Story/content
    subject: str = ""  # What is this song about?
    perspective: str = ""  # Who is singing? To whom?
    vulnerability_level: int = 5  # 1-10
    
    # Sonic vision
    tempo_feel: str = ""  # "slow and heavy", "driving", etc.
    tempo_bpm: Optional[int] = None
    key: str = ""
    mode: str = ""  # major, minor, etc.
    
    # Genre/references
    genre: str = ""
    reference_artists: List[str] = field(default_factory=list)
    reference_songs: List[str] = field(default_factory=list)
    
    # Structure
    structure: List[str] = field(default_factory=list)  # ["verse", "chorus", etc.]
    section_emotions: Dict[str, str] = field(default_factory=dict)
    
    # Production vision
    production_style: str = ""  # "lo-fi bedroom", "polished", etc.
    key_instruments: List[str] = field(default_factory=list)
    production_rules_to_break: List[str] = field(default_factory=list)
    
    # Lyric fragments
    lyric_themes: List[str] = field(default_factory=list)
    key_phrases: List[str] = field(default_factory=list)
    
    # Meta
    confidence_level: int = 5  # How sure are they about this song?
    what_makes_this_different: str = ""


# Question banks for each phase
INTERROGATION_QUESTIONS = {
    SongPhase.INTENT: [
        "What do you NEED to say with this song? Not want - need.",
        "If someone heard this song, what should they FEEL?",
        "Is this song for you, or for someone else to hear?",
        "What's the one thing this song absolutely must accomplish?",
        "If this song was a message in a bottle, what would it say?",
    ],
    
    SongPhase.EMOTION: [
        "What's the dominant emotion? (Be specific - not just 'sad', but 'grief mixed with relief')",
        "Does the emotion change through the song? How?",
        "Where's the most vulnerable moment?",
        "What emotion do you want to END on?",
        "Is there anger hiding under the sadness, or sadness under the anger?",
    ],
    
    SongPhase.STORY: [
        "Who is the 'I' in this song? You? A character?",
        "Is this addressed to someone specific? Who?",
        "What happened right before this song starts?",
        "What's the specific moment or image at the core?",
        "What's the thing you're afraid to actually say?",
    ],
    
    SongPhase.SOUND: [
        "Close your eyes. What does this song SOUND like? Describe the texture.",
        "Is it dense or sparse? Why?",
        "What's the tempo feel? Not BPM - how does time move?",
        "What instrument or sound defines this song?",
        "Reference track: What song captures the FEEL you want?",
    ],
    
    SongPhase.STRUCTURE: [
        "Does this song build to something, or cycle?",
        "Where's the peak? Beginning, middle, or end?",
        "Does it need a chorus, or is this more of a narrative?",
        "What section carries the most weight?",
        "How does it end? Resolved or hanging?",
    ],
    
    SongPhase.LYRICS: [
        "What's the one line you already know belongs in this song?",
        "What's the metaphor or image that keeps coming back?",
        "Are you writing to be understood, or to process?",
        "What word are you avoiding? Maybe that's the title.",
        "If you had to write the whole song in one sentence, what is it?",
    ],
    
    SongPhase.PRODUCTION: [
        "Should this sound polished or raw? Why?",
        "What production rule do you want to break?",
        "Is the imperfection part of the message?",
        "How present should the voice be? Upfront or buried?",
        "What should the listener feel in their body when they hear this?",
    ],
}

# Follow-up prompts to go deeper
FOLLOW_UPS = [
    "Tell me more about that.",
    "What does that really mean to you?",
    "And beneath that?",
    "What are you not saying?",
    "Why does that matter?",
    "What would make that hit harder?",
    "Is that the truth, or what you want to be true?",
]

# Challenges to assumptions
CHALLENGES = [
    "Are you sure that's what this song is about?",
    "What if you're wrong about the tempo?",
    "What if the chorus isn't the point?",
    "What if you let it be uglier?",
    "What if you're holding back?",
    "What if the 'mistake' is the best part?",
    "What if you're overcomplicating it?",
]


class SongInterrogator:
    """
    Interactive song development through questioning.
    
    Implements the "Interrogate Before Generate" philosophy.
    Asks the hard questions before making suggestions.
    
    Usage:
        interrogator = SongInterrogator()
        context = interrogator.start_session()
        
        # After interrogation, context contains everything needed
        # to make meaningful creative suggestions
    """
    
    def __init__(self):
        self.context = SongContext()
        self.current_phase = SongPhase.INTENT
        self.questions_asked = []
        self.answers = []
    
    def start_session(self, title: Optional[str] = None) -> SongContext:
        """
        Start an interactive interrogation session.
        
        Args:
            title: Optional starting title
        
        Returns:
            SongContext built from responses
        """
        print("\n" + "=" * 60)
        print("🎵 SONG INTERROGATOR")
        print("=" * 60)
        print("\nLet's dig into what this song really needs to be.")
        print("Answer honestly. The song will thank you.\n")
        
        if title:
            self.context.title = title
            print(f"Working on: '{title}'\n")
        
        # Run through phases
        for phase in SongPhase:
            self._run_phase(phase)
            
            # Check if they want to continue
            try:
                cont = input("\nContinue to next phase? (y/n/skip): ").strip().lower()
                if cont == 'n':
                    break
                elif cont == 'skip':
                    continue
            except EOFError:
                break
        
        # Summarize
        self._summarize()
        
        return self.context
    
    def _run_phase(self, phase: SongPhase):
        """Run interrogation for a single phase."""
        print("\n" + "-" * 40)
        print(f"📋 {phase.value.upper()}")
        print("-" * 40 + "\n")
        
        questions = INTERROGATION_QUESTIONS[phase]
        
        for i, question in enumerate(questions[:3]):  # Ask 3 questions per phase
            print(f"Q: {question}")
            
            try:
                answer = input("A: ").strip()
            except EOFError:
                return
            
            if not answer:
                continue
            
            self.questions_asked.append(question)
            self.answers.append(answer)
            
            # Store in context based on phase
            self._store_answer(phase, question, answer)
            
            # Occasionally challenge or follow up
            if random.random() < 0.3 and i < len(questions) - 1:
                if random.random() < 0.5:
                    print(f"\n💭 {random.choice(FOLLOW_UPS)}")
                else:
                    print(f"\n⚡ {random.choice(CHALLENGES)}")
                
                try:
                    followup = input("A: ").strip()
                    if followup:
                        self.answers.append(followup)
                except EOFError:
                    pass
            
            print()
    
    def _store_answer(self, phase: SongPhase, question: str, answer: str):
        """Store answer in appropriate context field."""
        # Simple keyword matching to route answers
        answer_lower = answer.lower()
        
        if phase == SongPhase.INTENT:
            if not self.context.core_emotion:
                self.context.core_emotion = answer
        
        elif phase == SongPhase.EMOTION:
            if "emotion" in question.lower() and "dominant" in question.lower():
                self.context.core_emotion = answer
            elif "change" in question.lower():
                self.context.emotional_arc = [s.strip() for s in answer.split(",")]
            elif "vulnerable" in question.lower():
                # Try to extract vulnerability level
                try:
                    for word in answer.split():
                        if word.isdigit():
                            self.context.vulnerability_level = int(word)
                            break
                except:
                    pass
        
        elif phase == SongPhase.STORY:
            if "about" in question.lower():
                self.context.subject = answer
            elif "addressed" in question.lower() or "who" in question.lower():
                self.context.perspective = answer
        
        elif phase == SongPhase.SOUND:
            if "tempo" in question.lower():
                self.context.tempo_feel = answer
                # Try to extract BPM if mentioned
                for word in answer.split():
                    if word.isdigit():
                        bpm = int(word)
                        if 40 <= bpm <= 240:
                            self.context.tempo_bpm = bpm
            elif "reference" in question.lower():
                self.context.reference_songs.append(answer)
            elif "instrument" in question.lower():
                self.context.key_instruments = [s.strip() for s in answer.split(",")]
        
        elif phase == SongPhase.STRUCTURE:
            if "build" in question.lower() or "cycle" in question.lower():
                if "build" in answer_lower:
                    self.context.structure = ["intro", "verse", "chorus", "verse", "chorus", "bridge", "chorus", "outro"]
                else:
                    self.context.structure = ["verse", "verse", "verse", "verse"]
            elif "peak" in question.lower():
                self.context.section_emotions["peak"] = answer
        
        elif phase == SongPhase.LYRICS:
            if "line" in question.lower():
                self.context.key_phrases.append(answer)
            elif "metaphor" in question.lower() or "image" in question.lower():
                self.context.lyric_themes.append(answer)
        
        elif phase == SongPhase.PRODUCTION:
            if "polished" in question.lower() or "raw" in question.lower():
                self.context.production_style = answer
            elif "break" in question.lower():
                self.context.production_rules_to_break.append(answer)
    
    def _summarize(self):
        """Print summary of gathered context."""
        print("\n" + "=" * 60)
        print("📝 SONG BRIEF")
        print("=" * 60)
        
        if self.context.title:
            print(f"\nTitle: {self.context.title}")
        
        if self.context.core_emotion:
            print(f"Core emotion: {self.context.core_emotion}")
        
        if self.context.emotional_arc:
            print(f"Emotional arc: {' → '.join(self.context.emotional_arc)}")
        
        if self.context.subject:
            print(f"About: {self.context.subject}")
        
        if self.context.tempo_feel:
            print(f"Tempo feel: {self.context.tempo_feel}")
        
        if self.context.key_instruments:
            print(f"Key instruments: {', '.join(self.context.key_instruments)}")
        
        if self.context.production_style:
            print(f"Production: {self.context.production_style}")
        
        if self.context.key_phrases:
            print(f"Key phrases: {'; '.join(self.context.key_phrases)}")
        
        if self.context.production_rules_to_break:
            print(f"Rules to break: {', '.join(self.context.production_rules_to_break)}")
        
        print("\n" + "=" * 60)
        print("\nNow you know what you're making. Go make it brave.")
        print("=" * 60 + "\n")
    
    def quick_questions(self, phase: SongPhase, count: int = 3) -> List[str]:
        """Get questions for a specific phase without interactive session."""
        questions = INTERROGATION_QUESTIONS.get(phase, [])
        return random.sample(questions, min(count, len(questions)))
    
    def get_challenge(self) -> str:
        """Get a random challenge to assumptions."""
        return random.choice(CHALLENGES)
    
    def get_followup(self) -> str:
        """Get a random follow-up prompt."""
        return random.choice(FOLLOW_UPS)


def quick_interrogate(topic: str) -> List[str]:
    """
    Get relevant questions for a specific songwriting topic.
    
    Args:
        topic: Topic like "lyrics", "structure", "production"
    
    Returns:
        List of questions
    """
    topic_lower = topic.lower()
    
    for phase in SongPhase:
        if topic_lower in phase.value:
            return INTERROGATION_QUESTIONS[phase]
    
    # Return mix if no exact match
    all_questions = []
    for questions in INTERROGATION_QUESTIONS.values():
        all_questions.extend(questions)
    
    return random.sample(all_questions, 5)


def main():
    """Run interrogator from command line."""
    interrogator = SongInterrogator()
    interrogator.start_session()


if __name__ == "__main__":
    main()
