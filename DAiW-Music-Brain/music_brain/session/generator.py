"""
Song Generator - Generate song structures, progressions, and arrangements.

Generates:
- Chord progressions by mood/genre
- Song structures (verse/chorus/bridge arrangements)
- Basic MIDI arrangements
"""

import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field


# Progression templates by mood
PROGRESSION_TEMPLATES = {
    "hopeful": [
        ["I", "V", "vi", "IV"],
        ["I", "IV", "V", "I"],
        ["I", "iii", "IV", "V"],
    ],
    "melancholy": [
        ["i", "bVI", "bIII", "bVII"],
        ["i", "iv", "bVI", "V"],
        ["vi", "IV", "I", "V"],
    ],
    "triumphant": [
        ["I", "V", "vi", "IV", "I", "V", "I"],
        ["I", "IV", "I", "V"],
        ["I", "bVII", "IV", "I"],
    ],
    "mysterious": [
        ["i", "bII", "bVII", "i"],
        ["i", "bVI", "bVII", "i"],
        ["i", "iv", "bVI", "bVII"],
    ],
    "bittersweet": [
        ["I", "V", "vi", "iv"],  # Major to borrowed minor iv
        ["I", "IV", "iv", "I"],
        ["vi", "IV", "I", "iv"],
    ],
    "grief_reveal": [
        ["I", "V", "vi", "IV"],  # Happy setup
        ["I", "V", "vi", "iv"],  # Minor iv gut punch
        ["I", "bVI", "bVII", "I"],  # Borrowed chord devastation
    ],
    "nostalgia_loop": [
        ["I", "IV", "vi", "V"],
        ["IV", "iv", "I", "I"],  # The iv-I is the tearjerker
    ],
    "unresolved_ending": [
        ["I", "IV", "V", "IV"],  # Never returns to I
        ["I", "V", "vi", "bVII"],  # Ends on borrowed bVII
    ],
}

# Genre-specific characteristics
GENRE_TEMPLATES = {
    "lo_fi_bedroom": {
        "progressions": ["I", "vi", "IV", "V", "I", "vi", "ii", "V"],
        "tempo_range": (70, 95),
        "characteristics": [
            "Sparse arrangement",
            "Room sound/tape hiss",
            "Slightly detuned instruments",
            "Imperfect timing (humanized)",
        ],
    },
    "emo_confessional": {
        "progressions": ["vi", "IV", "I", "V", "vi", "IV", "I", "iii"],
        "tempo_range": (80, 110),
        "characteristics": [
            "Dynamic contrast (quiet verse, loud chorus)",
            "Register breaks in vocals",
            "Acoustic to electric builds",
            "Lyrical specificity over abstraction",
        ],
    },
    "indie_folk": {
        "progressions": ["I", "IV", "I", "V", "vi", "IV", "V", "I"],
        "tempo_range": (90, 130),
        "characteristics": [
            "Fingerpicked acoustic guitar",
            "Sparse percussion or none",
            "Vocal harmonies",
            "Natural room reverb",
        ],
    },
    "post_rock": {
        "progressions": ["i", "bVI", "bIII", "bVII", "i", "bVI", "IV", "i"],
        "tempo_range": (60, 100),
        "characteristics": [
            "Long instrumental builds",
            "Tremolo picking",
            "Heavy use of delay/reverb",
            "Dynamic crescendos",
        ],
    },
}

# Song structure templates
STRUCTURE_TEMPLATES = {
    "standard": ["intro", "verse", "chorus", "verse", "chorus", "bridge", "chorus", "outro"],
    "verse_heavy": ["intro", "verse", "verse", "chorus", "verse", "chorus", "outro"],
    "minimal": ["intro", "verse", "chorus", "verse", "chorus"],
    "progressive": ["intro", "verse", "bridge", "verse", "chorus", "bridge", "outro"],
    "building": ["intro", "verse", "verse", "prechorus", "chorus", "verse", "prechorus", "chorus", "chorus", "outro"],
    "storytelling": ["verse", "verse", "verse", "chorus", "verse", "chorus", "outro"],
}

# Roman numeral to semitone offset from tonic
NUMERAL_TO_SEMITONE = {
    "I": 0, "i": 0,
    "bII": 1, "II": 2, "ii": 2,
    "bIII": 3, "III": 4, "iii": 4,
    "IV": 5, "iv": 5,
    "#IV": 6, "bV": 6,
    "V": 7, "v": 7,
    "bVI": 8, "VI": 9, "vi": 9,
    "bVII": 10, "VII": 11, "vii": 11,
}

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


@dataclass
class GeneratedSection:
    """A generated song section."""
    name: str
    bars: int
    progression: List[str]  # Roman numerals
    chords: List[str]  # Actual chord names
    energy: float  # 0.0-1.0
    notes: str  # Production/performance notes


@dataclass
class GeneratedSong:
    """A complete generated song structure."""
    title: str = "Untitled"
    key: str = "C"
    mode: str = "major"
    tempo_bpm: float = 120.0
    time_signature: Tuple[int, int] = (4, 4)
    
    sections: List[GeneratedSection] = field(default_factory=list)
    genre: str = ""
    mood: str = ""
    
    # Metadata
    total_bars: int = 0
    duration_estimate_seconds: float = 0.0
    
    def get_all_chords(self) -> List[str]:
        """Get flat list of all chords in order."""
        chords = []
        for section in self.sections:
            chords.extend(section.chords)
        return chords
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "title": self.title,
            "key": self.key,
            "mode": self.mode,
            "tempo_bpm": self.tempo_bpm,
            "time_signature": list(self.time_signature),
            "genre": self.genre,
            "mood": self.mood,
            "total_bars": self.total_bars,
            "duration_estimate_seconds": self.duration_estimate_seconds,
            "sections": [
                {
                    "name": s.name,
                    "bars": s.bars,
                    "progression": s.progression,
                    "chords": s.chords,
                    "energy": s.energy,
                    "notes": s.notes,
                }
                for s in self.sections
            ],
        }
    
    def __str__(self) -> str:
        lines = [
            f"=== {self.title} ===",
            f"Key: {self.key} {self.mode} | Tempo: {self.tempo_bpm} BPM | Genre: {self.genre}",
            f"Duration: ~{self.duration_estimate_seconds:.0f}s ({self.total_bars} bars)",
            "",
        ]
        
        for section in self.sections:
            lines.append(f"[{section.name.upper()}] ({section.bars} bars, energy: {section.energy:.1f})")
            lines.append(f"  {' | '.join(section.chords)}")
            if section.notes:
                lines.append(f"  → {section.notes}")
            lines.append("")
        
        return "\n".join(lines)


class SongGenerator:
    """
    Generate song structures, progressions, and arrangements.
    
    Usage:
        gen = SongGenerator()
        song = gen.generate(key="F", mood="bittersweet", genre="lo_fi_bedroom")
        print(song)
    """
    
    def __init__(self):
        self.progression_templates = PROGRESSION_TEMPLATES
        self.genre_templates = GENRE_TEMPLATES
        self.structure_templates = STRUCTURE_TEMPLATES
    
    def generate(
        self,
        key: str = "C",
        mode: str = "major",
        mood: Optional[str] = None,
        genre: Optional[str] = None,
        structure: Optional[str] = None,
        tempo: Optional[float] = None,
    ) -> GeneratedSong:
        """
        Generate a complete song structure.
        
        Args:
            key: Musical key (C, F#, Bb, etc.)
            mode: major or minor
            mood: Emotional mood (hopeful, melancholy, bittersweet, etc.)
            genre: Genre template (lo_fi_bedroom, emo_confessional, etc.)
            structure: Structure template name or None for random
            tempo: BPM or None for genre-appropriate default
        
        Returns:
            GeneratedSong with complete structure
        """
        # Determine tempo
        if tempo is None:
            if genre and genre in self.genre_templates:
                tempo_range = self.genre_templates[genre]["tempo_range"]
                tempo = random.uniform(tempo_range[0], tempo_range[1])
            else:
                tempo = random.uniform(90, 130)
        
        # Choose structure
        if structure is None:
            structure = random.choice(list(self.structure_templates.keys()))
        
        structure_sections = self.structure_templates.get(structure, self.structure_templates["standard"])
        
        # Get base progression for mood
        base_progression = self._get_progression_for_mood(mood)
        
        # Generate sections
        sections = []
        key_num = NOTE_NAMES.index(key.replace('b', '').replace('#', ''))
        if 'b' in key:
            key_num = (key_num - 1) % 12
        elif '#' in key:
            key_num = (key_num + 1) % 12
        
        section_counts = {}
        for section_name in structure_sections:
            section_counts[section_name] = section_counts.get(section_name, 0) + 1
            count = section_counts[section_name]
            
            # Get progression for this section type
            progression = self._get_section_progression(section_name, base_progression, mood)
            
            # Convert to actual chords
            chords = self._numerals_to_chords(progression, key_num, mode)
            
            # Determine section characteristics
            bars = self._get_section_bars(section_name)
            energy = self._get_section_energy(section_name)
            notes = self._get_section_notes(section_name, genre)
            
            display_name = section_name if count == 1 else f"{section_name} {count}"
            
            sections.append(GeneratedSection(
                name=display_name,
                bars=bars,
                progression=progression,
                chords=chords,
                energy=energy,
                notes=notes,
            ))
        
        # Calculate totals
        total_bars = sum(s.bars for s in sections)
        beats_per_bar = 4  # Assuming 4/4
        duration_seconds = (total_bars * beats_per_bar * 60) / tempo
        
        return GeneratedSong(
            title=self._generate_title(mood, genre),
            key=key,
            mode=mode,
            tempo_bpm=round(tempo, 1),
            sections=sections,
            genre=genre or "general",
            mood=mood or "neutral",
            total_bars=total_bars,
            duration_estimate_seconds=duration_seconds,
        )
    
    def _get_progression_for_mood(self, mood: Optional[str]) -> List[str]:
        """Get a progression template for the given mood."""
        if mood and mood in self.progression_templates:
            templates = self.progression_templates[mood]
            if isinstance(templates[0], list):
                return random.choice(templates)
            return templates
        
        # Default progression
        return ["I", "V", "vi", "IV"]
    
    def _get_section_progression(
        self,
        section_name: str,
        base_progression: List[str],
        mood: Optional[str],
    ) -> List[str]:
        """Get progression for a specific section type."""
        
        if section_name == "intro":
            # Simpler version, often just I or I-IV
            return base_progression[:2] if len(base_progression) >= 2 else ["I"]
        
        elif section_name == "verse":
            return base_progression
        
        elif section_name == "prechorus":
            # Build tension
            return ["IV", "V", "vi", "V"]
        
        elif section_name == "chorus":
            # Higher energy version or slight variation
            if mood == "grief_reveal" and len(base_progression) > 1:
                # Use the gut-punch progression
                return self.progression_templates["grief_reveal"][1]
            return base_progression
        
        elif section_name == "bridge":
            # Contrast - different progression
            if mood in ["melancholy", "grief_reveal"]:
                return ["bVI", "bVII", "I", "I"]
            return ["vi", "IV", "I", "V"]
        
        elif section_name == "outro":
            # Wind down, often repeating I or IV-I
            return ["IV", "I", "IV", "I"]
        
        return base_progression
    
    def _numerals_to_chords(
        self,
        progression: List[str],
        key_num: int,
        mode: str,
    ) -> List[str]:
        """Convert Roman numerals to actual chord names."""
        chords = []
        
        for numeral in progression:
            # Get semitone offset
            clean_numeral = numeral.replace("7", "").replace("maj", "").replace("dim", "")
            offset = NUMERAL_TO_SEMITONE.get(clean_numeral, 0)
            
            root_num = (key_num + offset) % 12
            root_name = NOTE_NAMES[root_num]
            
            # Determine quality
            if numeral.islower() or numeral.startswith("b") and numeral[1:].islower():
                quality = "m"
            elif "dim" in numeral:
                quality = "dim"
            else:
                quality = ""
            
            # Add extensions
            if "7" in numeral:
                if "maj7" in numeral:
                    quality += "maj7"
                else:
                    quality += "7"
            
            chords.append(f"{root_name}{quality}")
        
        return chords
    
    def _get_section_bars(self, section_name: str) -> int:
        """Get typical bar count for section type."""
        defaults = {
            "intro": 4,
            "verse": 8,
            "prechorus": 4,
            "chorus": 8,
            "bridge": 8,
            "outro": 4,
        }
        return defaults.get(section_name, 8)
    
    def _get_section_energy(self, section_name: str) -> float:
        """Get typical energy level for section type."""
        defaults = {
            "intro": 0.3,
            "verse": 0.5,
            "prechorus": 0.7,
            "chorus": 0.9,
            "bridge": 0.6,
            "outro": 0.4,
        }
        return defaults.get(section_name, 0.5)
    
    def _get_section_notes(self, section_name: str, genre: Optional[str]) -> str:
        """Get production/performance notes for section."""
        genre_notes = {
            "lo_fi_bedroom": {
                "intro": "Sparse, maybe just guitar or keys with room sound",
                "verse": "Intimate, close mic'd vocals, minimal arrangement",
                "chorus": "Add subtle layers, keep it restrained",
                "bridge": "Strip back or add unexpected texture",
                "outro": "Let it breathe, fade naturally",
            },
            "emo_confessional": {
                "intro": "Set the scene - acoustic, vulnerable",
                "verse": "Build intensity through dynamics, not layers",
                "chorus": "Let it explode - full band, register breaks",
                "bridge": "The quiet before the final storm",
                "outro": "Catharsis or devastation, your choice",
            },
        }
        
        if genre and genre in genre_notes:
            return genre_notes[genre].get(section_name, "")
        
        return ""
    
    def _generate_title(self, mood: Optional[str], genre: Optional[str]) -> str:
        """Generate a placeholder title."""
        titles = {
            "grief_reveal": ["The Weight of Silence", "What I Found", "Still Frame"],
            "bittersweet": ["Golden Hour", "Almost Home", "Paper Hearts"],
            "melancholy": ["Empty Rooms", "Winter Light", "Fading"],
            "hopeful": ["New Dawn", "Rising", "Open Sky"],
        }
        
        if mood and mood in titles:
            return random.choice(titles[mood])
        
        return "Untitled"
    
    def suggest_progression(
        self,
        mood: str,
        key: str = "C",
        mode: str = "major",
        bars: int = 4,
    ) -> Dict:
        """
        Suggest a chord progression for a given mood.
        
        Args:
            mood: Target mood
            key: Musical key
            mode: major or minor
            bars: Number of bars
        
        Returns:
            Dict with progression info
        """
        progression = self._get_progression_for_mood(mood)
        
        # Adjust length
        while len(progression) < bars:
            progression = progression + progression
        progression = progression[:bars]
        
        key_num = NOTE_NAMES.index(key) if key in NOTE_NAMES else 0
        chords = self._numerals_to_chords(progression, key_num, mode)
        
        return {
            "mood": mood,
            "key": key,
            "mode": mode,
            "numerals": progression,
            "chords": chords,
            "bars": bars,
        }
