"""
Advanced Drum Analysis

Implements:
- Snare bounce/flam detection
- Hi-hat alternation (handedness)
- Rudiment pattern detection
- Drum technique signatures
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import math

from ..utils.ppq import STANDARD_PPQ, ticks_to_ms
from ..utils.instruments import get_drum_category, is_drum_channel


# Timing thresholds (in ms at 120 BPM)
FLAM_THRESHOLD_MS = 30          # Two hits within 30ms = flam
BUZZ_THRESHOLD_MS = 50          # Rapid hits within 50ms = buzz/roll
DRAG_THRESHOLD_MS = 80          # Grace notes within 80ms = drag
ALTERNATION_WINDOW_MS = 200     # Window for detecting hand alternation


@dataclass
class SnareBounceSignature:
    """Snare technique analysis."""
    flam_count: int = 0              # Two-note flams
    buzz_roll_regions: List[Tuple[int, int]] = field(default_factory=list)  # (start_tick, end_tick)
    drag_count: int = 0              # Drag rudiments (grace notes before main hit)
    avg_flam_gap_ms: float = 0.0     # Average time between flam notes
    avg_flam_velocity_ratio: float = 0.0  # Grace note velocity / main note velocity
    bounce_decay_rate: float = 0.0   # How fast velocity decays in bounces
    total_bounces: int = 0
    
    # Technique indicators
    has_buzz_rolls: bool = False
    has_ghost_drags: bool = False
    primary_technique: str = "standard"  # standard, jazzy, heavy, technical


@dataclass
class HiHatAlternation:
    """Hi-hat handedness analysis."""
    is_alternating: bool = False
    confidence: float = 0.0
    dominant_hand: str = "unknown"   # right, left, unknown
    
    # Velocity patterns
    downbeat_avg_velocity: float = 0.0
    upbeat_avg_velocity: float = 0.0
    velocity_alternation_ratio: float = 0.0  # downbeat/upbeat ratio
    
    # Timing patterns
    downbeat_avg_offset: float = 0.0  # Timing offset from grid
    upbeat_avg_offset: float = 0.0
    
    # Pattern consistency
    alternation_consistency: float = 0.0  # How consistent the pattern is
    accent_positions: List[int] = field(default_factory=list)  # Grid positions with accents


@dataclass
class DrumTechniqueProfile:
    """Complete drum technique analysis."""
    snare: SnareBounceSignature = field(default_factory=SnareBounceSignature)
    hihat: HiHatAlternation = field(default_factory=HiHatAlternation)
    
    # Overall characteristics
    tightness: float = 0.0       # How tight/loose the playing is (0-1)
    dynamics_range: float = 0.0  # Velocity range used
    ghost_note_density: float = 0.0  # Proportion of ghost notes
    fill_density: float = 0.0    # How often fills occur


class DrumAnalyzer:
    """
    Analyze drum performance techniques.
    
    Detects:
    - Snare bounces, flams, buzz rolls, drags
    - Hi-hat hand alternation patterns
    - Overall technique profile
    """
    
    def __init__(self, ppq: int = STANDARD_PPQ, bpm: float = 120.0):
        self.ppq = ppq
        self.bpm = bpm
        
        # Convert ms thresholds to ticks
        self.flam_ticks = self._ms_to_ticks(FLAM_THRESHOLD_MS)
        self.buzz_ticks = self._ms_to_ticks(BUZZ_THRESHOLD_MS)
        self.drag_ticks = self._ms_to_ticks(DRAG_THRESHOLD_MS)
        self.alternation_ticks = self._ms_to_ticks(ALTERNATION_WINDOW_MS)
    
    def _ms_to_ticks(self, ms: float) -> int:
        """Convert milliseconds to ticks."""
        ticks_per_ms = self.ppq * self.bpm / 60000
        return int(ms * ticks_per_ms)
    
    def _ticks_to_ms(self, ticks: int) -> float:
        """Convert ticks to milliseconds."""
        return ticks_to_ms(ticks, self.ppq, self.bpm)
    
    def analyze(self, notes: List, bpm: Optional[float] = None) -> DrumTechniqueProfile:
        """
        Analyze drum technique from note list.
        
        Args:
            notes: List of MidiNote objects
            bpm: Override BPM (uses self.bpm if None)
        
        Returns:
            DrumTechniqueProfile with all analysis
        """
        if bpm:
            self.bpm = bpm
            self.flam_ticks = self._ms_to_ticks(FLAM_THRESHOLD_MS)
            self.buzz_ticks = self._ms_to_ticks(BUZZ_THRESHOLD_MS)
            self.drag_ticks = self._ms_to_ticks(DRAG_THRESHOLD_MS)
            self.alternation_ticks = self._ms_to_ticks(ALTERNATION_WINDOW_MS)
        
        # Filter to drum notes only
        drum_notes = [n for n in notes if is_drum_channel(n.channel)]
        if not drum_notes:
            return DrumTechniqueProfile()
        
        # Separate by instrument
        snare_notes = [n for n in drum_notes if get_drum_category(n.pitch) == 'snare']
        hihat_notes = [n for n in drum_notes if get_drum_category(n.pitch) == 'hihat']
        
        # Analyze each
        snare_sig = self._analyze_snare_bounces(snare_notes)
        hihat_alt = self._analyze_hihat_alternation(hihat_notes)
        
        # Overall profile
        profile = DrumTechniqueProfile(
            snare=snare_sig,
            hihat=hihat_alt
        )
        
        # Calculate overall characteristics
        profile.tightness = self._calculate_tightness(drum_notes)
        profile.dynamics_range = self._calculate_dynamics_range(drum_notes)
        profile.ghost_note_density = self._calculate_ghost_density(drum_notes)
        
        return profile
    
    def _analyze_snare_bounces(self, snare_notes: List) -> SnareBounceSignature:
        """
        Detect snare bounce patterns: flams, buzz rolls, drags.
        """
        if len(snare_notes) < 2:
            return SnareBounceSignature()
        
        # Sort by time
        snare_notes = sorted(snare_notes, key=lambda n: n.onset_ticks)
        
        flams = []           # (grace_note, main_note) pairs
        buzz_regions = []    # (start, end) tick ranges
        drags = []           # (grace_notes, main_note) tuples
        bounces = []         # All detected bounces
        
        i = 0
        while i < len(snare_notes) - 1:
            current = snare_notes[i]
            
            # Look ahead for close notes
            cluster = [current]
            j = i + 1
            
            while j < len(snare_notes):
                gap = snare_notes[j].onset_ticks - cluster[-1].onset_ticks
                
                if gap <= self.buzz_ticks:
                    cluster.append(snare_notes[j])
                    j += 1
                else:
                    break
            
            # Analyze cluster
            if len(cluster) >= 2:
                gap_ms = self._ticks_to_ms(cluster[1].onset_ticks - cluster[0].onset_ticks)
                
                if len(cluster) == 2 and gap_ms <= FLAM_THRESHOLD_MS:
                    # FLAM: two notes, grace note quieter
                    if cluster[0].velocity < cluster[1].velocity:
                        flams.append((cluster[0], cluster[1]))
                        bounces.append({
                            'type': 'flam',
                            'gap_ms': gap_ms,
                            'velocity_ratio': cluster[0].velocity / cluster[1].velocity
                        })
                    elif cluster[1].velocity < cluster[0].velocity:
                        flams.append((cluster[1], cluster[0]))
                        bounces.append({
                            'type': 'flam',
                            'gap_ms': gap_ms,
                            'velocity_ratio': cluster[1].velocity / cluster[0].velocity
                        })
                
                elif len(cluster) >= 3:
                    # Could be buzz roll or drag
                    velocities = [n.velocity for n in cluster]
                    
                    # Buzz roll: many notes, relatively even velocity
                    vel_std = self._std(velocities)
                    if vel_std < 20 and len(cluster) >= 4:
                        buzz_regions.append((cluster[0].onset_ticks, cluster[-1].onset_ticks))
                        bounces.append({'type': 'buzz', 'length': len(cluster)})
                    
                    # Drag: grace notes (quieter) before main hit (louder)
                    elif velocities[-1] > max(velocities[:-1]):
                        drags.append((cluster[:-1], cluster[-1]))
                        bounces.append({
                            'type': 'drag',
                            'grace_count': len(cluster) - 1,
                            'velocity_ratio': sum(velocities[:-1]) / len(velocities[:-1]) / velocities[-1]
                        })
                
                i = j  # Skip past cluster
            else:
                i += 1
        
        # Build signature
        sig = SnareBounceSignature(
            flam_count=len(flams),
            buzz_roll_regions=buzz_regions,
            drag_count=len(drags),
            total_bounces=len(bounces),
            has_buzz_rolls=len(buzz_regions) > 0,
            has_ghost_drags=len(drags) > 0
        )
        
        # Calculate averages
        if flams:
            gaps = [self._ticks_to_ms(m.onset_ticks - g.onset_ticks) for g, m in flams]
            ratios = [g.velocity / m.velocity for g, m in flams]
            sig.avg_flam_gap_ms = sum(gaps) / len(gaps)
            sig.avg_flam_velocity_ratio = sum(ratios) / len(ratios)
        
        # Determine primary technique
        if len(buzz_regions) > 3:
            sig.primary_technique = "technical"  # Uses buzz rolls
        elif len(drags) > len(flams):
            sig.primary_technique = "jazzy"      # Drag-heavy
        elif len(flams) > len(snare_notes) * 0.1:
            sig.primary_technique = "heavy"      # Lots of flams
        else:
            sig.primary_technique = "standard"
        
        return sig
    
    def _analyze_hihat_alternation(self, hihat_notes: List) -> HiHatAlternation:
        """
        Detect hi-hat hand alternation patterns.
        
        Right-handed drummers: stronger on downbeats (right hand leads)
        Left-handed drummers: stronger on upbeats
        """
        if len(hihat_notes) < 8:
            return HiHatAlternation()
        
        # Sort by time
        hihat_notes = sorted(hihat_notes, key=lambda n: n.onset_ticks)
        
        # Separate into downbeats and upbeats (8th note grid)
        eighth_ticks = self.ppq // 2
        
        downbeat_notes = []  # Even 8th positions (0, 2, 4, 6)
        upbeat_notes = []    # Odd 8th positions (1, 3, 5, 7)
        
        for note in hihat_notes:
            # Position within beat
            pos_in_beat = note.onset_ticks % self.ppq
            eighth_pos = round(pos_in_beat / eighth_ticks)
            
            # Check if close to grid
            nearest_eighth = eighth_pos * eighth_ticks
            offset = abs(pos_in_beat - nearest_eighth)
            
            if offset < eighth_ticks * 0.3:  # Within 30% of grid
                if eighth_pos % 2 == 0:
                    downbeat_notes.append(note)
                else:
                    upbeat_notes.append(note)
        
        if not downbeat_notes or not upbeat_notes:
            return HiHatAlternation()
        
        # Calculate velocity stats
        down_vels = [n.velocity for n in downbeat_notes]
        up_vels = [n.velocity for n in upbeat_notes]
        
        down_avg = sum(down_vels) / len(down_vels)
        up_avg = sum(up_vels) / len(up_vels)
        
        # Velocity ratio
        vel_ratio = down_avg / up_avg if up_avg > 0 else 1.0
        
        # Detect alternation pattern
        # Strong alternation: ratio significantly different from 1.0
        alternation_strength = abs(vel_ratio - 1.0)
        is_alternating = alternation_strength > 0.1
        
        # Determine dominant hand
        if vel_ratio > 1.1:
            dominant = "right"  # Stronger on downbeats = right-hand lead
        elif vel_ratio < 0.9:
            dominant = "left"   # Stronger on upbeats = left-hand lead (or cross-stick)
        else:
            dominant = "unknown"
        
        # Calculate timing offsets
        down_offsets = []
        up_offsets = []
        
        for note in downbeat_notes:
            pos = note.onset_ticks % self.ppq
            nearest = round(pos / eighth_ticks) * eighth_ticks
            down_offsets.append(pos - nearest)
        
        for note in upbeat_notes:
            pos = note.onset_ticks % self.ppq
            nearest = round(pos / eighth_ticks) * eighth_ticks
            up_offsets.append(pos - nearest)
        
        # Consistency: how consistent is the velocity pattern
        down_std = self._std(down_vels)
        up_std = self._std(up_vels)
        consistency = 1.0 - (down_std + up_std) / 254  # Normalize to 0-1
        
        # Find accent positions (significantly louder notes)
        all_vels = down_vels + up_vels
        vel_threshold = sum(all_vels) / len(all_vels) + self._std(all_vels)
        
        accent_positions = []
        for note in hihat_notes:
            if note.velocity > vel_threshold:
                grid_pos = (note.onset_ticks % (self.ppq * 4)) // (self.ppq // 4)
                accent_positions.append(int(grid_pos) % 16)
        
        return HiHatAlternation(
            is_alternating=is_alternating,
            confidence=min(1.0, alternation_strength * 2),  # Scale to 0-1
            dominant_hand=dominant,
            downbeat_avg_velocity=down_avg,
            upbeat_avg_velocity=up_avg,
            velocity_alternation_ratio=vel_ratio,
            downbeat_avg_offset=sum(down_offsets) / len(down_offsets) if down_offsets else 0,
            upbeat_avg_offset=sum(up_offsets) / len(up_offsets) if up_offsets else 0,
            alternation_consistency=consistency,
            accent_positions=list(set(accent_positions))
        )
    
    def _calculate_tightness(self, notes: List) -> float:
        """
        Calculate overall timing tightness (0=loose, 1=tight).
        """
        if len(notes) < 10:
            return 0.5
        
        # Quantize to 16th grid and measure offsets
        sixteenth_ticks = self.ppq // 4
        offsets = []
        
        for note in notes:
            pos = note.onset_ticks % (self.ppq * 4)
            nearest = round(pos / sixteenth_ticks) * sixteenth_ticks
            offset = abs(pos - nearest)
            offsets.append(offset)
        
        # Average offset as proportion of grid unit
        avg_offset = sum(offsets) / len(offsets)
        tightness = 1.0 - min(1.0, avg_offset / sixteenth_ticks)
        
        return tightness
    
    def _calculate_dynamics_range(self, notes: List) -> float:
        """Calculate velocity range used (0-1)."""
        if not notes:
            return 0.0
        
        vels = [n.velocity for n in notes]
        return (max(vels) - min(vels)) / 127
    
    def _calculate_ghost_density(self, notes: List) -> float:
        """Calculate proportion of ghost notes."""
        if not notes:
            return 0.0
        
        ghost_count = sum(1 for n in notes if n.velocity < 40)
        return ghost_count / len(notes)
    
    def _std(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return math.sqrt(variance)


def analyze_drum_technique(notes: List, ppq: int = 480, bpm: float = 120.0) -> DrumTechniqueProfile:
    """Convenience function for drum analysis."""
    analyzer = DrumAnalyzer(ppq=ppq, bpm=bpm)
    return analyzer.analyze(notes, bpm=bpm)
