"""
Rule-Breaking Recipe Book

A searchable database of "musical rule violations" with emotional context,
audio examples, and implementation guides.

Proposal: ChatGPT - Rule-Breaking Recipe Book
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json
from pathlib import Path


class RuleCategory(str, Enum):
    """Categories of musical rules that can be broken."""
    HARMONY = "harmony"
    RHYTHM = "rhythm"
    PRODUCTION = "production"
    ARRANGEMENT = "arrangement"
    MELODY = "melody"
    FORM = "form"


class EmotionalEffect(str, Enum):
    """Emotional effects of rule-breaking."""
    TENSION = "tension"
    RELEASE = "release"
    UNEASE = "unease"
    NOSTALGIA = "nostalgia"
    ANGER = "anger"
    SADNESS = "sadness"
    JOY = "joy"
    SURPRISE = "surprise"
    INTIMACY = "intimacy"
    DISTANCE = "distance"
    CHAOS = "chaos"
    PEACE = "peace"
    YEARNING = "yearning"
    DEFIANCE = "defiance"
    VULNERABILITY = "vulnerability"


class RiskLevel(str, Enum):
    """How risky is this rule-break?"""
    LOW = "low"           # Usually works well
    MEDIUM = "medium"     # Requires context awareness
    HIGH = "high"         # Can easily backfire
    EXTREME = "extreme"   # For experts only


@dataclass
class FamousExample:
    """A famous song that uses this technique."""
    song: str
    artist: str
    year: Optional[int] = None
    timestamp: Optional[str] = None  # Where in the song
    notes: str = ""

    def __str__(self):
        return f'"{self.song}" by {self.artist}' + (f" ({self.year})" if self.year else "")


@dataclass
class Recipe:
    """A rule-breaking recipe."""
    id: str
    name: str
    category: RuleCategory

    # The rule being broken
    the_rule: str
    why_it_exists: str

    # The break
    how_to_break: str
    emotional_effect: List[EmotionalEffect]
    risk_level: RiskLevel

    # Examples and guidance
    famous_examples: List[FamousExample] = field(default_factory=list)
    implementation_steps: List[str] = field(default_factory=list)
    danger_zone: List[str] = field(default_factory=list)  # When it backfires

    # Metadata
    tags: List[str] = field(default_factory=list)
    related_recipes: List[str] = field(default_factory=list)  # Recipe IDs

    # Intent schema integration
    intent_schema_option: Optional[str] = None  # Maps to HarmonyRuleBreak, etc.

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "the_rule": self.the_rule,
            "why_it_exists": self.why_it_exists,
            "how_to_break": self.how_to_break,
            "emotional_effect": [e.value for e in self.emotional_effect],
            "risk_level": self.risk_level.value,
            "famous_examples": [
                {"song": e.song, "artist": e.artist, "year": e.year, "notes": e.notes}
                for e in self.famous_examples
            ],
            "implementation_steps": self.implementation_steps,
            "danger_zone": self.danger_zone,
            "tags": self.tags,
            "related_recipes": self.related_recipes,
            "intent_schema_option": self.intent_schema_option,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Recipe":
        return cls(
            id=data["id"],
            name=data["name"],
            category=RuleCategory(data["category"]),
            the_rule=data["the_rule"],
            why_it_exists=data["why_it_exists"],
            how_to_break=data["how_to_break"],
            emotional_effect=[EmotionalEffect(e) for e in data.get("emotional_effect", [])],
            risk_level=RiskLevel(data.get("risk_level", "medium")),
            famous_examples=[
                FamousExample(**e) for e in data.get("famous_examples", [])
            ],
            implementation_steps=data.get("implementation_steps", []),
            danger_zone=data.get("danger_zone", []),
            tags=data.get("tags", []),
            related_recipes=data.get("related_recipes", []),
            intent_schema_option=data.get("intent_schema_option"),
        )


# =============================================================================
# Built-in Recipes
# =============================================================================

RECIPES = [
    # HARMONY
    Recipe(
        id="parallel_fifths",
        name="Parallel Fifths (Power Chord Movement)",
        category=RuleCategory.HARMONY,
        the_rule="Avoid parallel perfect fifths between voices",
        why_it_exists="In classical music, parallel fifths reduce voice independence and create a 'hollow' sound",
        how_to_break="Move two voices in parallel fifth intervals for a powerful, medieval, or rock sound",
        emotional_effect=[EmotionalEffect.DEFIANCE, EmotionalEffect.TENSION],
        risk_level=RiskLevel.LOW,
        famous_examples=[
            FamousExample("Smoke on the Water", "Deep Purple", 1972, "Main riff"),
            FamousExample("You Really Got Me", "The Kinks", 1964, "Guitar riff"),
            FamousExample("Iron Man", "Black Sabbath", 1970, "Iconic opening"),
        ],
        implementation_steps=[
            "Choose a root note melody line",
            "Double it a perfect fifth above (or fourth below)",
            "Move both voices in parallel motion",
            "Works best with distorted guitars or synths",
        ],
        danger_zone=[
            "In delicate acoustic arrangements, can sound crude",
            "Overuse removes the impact - save for emphasis",
            "In vocal arrangements, can sound like a mistake",
        ],
        tags=["rock", "metal", "power", "guitar", "medieval"],
        intent_schema_option="HARMONY_ParallelMotion",
    ),

    Recipe(
        id="unresolved_dominant",
        name="The Eternal Dominant (Never Resolving)",
        category=RuleCategory.HARMONY,
        the_rule="Dominant chords (V) should resolve to tonic (I)",
        why_it_exists="Resolution provides closure and satisfaction",
        how_to_break="End on a dominant chord, or repeatedly defer resolution",
        emotional_effect=[EmotionalEffect.YEARNING, EmotionalEffect.TENSION, EmotionalEffect.UNEASE],
        risk_level=RiskLevel.MEDIUM,
        famous_examples=[
            FamousExample("A Day in the Life", "The Beatles", 1967, "Final chord fades out"),
            FamousExample("Purple Haze", "Jimi Hendrix", 1967, "Perpetual dominant feel"),
            FamousExample("Creep", "Radiohead", 1992, "Chorus never fully resolves"),
        ],
        implementation_steps=[
            "Build tension with dominant harmony",
            "When resolution is expected, move to another dominant or related chord",
            "Or simply end the song on the dominant",
            "Use sustain/reverb to let it hang in the air",
        ],
        danger_zone=[
            "Can feel 'incomplete' in a bad way if context doesn't support it",
            "Works best when lyrics/mood justify the lack of resolution",
            "Commercial music often needs SOME resolution",
        ],
        tags=["tension", "unresolved", "yearning", "experimental"],
        intent_schema_option="HARMONY_AvoidTonicResolution",
    ),

    Recipe(
        id="modal_interchange",
        name="Borrowed Color (Modal Interchange)",
        category=RuleCategory.HARMONY,
        the_rule="Stay within the key's diatonic chords",
        why_it_exists="Diatonic harmony is predictable and 'safe'",
        how_to_break="Borrow chords from parallel modes (minor from major, etc.)",
        emotional_effect=[EmotionalEffect.NOSTALGIA, EmotionalEffect.SADNESS, EmotionalEffect.SURPRISE],
        risk_level=RiskLevel.LOW,
        famous_examples=[
            FamousExample("Creep", "Radiohead", 1992, "iv chord in major key"),
            FamousExample("Space Oddity", "David Bowie", 1969, "♭VII chord usage"),
            FamousExample("No Woman No Cry", "Bob Marley", 1974, "♭VI - ♭VII progression"),
        ],
        implementation_steps=[
            "In a major key, try: ♭III, ♭VI, ♭VII, iv (minor four)",
            "In a minor key, try: IV (major four), ♭II (Neapolitan)",
            "Use chromatic voice leading for smooth transitions",
            "The 'surprise' chord often appears before returning home",
        ],
        danger_zone=[
            "Too many borrowed chords loses the home key feeling",
            "Some combinations sound jazzy when you want pop",
            "The borrowed chord needs to earn its place emotionally",
        ],
        tags=["color", "borrowing", "modal", "chromatic", "surprise"],
        intent_schema_option="HARMONY_ModalInterchange",
    ),

    # RHYTHM
    Recipe(
        id="metric_displacement",
        name="The Shifted Groove (Metric Displacement)",
        category=RuleCategory.RHYTHM,
        the_rule="Emphasize beats 1 and 3 (or 2 and 4 in backbeat)",
        why_it_exists="Clear metric emphasis helps listeners follow along",
        how_to_break="Start phrases on unexpected beats, shift the entire groove",
        emotional_effect=[EmotionalEffect.UNEASE, EmotionalEffect.SURPRISE, EmotionalEffect.CHAOS],
        risk_level=RiskLevel.HIGH,
        famous_examples=[
            FamousExample("Schism", "Tool", 2001, "5/8 + 7/8 patterns"),
            FamousExample("The Ocean", "Led Zeppelin", 1973, "7/8 groove"),
            FamousExample("Money", "Pink Floyd", 1973, "7/4 time signature"),
        ],
        implementation_steps=[
            "Take a standard groove and shift it by an 8th or 16th note",
            "Or write in an odd time signature (5/4, 7/8)",
            "Keep ONE element anchored (kick, snare, or hi-hat)",
            "Let listeners adjust for 4-8 bars before changing",
        ],
        danger_zone=[
            "Can alienate listeners who want to dance/nod along",
            "Musicians may struggle to stay locked in",
            "Often needs a 'release' section in normal time",
        ],
        tags=["odd-time", "progressive", "complex", "disorienting"],
        intent_schema_option="RHYTHM_ConstantDisplacement",
    ),

    Recipe(
        id="tempo_drift",
        name="The Human Clock (Tempo Drift)",
        category=RuleCategory.RHYTHM,
        the_rule="Maintain consistent tempo throughout",
        why_it_exists="Steady tempo is expected, especially in electronic/pop music",
        how_to_break="Allow intentional tempo fluctuations for emotional effect",
        emotional_effect=[EmotionalEffect.INTIMACY, EmotionalEffect.VULNERABILITY, EmotionalEffect.NOSTALGIA],
        risk_level=RiskLevel.MEDIUM,
        famous_examples=[
            FamousExample("Bohemian Rhapsody", "Queen", 1975, "Dramatic tempo changes"),
            FamousExample("Stairway to Heaven", "Led Zeppelin", 1971, "Gradual acceleration"),
            FamousExample("When the Levee Breaks", "Led Zeppelin", 1971, "Natural drum feel"),
        ],
        implementation_steps=[
            "Record without a click track, following the feel",
            "Or automate tempo changes (±2-5 BPM) at emotional moments",
            "Speed up subtly into choruses, slow down in verses",
            "Let the drummer 'breathe' rather than be grid-locked",
        ],
        danger_zone=[
            "Can sound like a mistake if not confident",
            "Hard to mix with grid-based electronic elements",
            "Modern listeners expect perfection - this sounds 'old school'",
        ],
        tags=["organic", "human", "live", "natural", "breathing"],
        intent_schema_option="RHYTHM_TempoFluctuation",
    ),

    # PRODUCTION
    Recipe(
        id="buried_vocals",
        name="Lost in the Mix (Buried Vocals)",
        category=RuleCategory.PRODUCTION,
        the_rule="Vocals should be clearly audible above the mix",
        why_it_exists="Lyrics are usually the focal point; intelligibility matters",
        how_to_break="Push vocals back in the mix, let them blend with instruments",
        emotional_effect=[EmotionalEffect.DISTANCE, EmotionalEffect.INTIMACY, EmotionalEffect.UNEASE],
        risk_level=RiskLevel.HIGH,
        famous_examples=[
            FamousExample("Loveless", "My Bloody Valentine", 1991, "Entire album"),
            FamousExample("Only Shallow", "My Bloody Valentine", 1991, "Vocals as texture"),
            FamousExample("Teen Age Riot", "Sonic Youth", 1988, "Voice buried in noise"),
        ],
        implementation_steps=[
            "Lower vocal fader until voice becomes another instrument",
            "Add heavy reverb/delay to push vocals back in space",
            "EQ to remove presence frequencies (2-5kHz)",
            "Let consonants get lost; only vowels survive",
        ],
        danger_zone=[
            "Radio/streaming playlists expect clear vocals",
            "Can frustrate listeners who want to hear lyrics",
            "Requires strong instrumental arrangement to compensate",
        ],
        tags=["shoegaze", "dreamy", "texture", "ambient", "lo-fi"],
        intent_schema_option="ARRANGEMENT_BuriedVocals",
    ),

    Recipe(
        id="intentional_clipping",
        name="Beautiful Destruction (Intentional Clipping)",
        category=RuleCategory.PRODUCTION,
        the_rule="Avoid digital clipping; maintain headroom",
        why_it_exists="Clipping causes harsh digital distortion",
        how_to_break="Use clipping as a creative texture and loudness tool",
        emotional_effect=[EmotionalEffect.ANGER, EmotionalEffect.CHAOS, EmotionalEffect.DEFIANCE],
        risk_level=RiskLevel.EXTREME,
        famous_examples=[
            FamousExample("Death Grips", "Various", 2012, "Entire discography"),
            FamousExample("Yeezus", "Kanye West", 2013, "On Sight, Black Skinhead"),
            FamousExample("SOPHIE", "Various", 2018, "Extreme digital sound design"),
        ],
        implementation_steps=[
            "Drive levels into the red intentionally",
            "Use soft clippers before hard clipping for control",
            "Layer clipped and clean versions for depth",
            "Apply to specific elements, not the whole mix (usually)",
        ],
        danger_zone=[
            "Can sound like a mistake to untrained ears",
            "Fatiguing over long listening sessions",
            "Streaming services may reject or flag the audio",
            "Can damage speakers if overdone",
        ],
        tags=["aggressive", "experimental", "digital", "noise", "industrial"],
        intent_schema_option="PRODUCTION_HardClipping",
    ),

    Recipe(
        id="lo_fi_aesthetic",
        name="The Warm Blanket (Lo-Fi Aesthetic)",
        category=RuleCategory.PRODUCTION,
        the_rule="Maximize fidelity; minimize noise and distortion",
        why_it_exists="High fidelity captures the 'true' sound",
        how_to_break="Intentionally degrade audio quality for warmth and nostalgia",
        emotional_effect=[EmotionalEffect.NOSTALGIA, EmotionalEffect.INTIMACY, EmotionalEffect.PEACE],
        risk_level=RiskLevel.LOW,
        famous_examples=[
            FamousExample("For Emma, Forever Ago", "Bon Iver", 2007, "Cabin recordings"),
            FamousExample("In Rainbows", "Radiohead", 2007, "Warm, analog feel"),
            FamousExample("Lo-Fi Hip Hop beats", "Various", 2010, "Entire genre"),
        ],
        implementation_steps=[
            "Add vinyl crackle, tape hiss, or room tone",
            "Roll off high frequencies (low-pass filter at 10-15kHz)",
            "Add subtle pitch wobble (like old tape)",
            "Use bit-crushing or sample rate reduction sparingly",
            "Saturate with tape or tube emulation",
        ],
        danger_zone=[
            "Can sound dated or cheap if overdone",
            "May not translate well to high-end systems",
            "The 'lo-fi' market is saturated - needs unique character",
        ],
        tags=["lo-fi", "warm", "vintage", "tape", "cozy", "chill"],
        intent_schema_option="PRODUCTION_LoFiDegradation",
    ),

    # ARRANGEMENT
    Recipe(
        id="extreme_dynamics",
        name="Whisper to Scream (Extreme Dynamic Range)",
        category=RuleCategory.ARRANGEMENT,
        the_rule="Maintain consistent loudness for radio/streaming",
        why_it_exists="Loudness normalization and listening environments",
        how_to_break="Use dramatic volume contrasts for emotional impact",
        emotional_effect=[EmotionalEffect.SURPRISE, EmotionalEffect.TENSION, EmotionalEffect.RELEASE],
        risk_level=RiskLevel.MEDIUM,
        famous_examples=[
            FamousExample("Smells Like Teen Spirit", "Nirvana", 1991, "Quiet verse, loud chorus"),
            FamousExample("Where Is My Mind?", "Pixies", 1988, "Quiet-loud-quiet"),
            FamousExample("A Day in the Life", "The Beatles", 1967, "Orchestral crescendo"),
        ],
        implementation_steps=[
            "Strip arrangement to minimum for quiet sections",
            "Add all elements simultaneously for impact",
            "Use automation to exaggerate the contrast",
            "Consider a 10-20dB difference between sections",
        ],
        danger_zone=[
            "Streaming normalization reduces the effect",
            "Listeners in cars/earbuds may miss quiet parts",
            "Can seem 'amateurish' if transitions aren't smooth",
        ],
        tags=["dynamics", "contrast", "loud-quiet", "impact", "crescendo"],
        intent_schema_option="ARRANGEMENT_ExtremeDynamicRange",
    ),

    Recipe(
        id="wrong_instrument",
        name="Fish Out of Water (Wrong Instrument)",
        category=RuleCategory.ARRANGEMENT,
        the_rule="Use genre-appropriate instrumentation",
        why_it_exists="Certain instruments 'belong' in certain genres",
        how_to_break="Introduce unexpected instruments for surprise and texture",
        emotional_effect=[EmotionalEffect.SURPRISE, EmotionalEffect.JOY, EmotionalEffect.NOSTALGIA],
        risk_level=RiskLevel.MEDIUM,
        famous_examples=[
            FamousExample("Eleanor Rigby", "The Beatles", 1966, "String quartet in pop"),
            FamousExample("Hurt", "Johnny Cash", 2002, "Piano in industrial song"),
            FamousExample("Old Town Road", "Lil Nas X", 2019, "Banjo in trap"),
        ],
        implementation_steps=[
            "Identify an instrument that 'doesn't belong'",
            "Give it a prominent role, don't hide it",
            "Arrange it to play idiomatically for THAT instrument",
            "Use the contrast as a feature, not a gimmick",
        ],
        danger_zone=[
            "Can seem like a novelty or joke",
            "Genre purists may reject it",
            "The instrument needs to serve the song, not distract",
        ],
        tags=["unexpected", "fusion", "surprise", "creative", "genre-bending"],
        intent_schema_option="ARRANGEMENT_UnexpectedInstrumentation",
    ),
]


# =============================================================================
# Recipe Book Class
# =============================================================================

class RecipeBook:
    """
    Searchable database of rule-breaking recipes.

    Usage:
        book = RecipeBook()
        recipes = book.search_by_emotion(EmotionalEffect.YEARNING)
        recipe = book.get("unresolved_dominant")
        print(recipe.format())
    """

    def __init__(self, custom_recipes: Optional[List[Recipe]] = None):
        self.recipes: Dict[str, Recipe] = {}

        # Load built-in recipes
        for recipe in RECIPES:
            self.recipes[recipe.id] = recipe

        # Add custom recipes
        if custom_recipes:
            for recipe in custom_recipes:
                self.recipes[recipe.id] = recipe

    def get(self, recipe_id: str) -> Optional[Recipe]:
        """Get a recipe by ID."""
        return self.recipes.get(recipe_id)

    def all(self) -> List[Recipe]:
        """Get all recipes."""
        return list(self.recipes.values())

    def search_by_category(self, category: RuleCategory) -> List[Recipe]:
        """Find recipes by category."""
        return [r for r in self.recipes.values() if r.category == category]

    def search_by_emotion(self, emotion: EmotionalEffect) -> List[Recipe]:
        """Find recipes by emotional effect."""
        return [r for r in self.recipes.values() if emotion in r.emotional_effect]

    def search_by_tag(self, tag: str) -> List[Recipe]:
        """Find recipes by tag."""
        tag_lower = tag.lower()
        return [r for r in self.recipes.values() if tag_lower in [t.lower() for t in r.tags]]

    def search_by_risk(self, max_risk: RiskLevel) -> List[Recipe]:
        """Find recipes up to a certain risk level."""
        risk_order = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.EXTREME]
        max_idx = risk_order.index(max_risk)
        return [r for r in self.recipes.values()
                if risk_order.index(r.risk_level) <= max_idx]

    def search(self, query: str) -> List[Recipe]:
        """Full-text search across recipes."""
        query_lower = query.lower()
        results = []

        for recipe in self.recipes.values():
            # Search in name, rule, how_to_break, tags
            searchable = " ".join([
                recipe.name,
                recipe.the_rule,
                recipe.how_to_break,
                " ".join(recipe.tags),
            ]).lower()

            if query_lower in searchable:
                results.append(recipe)

        return results

    def suggest_for_intent(self, mood: str, vulnerability: str = "medium") -> List[Recipe]:
        """
        Suggest recipes based on intent schema inputs.

        Maps common moods to emotional effects.
        """
        mood_map = {
            "angry": [EmotionalEffect.ANGER, EmotionalEffect.DEFIANCE],
            "sad": [EmotionalEffect.SADNESS, EmotionalEffect.YEARNING],
            "anxious": [EmotionalEffect.UNEASE, EmotionalEffect.TENSION],
            "nostalgic": [EmotionalEffect.NOSTALGIA, EmotionalEffect.INTIMACY],
            "defiant": [EmotionalEffect.DEFIANCE, EmotionalEffect.CHAOS],
            "vulnerable": [EmotionalEffect.VULNERABILITY, EmotionalEffect.INTIMACY],
            "peaceful": [EmotionalEffect.PEACE, EmotionalEffect.RELEASE],
            "joyful": [EmotionalEffect.JOY, EmotionalEffect.SURPRISE],
        }

        emotions = mood_map.get(mood.lower(), [])
        results = []

        for emotion in emotions:
            results.extend(self.search_by_emotion(emotion))

        # Filter by risk based on vulnerability
        risk_map = {"low": RiskLevel.LOW, "medium": RiskLevel.MEDIUM, "high": RiskLevel.EXTREME}
        max_risk = risk_map.get(vulnerability.lower(), RiskLevel.MEDIUM)

        safe_results = [r for r in results if r.risk_level.value <= max_risk.value]

        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for r in safe_results:
            if r.id not in seen:
                seen.add(r.id)
                unique.append(r)

        return unique

    def format_recipe(self, recipe: Recipe) -> str:
        """Format a recipe for display."""
        lines = [
            "=" * 60,
            f"🎵 {recipe.name}",
            "=" * 60,
            "",
            f"Category: {recipe.category.value.title()}",
            f"Risk Level: {'⚠️ ' * ['low', 'medium', 'high', 'extreme'].index(recipe.risk_level.value)}{recipe.risk_level.value.upper()}",
            "",
            "THE RULE:",
            f"  \"{recipe.the_rule}\"",
            f"  Why it exists: {recipe.why_it_exists}",
            "",
            "HOW TO BREAK IT:",
            f"  {recipe.how_to_break}",
            "",
            "EMOTIONAL EFFECT:",
            f"  {', '.join(e.value.title() for e in recipe.emotional_effect)}",
            "",
        ]

        if recipe.famous_examples:
            lines.append("FAMOUS EXAMPLES:")
            for ex in recipe.famous_examples:
                lines.append(f"  • {ex}")
                if ex.notes:
                    lines.append(f"    ({ex.notes})")

        if recipe.implementation_steps:
            lines.append("")
            lines.append("IMPLEMENTATION:")
            for i, step in enumerate(recipe.implementation_steps, 1):
                lines.append(f"  {i}. {step}")

        if recipe.danger_zone:
            lines.append("")
            lines.append("⚠️  DANGER ZONE (when this backfires):")
            for danger in recipe.danger_zone:
                lines.append(f"  • {danger}")

        if recipe.tags:
            lines.append("")
            lines.append(f"Tags: {', '.join(recipe.tags)}")

        return "\n".join(lines)

    def save(self, path: str):
        """Save recipes to JSON file."""
        with open(path, 'w') as f:
            json.dump([r.to_dict() for r in self.recipes.values()], f, indent=2)

    def load(self, path: str):
        """Load recipes from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)
            for item in data:
                recipe = Recipe.from_dict(item)
                self.recipes[recipe.id] = recipe


# =============================================================================
# Convenience Functions
# =============================================================================

_book: Optional[RecipeBook] = None


def get_recipe_book() -> RecipeBook:
    """Get the global recipe book instance."""
    global _book
    if _book is None:
        _book = RecipeBook()
    return _book


def search_recipes(query: str) -> List[Recipe]:
    """Search for recipes."""
    return get_recipe_book().search(query)


def get_recipe(recipe_id: str) -> Optional[Recipe]:
    """Get a specific recipe."""
    return get_recipe_book().get(recipe_id)


def suggest_rule_breaks(mood: str, vulnerability: str = "medium") -> List[Recipe]:
    """Suggest rule-breaking recipes based on mood."""
    return get_recipe_book().suggest_for_intent(mood, vulnerability)
