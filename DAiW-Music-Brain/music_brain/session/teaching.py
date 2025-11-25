"""
Rule-Breaking Teaching Module - Interactive lessons on creative music theory.

Teaches:
- Borrowed chords and modal mixture
- Emotional chord substitutions  
- Rhythmic misdirection
- Production philosophy
- When and why to break rules

Philosophy: "The wrong note played with conviction is the right note."
"""

import random
from typing import List, Dict, Optional
from dataclasses import dataclass


# Teaching content database
LESSONS = {
    "borrowed_chords": {
        "title": "Borrowed Chords & Modal Mixture",
        "intro": """
Borrowed chords come from the parallel mode of your key.
In F major, you can "borrow" chords from F minor to add color.

The most common borrowed chords:
- iv (Bbm in F) - The "sad IV", darker than major IV
- bVI (Db in F) - Epic, cinematic, "here comes the emotional part"
- bVII (Eb in F) - Rock's favorite chord, mixolydian feel
- bIII (Ab in F) - Unexpected brightness from minor
""",
        "examples": [
            {
                "name": "iv for IV (Sad IV)",
                "original": "F - C - Bb - F",
                "borrowed": "F - C - Bbm - F",
                "effect": "Adds melancholy without leaving the key",
                "famous_use": "Radiohead 'Creep' - the Cm chord",
            },
            {
                "name": "bVI (The Epic Chord)",
                "original": "F - C - Am - Dm",
                "borrowed": "F - C - Db - F",
                "effect": "Cinematic lift, unexpected resolution",
                "famous_use": "Every 80s power ballad ever",
            },
            {
                "name": "bVII (Rock's Favorite)",
                "original": "F - C - G - F",
                "borrowed": "F - C - Eb - F",
                "effect": "Mixolydian swagger, avoids cliché V chord",
                "famous_use": "Beatles 'Norwegian Wood'",
            },
        ],
        "exercise": "Take your progression and replace ONE major chord with its minor borrowed equivalent. Listen to how the mood shifts.",
    },
    
    "modal_mixture": {
        "title": "Modal Mixture Deep Dive",
        "intro": """
Modal mixture is borrowing chords from ANY mode, not just parallel minor.

In F major, you can borrow from:
- F Dorian (jazzier minors)
- F Lydian (raised 4th = dreamier)
- F Mixolydian (flat 7 = rock feel)
- F Phrygian (flat 2 = tension, Spanish flavor)

The key: Use borrowed chords at moments of emotional shift.
""",
        "examples": [
            {
                "name": "Lydian Lift",
                "original": "F - Bb - C - F",
                "mixed": "F - B - C - F",
                "effect": "The B natural creates floating, dreamy quality",
                "when_to_use": "Moments of hope, transcendence, 'rising above'",
            },
            {
                "name": "Dorian Color",
                "original": "Dm - G - C - F",
                "mixed": "Dm - G7 - C - F",
                "effect": "The natural 6 in Dorian adds sophistication",
                "when_to_use": "When you want sad but not tragic",
            },
        ],
        "exercise": "Write a 4-chord progression. Insert a chord from a different mode at the emotional peak.",
    },
    
    "emotional_substitutions": {
        "title": "Emotional Chord Substitutions",
        "intro": """
Every chord has an emotional signature. Substitutions change the feeling
while maintaining harmonic function.

Key insight: The "function" of a chord (tonic, subdominant, dominant)
matters more than its exact identity.

Substitute based on emotion, not just theory.
""",
        "examples": [
            {
                "emotion": "grief",
                "original": "I - IV - V - I",
                "substitution": "I - iv - bVI - I",
                "explanation": "Minor iv adds weight, bVI delays resolution",
            },
            {
                "emotion": "nostalgia",
                "original": "I - vi - IV - V",
                "substitution": "Imaj7 - vi7 - IVmaj7 - V7sus4",
                "explanation": "7ths add memory-like haziness, sus4 refuses clean resolution",
            },
            {
                "emotion": "anger",
                "original": "i - iv - V - i",
                "substitution": "i - iv - bVII - i",
                "explanation": "bVII is defiant, refuses traditional resolution",
            },
            {
                "emotion": "acceptance",
                "original": "I - V - vi - IV",
                "substitution": "I - V - vi - IVadd9",
                "explanation": "Add9 on IV creates open, resolved feeling",
            },
            {
                "emotion": "dissociation",
                "original": "I - IV - V - I",
                "substitution": "Imaj7 - bVII - IV - I",
                "explanation": "bVII creates floating, disconnected sensation",
            },
        ],
        "exercise": "Pick an emotion. Find a stock progression. Substitute one chord to make it actually feel that way.",
    },
    
    "rhythmic_misdirection": {
        "title": "Rhythmic Misdirection",
        "intro": """
Rhythm is where amateur and professional productions diverge most.

Key concepts:
- Anticipation: Playing BEFORE the beat
- Delay: Playing AFTER the beat (laid back)
- Syncopation: Accenting the 'wrong' beats
- Polyrhythm: Multiple rhythmic feels simultaneously

The goal: Make listeners FEEL something in their body, not just their ears.
""",
        "examples": [
            {
                "technique": "Ghost Notes",
                "description": "Very quiet notes between main beats",
                "effect": "Creates 'breathing' feel, humanizes groove",
                "genre": "Funk, R&B, Hip-hop",
            },
            {
                "technique": "Push the 1",
                "description": "Start phrase slightly before downbeat",
                "effect": "Creates urgency, forward momentum",
                "genre": "Rock, Punk, some Pop",
            },
            {
                "technique": "Laid Back Snare",
                "description": "Snare hits slightly behind the beat",
                "effect": "Creates 'swagger', deep pocket feel",
                "genre": "Hip-hop, Neo-soul, Blues",
            },
            {
                "technique": "Metric Modulation",
                "description": "Change the perceived tempo without changing BPM",
                "effect": "Disorientation, then resolution",
                "genre": "Progressive, Jazz, Art rock",
            },
        ],
        "exercise": "Take a quantized MIDI drum pattern. Move the snare 10-20ms late. Move hi-hats slightly early. Notice how the feel changes completely.",
    },
    
    "production_philosophy": {
        "title": "Production Rule-Breaking Philosophy",
        "intro": """
The 'rules' of production are generalizations that work MOST of the time.
Breaking them intentionally creates signature sounds.

Core principle: If it sounds good, it IS good.
But 'good' means 'serves the song', not 'technically correct'.

Imperfection is a feature, not a bug.
""",
        "examples": [
            {
                "rule": "Cut mud around 200-400Hz",
                "break_it": "Leave the mud if the song is about feeling trapped",
                "famous_example": "Billie Eilish - breathy, bass-heavy mixes",
            },
            {
                "rule": "Vocals should be clear and upfront",
                "break_it": "Bury vocals for intimacy or dissociation",
                "famous_example": "My Bloody Valentine - vocals as texture",
            },
            {
                "rule": "Remove room noise",
                "break_it": "Keep room sound for authenticity",
                "famous_example": "Bon Iver 'For Emma' - cabin recordings",
            },
            {
                "rule": "Fix pitch problems",
                "break_it": "Leave pitch drift for emotional honesty",
                "famous_example": "Elliott Smith - intentionally imperfect delivery",
            },
            {
                "rule": "Mix for clarity",
                "break_it": "Mix for FEELING - sometimes blur is the point",
                "famous_example": "Shoegaze genre - deliberately obscured",
            },
        ],
        "exercise": "Pick one 'rule' you always follow. Break it intentionally in your next mix. Document what emotion it creates.",
    },
}

# Wisdom quotes for random inspiration
WISDOM = [
    "The wrong note played with conviction is the right note.",
    "Rules exist so you know what you're breaking.",
    "If everyone can hear that it's 'wrong', it's amateur. If they feel something, it's art.",
    "The best chord is the one that makes the lyric hit harder.",
    "Perfection is the enemy of soul.",
    "Your limitations are your signature.",
    "The crack in the voice IS the emotion.",
    "Theory explains what works. It doesn't create what works.",
    "Every genre was invented by someone who didn't know the rules.",
    "The audience doesn't hear 'borrowed from Dorian'. They hear 'that part made me cry'.",
    "Quantize the drums and you've killed the drummer.",
    "The greatest producers know all the rules and choose which ones to ignore.",
    "Your 'mistakes' are what make you sound like you.",
    "A song isn't finished. It escapes.",
    "The silence between notes is as important as the notes themselves.",
]


class RuleBreakingTeacher:
    """
    Interactive teaching module for creative music theory and rule-breaking.
    
    Usage:
        teacher = RuleBreakingTeacher()
        teacher.interactive_session("borrowed_chords")
        
        # Or quick lesson
        teacher.quick_lesson("modal_mixture")
        
        # Random wisdom
        print(teacher.get_wisdom())
    """
    
    def __init__(self):
        self.lessons = LESSONS
        self.wisdom = WISDOM
        self.history = []
    
    def list_topics(self) -> List[str]:
        """Get list of available topics."""
        return list(self.lessons.keys())
    
    def get_wisdom(self) -> str:
        """Get a random piece of wisdom."""
        return random.choice(self.wisdom)
    
    def quick_lesson(self, topic: str):
        """
        Print a quick lesson on a topic.
        
        Args:
            topic: Topic key (borrowed_chords, modal_mixture, etc.)
        """
        topic = topic.lower().replace("-", "_").replace(" ", "_")
        
        if topic not in self.lessons:
            print(f"Unknown topic: {topic}")
            print(f"Available topics: {', '.join(self.list_topics())}")
            return
        
        lesson = self.lessons[topic]
        
        print("\n" + "=" * 60)
        print(f"📚 {lesson['title']}")
        print("=" * 60)
        print(lesson['intro'])
        
        print("\n" + "-" * 40)
        print("EXAMPLES:")
        print("-" * 40)
        
        for i, example in enumerate(lesson['examples'][:3], 1):
            name_key = next((k for k in ['name', 'technique', 'emotion', 'rule'] if k in example), 'Example')
            print(f"\n{i}. {example.get(name_key, 'Example')}")
            for key, value in example.items():
                if key != name_key:
                    print(f"   {key.replace('_', ' ').title()}: {value}")
        
        print("\n" + "-" * 40)
        print("💡 EXERCISE:")
        print("-" * 40)
        print(lesson['exercise'])
        
        print("\n" + "=" * 60)
        print(f"🎵 Wisdom: \"{self.get_wisdom()}\"")
        print("=" * 60 + "\n")
        
        self.history.append(topic)
    
    def interactive_session(self, topic: Optional[str] = None):
        """
        Run an interactive teaching session.
        
        Args:
            topic: Starting topic (optional, shows menu if not provided)
        """
        print("\n" + "=" * 60)
        print("🎸 DAiW RULE-BREAKING TEACHING MODULE")
        print("=" * 60)
        print("\nLearn when and why to break the rules.\n")
        
        if topic is None:
            print("Available topics:")
            for i, (key, lesson) in enumerate(self.lessons.items(), 1):
                print(f"  {i}. {lesson['title']}")
            print(f"  {len(self.lessons) + 1}. Random wisdom")
            print(f"  {len(self.lessons) + 2}. Exit")
            
            try:
                choice = input("\nSelect topic (number): ").strip()
                if not choice.isdigit():
                    print("Please enter a number.")
                    return
                
                choice = int(choice)
                if choice == len(self.lessons) + 1:
                    print(f"\n🎵 \"{self.get_wisdom()}\"\n")
                    return
                elif choice == len(self.lessons) + 2:
                    print("\nKeep breaking rules! 🎸\n")
                    return
                elif 1 <= choice <= len(self.lessons):
                    topic = list(self.lessons.keys())[choice - 1]
                else:
                    print("Invalid choice.")
                    return
            except (ValueError, EOFError):
                return
        
        self.quick_lesson(topic)
        
        try:
            another = input("Learn another topic? (y/n): ").strip().lower()
            if another == 'y':
                self.interactive_session()
        except EOFError:
            pass
    
    def get_lesson_content(self, topic: str) -> Optional[Dict]:
        """Get raw lesson content for programmatic use."""
        return self.lessons.get(topic)
    
    def suggest_for_emotion(self, emotion: str) -> Dict:
        """
        Suggest rule-breaking techniques for a target emotion.
        
        Args:
            emotion: Target emotion (grief, nostalgia, anger, etc.)
        
        Returns:
            Dict with suggested techniques
        """
        emotion = emotion.lower()
        
        suggestions = {
            "emotion": emotion,
            "chord_substitutions": [],
            "production_tips": [],
            "rhythmic_ideas": [],
        }
        
        # Find matching substitutions
        sub_lesson = self.lessons.get("emotional_substitutions", {})
        for example in sub_lesson.get("examples", []):
            if example.get("emotion", "").lower() == emotion:
                suggestions["chord_substitutions"].append(example)
        
        # Add general tips based on emotion
        if emotion in ["grief", "sadness", "melancholy"]:
            suggestions["production_tips"] = [
                "Consider leaving pitch imperfections for emotional honesty",
                "Let the room breathe - don't over-compress",
                "Slower attack times create 'weight'",
            ]
            suggestions["rhythmic_ideas"] = [
                "Lay back the tempo slightly (rubato)",
                "Ghost notes add vulnerability",
                "Let silence do work - don't fill every space",
            ]
        
        elif emotion in ["anger", "frustration", "intensity"]:
            suggestions["production_tips"] = [
                "Don't be afraid of distortion and saturation",
                "Hard compression creates aggression",
                "Let frequencies clash intentionally",
            ]
            suggestions["rhythmic_ideas"] = [
                "Push the beat forward",
                "Hard, quantized drums for mechanical anger",
                "Sudden dynamic shifts create tension",
            ]
        
        elif emotion in ["nostalgia", "memory", "bittersweet"]:
            suggestions["production_tips"] = [
                "Lo-fi textures evoke memory",
                "Reverb = distance = the past",
                "Tape warble and vinyl crackle add time-distance",
            ]
            suggestions["rhythmic_ideas"] = [
                "Slight swing creates warmth",
                "Imprecise timing feels more 'remembered'",
                "Rubato on melodic instruments",
            ]
        
        elif emotion in ["hope", "transcendence", "uplift"]:
            suggestions["production_tips"] = [
                "Open up the high end",
                "Lydian mode chord borrowing",
                "Wide stereo field = expansiveness",
            ]
            suggestions["rhythmic_ideas"] = [
                "Driving, forward momentum",
                "Build energy through density",
                "Release tension at key moments",
            ]
        
        return suggestions


def main():
    """Run the teaching module from command line."""
    import sys
    
    teacher = RuleBreakingTeacher()
    
    if len(sys.argv) > 1:
        topic = sys.argv[1]
        teacher.quick_lesson(topic)
    else:
        teacher.interactive_session()


if __name__ == "__main__":
    main()
