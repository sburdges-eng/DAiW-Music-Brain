"""
Instrument Definitions - Comprehensive instrument metadata for teaching.

Provides:
- InstrumentFamily enum for categorization
- Instrument dataclass with teaching-relevant metadata
- Pre-defined instruments with learning characteristics
- Beginner-friendly instrument recommendations

Philosophy: "Every instrument has its voice. Help the student find the one that speaks to them."
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


class InstrumentFamily(Enum):
    """Families of musical instruments."""
    # Standard orchestral families
    STRINGS = auto()           # Violin, viola, cello, bass, guitar
    WOODWINDS = auto()         # Flute, clarinet, oboe, saxophone
    BRASS = auto()             # Trumpet, trombone, horn, tuba
    PERCUSSION = auto()        # Drums, timpani, mallets, auxiliary
    KEYBOARD = auto()          # Piano, organ, synthesizer

    # Modern categories
    ELECTRONIC = auto()        # Synthesizers, drum machines, DAWs
    VOICE = auto()             # Singing, vocal techniques
    FRETTED = auto()           # Guitar, bass, ukulele, banjo

    # World instruments
    WORLD_STRINGS = auto()     # Sitar, koto, oud, erhu
    WORLD_WINDS = auto()       # Shakuhachi, bansuri, didgeridoo
    WORLD_PERCUSSION = auto()  # Tabla, djembe, cajon


@dataclass
class Instrument:
    """Comprehensive instrument definition for teaching."""
    id: str
    name: str
    family: InstrumentFamily
    aliases: List[str] = field(default_factory=list)

    # Learning characteristics
    beginner_friendly: bool = True
    solo_instrument: bool = True
    ensemble_instrument: bool = True
    requires_accompaniment: bool = False

    # Physical requirements
    minimum_age: int = 5
    physical_demands: str = "low"  # low, medium, high
    requires_both_hands: bool = True
    requires_breath: bool = False

    # Learning curve
    days_to_first_song: int = 7      # Approximate with practice
    months_to_intermediate: int = 12
    skill_ceiling: str = "high"      # low, medium, high, very_high

    # Equipment
    starter_cost_usd: tuple = (100, 500)  # Min, max for beginner instrument
    needs_amplification: bool = False
    portable: bool = True

    # Teaching notes
    common_challenges: List[str] = field(default_factory=list)
    first_skills: List[str] = field(default_factory=list)
    practice_tips: List[str] = field(default_factory=list)

    # Genre associations
    primary_genres: List[str] = field(default_factory=list)

    # Related instruments (for students to explore)
    related_instruments: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "family": self.family.name,
            "aliases": self.aliases,
            "beginner_friendly": self.beginner_friendly,
            "solo_instrument": self.solo_instrument,
            "ensemble_instrument": self.ensemble_instrument,
            "requires_accompaniment": self.requires_accompaniment,
            "minimum_age": self.minimum_age,
            "physical_demands": self.physical_demands,
            "requires_both_hands": self.requires_both_hands,
            "requires_breath": self.requires_breath,
            "days_to_first_song": self.days_to_first_song,
            "months_to_intermediate": self.months_to_intermediate,
            "skill_ceiling": self.skill_ceiling,
            "starter_cost_usd": list(self.starter_cost_usd),
            "needs_amplification": self.needs_amplification,
            "portable": self.portable,
            "common_challenges": self.common_challenges,
            "first_skills": self.first_skills,
            "practice_tips": self.practice_tips,
            "primary_genres": self.primary_genres,
            "related_instruments": self.related_instruments,
        }


# Comprehensive instrument database
INSTRUMENTS: Dict[str, Instrument] = {
    # =========================================================================
    # KEYBOARD INSTRUMENTS
    # =========================================================================
    "piano": Instrument(
        id="piano",
        name="Piano",
        family=InstrumentFamily.KEYBOARD,
        aliases=["keyboard", "keys", "pianoforte"],
        beginner_friendly=True,
        solo_instrument=True,
        ensemble_instrument=True,
        minimum_age=4,
        physical_demands="low",
        days_to_first_song=3,
        months_to_intermediate=18,
        skill_ceiling="very_high",
        starter_cost_usd=(200, 800),
        portable=False,
        common_challenges=[
            "Hand independence - playing different rhythms with each hand",
            "Reading two clefs simultaneously",
            "Developing finger strength and dexterity",
            "Pedal technique and timing",
            "Playing expressively while maintaining technique",
        ],
        first_skills=[
            "Hand position and posture",
            "Finding and naming notes on the keyboard",
            "Playing simple 5-finger patterns",
            "Basic rhythm and counting",
            "Reading single-line melodies",
        ],
        practice_tips=[
            "Start with hands separately before combining",
            "Practice slowly with a metronome",
            "Focus on problem spots, not just playing through",
            "Spend time on scales and arpeggios daily",
            "Listen to recordings of pieces you're learning",
        ],
        primary_genres=["classical", "jazz", "pop", "rock", "blues", "gospel"],
        related_instruments=["organ", "synthesizer", "electric_piano"],
    ),

    "synthesizer": Instrument(
        id="synthesizer",
        name="Synthesizer",
        family=InstrumentFamily.ELECTRONIC,
        aliases=["synth", "keyboard synth", "analog synth", "digital synth"],
        beginner_friendly=True,
        solo_instrument=True,
        minimum_age=8,
        physical_demands="low",
        days_to_first_song=1,
        months_to_intermediate=12,
        skill_ceiling="very_high",
        starter_cost_usd=(150, 600),
        needs_amplification=True,
        common_challenges=[
            "Understanding synthesis concepts (oscillators, filters, envelopes)",
            "Sound design vs. playing technique",
            "Managing patches and presets",
            "MIDI and DAW integration",
            "Avoiding preset dependency",
        ],
        first_skills=[
            "Basic keyboard technique",
            "Understanding subtractive synthesis",
            "Using presets effectively",
            "Basic MIDI concepts",
            "Creating simple patches",
        ],
        practice_tips=[
            "Learn piano basics alongside synthesis",
            "Start with subtractive synthesis fundamentals",
            "Recreate sounds you hear in music",
            "Document your patches",
            "Practice programming as much as playing",
        ],
        primary_genres=["electronic", "pop", "film_score", "ambient", "experimental"],
        related_instruments=["piano", "organ", "drum_machine"],
    ),

    # =========================================================================
    # GUITAR FAMILY
    # =========================================================================
    "acoustic_guitar": Instrument(
        id="acoustic_guitar",
        name="Acoustic Guitar",
        family=InstrumentFamily.FRETTED,
        aliases=["guitar", "steel-string guitar", "folk guitar"],
        beginner_friendly=True,
        solo_instrument=True,
        ensemble_instrument=True,
        minimum_age=6,
        physical_demands="medium",
        days_to_first_song=7,
        months_to_intermediate=12,
        skill_ceiling="very_high",
        starter_cost_usd=(100, 400),
        common_challenges=[
            "Finger pain during callus development",
            "Chord transitions, especially barre chords",
            "Strumming patterns and rhythm",
            "Finger independence for fingerpicking",
            "Tuning and intonation",
        ],
        first_skills=[
            "Proper posture and hand position",
            "Tuning the guitar",
            "Open chords: G, C, D, E, A",
            "Basic strumming patterns",
            "Simple chord progressions",
        ],
        practice_tips=[
            "Short, frequent sessions while building calluses",
            "Practice chord changes slowly and accurately",
            "Use a metronome for strumming patterns",
            "Learn songs you love to stay motivated",
            "Focus on clean, buzzes-free notes",
        ],
        primary_genres=["folk", "country", "rock", "pop", "singer-songwriter"],
        related_instruments=["electric_guitar", "ukulele", "bass"],
    ),

    "electric_guitar": Instrument(
        id="electric_guitar",
        name="Electric Guitar",
        family=InstrumentFamily.FRETTED,
        aliases=["e-guitar", "solid body guitar"],
        beginner_friendly=True,
        minimum_age=7,
        physical_demands="medium",
        days_to_first_song=7,
        months_to_intermediate=12,
        skill_ceiling="very_high",
        starter_cost_usd=(150, 500),
        needs_amplification=True,
        common_challenges=[
            "String bending and vibrato technique",
            "Managing amplifier tone and effects",
            "Muting unwanted string noise",
            "Speed and accuracy for lead playing",
            "Barre chord stamina",
        ],
        first_skills=[
            "Basic chord shapes",
            "Power chords",
            "Palm muting",
            "Simple riffs and licks",
            "Using an amplifier",
        ],
        practice_tips=[
            "Practice both clean and with distortion",
            "Work on muting technique early",
            "Learn songs in styles you enjoy",
            "Record yourself to identify issues",
            "Practice standing if you plan to perform",
        ],
        primary_genres=["rock", "blues", "metal", "jazz", "funk", "pop"],
        related_instruments=["acoustic_guitar", "bass", "ukulele"],
    ),

    "bass": Instrument(
        id="bass",
        name="Bass Guitar",
        family=InstrumentFamily.FRETTED,
        aliases=["electric bass", "bass guitar", "4-string"],
        beginner_friendly=True,
        ensemble_instrument=True,
        solo_instrument=False,
        minimum_age=8,
        physical_demands="medium",
        days_to_first_song=3,
        months_to_intermediate=12,
        skill_ceiling="very_high",
        starter_cost_usd=(150, 400),
        needs_amplification=True,
        common_challenges=[
            "Developing finger strength for thicker strings",
            "Locking in with the drummer",
            "Understanding the harmonic role of bass",
            "Slap and pop technique",
            "Reading bass clef",
        ],
        first_skills=[
            "Proper fingering technique",
            "Root notes of common chords",
            "Basic rhythmic patterns",
            "Playing with a drummer/metronome",
            "Simple walking bass lines",
        ],
        practice_tips=[
            "Always practice with a metronome or drum track",
            "Focus on groove before speed",
            "Learn to listen to the whole band",
            "Study bass lines in songs you love",
            "Practice standing with a strap",
        ],
        primary_genres=["rock", "funk", "jazz", "r&b", "metal", "pop"],
        related_instruments=["electric_guitar", "upright_bass"],
    ),

    "ukulele": Instrument(
        id="ukulele",
        name="Ukulele",
        family=InstrumentFamily.FRETTED,
        aliases=["uke", "soprano ukulele"],
        beginner_friendly=True,
        solo_instrument=True,
        minimum_age=4,
        physical_demands="low",
        days_to_first_song=1,
        months_to_intermediate=6,
        skill_ceiling="medium",
        starter_cost_usd=(30, 150),
        common_challenges=[
            "Developing calluses (less severe than guitar)",
            "Transitioning between chords smoothly",
            "Strumming with the fingers",
            "Intonation on cheaper instruments",
            "Understanding the re-entrant tuning",
        ],
        first_skills=[
            "Tuning (G-C-E-A)",
            "Basic chords: C, G, Am, F",
            "Simple strumming patterns",
            "Fingerpicking basics",
            "Playing and singing simultaneously",
        ],
        practice_tips=[
            "Perfect for short practice sessions",
            "Great for learning music theory basics",
            "Practice chord changes before strumming",
            "Invest in a good tuner",
            "Take it everywhere - it's portable!",
        ],
        primary_genres=["hawaiian", "folk", "pop", "indie"],
        related_instruments=["acoustic_guitar", "mandolin"],
    ),

    # =========================================================================
    # DRUMS & PERCUSSION
    # =========================================================================
    "drums": Instrument(
        id="drums",
        name="Drum Kit",
        family=InstrumentFamily.PERCUSSION,
        aliases=["drum set", "drum kit", "trap set", "kit"],
        beginner_friendly=True,
        ensemble_instrument=True,
        solo_instrument=False,
        minimum_age=5,
        physical_demands="high",
        days_to_first_song=3,
        months_to_intermediate=12,
        skill_ceiling="very_high",
        starter_cost_usd=(300, 800),
        portable=False,
        common_challenges=[
            "Limb independence - different patterns with each limb",
            "Maintaining consistent tempo",
            "Developing speed and endurance",
            "Managing dynamics and touch",
            "Noise/practice space issues",
        ],
        first_skills=[
            "Proper grip and stroke technique",
            "Basic rock beats",
            "Playing with a metronome",
            "Rudiments: single stroke, double stroke",
            "Hi-hat, snare, and kick coordination",
        ],
        practice_tips=[
            "Practice pad work for quiet practice",
            "Start slow with a metronome, increase gradually",
            "Work on rudiments daily",
            "Play along with music",
            "Record yourself to check timing",
        ],
        primary_genres=["rock", "jazz", "pop", "funk", "metal", "hip-hop"],
        related_instruments=["percussion", "cajon", "electronic_drums"],
    ),

    "cajon": Instrument(
        id="cajon",
        name="Cajón",
        family=InstrumentFamily.PERCUSSION,
        aliases=["box drum", "cajon"],
        beginner_friendly=True,
        ensemble_instrument=True,
        minimum_age=5,
        physical_demands="medium",
        days_to_first_song=1,
        months_to_intermediate=6,
        skill_ceiling="medium",
        starter_cost_usd=(50, 200),
        common_challenges=[
            "Developing different tones (bass, slap, tone)",
            "Maintaining good posture while playing",
            "Building hand endurance",
            "Ghost notes and dynamics",
        ],
        first_skills=[
            "Sitting position and posture",
            "Bass tone (center of the playing surface)",
            "Slap tone (top edges)",
            "Basic rock and folk patterns",
            "Playing with brushes",
        ],
        practice_tips=[
            "Listen for distinct bass and slap tones",
            "Start with simple patterns",
            "Great acoustic alternative to drum kit",
            "Practice both sitting and standing positions",
        ],
        primary_genres=["flamenco", "folk", "acoustic", "world"],
        related_instruments=["drums", "djembe", "bongos"],
    ),

    # =========================================================================
    # VOICE
    # =========================================================================
    "voice": Instrument(
        id="voice",
        name="Voice / Vocals",
        family=InstrumentFamily.VOICE,
        aliases=["singing", "vocals", "singer"],
        beginner_friendly=True,
        solo_instrument=True,
        ensemble_instrument=True,
        requires_breath=True,
        requires_both_hands=False,
        minimum_age=5,
        physical_demands="medium",
        days_to_first_song=1,
        months_to_intermediate=12,
        skill_ceiling="very_high",
        starter_cost_usd=(0, 100),  # Just lessons/courses
        common_challenges=[
            "Breath support and control",
            "Pitch accuracy",
            "Extending vocal range",
            "Managing vocal health",
            "Performance anxiety",
        ],
        first_skills=[
            "Breathing technique",
            "Pitch matching",
            "Posture and body alignment",
            "Simple scales and exercises",
            "Singing in your comfortable range",
        ],
        practice_tips=[
            "Stay hydrated - drink lots of water",
            "Warm up before singing",
            "Record yourself to hear objectively",
            "Rest your voice when tired",
            "Work with a teacher to avoid bad habits",
        ],
        primary_genres=["pop", "rock", "classical", "jazz", "r&b", "musical_theater"],
        related_instruments=["piano", "guitar"],
    ),

    # =========================================================================
    # WOODWINDS
    # =========================================================================
    "flute": Instrument(
        id="flute",
        name="Flute",
        family=InstrumentFamily.WOODWINDS,
        aliases=["western flute", "concert flute", "C flute"],
        beginner_friendly=True,
        requires_breath=True,
        minimum_age=8,
        physical_demands="medium",
        days_to_first_song=14,
        months_to_intermediate=18,
        skill_ceiling="very_high",
        starter_cost_usd=(200, 600),
        common_challenges=[
            "Producing a consistent sound (embouchure)",
            "Breath support for long phrases",
            "Finger coordination",
            "Intonation in the upper register",
            "Tone quality development",
        ],
        first_skills=[
            "Assembling and holding the flute",
            "Producing a sound (head joint only)",
            "Basic fingerings for first octave",
            "Breathing and phrasing",
            "Simple scales",
        ],
        practice_tips=[
            "Start with just the head joint for tone production",
            "Use a mirror to check embouchure",
            "Practice long tones daily",
            "Work on breathing exercises",
            "Progress slowly through registers",
        ],
        primary_genres=["classical", "jazz", "folk", "world"],
        related_instruments=["piccolo", "clarinet", "recorder"],
    ),

    "clarinet": Instrument(
        id="clarinet",
        name="Clarinet",
        family=InstrumentFamily.WOODWINDS,
        aliases=["Bb clarinet", "soprano clarinet"],
        beginner_friendly=True,
        requires_breath=True,
        minimum_age=9,
        physical_demands="medium",
        days_to_first_song=14,
        months_to_intermediate=18,
        skill_ceiling="very_high",
        starter_cost_usd=(200, 700),
        common_challenges=[
            "Embouchure development",
            "Reed selection and maintenance",
            "Crossing the 'break' (throat to clarion register)",
            "Finger covering (especially on lower notes)",
            "Squeaks and tone control",
        ],
        first_skills=[
            "Assembling the instrument",
            "Reed placement and care",
            "Producing a sound with good embouchure",
            "Chalumeau register fingerings",
            "Basic articulation",
        ],
        practice_tips=[
            "Start with quality reeds (not too hard)",
            "Focus on long tones for tone development",
            "Practice register transitions slowly",
            "Keep instrument clean and maintained",
            "Work on scales in comfortable range",
        ],
        primary_genres=["classical", "jazz", "klezmer", "band"],
        related_instruments=["saxophone", "bass_clarinet", "oboe"],
    ),

    "saxophone": Instrument(
        id="saxophone",
        name="Saxophone",
        family=InstrumentFamily.WOODWINDS,
        aliases=["sax", "alto sax", "tenor sax"],
        beginner_friendly=True,
        requires_breath=True,
        minimum_age=9,
        physical_demands="medium",
        days_to_first_song=7,
        months_to_intermediate=12,
        skill_ceiling="very_high",
        starter_cost_usd=(300, 1000),
        common_challenges=[
            "Embouchure consistency",
            "Breath support for projection",
            "Intonation (saxophone is not naturally in tune)",
            "Reed selection",
            "Developing personal tone",
        ],
        first_skills=[
            "Assembling and holding the saxophone",
            "Basic embouchure",
            "First octave fingerings",
            "Producing a centered tone",
            "Simple scales and songs",
        ],
        practice_tips=[
            "Alto saxophone is most common for beginners",
            "Work on long tones daily",
            "Play along with recordings",
            "Learn to adjust intonation by ear",
            "Explore different musical styles",
        ],
        primary_genres=["jazz", "rock", "funk", "classical", "pop"],
        related_instruments=["clarinet", "flute"],
    ),

    # =========================================================================
    # BRASS
    # =========================================================================
    "trumpet": Instrument(
        id="trumpet",
        name="Trumpet",
        family=InstrumentFamily.BRASS,
        aliases=["Bb trumpet", "cornet"],
        beginner_friendly=True,
        requires_breath=True,
        minimum_age=8,
        physical_demands="medium",
        days_to_first_song=14,
        months_to_intermediate=18,
        skill_ceiling="very_high",
        starter_cost_usd=(150, 600),
        common_challenges=[
            "Embouchure development and endurance",
            "Building range (especially high notes)",
            "Maintaining air support",
            "Intonation",
            "Managing fatigue",
        ],
        first_skills=[
            "Buzzing on the mouthpiece",
            "Producing first notes (middle register)",
            "Basic fingerings",
            "Breathing and air support",
            "Simple scales",
        ],
        practice_tips=[
            "Rest as much as you play (especially early on)",
            "Start with mouthpiece buzzing exercises",
            "Don't force high notes - build range gradually",
            "Practice long tones for endurance",
            "Listen to great trumpet players",
        ],
        primary_genres=["jazz", "classical", "latin", "mariachi", "brass_band"],
        related_instruments=["cornet", "flugelhorn", "trombone"],
    ),

    "trombone": Instrument(
        id="trombone",
        name="Trombone",
        family=InstrumentFamily.BRASS,
        aliases=["tenor trombone", "slide trombone"],
        beginner_friendly=True,
        requires_breath=True,
        minimum_age=9,
        physical_demands="medium",
        days_to_first_song=14,
        months_to_intermediate=18,
        skill_ceiling="very_high",
        starter_cost_usd=(200, 700),
        common_challenges=[
            "Slide position accuracy (no frets or valves)",
            "Arm reach for outer positions",
            "Embouchure development",
            "Legato playing",
            "Intonation without visual reference",
        ],
        first_skills=[
            "Buzzing on the mouthpiece",
            "Learning the 7 slide positions",
            "Producing first notes",
            "Glissando and legato technique",
            "Basic scales",
        ],
        practice_tips=[
            "Mark slide positions initially for reference",
            "Practice with a tuner frequently",
            "Work on smooth slide movement",
            "Long tones are essential",
            "Listen to develop intonation sense",
        ],
        primary_genres=["jazz", "classical", "ska", "brass_band", "marching_band"],
        related_instruments=["trumpet", "euphonium", "tuba"],
    ),

    # =========================================================================
    # STRINGS (ORCHESTRAL)
    # =========================================================================
    "violin": Instrument(
        id="violin",
        name="Violin",
        family=InstrumentFamily.STRINGS,
        aliases=["fiddle"],
        beginner_friendly=False,
        minimum_age=4,
        physical_demands="medium",
        days_to_first_song=30,
        months_to_intermediate=24,
        skill_ceiling="very_high",
        starter_cost_usd=(100, 500),
        common_challenges=[
            "Intonation (no frets)",
            "Bowing technique and tone production",
            "Left hand position and finger placement",
            "Holding the instrument without tension",
            "Developing vibrato",
        ],
        first_skills=[
            "Proper posture and instrument hold",
            "Bow hold and straight bowing",
            "Open strings with good tone",
            "First finger placement",
            "Simple scales on one string",
        ],
        practice_tips=[
            "Use tapes on fingerboard initially",
            "Practice with a tuner constantly",
            "Focus on bow control before left hand",
            "Short practice sessions for young students",
            "Work with a teacher - self-teaching is difficult",
        ],
        primary_genres=["classical", "folk", "irish", "country", "jazz"],
        related_instruments=["viola", "cello", "upright_bass"],
    ),

    "cello": Instrument(
        id="cello",
        name="Cello",
        family=InstrumentFamily.STRINGS,
        aliases=["violoncello"],
        beginner_friendly=False,
        minimum_age=5,
        physical_demands="medium",
        days_to_first_song=30,
        months_to_intermediate=24,
        skill_ceiling="very_high",
        starter_cost_usd=(300, 1000),
        portable=False,
        common_challenges=[
            "Intonation across a large fingerboard",
            "Bowing technique and arm weight",
            "Thumb position in upper registers",
            "Transporting the large instrument",
            "Endpin adjustment and posture",
        ],
        first_skills=[
            "Seated posture and instrument position",
            "Bow hold and basic bow strokes",
            "Open strings",
            "First position fingerings",
            "Simple scales",
        ],
        practice_tips=[
            "Get the right size instrument for your body",
            "Focus on relaxed posture",
            "Work on shifting carefully",
            "Listen to cello recordings for tone reference",
            "Practice with drone notes for intonation",
        ],
        primary_genres=["classical", "film_score", "folk", "rock_cello"],
        related_instruments=["violin", "viola", "upright_bass"],
    ),

    # =========================================================================
    # PRODUCTION
    # =========================================================================
    "production": Instrument(
        id="production",
        name="Music Production",
        family=InstrumentFamily.ELECTRONIC,
        aliases=["DAW", "beatmaking", "producing", "electronic music production"],
        beginner_friendly=True,
        solo_instrument=True,
        requires_both_hands=True,
        minimum_age=10,
        physical_demands="low",
        days_to_first_song=1,
        months_to_intermediate=12,
        skill_ceiling="very_high",
        starter_cost_usd=(0, 500),  # Free DAWs exist
        common_challenges=[
            "DAW learning curve",
            "Understanding signal flow",
            "Mixing and EQ concepts",
            "Arrangement and song structure",
            "Finishing songs",
        ],
        first_skills=[
            "DAW navigation and basics",
            "Working with loops and samples",
            "Basic MIDI programming",
            "Simple arrangement structure",
            "Exporting and sharing",
        ],
        practice_tips=[
            "Start with one DAW and learn it deeply",
            "Finish songs, even if imperfect",
            "Learn basic music theory",
            "Study reference tracks",
            "Focus on arrangement before mixing",
        ],
        primary_genres=["electronic", "hip-hop", "pop", "edm", "ambient"],
        related_instruments=["synthesizer", "drum_machine", "midi_controller"],
    ),
}


def get_instrument(instrument_id: str) -> Optional[Instrument]:
    """Get an instrument by ID or alias."""
    # Direct lookup
    if instrument_id in INSTRUMENTS:
        return INSTRUMENTS[instrument_id]

    # Check aliases
    instrument_id_lower = instrument_id.lower()
    for inst in INSTRUMENTS.values():
        if instrument_id_lower in [a.lower() for a in inst.aliases]:
            return inst
        if instrument_id_lower == inst.name.lower():
            return inst

    return None


def get_instruments_by_family(family: InstrumentFamily) -> List[Instrument]:
    """Get all instruments in a family."""
    return [i for i in INSTRUMENTS.values() if i.family == family]


def get_beginner_instruments() -> List[Instrument]:
    """Get instruments suitable for beginners."""
    return sorted(
        [i for i in INSTRUMENTS.values() if i.beginner_friendly],
        key=lambda x: x.days_to_first_song,
    )


def get_instruments_by_genre(genre: str) -> List[Instrument]:
    """Get instruments commonly used in a genre."""
    genre_lower = genre.lower()
    return [
        i for i in INSTRUMENTS.values()
        if genre_lower in [g.lower() for g in i.primary_genres]
    ]


def suggest_instrument(
    age: int,
    physical_ability: str = "normal",
    goals: Optional[List[str]] = None,
    budget_usd: int = 500,
) -> List[Dict[str, Any]]:
    """
    Suggest instruments based on student profile.

    Args:
        age: Student's age
        physical_ability: "limited", "normal", or "athletic"
        goals: List of goals like "play in band", "solo performance", "songwriting"
        budget_usd: Maximum budget for starter instrument

    Returns:
        List of suggested instruments with reasoning
    """
    suggestions = []
    goals = goals or []

    for inst in INSTRUMENTS.values():
        score = 0
        reasons = []

        # Age check
        if age < inst.minimum_age:
            continue

        # Physical demands
        if physical_ability == "limited" and inst.physical_demands == "high":
            continue
        if physical_ability == "athletic" and inst.physical_demands == "low":
            score += 1

        # Budget check
        if inst.starter_cost_usd[0] <= budget_usd:
            score += 2
            reasons.append("Within budget")

        # Beginner friendliness
        if inst.beginner_friendly:
            score += 3
            reasons.append("Beginner-friendly")

        # Goal matching
        if "play in band" in goals and inst.ensemble_instrument:
            score += 2
            reasons.append("Great for ensemble playing")
        if "solo performance" in goals and inst.solo_instrument:
            score += 2
            reasons.append("Great for solo performance")
        if "songwriting" in goals and inst.id in ["piano", "acoustic_guitar", "ukulele"]:
            score += 3
            reasons.append("Excellent for songwriting")

        # Quick progress
        if inst.days_to_first_song <= 7:
            score += 2
            reasons.append("Quick path to first song")

        if score > 0:
            suggestions.append({
                "instrument": inst,
                "score": score,
                "reasons": reasons,
            })

    return sorted(suggestions, key=lambda x: x["score"], reverse=True)[:5]


# Instrument learning path recommendations
INSTRUMENT_LEARNING_PATHS = {
    "piano": {
        "starter_path": ["posture", "note_reading", "basic_chords", "scales", "simple_songs"],
        "intermediate_path": ["arpeggios", "hand_independence", "pedaling", "dynamics", "repertoire"],
        "advanced_path": ["advanced_technique", "improvisation", "sight_reading", "performance"],
        "recommended_order": ["technique", "theory", "repertoire", "ear_training"],
    },
    "guitar": {
        "starter_path": ["tuning", "posture", "open_chords", "strumming", "simple_songs"],
        "intermediate_path": ["barre_chords", "fingerpicking", "scales", "music_theory", "lead_playing"],
        "advanced_path": ["advanced_technique", "improvisation", "songwriting", "performance"],
        "recommended_order": ["rhythm", "chords", "scales", "theory"],
    },
    "drums": {
        "starter_path": ["grip", "basic_beats", "timing", "coordination", "simple_fills"],
        "intermediate_path": ["rudiments", "dynamics", "styles", "independence", "groove"],
        "advanced_path": ["advanced_rudiments", "odd_time", "polyrhythms", "performance"],
        "recommended_order": ["timing", "technique", "rudiments", "musicality"],
    },
    "voice": {
        "starter_path": ["breathing", "posture", "pitch_matching", "range_finding", "simple_songs"],
        "intermediate_path": ["breath_support", "registration", "dynamics", "phrasing", "repertoire"],
        "advanced_path": ["advanced_technique", "styles", "performance", "improvisation"],
        "recommended_order": ["breathing", "technique", "repertoire", "performance"],
    },
}
