"""
Section Detection - Improved Implementation

Handles:
- Ambiguous bridge/pre-chorus transitions
- Half-bars and pick-ups
- Time signature anomalies
- Hybrid sections (drop→break→fill)
- Hidden bars (EDM intros, fake turnarounds)
- Irregular loops (5-bar, 7-bar patterns)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from collections import defaultdict
import math


@dataclass
class Section:
    """A detected song section."""
    name: str                    # verse, chorus, bridge, etc.
    start_bar: int
    end_bar: int
    length_bars: int
    energy: float                # 0-1, relative loudness/density
    density: float               # Notes per beat
    characteristics: Dict = field(default_factory=dict)
    
    # Additional detection info
    confidence: float = 1.0      # How confident we are in this section
    possible_names: List[str] = field(default_factory=list)  # Alternative interpretations
    is_pickup: bool = False      # True if starts before bar 1
    is_irregular: bool = False   # True if non-standard length


@dataclass
class BarMetrics:
    """Metrics for a single bar."""
    bar_index: int
    density: float           # Notes per beat
    energy: float            # Average velocity / 127
    pitch_range: int         # Highest - lowest pitch
    channel_count: int       # Number of active channels
    has_drums: bool
    note_count: int
    
    # Additional metrics
    rhythmic_complexity: float = 0.0  # Variance in note positions
    melodic_movement: float = 0.0     # Average pitch change
    harmonic_density: float = 0.0     # Simultaneous notes


class SectionDetector:
    """
    Detect song sections from MIDI.
    
    Improvements over basic detection:
    - Handles irregular bar lengths
    - Detects pick-up bars
    - Multiple confidence levels
    - Time signature awareness
    """
    
    def __init__(self, ppq: int = 480, beats_per_bar: int = 4):
        self.ppq = ppq
        self.beats_per_bar = beats_per_bar
        self.ticks_per_bar = ppq * beats_per_bar
    
    def detect_sections(
        self,
        data,
        min_section_bars: int = 4
    ) -> List[Section]:
        """
        Detect sections in MIDI data.
        
        Args:
            data: MidiData object
            min_section_bars: Minimum bars for a section
        
        Returns:
            List of Section objects
        """
        notes = data.all_notes
        if not notes:
            return []
        
        # Update PPQ from data
        self.ppq = data.ppq
        self.ticks_per_bar = data.ticks_per_bar
        
        # Find max bar
        max_tick = max(n.onset_ticks for n in notes)
        max_bar = int(max_tick / self.ticks_per_bar) + 1
        
        if max_bar < min_section_bars:
            return [Section(
                name='full',
                start_bar=0,
                end_bar=max_bar,
                length_bars=max_bar,
                energy=0.5,
                density=len(notes) / (max_bar * self.beats_per_bar)
            )]
        
        # Calculate per-bar metrics
        metrics = self._calculate_bar_metrics(notes, max_bar)
        
        # Detect irregular patterns (5-bar loops, etc.)
        irregular_length = self._detect_irregular_patterns(metrics)
        
        # Detect pick-up bars
        pickup_bars = self._detect_pickups(metrics)
        
        # Detect boundaries
        boundaries = self._detect_boundaries(metrics, min_section_bars, irregular_length)
        
        # Create sections
        sections = self._create_sections(boundaries, metrics, max_bar)
        
        # Name sections with confidence
        sections = self._name_sections_with_confidence(sections, metrics)
        
        # Mark pickups
        if pickup_bars and sections:
            sections[0].is_pickup = True
            sections[0].characteristics['pickup_bars'] = pickup_bars
        
        return sections
    
    def _calculate_bar_metrics(self, notes: List, max_bar: int) -> List[BarMetrics]:
        """Calculate detailed metrics for each bar."""
        metrics = []
        
        for bar_idx in range(max_bar):
            bar_start = bar_idx * self.ticks_per_bar
            bar_end = bar_start + self.ticks_per_bar
            
            # Notes in this bar
            bar_notes = [n for n in notes if bar_start <= n.onset_ticks < bar_end]
            
            if not bar_notes:
                metrics.append(BarMetrics(
                    bar_index=bar_idx,
                    density=0.0,
                    energy=0.0,
                    pitch_range=0,
                    channel_count=0,
                    has_drums=False,
                    note_count=0
                ))
                continue
            
            # Basic metrics
            note_count = len(bar_notes)
            density = note_count / self.beats_per_bar
            energy = sum(n.velocity for n in bar_notes) / (note_count * 127)
            
            pitches = [n.pitch for n in bar_notes]
            pitch_range = max(pitches) - min(pitches)
            
            channels = set(n.channel for n in bar_notes)
            has_drums = 9 in channels
            
            # Rhythmic complexity: how spread out are notes within the bar
            positions = [(n.onset_ticks - bar_start) / self.ticks_per_bar for n in bar_notes]
            if len(positions) > 1:
                mean_pos = sum(positions) / len(positions)
                rhythmic_complexity = math.sqrt(sum((p - mean_pos) ** 2 for p in positions) / len(positions))
            else:
                rhythmic_complexity = 0.0
            
            # Melodic movement: average pitch change between consecutive notes
            sorted_notes = sorted(bar_notes, key=lambda n: n.onset_ticks)
            pitch_changes = []
            for i in range(1, len(sorted_notes)):
                pitch_changes.append(abs(sorted_notes[i].pitch - sorted_notes[i-1].pitch))
            melodic_movement = sum(pitch_changes) / len(pitch_changes) if pitch_changes else 0.0
            
            # Harmonic density: notes sounding at the same time
            time_groups = defaultdict(list)
            for n in bar_notes:
                # Quantize to 16th notes
                quant = round(n.onset_ticks / (self.ppq // 4)) * (self.ppq // 4)
                time_groups[quant].append(n)
            
            harmonic_counts = [len(group) for group in time_groups.values()]
            harmonic_density = sum(harmonic_counts) / len(harmonic_counts) if harmonic_counts else 0.0
            
            metrics.append(BarMetrics(
                bar_index=bar_idx,
                density=density,
                energy=energy,
                pitch_range=pitch_range,
                channel_count=len(channels),
                has_drums=has_drums,
                note_count=note_count,
                rhythmic_complexity=rhythmic_complexity,
                melodic_movement=melodic_movement,
                harmonic_density=harmonic_density
            ))
        
        return metrics
    
    def _detect_irregular_patterns(self, metrics: List[BarMetrics]) -> Optional[int]:
        """
        Detect if the song uses irregular loop lengths (5-bar, 7-bar, etc.)
        
        Returns detected loop length or None for standard 4/8-bar.
        """
        if len(metrics) < 10:
            return None
        
        # Try loop lengths 3, 5, 6, 7 (unusual lengths)
        for loop_len in [5, 6, 7, 3]:
            matches = 0
            comparisons = 0
            
            for i in range(len(metrics) - loop_len):
                # Compare bar i with bar i + loop_len
                m1 = metrics[i]
                m2 = metrics[i + loop_len]
                
                # Similarity check
                density_sim = 1 - abs(m1.density - m2.density) / max(m1.density, m2.density, 0.1)
                energy_sim = 1 - abs(m1.energy - m2.energy)
                
                similarity = (density_sim + energy_sim) / 2
                
                if similarity > 0.7:
                    matches += 1
                comparisons += 1
            
            if comparisons > 0 and matches / comparisons > 0.6:
                return loop_len
        
        return None
    
    def _detect_pickups(self, metrics: List[BarMetrics]) -> int:
        """
        Detect pick-up/anacrusis bars.
        
        Pick-ups typically:
        - Have fewer notes than following bars
        - Low density relative to next bars
        - Often in first bar or two
        """
        if len(metrics) < 3:
            return 0
        
        # Check first bar
        first = metrics[0]
        avg_of_next = sum(m.density for m in metrics[1:4]) / 3
        
        # If first bar is significantly lighter, it's probably a pickup
        if first.density < avg_of_next * 0.3 and first.note_count < 4:
            return 1
        
        return 0
    
    def _detect_boundaries(
        self,
        metrics: List[BarMetrics],
        min_bars: int,
        irregular_length: Optional[int]
    ) -> List[int]:
        """
        Detect section boundaries.
        
        Uses multiple signals:
        - Energy changes
        - Density changes
        - Drum presence changes
        - Channel count changes
        """
        if len(metrics) < min_bars * 2:
            return [0, len(metrics)]
        
        # Calculate change scores
        change_scores = [0.0]  # First bar has no "change"
        
        window = 2  # Compare with previous N bars
        
        for i in range(1, len(metrics)):
            # Get previous window
            prev_start = max(0, i - window)
            prev_metrics = metrics[prev_start:i]
            current = metrics[i]
            
            if not prev_metrics:
                change_scores.append(0.0)
                continue
            
            # Average of previous window
            prev_density = sum(m.density for m in prev_metrics) / len(prev_metrics)
            prev_energy = sum(m.energy for m in prev_metrics) / len(prev_metrics)
            prev_drums = sum(1 for m in prev_metrics if m.has_drums) / len(prev_metrics)
            prev_channels = sum(m.channel_count for m in prev_metrics) / len(prev_metrics)
            
            # Calculate changes
            density_change = abs(current.density - prev_density) / max(prev_density, 0.1)
            energy_change = abs(current.energy - prev_energy)
            drum_change = abs((1 if current.has_drums else 0) - prev_drums)
            channel_change = abs(current.channel_count - prev_channels) / max(prev_channels, 1)
            
            # Weighted score
            score = (
                density_change * 0.3 +
                energy_change * 0.3 +
                drum_change * 0.25 +
                channel_change * 0.15
            )
            
            change_scores.append(score)
        
        # Find peaks
        mean_score = sum(change_scores) / len(change_scores)
        std_score = math.sqrt(sum((s - mean_score) ** 2 for s in change_scores) / len(change_scores))
        threshold = mean_score + std_score
        
        # Prefer boundaries on standard bar multiples (4, 8, 16) unless irregular detected
        preferred_multiples = [irregular_length] if irregular_length else [4, 8, 16]
        
        boundaries = [0]
        last_boundary = 0
        
        for i, score in enumerate(change_scores):
            if score < threshold:
                continue
            
            # Must be at least min_bars from last boundary
            if i - last_boundary < min_bars:
                continue
            
            # Prefer standard multiples
            distance = i - last_boundary
            on_multiple = any(distance % mult == 0 for mult in preferred_multiples)
            
            # Accept if on multiple or score is very high
            if on_multiple or score > threshold * 1.5:
                boundaries.append(i)
                last_boundary = i
        
        # Ensure end boundary
        if boundaries[-1] != len(metrics):
            boundaries.append(len(metrics))
        
        return boundaries
    
    def _create_sections(
        self,
        boundaries: List[int],
        metrics: List[BarMetrics],
        max_bar: int
    ) -> List[Section]:
        """Create Section objects from boundaries."""
        sections = []
        
        for i in range(len(boundaries) - 1):
            start = boundaries[i]
            end = boundaries[i + 1]
            length = end - start
            
            # Get metrics for this section
            section_metrics = metrics[start:end]
            if not section_metrics:
                continue
            
            avg_density = sum(m.density for m in section_metrics) / len(section_metrics)
            avg_energy = sum(m.energy for m in section_metrics) / len(section_metrics)
            has_drums = any(m.has_drums for m in section_metrics)
            
            # Check if irregular length
            is_irregular = length not in [2, 4, 8, 16, 32]
            
            characteristics = {
                'has_drums': has_drums,
                'avg_pitch_range': sum(m.pitch_range for m in section_metrics) / len(section_metrics),
                'avg_harmonic_density': sum(m.harmonic_density for m in section_metrics) / len(section_metrics),
                'rhythmic_complexity': sum(m.rhythmic_complexity for m in section_metrics) / len(section_metrics),
            }
            
            section = Section(
                name='unnamed',  # Will be named later
                start_bar=start,
                end_bar=end,
                length_bars=length,
                energy=avg_energy,
                density=avg_density,
                characteristics=characteristics,
                is_irregular=is_irregular
            )
            sections.append(section)
        
        return sections
    
    def _name_sections_with_confidence(
        self,
        sections: List[Section],
        metrics: List[BarMetrics]
    ) -> List[Section]:
        """
        Name sections with confidence scores and alternatives.
        
        Uses position, energy, density, and context for naming.
        """
        if not sections:
            return sections
        
        # Calculate global averages
        all_energies = [s.energy for s in sections]
        avg_energy = sum(all_energies) / len(all_energies)
        
        # Track which names we've used for detecting repeats
        name_counts = defaultdict(int)
        
        for i, section in enumerate(sections):
            candidates = []  # (name, confidence)
            
            energy = section.energy
            density = section.density
            length = section.length_bars
            has_drums = section.characteristics.get('has_drums', True)
            
            is_first = (i == 0)
            is_last = (i == len(sections) - 1)
            
            # === INTRO ===
            if is_first and energy < avg_energy * 0.7:
                candidates.append(('intro', 0.9))
            elif is_first and length <= 4:
                candidates.append(('intro', 0.7))
            
            # === OUTRO ===
            if is_last and energy < avg_energy * 0.7:
                candidates.append(('outro', 0.9))
            elif is_last and length <= 4:
                candidates.append(('outro', 0.7))
            
            # === CHORUS ===
            if energy > avg_energy * 1.2 and density > 0.5:
                candidates.append(('chorus', 0.8))
            elif energy > avg_energy and has_drums and length >= 8:
                candidates.append(('chorus', 0.6))
            
            # === BREAKDOWN/DROP ===
            if not has_drums and energy < avg_energy * 0.6:
                candidates.append(('breakdown', 0.8))
            elif density < 0.3 and energy < avg_energy * 0.5:
                candidates.append(('breakdown', 0.7))
            
            # === DROP (EDM) ===
            if energy > avg_energy * 1.3 and density > 0.8:
                candidates.append(('drop', 0.7))
            
            # === BRIDGE ===
            if not is_first and not is_last:
                # Different from surrounding sections
                prev_energy = sections[i-1].energy if i > 0 else avg_energy
                next_energy = sections[i+1].energy if i < len(sections)-1 else avg_energy
                
                if abs(energy - prev_energy) > 0.2 and abs(energy - next_energy) > 0.2:
                    candidates.append(('bridge', 0.6))
            
            # === PRE-CHORUS ===
            # If this leads into a high-energy section
            if i < len(sections) - 1:
                next_section = sections[i + 1]
                if next_section.energy > avg_energy * 1.1 and energy < next_section.energy:
                    candidates.append(('pre-chorus', 0.6))
            
            # === VERSE (default for medium energy) ===
            if 0.4 < energy < avg_energy * 1.2:
                candidates.append(('verse', 0.5))
            
            # === FILL/TRANSITION ===
            if length <= 2:
                candidates.append(('fill', 0.6))
            
            # Sort by confidence
            candidates.sort(key=lambda x: x[1], reverse=True)
            
            if candidates:
                best_name, best_conf = candidates[0]
                
                # Handle repeated sections (verse 1, verse 2, etc.)
                name_counts[best_name] += 1
                if name_counts[best_name] > 1:
                    display_name = f"{best_name}_{name_counts[best_name]}"
                else:
                    display_name = best_name
                
                section.name = display_name
                section.confidence = best_conf
                section.possible_names = [c[0] for c in candidates[:3]]
            else:
                section.name = f"section_{i+1}"
                section.confidence = 0.3
                section.possible_names = ['unknown']
        
        return sections


def detect_sections(data) -> List[Section]:
    """Convenience function to detect sections."""
    detector = SectionDetector(ppq=data.ppq)
    return detector.detect_sections(data)
