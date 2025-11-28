"""
Groove Application - Apply extracted grooves to MIDI files

This module takes a GrooveProfile and applies it to new MIDI drum patterns,
transferring the timing feel and velocity dynamics.

Philosophy: "Humanize the machine - inject feel into the grid."
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import json


@dataclass
class GrooveTemplate:
    """Simplified groove template for storage and application"""
    name: str
    tempo_bpm: float
    swing_percentage: float
    push_pull: Dict[str, float]  # note_type -> ms deviation
    velocity_map: Dict[str, int]  # note_type -> base velocity
    accent_pattern: List[int]  # Beat positions that should be accented (0-15 for 16ths)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON storage"""
        return {
            'name': self.name,
            'tempo_bpm': self.tempo_bpm,
            'swing_percentage': self.swing_percentage,
            'push_pull': self.push_pull,
            'velocity_map': self.velocity_map,
            'accent_pattern': self.accent_pattern
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GrooveTemplate':
        """Load from dictionary"""
        return cls(**data)
    
    def save(self, path: str):
        """Save template to JSON file"""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'GrooveTemplate':
        """Load template from JSON file"""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


class GrooveApplicator:
    """
    Apply groove templates to MIDI drum patterns.
    
    Takes quantized/rigid MIDI and applies:
    - Swing timing
    - Push/pull per instrument
    - Velocity humanization
    - Accent patterns
    """
    
    # Genre groove templates (built-in)
    GENRE_TEMPLATES = {
        'funk': GrooveTemplate(
            name='funk_pocket',
            tempo_bpm=95,
            swing_percentage=58,
            push_pull={'kick': 15, 'snare': -5, 'hihat': -10},
            velocity_map={'kick': 100, 'snare': 110, 'hihat': 70},
            accent_pattern=[0, 8]  # Beats 1 and 3
        ),
        'boom_bap': GrooveTemplate(
            name='boom_bap_pocket',
            tempo_bpm=92,
            swing_percentage=54,
            push_pull={'kick': 10, 'snare': 5, 'hihat': -8},
            velocity_map={'kick': 110, 'snare': 115, 'hihat': 60},
            accent_pattern=[4, 12]  # Snare hits (beats 2 and 4)
        ),
        'dilla': GrooveTemplate(
            name='dilla_swing',
            tempo_bpm=88,
            swing_percentage=62,
            push_pull={'kick': 20, 'snare': -10, 'hihat': -15},
            velocity_map={'kick': 105, 'snare': 100, 'hihat': 55},
            accent_pattern=[0, 6, 12]  # Uneven accents
        ),
        'straight': GrooveTemplate(
            name='straight_quantized',
            tempo_bpm=120,
            swing_percentage=50,
            push_pull={'kick': 0, 'snare': 0, 'hihat': 0},
            velocity_map={'kick': 100, 'snare': 100, 'hihat': 80},
            accent_pattern=[0, 4, 8, 12]  # Every beat
        ),
        'trap': GrooveTemplate(
            name='trap_rolls',
            tempo_bpm=140,
            swing_percentage=51,
            push_pull={'kick': 0, 'snare': 0, 'hihat': 2},
            velocity_map={'kick': 110, 'snare': 105, 'hihat': 75},
            accent_pattern=[0, 8]  # Kicks on 1 and 3
        ),
    }
    
    def __init__(self, ppq: int = 480):
        """
        Initialize groove applicator.
        
        Args:
            ppq: Pulses per quarter note (MIDI ticks per beat)
        """
        self.ppq = ppq
    
    def apply_groove(
        self,
        input_midi_path: str,
        output_midi_path: str,
        groove: GrooveTemplate,
        intensity: float = 1.0
    ):
        """
        Apply groove template to MIDI file.
        
        Args:
            input_midi_path: Source MIDI file (usually quantized)
            output_midi_path: Destination MIDI file (with groove applied)
            groove: GrooveTemplate to apply
            intensity: 0.0-1.0, how strongly to apply groove (1.0 = full)
        """
        import mido
        
        # Load input MIDI
        mid = mido.MidiFile(input_midi_path)
        
        # Create output MIDI
        out_mid = mido.MidiFile(ticks_per_beat=self.ppq)
        
        for track in mid.tracks:
            out_track = mido.MidiTrack()
            out_mid.tracks.append(out_track)
            
            # Process each message
            current_time = 0
            pending_notes = []
            
            for msg in track:
                current_time += msg.time
                
                if msg.type in ['note_on', 'note_off']:
                    # Apply groove transformations
                    new_msg = self._apply_groove_to_note(
                        msg, current_time, groove, intensity
                    )
                    pending_notes.append((current_time, new_msg))
                else:
                    # Copy non-note messages as-is
                    out_track.append(msg.copy())
            
            # Sort by time and calculate deltas
            pending_notes.sort(key=lambda x: x[0])
            last_time = 0
            
            for abs_time, msg in pending_notes:
                delta = abs_time - last_time
                msg.time = max(0, delta)
                out_track.append(msg)
                last_time = abs_time
        
        # Save output
        out_mid.save(output_midi_path)
        print(f"✓ Groove applied: {output_midi_path}")
        print(f"  Template: {groove.name}")
        print(f"  Swing: {groove.swing_percentage:.1f}%")
        print(f"  Intensity: {intensity * 100:.0f}%")
    
    def _apply_groove_to_note(
        self,
        msg,
        time: int,
        groove: GrooveTemplate,
        intensity: float
    ):
        """Apply groove transformations to a single note"""
        new_msg = msg.copy()
        
        # Only process note_on with velocity > 0
        if msg.type != 'note_on' or msg.velocity == 0:
            return new_msg
        
        # Get note category
        note_cat = self._categorize_note(msg.note)
        
        # Apply timing adjustment (swing + push/pull)
        time_adjusted = self._apply_timing(
            time, note_cat, groove, intensity
        )
        
        # Apply velocity adjustment
        if msg.type == 'note_on' and msg.velocity > 0:
            new_msg.velocity = self._apply_velocity(
                msg.velocity, time, note_cat, groove, intensity
            )
        
        return new_msg
    
    def _categorize_note(self, note: int) -> str:
        """Categorize drum note"""
        KICK_NOTES = [35, 36]
        SNARE_NOTES = [38, 40]
        HIHAT_NOTES = [42, 44, 46]
        
        if note in KICK_NOTES:
            return 'kick'
        elif note in SNARE_NOTES:
            return 'snare'
        elif note in HIHAT_NOTES:
            return 'hihat'
        else:
            return 'other'
    
    def _apply_timing(
        self,
        time: int,
        note_category: str,
        groove: GrooveTemplate,
        intensity: float
    ) -> int:
        """
        Apply timing adjustments (swing + push/pull).
        
        Returns adjusted time in ticks.
        """
        # Calculate beat position
        beat_position = (time / self.ppq) % 4  # Position within 4-beat bar
        sixteenth_position = int((beat_position * 4) % 16)  # 0-15
        
        adjustment_ticks = 0
        
        # Apply swing to offbeats (odd 16th notes)
        if sixteenth_position % 2 == 1:
            # Swing amount: deviation from 50% (straight 16ths)
            swing_deviation = (groove.swing_percentage - 50) / 100
            sixteenth_ticks = self.ppq // 4
            swing_ticks = int(sixteenth_ticks * swing_deviation * intensity)
            adjustment_ticks += swing_ticks
        
        # Apply push/pull for this note category
        if note_category in groove.push_pull:
            # Convert ms to ticks
            # At 120 BPM, quarter note = 500ms
            # So ms_to_ticks = (ms / 500) * ppq * (120 / actual_tempo)
            tempo_factor = 120 / groove.tempo_bpm
            ms = groove.push_pull[note_category]
            push_pull_ticks = int((ms / 500) * self.ppq * tempo_factor * intensity)
            adjustment_ticks += push_pull_ticks
        
        return time + adjustment_ticks
    
    def _apply_velocity(
        self,
        velocity: int,
        time: int,
        note_category: str,
        groove: GrooveTemplate,
        intensity: float
    ) -> int:
        """Apply velocity adjustments (humanization + accents)"""
        # Start with base velocity for this note type
        if note_category in groove.velocity_map:
            base_velocity = groove.velocity_map[note_category]
        else:
            base_velocity = velocity
        
        # Blend original with groove velocity based on intensity
        blended_velocity = int(
            velocity * (1 - intensity) + base_velocity * intensity
        )
        
        # Check if this beat should be accented
        beat_position = (time / self.ppq) % 4
        sixteenth_position = int((beat_position * 4) % 16)
        
        if sixteenth_position in groove.accent_pattern:
            # Apply accent (20% boost)
            blended_velocity = int(blended_velocity * 1.2)
        
        # Apply slight random humanization (±5 velocity)
        import random
        humanization = random.randint(-5, 5)
        blended_velocity += int(humanization * intensity)
        
        # Clamp to valid MIDI range
        return max(1, min(127, blended_velocity))
    
    def get_genre_template(self, genre: str) -> Optional[GrooveTemplate]:
        """Get a built-in genre template"""
        return self.GENRE_TEMPLATES.get(genre.lower())
    
    def list_genre_templates(self) -> List[str]:
        """List available genre templates"""
        return list(self.GENRE_TEMPLATES.keys())


# ============================================================================
# GENRE TEMPLATE LIBRARY
# ============================================================================

def create_genre_library(output_dir: str = "/mnt/user-data/outputs/groove_templates"):
    """Create a library of genre groove templates"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    applicator = GrooveApplicator()
    
    for genre_name, template in applicator.GENRE_TEMPLATES.items():
        filepath = f"{output_dir}/{genre_name}.json"
        template.save(filepath)
        print(f"✓ Saved: {filepath}")
    
    print(f"\n✓ Genre library created: {output_dir}")
    print(f"  Templates: {', '.join(applicator.list_genre_templates())}")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("GROOVE APPLICATOR - Example Usage")
    print("=" * 70 + "\n")
    
    # Create genre library
    print("Creating genre groove library...")
    create_genre_library()
    
    print("\n" + "=" * 70)
    print("APPLYING GROOVES TO TEST PATTERN")
    print("=" * 70 + "\n")
    
    # Create a quantized (robotic) test pattern
    import mido
    
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    tempo = mido.bpm2tempo(95)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))
    
    ppq = mid.ticks_per_beat
    sixteenth = ppq // 4
    
    # Perfectly quantized pattern (no groove)
    # K-h-K-h-S-h-K-h (repeat)
    pattern = [
        (36, 100),  # Kick
        (42, 80),   # Hihat
        (36, 100),  # Kick
        (42, 80),   # Hihat
        (38, 100),  # Snare
        (42, 80),   # Hihat
        (36, 100),  # Kick
        (42, 80),   # Hihat
    ]
    
    # Add notes (perfectly quantized)
    for note, velocity in pattern * 4:  # 4 bars
        track.append(mido.Message('note_on', note=note, velocity=velocity, time=0))
        track.append(mido.Message('note_off', note=note, velocity=0, time=sixteenth))
    
    # Save quantized version
    quantized_path = "/home/claude/quantized_pattern.mid"
    mid.save(quantized_path)
    print(f"✓ Created quantized pattern: {quantized_path}\n")
    
    # Apply different grooves
    applicator = GrooveApplicator()
    
    grooves_to_test = ['funk', 'boom_bap', 'dilla', 'straight']
    
    for genre in grooves_to_test:
        groove = applicator.get_genre_template(genre)
        output_path = f"/mnt/user-data/outputs/groove_applied_{genre}.mid"
        
        applicator.apply_groove(
            quantized_path,
            output_path,
            groove,
            intensity=1.0
        )
        print()
    
    print("=" * 70)
    print("COMPARISON FILES CREATED")
    print("=" * 70)
    print("\nImport these into your DAW to hear the difference:")
    print("  • quantized_pattern.mid (robotic, no feel)")
    print("  • groove_applied_funk.mid (funk pocket)")
    print("  • groove_applied_boom_bap.mid (hip-hop pocket)")
    print("  • groove_applied_dilla.mid (J Dilla swing)")
    print("  • groove_applied_straight.mid (tight but humanized)")
    print("\n" + "=" * 70)
