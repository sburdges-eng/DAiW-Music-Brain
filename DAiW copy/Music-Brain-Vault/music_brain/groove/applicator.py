"""
Groove Applicator - Real Implementation

Applies groove templates with:
- PPQ-aware scaling (critical: templates scale to target file's PPQ)
- Ghost-aware application (separate treatment for ghost notes)
- Per-instrument swing application
- Beat-position-aware offset mapping (not random indices)
- Track-safe modification (preserves all non-note events)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import random
import math

from ..utils.ppq import (
    STANDARD_PPQ, scale_template, scale_pocket_rules,
    grid_position, ticks_per_bar
)
from ..utils.instruments import (
    classify_note, get_drum_category, is_drum_channel,
    get_groove_instruments
)
from ..utils.midi_io import load_midi, save_midi, modify_notes_safe, MidiNote


# Ghost velocity threshold
GHOST_VELOCITY_THRESHOLD = 40


@dataclass
class ApplicationStats:
    """Statistics from groove application."""
    notes_modified: int = 0
    timing_shifts_applied: int = 0
    velocity_changes_applied: int = 0
    swing_adjustments: int = 0
    ghost_notes_preserved: int = 0
    source_ppq: int = 480
    target_ppq: int = 480
    scale_factor: float = 1.0


class GrooveApplicator:
    """
    Apply groove templates to MIDI files.
    
    Critical features:
    - PPQ scaling: Template offsets are scaled to target file's resolution
    - Beat-position-aware: Correct offset applied per grid position
    - Track-safe: Non-note events preserved exactly
    - Ghost-aware: Ghost notes get separate treatment
    """
    
    def __init__(self, randomness: float = 0.3):
        """
        Args:
            randomness: Amount of random variation (0-1)
        """
        self.randomness = randomness
    
    def apply_genre_pocket(
        self,
        input_path: str,
        output_path: str,
        genre: str,
        intensity: float = 1.0
    ) -> ApplicationStats:
        """
        Apply pre-built genre pocket rules.
        
        Args:
            input_path: Source MIDI file
            output_path: Output MIDI file
            genre: Genre name (hiphop, jazz, etc.)
            intensity: How much to apply (0-1)
        
        Returns:
            ApplicationStats with details
        """
        from .pocket_rules import get_pocket, GENRE_POCKETS
        
        if genre not in GENRE_POCKETS:
            raise ValueError(f"Unknown genre: {genre}. Available: {list(GENRE_POCKETS.keys())}")
        
        # Load MIDI WITHOUT normalizing - we need the original PPQ
        data = load_midi(input_path, normalize_ppq=False)
        target_ppq = data.ppq
        
        # Get pocket rules (defined at STANDARD_PPQ)
        pocket = get_pocket(genre)
        
        # CRITICAL: Scale pocket to target file's PPQ
        if target_ppq != STANDARD_PPQ:
            pocket = scale_pocket_rules(pocket, STANDARD_PPQ, target_ppq)
        
        stats = ApplicationStats(
            source_ppq=STANDARD_PPQ,
            target_ppq=target_ppq,
            scale_factor=target_ppq / STANDARD_PPQ
        )
        
        push_pull = pocket.get('push_pull', {})
        swing = pocket.get('swing', 0.5)
        velocity_ranges = pocket.get('velocity', {})
        
        tpb = data.ticks_per_bar
        eighth_ticks = data.ppq // 2
        
        def modifier(note: MidiNote) -> MidiNote:
            """Modify a single note according to pocket rules."""
            nonlocal stats
            
            # Classify instrument
            if is_drum_channel(note.channel):
                inst = get_drum_category(note.pitch)
            else:
                inst = classify_note(note.channel, note.pitch)
            
            # Is this a ghost note?
            is_ghost = note.velocity < GHOST_VELOCITY_THRESHOLD
            if is_ghost:
                stats.ghost_notes_preserved += 1
                # Minimal modification for ghosts - just slight humanization
                timing_jitter = int(random.gauss(0, 3 * stats.scale_factor))
                new_onset = max(0, note.onset_ticks + timing_jitter)
                return MidiNote(
                    pitch=note.pitch,
                    velocity=note.velocity,
                    onset_ticks=new_onset,
                    duration_ticks=note.duration_ticks,
                    channel=note.channel,
                    track_index=note.track_index
                )
            
            # Get timing offset for this instrument
            base_offset = push_pull.get(inst, 0)
            
            # Apply with intensity and randomness
            random_factor = 1.0 + random.gauss(0, self.randomness * 0.5)
            timing_offset = int(base_offset * intensity * random_factor)
            
            # Apply swing to off-beat 8th notes
            if swing > 0.5:
                eighth_pos = (note.onset_ticks % tpb) // eighth_ticks
                is_offbeat = (eighth_pos % 2 == 1)
                
                if is_offbeat:
                    # Swing: delay off-beats
                    # swing 0.5 = no delay, 0.66 = triplet feel
                    swing_amount = (swing - 0.5) * eighth_ticks * 2 * intensity
                    timing_offset += int(swing_amount)
                    stats.swing_adjustments += 1
            
            # Calculate new onset
            new_onset = max(0, note.onset_ticks + timing_offset)
            if timing_offset != 0:
                stats.timing_shifts_applied += 1
            
            # Apply velocity modification
            new_velocity = note.velocity
            if inst in velocity_ranges:
                vel_range = velocity_ranges[inst]
                if isinstance(vel_range, (list, tuple)) and len(vel_range) == 2:
                    target_vel = (vel_range[0] + vel_range[1]) // 2
                    # Move toward target with 50% intensity
                    vel_diff = target_vel - note.velocity
                    new_velocity = note.velocity + int(vel_diff * intensity * 0.5)
                    
            # Add velocity randomness
            vel_jitter = int(random.gauss(0, 5))
            new_velocity = max(1, min(127, new_velocity + vel_jitter))
            
            if new_velocity != note.velocity:
                stats.velocity_changes_applied += 1
            
            stats.notes_modified += 1
            
            return MidiNote(
                pitch=note.pitch,
                velocity=new_velocity,
                onset_ticks=new_onset,
                duration_ticks=note.duration_ticks,
                channel=note.channel,
                track_index=note.track_index
            )
        
        # Apply modification (track-safe)
        modified_data = modify_notes_safe(data, modifier)
        
        # Save with original PPQ
        save_midi(modified_data, output_path, target_ppq=target_ppq)
        
        return stats
    
    def apply_template(
        self,
        input_path: str,
        output_path: str,
        template: Dict[str, Any],
        intensity: float = 1.0
    ) -> ApplicationStats:
        """
        Apply extracted groove template.
        
        Args:
            input_path: Source MIDI file
            output_path: Output MIDI file
            template: Groove template dict
            intensity: How much to apply (0-1)
        
        Returns:
            ApplicationStats
        """
        # Load MIDI without normalizing
        data = load_midi(input_path, normalize_ppq=False)
        target_ppq = data.ppq
        
        # Get template's PPQ
        template_ppq = template.get('ppq', STANDARD_PPQ)
        
        # CRITICAL: Scale template to target PPQ
        if template_ppq != target_ppq:
            template = scale_template(template, template_ppq, target_ppq)
        
        stats = ApplicationStats(
            source_ppq=template_ppq,
            target_ppq=target_ppq,
            scale_factor=target_ppq / template_ppq
        )
        
        push_pull = template.get('push_pull', {})
        swing = template.get('swing', 0.5)
        per_inst_swing = template.get('per_instrument_swing', {})
        velocity_curves = template.get('velocity_curves', {})
        ghost_timing = template.get('ghost_timing', {})
        
        tpb = data.ticks_per_bar
        eighth_ticks = data.ppq // 2
        grid_ticks = tpb // 16  # 16th note grid
        
        def modifier(note: MidiNote) -> MidiNote:
            """Modify note according to template."""
            nonlocal stats
            
            # Classify instrument
            if is_drum_channel(note.channel):
                inst = get_drum_category(note.pitch)
            else:
                inst = classify_note(note.channel, note.pitch)
            
            # Beat-position-aware: get grid position within bar
            position_in_bar = note.onset_ticks % tpb
            grid_idx = int(position_in_bar // grid_ticks) % 16
            
            is_ghost = note.velocity < GHOST_VELOCITY_THRESHOLD
            
            # === TIMING ===
            timing_offset = 0
            
            if is_ghost:
                stats.ghost_notes_preserved += 1
                # Use ghost-specific timing if available
                if inst in ghost_timing and grid_idx in ghost_timing[inst]:
                    timing_offset = ghost_timing[inst][grid_idx]
                else:
                    # Minimal jitter for ghosts
                    timing_offset = int(random.gauss(0, 3))
            else:
                # Get timing offset for this instrument at this position
                if inst in push_pull:
                    inst_offsets = push_pull[inst]
                    if isinstance(inst_offsets, dict):
                        timing_offset = inst_offsets.get(grid_idx, inst_offsets.get(str(grid_idx), 0))
                    else:
                        timing_offset = inst_offsets
                
                # Apply per-instrument swing if available
                inst_swing = swing
                if inst in per_inst_swing:
                    swing_data = per_inst_swing[inst]
                    if isinstance(swing_data, dict):
                        inst_swing = swing_data.get('ratio', swing)
                    else:
                        inst_swing = swing_data
                
                # Apply swing to off-beats
                if inst_swing > 0.52:  # More than subtle
                    eighth_pos = (note.onset_ticks % tpb) // eighth_ticks
                    is_offbeat = (eighth_pos % 2 == 1)
                    
                    if is_offbeat:
                        swing_amount = (inst_swing - 0.5) * eighth_ticks * 2 * intensity
                        timing_offset += int(swing_amount)
                        stats.swing_adjustments += 1
            
            # Apply intensity and randomness
            random_factor = 1.0 + random.gauss(0, self.randomness * 0.3)
            final_offset = int(timing_offset * intensity * random_factor)
            
            new_onset = max(0, note.onset_ticks + final_offset)
            if final_offset != 0:
                stats.timing_shifts_applied += 1
            
            # === VELOCITY ===
            new_velocity = note.velocity
            
            if not is_ghost and inst in velocity_curves:
                curve = velocity_curves[inst]
                if isinstance(curve, dict) and 'mean_by_position' in curve:
                    pos_key = grid_idx
                    if str(pos_key) in curve['mean_by_position']:
                        pos_key = str(pos_key)
                    
                    if pos_key in curve['mean_by_position']:
                        target_vel = curve['mean_by_position'][pos_key]
                        if target_vel > 1:  # Assumes 0-127
                            target_vel = target_vel  # Already in 0-127
                        else:  # Normalized 0-1
                            target_vel = target_vel * 127
                        
                        vel_diff = target_vel - note.velocity
                        new_velocity = note.velocity + int(vel_diff * intensity * 0.7)
            
            # Add velocity humanization
            vel_jitter = int(random.gauss(0, 4))
            new_velocity = max(1, min(127, new_velocity + vel_jitter))
            
            if new_velocity != note.velocity:
                stats.velocity_changes_applied += 1
            
            stats.notes_modified += 1
            
            return MidiNote(
                pitch=note.pitch,
                velocity=new_velocity,
                onset_ticks=new_onset,
                duration_ticks=note.duration_ticks,
                channel=note.channel,
                track_index=note.track_index
            )
        
        modified_data = modify_notes_safe(data, modifier)
        save_midi(modified_data, output_path, target_ppq=target_ppq)
        
        return stats
    
    def humanize(
        self,
        input_path: str,
        output_path: str,
        timing_range: int = 10,
        velocity_range: int = 15
    ) -> ApplicationStats:
        """
        Apply basic random humanization.
        
        Args:
            timing_range: Max timing shift in ticks (will be scaled to PPQ)
            velocity_range: Max velocity shift
        
        Returns:
            ApplicationStats
        """
        data = load_midi(input_path, normalize_ppq=False)
        target_ppq = data.ppq
        
        # Scale timing range to file's PPQ
        scaled_timing = int(timing_range * target_ppq / STANDARD_PPQ)
        
        stats = ApplicationStats(
            source_ppq=STANDARD_PPQ,
            target_ppq=target_ppq,
            scale_factor=target_ppq / STANDARD_PPQ
        )
        
        def modifier(note: MidiNote) -> MidiNote:
            nonlocal stats
            
            # Gaussian random timing
            timing_offset = int(random.gauss(0, scaled_timing / 2))
            new_onset = max(0, note.onset_ticks + timing_offset)
            
            # Gaussian random velocity
            vel_offset = int(random.gauss(0, velocity_range / 2))
            new_velocity = max(1, min(127, note.velocity + vel_offset))
            
            if timing_offset != 0:
                stats.timing_shifts_applied += 1
            if vel_offset != 0:
                stats.velocity_changes_applied += 1
            
            stats.notes_modified += 1
            
            return MidiNote(
                pitch=note.pitch,
                velocity=new_velocity,
                onset_ticks=new_onset,
                duration_ticks=note.duration_ticks,
                channel=note.channel,
                track_index=note.track_index
            )
        
        modified_data = modify_notes_safe(data, modifier)
        save_midi(modified_data, output_path, target_ppq=target_ppq)
        
        return stats
    
    def apply_from_storage(
        self,
        input_path: str,
        output_path: str,
        genre: str,
        intensity: float = 1.0,
        version: Optional[str] = None
    ) -> ApplicationStats:
        """
        Load template from storage and apply.
        """
        from .templates import get_storage
        
        storage = get_storage()
        template = storage.load(genre, version)
        
        if template is None:
            raise ValueError(f"No template found for genre: {genre}")
        
        return self.apply_template(input_path, output_path, template, intensity)


def apply_groove(
    input_path: str,
    output_path: str,
    source: str,
    intensity: float = 1.0,
    randomness: float = 0.3
) -> ApplicationStats:
    """
    Convenience function to apply groove.
    
    Args:
        input_path: Source MIDI file
        output_path: Output MIDI file
        source: Genre name OR path to template JSON
        intensity: How much to apply (0-1)
        randomness: Random variation amount
    
    Returns:
        ApplicationStats
    """
    import os
    import json
    
    applicator = GrooveApplicator(randomness=randomness)
    
    # Check if source is a file path
    if os.path.exists(source):
        with open(source, 'r') as f:
            template = json.load(f)
        return applicator.apply_template(input_path, output_path, template, intensity)
    
    # Check if it's a known genre
    from .pocket_rules import GENRE_POCKETS
    if source in GENRE_POCKETS:
        return applicator.apply_genre_pocket(input_path, output_path, source, intensity)
    
    # Try loading from storage
    try:
        return applicator.apply_from_storage(input_path, output_path, source, intensity)
    except ValueError:
        pass
    
    raise ValueError(f"Unknown source: {source}. Provide genre name, template path, or valid storage key.")
