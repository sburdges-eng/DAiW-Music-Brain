#!/usr/bin/env python3
"""
Groove Applicator
Apply groove templates and genre pocket maps to MIDI files.

Takes extracted groove data and applies it to quantized/robotic MIDI
to humanize timing, velocity, and feel.
"""

import argparse
import json
import random
from pathlib import Path
from copy import deepcopy

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False
    print("Error: mido required. Install with: pip install mido")

# ============================================================================
# Configuration
# ============================================================================

TEMPLATES_PATH = Path.home() / "Music-Brain" / "groove-library" / "templates"
POCKET_MAPS_PATH = Path(__file__).parent / "genre_pocket_maps.json"

STANDARD_PPQ = 480

# GM Drum Map
GM_DRUM_MAP = {
    35: 'kick', 36: 'kick',
    38: 'snare', 40: 'snare',
    37: 'sidestick',
    42: 'hihat_closed', 44: 'hihat_pedal', 46: 'hihat_open',
    41: 'tom_low', 43: 'tom_low', 45: 'tom_mid', 47: 'tom_mid', 48: 'tom_high', 50: 'tom_high',
    49: 'crash', 57: 'crash',
    51: 'ride', 59: 'ride',
}

# Reverse map for drum names
DRUM_NAMES_TO_NOTES = {}
for note, name in GM_DRUM_MAP.items():
    if name not in DRUM_NAMES_TO_NOTES:
        DRUM_NAMES_TO_NOTES[name] = []
    DRUM_NAMES_TO_NOTES[name].append(note)

# ============================================================================
# Load Data
# ============================================================================

def load_pocket_maps():
    """Load genre pocket maps from JSON."""
    if POCKET_MAPS_PATH.exists():
        with open(POCKET_MAPS_PATH, 'r') as f:
            return json.load(f)
    return {}

def load_groove_template(template_path):
    """Load groove template from JSON file."""
    with open(template_path, 'r') as f:
        return json.load(f)

def list_genres():
    """List available genre pocket maps."""
    maps = load_pocket_maps()
    print("\nAvailable Genre Pocket Maps:\n")
    for key, data in maps.items():
        if key.startswith('_'):
            continue
        bpm = data.get('bpm_range', [0, 0])
        swing = data.get('swing', {}).get('overall', 50)
        print(f"  {key:<15} {data['name']:<25} BPM: {bpm[0]}-{bpm[1]}, Swing: {swing}%")

def list_templates():
    """List available groove templates."""
    if not TEMPLATES_PATH.exists():
        print("No templates found. Extract some with groove_extractor.py first.")
        return
    
    templates = list(TEMPLATES_PATH.glob("*.json"))
    print(f"\nAvailable Groove Templates ({len(templates)}):\n")
    for t in templates[:20]:
        print(f"  {t.stem}")
    if len(templates) > 20:
        print(f"  ... and {len(templates) - 20} more")

# ============================================================================
# MIDI Processing
# ============================================================================

def classify_note(channel, note):
    """Classify a MIDI note by instrument type."""
    if channel == 9:  # Drums
        return GM_DRUM_MAP.get(note, 'drums_other')
    return 'melodic'

def get_beat_position(tick, ppq, beats_per_bar=4):
    """Get position in bar (0.0 to beats_per_bar)."""
    ticks_per_bar = ppq * beats_per_bar
    tick_in_bar = tick % ticks_per_bar
    return tick_in_bar / ppq

def apply_timing_offset(tick, offset_ticks, randomness=0.3):
    """Apply timing offset with optional randomness."""
    if randomness > 0:
        # Add human variation
        variation = random.gauss(0, abs(offset_ticks) * randomness)
        offset_ticks += variation
    return int(tick + offset_ticks)

def apply_velocity_curve(velocity, target_mean, target_std, randomness=0.2):
    """Apply velocity transformation with variation."""
    # Center around target mean
    diff = target_mean - 85  # Assume 85 is "neutral"
    new_vel = velocity + diff
    
    # Add variation
    if randomness > 0 and target_std > 0:
        variation = random.gauss(0, target_std * randomness)
        new_vel += variation
    
    # Clamp to valid range
    return max(1, min(127, int(new_vel)))

def apply_swing(tick, ppq, swing_ratio, grid_division=8):
    """
    Apply swing to a tick position.
    swing_ratio: 50 = straight, 66 = triplet feel
    """
    if swing_ratio == 50:
        return tick  # No swing
    
    ticks_per_grid = (ppq * 4) / grid_division
    
    # Find grid position
    grid_pos = tick / ticks_per_grid
    grid_index = int(grid_pos)
    
    # Only swing off-beat positions (odd indices for 8th note swing)
    if grid_index % 2 == 1:
        # Calculate swing offset
        swing_factor = (swing_ratio - 50) / 50  # 0 to 0.32 for 50-66%
        offset = ticks_per_grid * swing_factor
        return int(tick + offset)
    
    return tick

# ============================================================================
# Groove Application
# ============================================================================

def apply_genre_pocket(midi_path, genre, output_path=None, intensity=1.0):
    """
    Apply genre pocket map to MIDI file.
    
    intensity: 0.0 to 1.0 - how much to apply (1.0 = full effect)
    """
    if not MIDO_AVAILABLE:
        raise ImportError("mido required")
    
    pocket_maps = load_pocket_maps()
    if genre not in pocket_maps:
        print(f"Genre '{genre}' not found. Available: {[k for k in pocket_maps.keys() if not k.startswith('_')]}")
        return
    
    pocket = pocket_maps[genre]
    
    print(f"Applying '{pocket['name']}' pocket map...")
    print(f"  Swing: {pocket['swing']['overall']}%")
    print(f"  Intensity: {intensity*100:.0f}%")
    
    # Load MIDI
    mid = mido.MidiFile(midi_path)
    ppq = mid.ticks_per_beat
    
    # Create new MIDI with same structure
    new_mid = mido.MidiFile(ticks_per_beat=ppq)
    
    for track in mid.tracks:
        new_track = mido.MidiTrack()
        new_mid.tracks.append(new_track)
        
        current_tick = 0
        pending_events = []  # (absolute_tick, msg)
        
        for msg in track:
            current_tick += msg.time
            
            if msg.type in ['note_on', 'note_off']:
                new_tick = current_tick
                new_velocity = msg.velocity
                
                # Classify instrument
                inst_type = classify_note(msg.channel, msg.note)
                
                # Get push/pull offset for this instrument
                push_pull = pocket.get('push_pull', {})
                
                # Map drum types to generic
                lookup_type = inst_type
                if inst_type.startswith('drums_'):
                    drum_part = inst_type.replace('drums_', '')
                    if drum_part in ['kick']:
                        lookup_type = 'kick'
                    elif drum_part in ['snare', 'sidestick']:
                        lookup_type = 'snare'
                    elif drum_part.startswith('hihat'):
                        lookup_type = 'hihat'
                
                if lookup_type in push_pull:
                    offset = push_pull[lookup_type].get('offset', 0) * intensity
                    # Scale offset to this file's PPQ
                    offset_scaled = (offset / 480) * ppq
                    new_tick = apply_timing_offset(current_tick, offset_scaled, randomness=0.3)
                
                # Apply swing
                swing_data = pocket.get('swing', {})
                swing_ratio = swing_data.get('overall', 50)
                if inst_type.startswith('hihat'):
                    swing_ratio = swing_data.get('hihat', swing_ratio)
                
                swing_ratio = 50 + (swing_ratio - 50) * intensity  # Scale by intensity
                new_tick = apply_swing(new_tick, ppq, swing_ratio)
                
                # Apply velocity
                if msg.type == 'note_on' and msg.velocity > 0:
                    vel_data = pocket.get('velocity', {})
                    if lookup_type in vel_data:
                        vel_range = vel_data[lookup_type]
                        target_mean = (vel_range[0] + vel_range[1]) / 2
                        target_std = (vel_range[1] - vel_range[0]) / 4
                        new_velocity = apply_velocity_curve(
                            msg.velocity, target_mean, target_std,
                            randomness=0.25 * intensity
                        )
                
                # Ensure tick doesn't go negative
                new_tick = max(0, new_tick)
                
                # Create modified message
                new_msg = msg.copy()
                if hasattr(new_msg, 'velocity'):
                    new_msg.velocity = new_velocity
                
                pending_events.append((new_tick, new_msg))
            else:
                pending_events.append((current_tick, msg.copy()))
        
        # Sort events by time and convert to delta time
        pending_events.sort(key=lambda x: x[0])
        
        last_tick = 0
        for abs_tick, msg in pending_events:
            msg.time = abs_tick - last_tick
            if msg.time < 0:
                msg.time = 0
            new_track.append(msg)
            last_tick = abs_tick
    
    # Save output
    if output_path is None:
        stem = Path(midi_path).stem
        output_path = Path(midi_path).parent / f"{stem}_{genre}_groove.mid"
    
    new_mid.save(output_path)
    print(f"Saved: {output_path}")
    return output_path

def apply_template(midi_path, template_path, output_path=None, intensity=1.0):
    """
    Apply extracted groove template to MIDI file.
    """
    if not MIDO_AVAILABLE:
        raise ImportError("mido required")
    
    template = load_groove_template(template_path)
    
    print(f"Applying template: {template['metadata']['name']}")
    print(f"  Source: {template['metadata'].get('genre', 'Unknown')}")
    print(f"  Intensity: {intensity*100:.0f}%")
    
    # Load MIDI
    mid = mido.MidiFile(midi_path)
    ppq = mid.ticks_per_beat
    template_ppq = template['metadata'].get('ppq', 480)
    
    # Create new MIDI
    new_mid = mido.MidiFile(ticks_per_beat=ppq)
    
    for track in mid.tracks:
        new_track = mido.MidiTrack()
        new_mid.tracks.append(new_track)
        
        current_tick = 0
        pending_events = []
        
        for msg in track:
            current_tick += msg.time
            
            if msg.type in ['note_on', 'note_off']:
                new_tick = current_tick
                new_velocity = msg.velocity
                
                # Classify instrument
                inst_type = classify_note(msg.channel, msg.note)
                
                # Get beat position (0-15 for 16th notes)
                beat_pos = get_beat_position(current_tick, ppq)
                beat_pos_16th = int(beat_pos * 4) % 16  # Convert to 16th note position
                
                # Apply push/pull from template
                push_pull = template.get('push_pull', {})
                if inst_type in push_pull:
                    pp_data = push_pull[inst_type]
                    # Find closest beat position in template
                    closest_pos = min(pp_data.keys(), key=lambda x: abs(float(x) - beat_pos_16th), default=None)
                    if closest_pos:
                        offset = pp_data[closest_pos].get('offset_mean', 0) * intensity
                        # Scale to target PPQ
                        offset_scaled = (offset / template_ppq) * ppq
                        new_tick = apply_timing_offset(current_tick, offset_scaled, randomness=0.25)
                
                # Apply velocity curve from template
                if msg.type == 'note_on' and msg.velocity > 0:
                    vel_curves = template.get('velocity_curves', {})
                    if inst_type in vel_curves:
                        vel_data = vel_curves[inst_type]
                        closest_pos = min(vel_data.keys(), key=lambda x: abs(int(x) - beat_pos_16th), default=None)
                        if closest_pos:
                            target_mean = vel_data[closest_pos].get('mean', msg.velocity)
                            target_std = vel_data[closest_pos].get('std', 10)
                            new_velocity = apply_velocity_curve(
                                msg.velocity, target_mean, target_std,
                                randomness=0.3 * intensity
                            )
                
                # Apply swing from template
                swing_data = template.get('swing', {})
                if inst_type in swing_data:
                    swing_ratio = swing_data[inst_type].get('swing_ratio', 50)
                    if swing_ratio:
                        swing_ratio = 50 + (swing_ratio - 50) * intensity
                        new_tick = apply_swing(new_tick, ppq, swing_ratio)
                
                new_tick = max(0, new_tick)
                
                new_msg = msg.copy()
                if hasattr(new_msg, 'velocity'):
                    new_msg.velocity = new_velocity
                
                pending_events.append((new_tick, new_msg))
            else:
                pending_events.append((current_tick, msg.copy()))
        
        # Sort and convert to delta time
        pending_events.sort(key=lambda x: x[0])
        
        last_tick = 0
        for abs_tick, msg in pending_events:
            msg.time = abs_tick - last_tick
            if msg.time < 0:
                msg.time = 0
            new_track.append(msg)
            last_tick = abs_tick
    
    # Save
    if output_path is None:
        stem = Path(midi_path).stem
        output_path = Path(midi_path).parent / f"{stem}_grooved.mid"
    
    new_mid.save(output_path)
    print(f"Saved: {output_path}")
    return output_path

def humanize_basic(midi_path, output_path=None, timing_range=10, velocity_range=15, intensity=1.0):
    """
    Basic humanization without a template.
    Adds random timing and velocity variation.
    """
    if not MIDO_AVAILABLE:
        raise ImportError("mido required")
    
    print(f"Basic humanization...")
    print(f"  Timing range: ±{timing_range} ticks")
    print(f"  Velocity range: ±{velocity_range}")
    print(f"  Intensity: {intensity*100:.0f}%")
    
    mid = mido.MidiFile(midi_path)
    ppq = mid.ticks_per_beat
    
    new_mid = mido.MidiFile(ticks_per_beat=ppq)
    
    actual_timing = timing_range * intensity
    actual_velocity = velocity_range * intensity
    
    for track in mid.tracks:
        new_track = mido.MidiTrack()
        new_mid.tracks.append(new_track)
        
        current_tick = 0
        pending_events = []
        
        for msg in track:
            current_tick += msg.time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                # Random timing offset
                timing_offset = random.gauss(0, actual_timing / 2)
                new_tick = max(0, int(current_tick + timing_offset))
                
                # Random velocity offset
                vel_offset = random.gauss(0, actual_velocity / 2)
                new_velocity = max(1, min(127, int(msg.velocity + vel_offset)))
                
                new_msg = msg.copy()
                new_msg.velocity = new_velocity
                pending_events.append((new_tick, new_msg))
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                # Match note-off timing to note-on timing (approximately)
                timing_offset = random.gauss(0, actual_timing / 2)
                new_tick = max(0, int(current_tick + timing_offset))
                pending_events.append((new_tick, msg.copy()))
            else:
                pending_events.append((current_tick, msg.copy()))
        
        # Sort and convert
        pending_events.sort(key=lambda x: x[0])
        
        last_tick = 0
        for abs_tick, msg in pending_events:
            msg.time = abs_tick - last_tick
            if msg.time < 0:
                msg.time = 0
            new_track.append(msg)
            last_tick = abs_tick
    
    if output_path is None:
        stem = Path(midi_path).stem
        output_path = Path(midi_path).parent / f"{stem}_humanized.mid"
    
    new_mid.save(output_path)
    print(f"Saved: {output_path}")
    return output_path

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Groove Applicator - Apply groove templates to MIDI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s genre drums.mid hiphop
  %(prog)s genre song.mid jazz --intensity 0.7
  %(prog)s template drums.mid groove.json
  %(prog)s humanize song.mid --timing 15 --velocity 20
  %(prog)s list-genres
  %(prog)s list-templates
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Genre pocket command
    genre_parser = subparsers.add_parser('genre', help='Apply genre pocket map')
    genre_parser.add_argument('midi', help='Input MIDI file')
    genre_parser.add_argument('genre', help='Genre name (hiphop, jazz, rock, etc.)')
    genre_parser.add_argument('--output', '-o', help='Output file path')
    genre_parser.add_argument('--intensity', '-i', type=float, default=1.0, help='Effect intensity 0.0-1.0')
    
    # Template command
    template_parser = subparsers.add_parser('template', help='Apply groove template')
    template_parser.add_argument('midi', help='Input MIDI file')
    template_parser.add_argument('template', help='Template JSON file')
    template_parser.add_argument('--output', '-o', help='Output file path')
    template_parser.add_argument('--intensity', '-i', type=float, default=1.0, help='Effect intensity 0.0-1.0')
    
    # Basic humanize command
    humanize_parser = subparsers.add_parser('humanize', help='Basic humanization')
    humanize_parser.add_argument('midi', help='Input MIDI file')
    humanize_parser.add_argument('--output', '-o', help='Output file path')
    humanize_parser.add_argument('--timing', '-t', type=int, default=10, help='Timing variation in ticks')
    humanize_parser.add_argument('--velocity', '-v', type=int, default=15, help='Velocity variation')
    humanize_parser.add_argument('--intensity', '-i', type=float, default=1.0, help='Effect intensity 0.0-1.0')
    
    # List commands
    subparsers.add_parser('list-genres', help='List available genres')
    subparsers.add_parser('list-templates', help='List available templates')
    
    args = parser.parse_args()
    
    if args.command == 'genre':
        apply_genre_pocket(args.midi, args.genre, args.output, args.intensity)
    
    elif args.command == 'template':
        apply_template(args.midi, args.template, args.output, args.intensity)
    
    elif args.command == 'humanize':
        humanize_basic(args.midi, args.output, args.timing, args.velocity, args.intensity)
    
    elif args.command == 'list-genres':
        list_genres()
    
    elif args.command == 'list-templates':
        list_templates()
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
