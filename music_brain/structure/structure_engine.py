"""
Structural Architect - Song Form Generation
============================================

Generates song structures based on narrative archetypes.
Outputs a timeline of bar-by-bar parameters for:
- Velocity/energy targets
- Rhythmic chaos (entropy)
- Harmonic density

This integrates with the tension curve module for emotional contour.
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class Section:
    """Definition of a song section with its characteristic parameters."""
    name: str
    bars: int
    energy: float       # 0.0-1.0 (maps to velocity/volume)
    entropy: float      # 0.0-1.0 (rhythmic chaos/humanization)
    harmonic_load: float  # 0.0-1.0 (chord complexity)


class StructuralArchitect:
    """
    Generates song forms based on narrative archetypes.

    Each archetype is a sequence of section names that get expanded
    into bar-by-bar parameters for the renderer.
    """

    # Song form archetypes
    FORMS: Dict[str, List[str]] = {
        "pop_standard": [
            "Intro", "Verse", "Chorus", "Verse", "Chorus",
            "Bridge", "Chorus", "Outro"
        ],
        "electronic_build": [
            "Intro", "Build_A", "Build_B", "Drop", "Breakdown",
            "Build_B", "Drop", "Outro"
        ],
        "punk_assault": [
            "Intro", "Chorus", "Verse", "Chorus", "Bridge",
            "Chorus", "End"
        ],
        "ballad": [
            "Intro", "Verse", "Verse", "Chorus", "Verse",
            "Chorus", "Bridge", "Chorus", "Outro"
        ],
        "ambient_drift": [
            "Intro", "Build_A", "Plateau", "Build_B", "Plateau",
            "Breakdown", "Outro"
        ],
        "minimal_loop": [
            "Intro", "Loop_A", "Loop_B", "Loop_A", "Outro"
        ],
    }

    # Section definitions with default parameters
    SECTION_DEFINITIONS: Dict[str, Section] = {
        # Standard sections
        "Intro":      Section("Intro", 8, 0.4, 0.1, 0.2),
        "Verse":      Section("Verse", 16, 0.6, 0.2, 0.3),
        "Chorus":     Section("Chorus", 16, 0.9, 0.1, 0.4),
        "Bridge":     Section("Bridge", 12, 0.5, 0.9, 0.9),
        "Outro":      Section("Outro", 8, 0.4, 0.1, 0.1),
        "End":        Section("End", 4, 1.0, 0.0, 1.0),

        # Electronic sections
        "Build_A":    Section("Build", 16, 0.7, 0.3, 0.5),
        "Build_B":    Section("Pre-Drop", 8, 0.8, 0.8, 0.7),
        "Drop":       Section("Drop", 16, 1.0, 0.2, 0.6),
        "Breakdown":  Section("Breakdown", 8, 0.3, 0.1, 0.8),

        # Ambient sections
        "Plateau":    Section("Plateau", 16, 0.5, 0.3, 0.4),
        "Loop_A":     Section("Loop A", 16, 0.6, 0.2, 0.3),
        "Loop_B":     Section("Loop B", 16, 0.7, 0.3, 0.4),
    }

    def __init__(self, bpm: int = 100):
        self.bpm = bpm

    def get_form_for_mood(self, mood: str) -> str:
        """
        Select appropriate form archetype based on detected mood.

        Args:
            mood: Primary affect from therapy session

        Returns:
            Form archetype name
        """
        mood_to_form = {
            "rage": "punk_assault",
            "defiance": "punk_assault",
            "fear": "electronic_build",
            "grief": "ballad",
            "dissociation": "ambient_drift",
            "awe": "ambient_drift",
            "nostalgia": "ballad",
            "tenderness": "ballad",
            "confusion": "electronic_build",
            "neutral": "pop_standard",
        }
        return mood_to_form.get(mood, "pop_standard")

    def generate_map(
        self,
        archetype: str = "pop_standard",
        total_bars: Optional[int] = None
    ) -> List[Dict]:
        """
        Generate a bar-by-bar structural map for the song.

        Args:
            archetype: Form archetype name
            total_bars: Optional override for total song length

        Returns:
            List of dicts with bar-level parameters:
            - bar_index: int
            - section: str (section name)
            - velocity_target: int (0-127)
            - jitter_sigma: float (timing chaos)
            - harmonic_density: float (0.0-1.0)
        """
        form_list = self.FORMS.get(archetype, self.FORMS["pop_standard"])
        timeline: List[Dict] = []
        current_bar = 0

        for section_name in form_list:
            sec_def = self.SECTION_DEFINITIONS.get(
                section_name,
                self.SECTION_DEFINITIONS["Verse"]
            )

            for i in range(sec_def.bars):
                # Calculate local position within section (0.0 to 1.0)
                local_progress = i / sec_def.bars if sec_def.bars > 0 else 0

                # Dynamic modulation based on section type
                velocity_mod = sec_def.energy
                chaos_mod = sec_def.entropy

                # Section-specific dynamics
                if section_name == "Verse":
                    # Verses build slightly
                    velocity_mod += (local_progress * 0.1)
                elif section_name == "Bridge":
                    # Bridges get progressively chaotic
                    chaos_mod += (local_progress * 0.3)
                elif section_name in ["Build_A", "Build_B"]:
                    # Builds increase energy
                    velocity_mod += (local_progress * 0.2)
                elif section_name == "Breakdown":
                    # Breakdowns pull back then build
                    velocity_mod = 0.3 + (local_progress * 0.4)
                elif section_name == "Drop":
                    # Drops start strong, slight decay
                    velocity_mod = 1.0 - (local_progress * 0.1)

                # Clamp values
                velocity_mod = max(0.0, min(1.0, velocity_mod))
                chaos_mod = max(0.0, min(1.0, chaos_mod))

                timeline.append({
                    "bar_index": current_bar,
                    "section": section_name,
                    "velocity_target": int(velocity_mod * 100) + 20,  # 20-120 range
                    "jitter_sigma": chaos_mod,
                    "harmonic_density": sec_def.harmonic_load,
                })
                current_bar += 1

        # If total_bars specified, trim or extend
        if total_bars is not None:
            if len(timeline) > total_bars:
                timeline = timeline[:total_bars]
            elif len(timeline) < total_bars:
                # Extend with last section parameters
                last = timeline[-1] if timeline else {
                    "bar_index": 0,
                    "section": "Outro",
                    "velocity_target": 60,
                    "jitter_sigma": 0.1,
                    "harmonic_density": 0.2,
                }
                while len(timeline) < total_bars:
                    new_bar = last.copy()
                    new_bar["bar_index"] = len(timeline)
                    timeline.append(new_bar)

        return timeline

    def get_section_boundaries(self, timeline: List[Dict]) -> List[Dict]:
        """
        Extract section boundaries from a timeline for DAW markers.

        Returns:
            List of {name, start_bar, end_bar} dicts
        """
        if not timeline:
            return []

        boundaries = []
        current_section = timeline[0]["section"]
        start_bar = 0

        for item in timeline:
            if item["section"] != current_section:
                boundaries.append({
                    "name": current_section,
                    "start_bar": start_bar,
                    "end_bar": item["bar_index"] - 1,
                })
                current_section = item["section"]
                start_bar = item["bar_index"]

        # Add final section
        boundaries.append({
            "name": current_section,
            "start_bar": start_bar,
            "end_bar": timeline[-1]["bar_index"],
        })

        return boundaries


def generate_structure_for_plan(mood: str, length_bars: int, bpm: int = 100) -> List[Dict]:
    """
    Convenience function to generate structure from mood and length.

    Args:
        mood: Primary affect
        length_bars: Total song length in bars
        bpm: Tempo

    Returns:
        Structure timeline
    """
    architect = StructuralArchitect(bpm)
    archetype = architect.get_form_for_mood(mood)
    return architect.generate_map(archetype, total_bars=length_bars)
