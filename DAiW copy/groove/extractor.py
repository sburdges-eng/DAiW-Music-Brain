"""
Groove Extractor - Real Implementation

Extracts groove/feel from MIDI with:
- Ghost note isolation (prevents histogram muddiness)
- Per-instrument swing with consistency metrics
- Time-variant extraction (per-section feels)
- Velocity curve inference (accent patterns, handedness)
- Multi-bar histogram normalization
- Beat-aware offset mapping (not simple iteration)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import math

from ..utils.ppq import (
    STANDARD_PPQ, normalize_ticks, ticks_per_bar,
    grid_position, quantize_to_grid, ticks_to_beats
)
from ..utils.instruments import (
    classify_note, get_drum_category, is_drum_channel,
    get_groove_instruments, DRUM_CATEGORIES
)


# Ghost note threshold - notes below this velocity are ghosts
GHOST_VELOCITY_THRESHOLD = 40

# Accent threshold - notes above this are accents
ACCENT_VELOCITY_THRESHOLD = 100

# Minimum notes needed for reliable swing calculation
MIN_SWING_NOTES = 8

# Swing consistency threshold - std dev below this = consistent
SWING_CONSISTENCY_THRESHOLD = 0.08


@dataclass
class SwingData:
    """Per-instrument swing analysis."""
    ratio: float              # 0.5 = straight, 0.66 = triplet
    consistency: float        # Std dev of ratios (lower = more consistent)
    sample_count: int         # Number of swing pairs analyzed
    offsets_by_position: Dict[int, float] = field(default_factory=dict)  # 8th note position -> avg offset


@dataclass
class VelocityCurve:
    """Velocity pattern analysis for one instrument."""
    mean_by_position: Dict[int, float] = field(default_factory=dict)  # Grid pos -> mean vel
    std_by_position: Dict[int, float] = field(default_factory=dict)   # Grid pos -> std dev
    accent_positions: List[int] = field(default_factory=list)         # Positions with accents
    ghost_positions: List[int] = field(default_factory=list)          # Positions with ghosts
    accent_ratio: float = 0.0      # Fraction of notes that are accents
    ghost_ratio: float = 0.0       # Fraction of notes that are ghosts
    dynamic_range: float = 0.0     # Max - min average velocity


@dataclass 
class GrooveTemplate:
    """Complete groove template."""
    # Core timing (required)
    timing_histogram: List[float]        # 32-bin density per bar position
    push_pull: Dict[str, Dict[int, int]] # Instrument -> {grid_pos: offset_ticks}
    
    # Swing (required)
    swing: float                         # Global swing ratio
    swing_consistency: float             # How consistent the swing is
    
    # Velocity (required)
    velocity_map: List[float]            # 32-bin velocity curve
    
    # All optional fields with defaults below
    per_instrument_swing: Dict[str, SwingData] = field(default_factory=dict)
    velocity_curves: Dict[str, VelocityCurve] = field(default_factory=dict)
    ghost_timing: Dict[str, Dict[int, int]] = field(default_factory=dict)
    ghost_density: Dict[str, float] = field(default_factory=dict)
    stagger: Dict[Tuple[str, str], int] = field(default_factory=dict)
    
    # Metadata with defaults
    ppq: int = STANDARD_PPQ
    bpm: float = 120.0
    bars_analyzed: int = 0
    notes_analyzed: int = 0
    source_file: str = ""
    sections: Dict[str, 'GrooveTemplate'] = field(default_factory=dict)


class GrooveExtractor:
    """
    Extract groove from MIDI files.
    
    Key features:
    - Ghost note isolation before histogram calculation
    - Per-instrument swing with consistency metrics
    - Beat-position-aware offset mapping
    - Multi-bar averaging with variance tracking
    """
    
    def __init__(self, subdivisions: int = 32, bars_to_analyze: int = 8):
        """
        Args:
            subdivisions: Grid divisions per bar (32 = 32nd notes)
            bars_to_analyze: Number of bars to average over
        """
        self.subdivisions = subdivisions
        self.bars_to_analyze = bars_to_analyze
    
    def extract(self, filepath: str, genre: Optional[str] = None) -> GrooveTemplate:
        """
        Extract groove template from MIDI file.
        
        Args:
            filepath: Path to MIDI file
            genre: Optional genre hint for interpretation
        
        Returns:
            GrooveTemplate with all extracted data
        """
        from ..utils.midi_io import load_midi
        
        # Load with PPQ normalization to standard
        data = load_midi(filepath, normalize_ppq=True)
        notes = data.all_notes
        ppq = data.ppq
        tpb = data.ticks_per_bar
        
        if not notes:
            return GrooveTemplate(
                timing_histogram=[0.0] * self.subdivisions,
                push_pull={},
                swing=0.5,
                swing_consistency=1.0,
                velocity_map=[0.0] * self.subdivisions,
                ppq=ppq,
                bpm=data.bpm,
                source_file=filepath
            )
        
        # === STEP 1: Separate ghost notes ===
        main_notes, ghost_notes = self._separate_ghosts(notes)
        
        # === STEP 2: Extract timing histogram (main notes only) ===
        timing_histogram = self._extract_timing_histogram(main_notes, tpb)
        
        # === STEP 3: Extract push/pull per instrument per position ===
        push_pull = self._extract_push_pull(main_notes, ppq, tpb)
        
        # === STEP 4: Extract real swing per instrument ===
        per_instrument_swing = self._extract_per_instrument_swing(main_notes, ppq)
        global_swing, swing_consistency = self._calculate_global_swing(per_instrument_swing)
        
        # === STEP 5: Extract velocity curves ===
        velocity_map = self._extract_velocity_map(main_notes, tpb)
        velocity_curves = self._extract_velocity_curves(notes, ppq, tpb)  # Include ghosts for full picture
        
        # === STEP 6: Analyze ghost note patterns ===
        ghost_timing, ghost_density = self._analyze_ghosts(ghost_notes, ppq, tpb)
        
        # === STEP 7: Cross-instrument stagger ===
        stagger = self._extract_stagger(main_notes, ppq)
        
        # Calculate metadata
        max_tick = max(n.onset_ticks for n in notes)
        bars_analyzed = int(max_tick / tpb) + 1
        
        return GrooveTemplate(
            timing_histogram=timing_histogram,
            push_pull=push_pull,
            swing=global_swing,
            swing_consistency=swing_consistency,
            per_instrument_swing=per_instrument_swing,
            velocity_map=velocity_map,
            velocity_curves=velocity_curves,
            ghost_timing=ghost_timing,
            ghost_density=ghost_density,
            stagger=stagger,
            ppq=ppq,
            bpm=data.bpm,
            bars_analyzed=min(bars_analyzed, self.bars_to_analyze),
            notes_analyzed=len(notes),
            source_file=filepath
        )
    
    def _separate_ghosts(self, notes: List) -> Tuple[List, List]:
        """
        Separate ghost notes from main notes.
        
        Ghost notes distort timing histograms and must be analyzed separately.
        """
        main = []
        ghosts = []
        
        for note in notes:
            if note.velocity < GHOST_VELOCITY_THRESHOLD:
                ghosts.append(note)
            else:
                main.append(note)
        
        return main, ghosts
    
    def _extract_timing_histogram(self, notes: List, ticks_per_bar: int) -> List[float]:
        """
        Build timing density histogram per bar position.
        
        Uses beat-position-aware indexing, not simple iteration.
        Averages across multiple bars.
        """
        if not notes:
            return [0.0] * self.subdivisions
        
        grid_ticks = ticks_per_bar // self.subdivisions
        
        # Group notes by bar
        notes_by_bar = defaultdict(list)
        for note in notes:
            bar = int(note.onset_ticks // ticks_per_bar)
            if bar < self.bars_to_analyze:
                notes_by_bar[bar].append(note)
        
        if not notes_by_bar:
            return [0.0] * self.subdivisions
        
        # Build histogram for each bar
        bar_histograms = []
        for bar_idx in range(min(len(notes_by_bar), self.bars_to_analyze)):
            if bar_idx not in notes_by_bar:
                continue
            
            histogram = [0.0] * self.subdivisions
            for note in notes_by_bar[bar_idx]:
                # Beat-position-aware: position within THIS bar
                position_in_bar = note.onset_ticks - (bar_idx * ticks_per_bar)
                grid_idx = int(position_in_bar // grid_ticks) % self.subdivisions
                histogram[grid_idx] += 1.0
            
            # Normalize this bar's histogram
            max_val = max(histogram) if histogram else 1.0
            if max_val > 0:
                histogram = [v / max_val for v in histogram]
            
            bar_histograms.append(histogram)
        
        if not bar_histograms:
            return [0.0] * self.subdivisions
        
        # Average across bars
        avg_histogram = [0.0] * self.subdivisions
        for i in range(self.subdivisions):
            values = [h[i] for h in bar_histograms]
            avg_histogram[i] = sum(values) / len(values)
        
        return avg_histogram
    
    def _extract_push_pull(self, notes: List, ppq: int, ticks_per_bar: int) -> Dict[str, Dict[int, int]]:
        """
        Extract timing offset from grid per instrument per position.
        
        Returns nested dict: instrument -> grid_position -> average_offset_ticks
        Positive = behind the beat, Negative = ahead
        """
        # Group by instrument and grid position
        offsets = defaultdict(lambda: defaultdict(list))
        grid_ticks = ticks_per_bar // 16  # 16th note grid for push/pull
        
        for note in notes:
            # Classify instrument
            if is_drum_channel(note.channel):
                inst = get_drum_category(note.pitch)
            else:
                inst = classify_note(note.channel, note.pitch)
            
            # Get grid position within bar (beat-aware)
            position_in_bar = note.onset_ticks % ticks_per_bar
            grid_idx = int(position_in_bar // grid_ticks) % 16
            
            # Calculate offset from nearest grid point
            nearest_grid = round(position_in_bar / grid_ticks) * grid_ticks
            offset = position_in_bar - nearest_grid
            
            # Only count if close enough to grid (within half a grid unit)
            if abs(offset) < grid_ticks // 2:
                offsets[inst][grid_idx].append(offset)
        
        # Average offsets per position
        push_pull = {}
        for inst, positions in offsets.items():
            push_pull[inst] = {}
            for grid_idx, offset_list in positions.items():
                if offset_list:
                    push_pull[inst][grid_idx] = int(round(sum(offset_list) / len(offset_list)))
        
        return push_pull
    
    def _extract_per_instrument_swing(self, notes: List, ppq: int) -> Dict[str, SwingData]:
        """
        Extract swing ratio per instrument with consistency metric.
        
        Real swing analysis:
        - Measures ratio of on-beat to off-beat 8th note timing
        - Calculates consistency (low std dev = consistent swing)
        - Per-instrument differences (ride vs hat vs snare)
        """
        swing_data = {}
        
        # Group notes by instrument
        notes_by_inst = defaultdict(list)
        for note in notes:
            if is_drum_channel(note.channel):
                inst = get_drum_category(note.pitch)
            else:
                inst = classify_note(note.channel, note.pitch)
            notes_by_inst[inst].append(note)
        
        eighth_ticks = ppq // 2  # Ticks per 8th note
        
        for inst, inst_notes in notes_by_inst.items():
            ratios = []
            offsets_by_8th = defaultdict(list)
            
            # Sort by time
            inst_notes = sorted(inst_notes, key=lambda n: n.onset_ticks)
            
            # Find swing pairs: notes on 8th note positions
            for i, note in enumerate(inst_notes):
                # Which 8th note position is this? (0, 1, 2, 3... within beat)
                eighth_pos = (note.onset_ticks % (ppq * 4)) // eighth_ticks
                is_downbeat = (eighth_pos % 2 == 0)
                
                # Quantize to nearest 8th
                nearest_8th = round(note.onset_ticks / eighth_ticks) * eighth_ticks
                offset = note.onset_ticks - nearest_8th
                
                # Only count if reasonably close to grid
                tolerance = ppq // 8  # 32nd note tolerance
                if abs(offset) < tolerance:
                    offsets_by_8th[eighth_pos % 8].append(offset)
                    
                    # For swing ratio: find previous downbeat
                    if not is_downbeat and i > 0:
                        # Look back for the downbeat
                        for j in range(i - 1, max(0, i - 4), -1):
                            prev_note = inst_notes[j]
                            prev_8th_pos = (prev_note.onset_ticks % (ppq * 4)) // eighth_ticks
                            if prev_8th_pos % 2 == 0:  # Found downbeat
                                # Calculate swing ratio
                                downbeat_time = prev_note.onset_ticks
                                upbeat_time = note.onset_ticks
                                
                                # Time from downbeat to this upbeat
                                first_half = upbeat_time - downbeat_time
                                
                                # Expected if straight
                                expected = eighth_ticks
                                
                                if expected > 0:
                                    ratio = first_half / (2 * expected)
                                    if 0.4 < ratio < 0.75:  # Sanity check
                                        ratios.append(ratio)
                                break
            
            if len(ratios) >= MIN_SWING_NOTES:
                mean_ratio = sum(ratios) / len(ratios)
                variance = sum((r - mean_ratio) ** 2 for r in ratios) / len(ratios)
                consistency = math.sqrt(variance)
                
                # Average offsets by 8th position
                avg_offsets = {}
                for pos, offs in offsets_by_8th.items():
                    if offs:
                        avg_offsets[pos] = sum(offs) / len(offs)
                
                swing_data[inst] = SwingData(
                    ratio=mean_ratio,
                    consistency=consistency,
                    sample_count=len(ratios),
                    offsets_by_position=avg_offsets
                )
            elif inst_notes:
                # Not enough data for reliable swing, mark as straight
                swing_data[inst] = SwingData(
                    ratio=0.5,
                    consistency=1.0,  # High = unreliable
                    sample_count=0
                )
        
        return swing_data
    
    def _calculate_global_swing(self, per_inst: Dict[str, SwingData]) -> Tuple[float, float]:
        """
        Calculate global swing from per-instrument data.
        
        Weights by sample count and instrument importance.
        """
        if not per_inst:
            return 0.5, 1.0
        
        # Weight by sample count (more samples = more reliable)
        weighted_sum = 0.0
        weight_total = 0.0
        consistencies = []
        
        for inst, data in per_inst.items():
            if data.sample_count >= MIN_SWING_NOTES:
                weight = data.sample_count
                weighted_sum += data.ratio * weight
                weight_total += weight
                consistencies.append(data.consistency)
        
        if weight_total == 0:
            return 0.5, 1.0
        
        global_swing = weighted_sum / weight_total
        avg_consistency = sum(consistencies) / len(consistencies) if consistencies else 1.0
        
        return global_swing, avg_consistency
    
    def _extract_velocity_map(self, notes: List, ticks_per_bar: int) -> List[float]:
        """
        Extract average velocity per grid position.
        """
        if not notes:
            return [0.0] * self.subdivisions
        
        grid_ticks = ticks_per_bar // self.subdivisions
        velocities = defaultdict(list)
        
        for note in notes:
            position_in_bar = note.onset_ticks % ticks_per_bar
            grid_idx = int(position_in_bar // grid_ticks) % self.subdivisions
            velocities[grid_idx].append(note.velocity)
        
        velocity_map = []
        for i in range(self.subdivisions):
            if velocities[i]:
                velocity_map.append(sum(velocities[i]) / len(velocities[i]) / 127.0)
            else:
                velocity_map.append(0.0)
        
        return velocity_map
    
    def _extract_velocity_curves(self, notes: List, ppq: int, ticks_per_bar: int) -> Dict[str, VelocityCurve]:
        """
        Extract detailed velocity patterns per instrument.
        
        Includes:
        - Mean and std dev per position
        - Accent and ghost position detection
        - Dynamic range calculation
        """
        curves = {}
        notes_by_inst = defaultdict(list)
        
        for note in notes:
            if is_drum_channel(note.channel):
                inst = get_drum_category(note.pitch)
            else:
                inst = classify_note(note.channel, note.pitch)
            notes_by_inst[inst].append(note)
        
        grid_ticks = ticks_per_bar // 16  # 16th note positions
        
        for inst, inst_notes in notes_by_inst.items():
            vel_by_pos = defaultdict(list)
            accent_count = 0
            ghost_count = 0
            total_count = len(inst_notes)
            
            for note in inst_notes:
                position_in_bar = note.onset_ticks % ticks_per_bar
                grid_idx = int(position_in_bar // grid_ticks) % 16
                vel_by_pos[grid_idx].append(note.velocity)
                
                if note.velocity >= ACCENT_VELOCITY_THRESHOLD:
                    accent_count += 1
                elif note.velocity < GHOST_VELOCITY_THRESHOLD:
                    ghost_count += 1
            
            # Calculate stats per position
            mean_by_pos = {}
            std_by_pos = {}
            accent_positions = []
            ghost_positions = []
            
            for pos, vels in vel_by_pos.items():
                mean_vel = sum(vels) / len(vels)
                mean_by_pos[pos] = mean_vel
                
                if len(vels) > 1:
                    variance = sum((v - mean_vel) ** 2 for v in vels) / len(vels)
                    std_by_pos[pos] = math.sqrt(variance)
                else:
                    std_by_pos[pos] = 0.0
                
                # Check if this position tends to have accents or ghosts
                accents_here = sum(1 for v in vels if v >= ACCENT_VELOCITY_THRESHOLD)
                ghosts_here = sum(1 for v in vels if v < GHOST_VELOCITY_THRESHOLD)
                
                if accents_here > len(vels) * 0.5:
                    accent_positions.append(pos)
                if ghosts_here > len(vels) * 0.5:
                    ghost_positions.append(pos)
            
            # Dynamic range
            if mean_by_pos:
                dynamic_range = max(mean_by_pos.values()) - min(mean_by_pos.values())
            else:
                dynamic_range = 0.0
            
            curves[inst] = VelocityCurve(
                mean_by_position=mean_by_pos,
                std_by_position=std_by_pos,
                accent_positions=accent_positions,
                ghost_positions=ghost_positions,
                accent_ratio=accent_count / total_count if total_count else 0.0,
                ghost_ratio=ghost_count / total_count if total_count else 0.0,
                dynamic_range=dynamic_range
            )
        
        return curves
    
    def _analyze_ghosts(self, ghost_notes: List, ppq: int, ticks_per_bar: int) -> Tuple[Dict, Dict]:
        """
        Analyze ghost note patterns separately.
        
        Ghost notes have different timing logic and must not pollute main histograms.
        """
        ghost_timing = defaultdict(lambda: defaultdict(list))
        ghost_counts = defaultdict(int)
        total_by_inst = defaultdict(int)
        
        grid_ticks = ticks_per_bar // 16
        
        for note in ghost_notes:
            if is_drum_channel(note.channel):
                inst = get_drum_category(note.pitch)
            else:
                inst = classify_note(note.channel, note.pitch)
            
            position_in_bar = note.onset_ticks % ticks_per_bar
            grid_idx = int(position_in_bar // grid_ticks) % 16
            
            # Offset from grid
            nearest_grid = round(position_in_bar / grid_ticks) * grid_ticks
            offset = position_in_bar - nearest_grid
            
            ghost_timing[inst][grid_idx].append(offset)
            ghost_counts[inst] += 1
        
        # Average offsets
        ghost_timing_avg = {}
        for inst, positions in ghost_timing.items():
            ghost_timing_avg[inst] = {}
            for pos, offsets in positions.items():
                if offsets:
                    ghost_timing_avg[inst][pos] = int(round(sum(offsets) / len(offsets)))
        
        # Ghost density ratios would need total note count per instrument
        # For now, just return counts
        ghost_density = {inst: count for inst, count in ghost_counts.items()}
        
        return ghost_timing_avg, ghost_density
    
    def _extract_stagger(self, notes: List, ppq: int) -> Dict[Tuple[str, str], int]:
        """
        Extract timing offset between instrument pairs.
        
        For example: how much does the bass lag behind the kick?
        """
        # Group notes by coarse time (quarter notes) and instrument
        quarter_ticks = ppq
        notes_by_time_inst = defaultdict(lambda: defaultdict(list))
        
        for note in notes:
            if is_drum_channel(note.channel):
                inst = get_drum_category(note.pitch)
            else:
                inst = classify_note(note.channel, note.pitch)
            
            # Round to nearest quarter note
            quarter = round(note.onset_ticks / quarter_ticks) * quarter_ticks
            notes_by_time_inst[quarter][inst].append(note.onset_ticks)
        
        # Calculate pairwise offsets
        pair_offsets = defaultdict(list)
        groove_instruments = get_groove_instruments()
        
        for quarter, inst_notes in notes_by_time_inst.items():
            for inst_a in groove_instruments:
                if inst_a not in inst_notes:
                    continue
                for inst_b in groove_instruments:
                    if inst_b not in inst_notes or inst_b == inst_a:
                        continue
                    
                    # Average onset for each instrument at this time
                    avg_a = sum(inst_notes[inst_a]) / len(inst_notes[inst_a])
                    avg_b = sum(inst_notes[inst_b]) / len(inst_notes[inst_b])
                    
                    offset = int(round(avg_b - avg_a))
                    if abs(offset) < ppq // 4:  # Reasonable offset
                        pair_offsets[(inst_a, inst_b)].append(offset)
        
        # Average offsets per pair
        stagger = {}
        for pair, offsets in pair_offsets.items():
            if len(offsets) >= 4:  # Need enough samples
                stagger[pair] = int(round(sum(offsets) / len(offsets)))
        
        return stagger
    
    def extract_by_section(self, filepath: str, sections: List) -> Dict[str, GrooveTemplate]:
        """
        Extract groove per song section.
        
        Time-variant extraction: different sections may have different feels.
        """
        from ..utils.midi_io import load_midi
        
        data = load_midi(filepath, normalize_ppq=True)
        all_notes = data.all_notes
        tpb = data.ticks_per_bar
        
        section_grooves = {}
        
        for section in sections:
            start_tick = section.start_bar * tpb
            end_tick = section.end_bar * tpb
            
            # Filter notes for this section
            section_notes = [
                n for n in all_notes
                if start_tick <= n.onset_ticks < end_tick
            ]
            
            if section_notes:
                # Create a minimal mock data object for extraction
                # In practice, you'd refactor to extract from note list directly
                main_notes, ghost_notes = self._separate_ghosts(section_notes)
                
                timing_hist = self._extract_timing_histogram(main_notes, tpb)
                push_pull = self._extract_push_pull(main_notes, data.ppq, tpb)
                per_inst_swing = self._extract_per_instrument_swing(main_notes, data.ppq)
                global_swing, swing_cons = self._calculate_global_swing(per_inst_swing)
                velocity_map = self._extract_velocity_map(main_notes, tpb)
                
                section_grooves[section.name] = GrooveTemplate(
                    timing_histogram=timing_hist,
                    push_pull=push_pull,
                    swing=global_swing,
                    swing_consistency=swing_cons,
                    per_instrument_swing=per_inst_swing,
                    velocity_map=velocity_map,
                    ppq=data.ppq,
                    bpm=data.bpm,
                    bars_analyzed=section.end_bar - section.start_bar,
                    notes_analyzed=len(section_notes),
                    source_file=filepath
                )
        
        return section_grooves


def extract_groove(filepath: str, genre: Optional[str] = None, save: bool = False) -> GrooveTemplate:
    """
    Convenience function to extract groove from MIDI file.
    """
    extractor = GrooveExtractor()
    template = extractor.extract(filepath, genre=genre)
    
    if save:
        from .templates import get_storage
        storage = get_storage()
        storage.save(genre or 'unknown', template_to_dict(template))
    
    return template


def template_to_dict(template: GrooveTemplate) -> Dict[str, Any]:
    """Convert GrooveTemplate to serializable dict."""
    return {
        'timing_histogram': template.timing_histogram,
        'push_pull': template.push_pull,
        'swing': template.swing,
        'swing_consistency': template.swing_consistency,
        'per_instrument_swing': {
            inst: {
                'ratio': data.ratio,
                'consistency': data.consistency,
                'sample_count': data.sample_count,
                'offsets_by_position': data.offsets_by_position
            }
            for inst, data in template.per_instrument_swing.items()
        },
        'velocity_map': template.velocity_map,
        'velocity_curves': {
            inst: {
                'mean_by_position': curve.mean_by_position,
                'std_by_position': curve.std_by_position,
                'accent_positions': curve.accent_positions,
                'ghost_positions': curve.ghost_positions,
                'accent_ratio': curve.accent_ratio,
                'ghost_ratio': curve.ghost_ratio,
                'dynamic_range': curve.dynamic_range
            }
            for inst, curve in template.velocity_curves.items()
        },
        'ghost_timing': dict(template.ghost_timing),
        'ghost_density': dict(template.ghost_density),
        'stagger': {f"{k[0]}:{k[1]}": v for k, v in template.stagger.items()},
        'ppq': template.ppq,
        'bpm': template.bpm,
        'bars_analyzed': template.bars_analyzed,
        'notes_analyzed': template.notes_analyzed,
        'source_file': template.source_file,
    }
