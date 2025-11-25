"""
Section Detection - Identify song sections from MIDI.

Detects:
- Verse, Chorus, Bridge, etc.
- Energy levels
- Transition points
- Repetition patterns
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from pathlib import Path
from enum import Enum

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False


class SectionType(Enum):
    INTRO = "intro"
    VERSE = "verse"
    PRECHORUS = "pre-chorus"
    CHORUS = "chorus"
    BRIDGE = "bridge"
    OUTRO = "outro"
    SOLO = "solo"
    BREAKDOWN = "breakdown"
    BUILDUP = "buildup"
    DROP = "drop"
    UNKNOWN = "unknown"


@dataclass
class Section:
    """Represents a detected song section."""
    name: str
    section_type: SectionType
    start_bar: int
    end_bar: int
    start_tick: int = 0
    end_tick: int = 0
    
    # Analysis metrics
    energy: float = 0.5  # 0.0-1.0
    note_density: float = 0.0  # Notes per beat
    avg_velocity: float = 64.0
    pitch_range: Tuple[int, int] = (0, 127)
    
    # Pattern info
    is_repeated: bool = False
    similar_to: Optional[int] = None  # Index of similar section
    
    @property
    def length_bars(self) -> int:
        return self.end_bar - self.start_bar


@dataclass
class SectionAnalysis:
    """Complete section analysis for a track."""
    sections: List[Section]
    total_bars: int
    ppq: int
    tempo_bpm: float
    time_signature: Tuple[int, int]
    
    def get_section_at_bar(self, bar: int) -> Optional[Section]:
        """Get section containing given bar."""
        for section in self.sections:
            if section.start_bar <= bar < section.end_bar:
                return section
        return None


def calculate_energy(
    notes: List[Tuple[int, int, int]],  # (tick, pitch, velocity)
    start_tick: int,
    end_tick: int,
    ppq: int,
) -> dict:
    """
    Calculate energy metrics for a section.
    
    Returns dict with energy, density, avg_velocity, pitch_range.
    """
    section_notes = [(t, p, v) for t, p, v in notes if start_tick <= t < end_tick]
    
    if not section_notes:
        return {
            "energy": 0.0,
            "density": 0.0,
            "avg_velocity": 0,
            "pitch_range": (60, 60),
        }
    
    # Note density (notes per beat)
    duration_beats = (end_tick - start_tick) / ppq
    density = len(section_notes) / max(duration_beats, 1)
    
    # Average velocity
    avg_velocity = sum(v for _, _, v in section_notes) / len(section_notes)
    
    # Pitch range
    pitches = [p for _, p, _ in section_notes]
    pitch_range = (min(pitches), max(pitches))
    
    # Combined energy score
    # Higher density + higher velocity + wider range = more energy
    density_factor = min(density / 8.0, 1.0)  # Normalize to ~8 notes/beat max
    velocity_factor = avg_velocity / 127.0
    range_factor = (pitch_range[1] - pitch_range[0]) / 48.0  # Normalize to 4 octaves
    
    energy = (density_factor * 0.4 + velocity_factor * 0.4 + range_factor * 0.2)
    
    return {
        "energy": min(energy, 1.0),
        "density": density,
        "avg_velocity": avg_velocity,
        "pitch_range": pitch_range,
    }


def detect_section_boundaries(
    energy_curve: List[float],
    threshold: float = 0.15,
) -> List[int]:
    """
    Detect section boundaries from energy curve.
    
    Returns list of bar indices where sections change.
    """
    if len(energy_curve) < 4:
        return [0]
    
    boundaries = [0]
    
    for i in range(1, len(energy_curve)):
        diff = abs(energy_curve[i] - energy_curve[i-1])
        if diff > threshold:
            boundaries.append(i)
    
    return boundaries


def classify_section(
    energy: float,
    position_ratio: float,  # 0.0 = start, 1.0 = end of song
    length_bars: int,
    prev_section: Optional[Section] = None,
) -> SectionType:
    """
    Classify section type based on metrics and position.
    """
    # Intro detection
    if position_ratio < 0.1:
        if energy < 0.3:
            return SectionType.INTRO
    
    # Outro detection  
    if position_ratio > 0.85:
        if energy < 0.4 or (prev_section and energy < prev_section.energy - 0.2):
            return SectionType.OUTRO
    
    # High energy = chorus/drop
    if energy > 0.7:
        return SectionType.CHORUS
    
    # Medium-high with buildup
    if energy > 0.5:
        if prev_section and prev_section.energy < energy - 0.2:
            return SectionType.CHORUS
        return SectionType.PRECHORUS
    
    # Low energy
    if energy < 0.35:
        return SectionType.BREAKDOWN
    
    # Default to verse
    return SectionType.VERSE


def detect_sections(
    midi_path: str,
    min_section_bars: int = 4,
    analysis_resolution: int = 2,  # Analyze every N bars
) -> List[Section]:
    """
    Detect sections in a MIDI file.
    
    Args:
        midi_path: Path to MIDI file
        min_section_bars: Minimum section length
        analysis_resolution: Bar resolution for energy analysis
    
    Returns:
        List of detected sections
    """
    if not MIDO_AVAILABLE:
        raise ImportError("mido package required. Install with: pip install mido")
    
    midi_path = Path(midi_path)
    if not midi_path.exists():
        raise FileNotFoundError(f"MIDI file not found: {midi_path}")
    
    mid = mido.MidiFile(str(midi_path))
    ppq = mid.ticks_per_beat
    
    # Get tempo and time signature
    tempo_bpm = 120.0
    time_sig = (4, 4)
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                tempo_bpm = mido.tempo2bpm(msg.tempo)
            elif msg.type == 'time_signature':
                time_sig = (msg.numerator, msg.denominator)
    
    ticks_per_bar = ppq * time_sig[0]
    
    # Collect all notes
    all_notes = []
    for track in mid.tracks:
        current_tick = 0
        for msg in track:
            current_tick += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                all_notes.append((current_tick, msg.note, msg.velocity))
    
    if not all_notes:
        return []
    
    # Calculate total length
    max_tick = max(t for t, _, _ in all_notes)
    total_bars = (max_tick // ticks_per_bar) + 1
    
    # Calculate energy for each analysis window
    energy_curve = []
    for bar in range(0, total_bars, analysis_resolution):
        start_tick = bar * ticks_per_bar
        end_tick = (bar + analysis_resolution) * ticks_per_bar
        metrics = calculate_energy(all_notes, start_tick, end_tick, ppq)
        energy_curve.append(metrics["energy"])
    
    # Detect boundaries
    boundary_indices = detect_section_boundaries(energy_curve)
    
    # Convert to bar boundaries
    bar_boundaries = [i * analysis_resolution for i in boundary_indices]
    bar_boundaries.append(total_bars)
    
    # Merge short sections
    merged_boundaries = [bar_boundaries[0]]
    for boundary in bar_boundaries[1:]:
        if boundary - merged_boundaries[-1] >= min_section_bars:
            merged_boundaries.append(boundary)
        elif merged_boundaries:
            merged_boundaries[-1] = boundary
    
    if merged_boundaries[-1] != total_bars:
        merged_boundaries.append(total_bars)
    
    # Build sections
    sections = []
    section_counts = {}  # Track section type counts for naming
    
    for i in range(len(merged_boundaries) - 1):
        start_bar = merged_boundaries[i]
        end_bar = merged_boundaries[i + 1]
        
        start_tick = start_bar * ticks_per_bar
        end_tick = end_bar * ticks_per_bar
        
        # Calculate section metrics
        metrics = calculate_energy(all_notes, start_tick, end_tick, ppq)
        
        # Classify section
        position_ratio = (start_bar + end_bar) / 2 / total_bars
        prev_section = sections[-1] if sections else None
        section_type = classify_section(
            metrics["energy"],
            position_ratio,
            end_bar - start_bar,
            prev_section,
        )
        
        # Generate name with count
        type_name = section_type.value
        section_counts[type_name] = section_counts.get(type_name, 0) + 1
        count = section_counts[type_name]
        name = f"{type_name.title()} {count}" if count > 1 else type_name.title()
        
        section = Section(
            name=name,
            section_type=section_type,
            start_bar=start_bar,
            end_bar=end_bar,
            start_tick=start_tick,
            end_tick=end_tick,
            energy=metrics["energy"],
            note_density=metrics["density"],
            avg_velocity=metrics["avg_velocity"],
            pitch_range=metrics["pitch_range"],
        )
        sections.append(section)
    
    # Detect repeated sections
    for i, section in enumerate(sections):
        for j, other in enumerate(sections[:i]):
            if abs(section.energy - other.energy) < 0.1:
                if section.section_type == other.section_type:
                    if abs(section.length_bars - other.length_bars) <= 2:
                        section.is_repeated = True
                        section.similar_to = j
                        break
    
    return sections
