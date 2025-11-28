#!/usr/bin/env python3
"""
Groove Template Extractor
Extract push/pull signatures, swing curves, and pocket maps from MIDI files.

Part of the Music Brain system.
Complements MAESTRO timing extraction with structured groove templates.
"""

import argparse
import json
import os
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import statistics

# MIDI parsing
try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False
    print("Error: mido required. Install with: pip install mido")

# ============================================================================
# Configuration
# ============================================================================

DB_PATH = Path.home() / "Music-Brain" / "groove-library" / "groove_templates.db"
TEMPLATES_PATH = Path.home() / "Music-Brain" / "groove-library" / "templates"

# Standard PPQ (pulses per quarter note) - we normalize to this
STANDARD_PPQ = 480

# GM Drum Map (channel 10)
GM_DRUM_MAP = {
    35: 'kick', 36: 'kick',
    38: 'snare', 40: 'snare',
    37: 'sidestick',
    42: 'hihat_closed', 44: 'hihat_pedal', 46: 'hihat_open',
    41: 'tom_low', 43: 'tom_low', 45: 'tom_mid', 47: 'tom_mid', 48: 'tom_high', 50: 'tom_high',
    49: 'crash', 57: 'crash',
    51: 'ride', 59: 'ride',
    39: 'clap',
    56: 'cowbell',
    54: 'tambourine',
}

# Instrument classification by channel/program
INSTRUMENT_CLASSES = {
    'drums': 'drums',
    'bass': 'bass',
    'keys': 'keys',
    'guitar': 'guitar',
    'strings': 'strings',
    'brass': 'brass',
    'lead': 'lead',
    'pad': 'pad',
}

# ============================================================================
# Database Setup
# ============================================================================

def init_database():
    """Initialize SQLite database for groove templates."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    TEMPLATES_PATH.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Main groove templates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groove_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            source_file TEXT,
            genre TEXT,
            subgenre TEXT,
            bpm_original REAL,
            time_signature TEXT DEFAULT '4/4',
            bars INTEGER,
            ppq INTEGER,
            date_extracted TEXT,
            notes TEXT
        )
    ''')
    
    # Push/pull signatures per instrument
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS push_pull_signatures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id INTEGER,
            instrument TEXT NOT NULL,
            beat_position REAL,
            offset_ticks REAL,
            offset_ms REAL,
            velocity_mean REAL,
            velocity_std REAL,
            sample_count INTEGER,
            FOREIGN KEY (template_id) REFERENCES groove_templates(id)
        )
    ''')
    
    # Swing curves (per beat subdivision)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS swing_curves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id INTEGER,
            instrument TEXT,
            subdivision INTEGER,
            swing_ratio REAL,
            swing_std REAL,
            sample_count INTEGER,
            FOREIGN KEY (template_id) REFERENCES groove_templates(id)
        )
    ''')
    
    # Cross-instrument stagger (timing relationships)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instrument_stagger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id INTEGER,
            instrument_a TEXT,
            instrument_b TEXT,
            beat_position REAL,
            mean_offset_ticks REAL,
            std_offset_ticks REAL,
            correlation REAL,
            sample_count INTEGER,
            FOREIGN KEY (template_id) REFERENCES groove_templates(id)
        )
    ''')
    
    # Velocity curves
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS velocity_curves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id INTEGER,
            instrument TEXT,
            beat_position REAL,
            velocity_mean REAL,
            velocity_std REAL,
            velocity_min REAL,
            velocity_max REAL,
            sample_count INTEGER,
            FOREIGN KEY (template_id) REFERENCES groove_templates(id)
        )
    ''')
    
    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_template_genre ON groove_templates(genre)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pushpull_template ON push_pull_signatures(template_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_swing_template ON swing_curves(template_id)')
    
    conn.commit()
    conn.close()
    print(f"Database initialized: {DB_PATH}")

def get_connection():
    """Get database connection."""
    if not DB_PATH.exists():
        init_database()
    return sqlite3.connect(DB_PATH)

# ============================================================================
# MIDI Parsing
# ============================================================================

def load_midi(filepath):
    """Load MIDI file and return parsed data."""
    if not MIDO_AVAILABLE:
        raise ImportError("mido library required")
    
    mid = mido.MidiFile(filepath)
    return mid

def get_ppq(mid):
    """Get ticks per beat from MIDI file."""
    return mid.ticks_per_beat

def normalize_ticks(ticks, source_ppq, target_ppq=STANDARD_PPQ):
    """Normalize ticks to standard PPQ."""
    return (ticks / source_ppq) * target_ppq

def get_tempo_from_midi(mid):
    """Extract tempo from MIDI file."""
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                return mido.tempo2bpm(msg.tempo)
    return 120.0  # Default

def classify_instrument(channel, program=None):
    """Classify instrument by channel and program number."""
    if channel == 9:  # Channel 10 in 1-indexed (drums)
        return 'drums'
    
    if program is None:
        return 'unknown'
    
    # GM program classification
    if 0 <= program <= 7:
        return 'keys'  # Piano
    elif 8 <= program <= 15:
        return 'keys'  # Chromatic percussion
    elif 16 <= program <= 23:
        return 'keys'  # Organ
    elif 24 <= program <= 31:
        return 'guitar'
    elif 32 <= program <= 39:
        return 'bass'
    elif 40 <= program <= 47:
        return 'strings'
    elif 48 <= program <= 55:
        return 'strings'  # Ensemble
    elif 56 <= program <= 63:
        return 'brass'
    elif 64 <= program <= 71:
        return 'brass'  # Reed
    elif 72 <= program <= 79:
        return 'lead'  # Pipe
    elif 80 <= program <= 87:
        return 'lead'  # Synth lead
    elif 88 <= program <= 95:
        return 'pad'
    else:
        return 'other'

def extract_notes_by_instrument(mid):
    """
    Extract all notes organized by instrument.
    Returns dict: {instrument: [(tick, note, velocity, duration), ...]}
    """
    ppq = get_ppq(mid)
    instruments = defaultdict(list)
    
    for track in mid.tracks:
        current_program = {}  # channel -> program
        current_tick = 0
        active_notes = {}  # (channel, note) -> (start_tick, velocity)
        
        for msg in track:
            current_tick += msg.time
            
            if msg.type == 'program_change':
                current_program[msg.channel] = msg.program
            
            elif msg.type == 'note_on' and msg.velocity > 0:
                key = (msg.channel, msg.note)
                active_notes[key] = (current_tick, msg.velocity)
            
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                key = (msg.channel, msg.note)
                if key in active_notes:
                    start_tick, velocity = active_notes.pop(key)
                    duration = current_tick - start_tick
                    
                    # Classify instrument
                    program = current_program.get(msg.channel, 0)
                    inst_class = classify_instrument(msg.channel, program)
                    
                    # For drums, also classify by note
                    if inst_class == 'drums' and msg.note in GM_DRUM_MAP:
                        drum_type = GM_DRUM_MAP[msg.note]
                        instruments[f'drums_{drum_type}'].append({
                            'tick': start_tick,
                            'note': msg.note,
                            'velocity': velocity,
                            'duration': duration,
                            'channel': msg.channel
                        })
                    
                    instruments[inst_class].append({
                        'tick': start_tick,
                        'note': msg.note,
                        'velocity': velocity,
                        'duration': duration,
                        'channel': msg.channel
                    })
    
    return dict(instruments), ppq

# ============================================================================
# Groove Analysis
# ============================================================================

def calculate_beat_position(tick, ppq, beats_per_bar=4):
    """
    Calculate position within a bar.
    Returns (bar_number, beat_in_bar, tick_offset_from_beat)
    """
    ticks_per_bar = ppq * beats_per_bar
    ticks_per_beat = ppq
    
    bar = tick // ticks_per_bar
    tick_in_bar = tick % ticks_per_bar
    beat_in_bar = tick_in_bar // ticks_per_beat
    tick_offset = tick_in_bar % ticks_per_beat
    
    # Calculate position as fraction of bar (0.0 to 4.0 for 4/4)
    beat_position = beat_in_bar + (tick_offset / ticks_per_beat)
    
    return bar, beat_position, tick_offset

def quantize_to_grid(tick, ppq, grid_division=16):
    """
    Find nearest grid position and offset from it.
    grid_division: 4=quarter, 8=eighth, 16=sixteenth, etc.
    """
    ticks_per_grid = (ppq * 4) / grid_division  # PPQ is per quarter note
    
    nearest_grid = round(tick / ticks_per_grid) * ticks_per_grid
    offset = tick - nearest_grid
    
    return nearest_grid, offset

def extract_push_pull_signature(notes, ppq, grid_division=16):
    """
    Extract push/pull timing signature.
    Returns offsets from grid for each beat position.
    """
    ticks_per_grid = (ppq * 4) / grid_division
    
    # Group notes by their quantized grid position
    grid_positions = defaultdict(list)
    
    for note in notes:
        tick = note['tick']
        nearest_grid, offset = quantize_to_grid(tick, ppq, grid_division)
        
        # Normalize grid position to within one bar (0-15 for 16th notes in 4/4)
        bar_length = ppq * 4  # Ticks per bar in 4/4
        grid_in_bar = (nearest_grid % bar_length) / ticks_per_grid
        
        grid_positions[grid_in_bar].append({
            'offset_ticks': offset,
            'velocity': note['velocity']
        })
    
    # Calculate statistics for each grid position
    signature = {}
    for grid_pos, hits in grid_positions.items():
        if len(hits) >= 2:  # Need multiple samples
            offsets = [h['offset_ticks'] for h in hits]
            velocities = [h['velocity'] for h in hits]
            
            signature[grid_pos] = {
                'offset_mean': statistics.mean(offsets),
                'offset_std': statistics.stdev(offsets) if len(offsets) > 1 else 0,
                'velocity_mean': statistics.mean(velocities),
                'velocity_std': statistics.stdev(velocities) if len(velocities) > 1 else 0,
                'count': len(hits)
            }
    
    return signature

def extract_swing_curve(notes, ppq):
    """
    Extract swing curve from notes.
    Measures the delay of off-beat notes (the "ands").
    """
    ticks_per_eighth = ppq / 2
    
    # Group by eighth note position
    eighth_positions = defaultdict(list)
    
    for note in notes:
        tick = note['tick']
        bar_length = ppq * 4
        tick_in_bar = tick % bar_length
        
        # Find nearest eighth note
        eighth_pos = round(tick_in_bar / ticks_per_eighth)
        offset = tick_in_bar - (eighth_pos * ticks_per_eighth)
        
        eighth_positions[eighth_pos % 8].append(offset)
    
    # Calculate swing ratio
    # Swing = ratio between on-beat and off-beat timing
    swing_data = {}
    
    for pos in range(8):
        if pos in eighth_positions and len(eighth_positions[pos]) >= 2:
            offsets = eighth_positions[pos]
            swing_data[pos] = {
                'mean_offset': statistics.mean(offsets),
                'std_offset': statistics.stdev(offsets) if len(offsets) > 1 else 0,
                'count': len(offsets)
            }
    
    # Calculate swing ratio (off-beats vs on-beats)
    # Traditional swing: 66% = triplet feel, 50% = straight
    on_beat_offsets = []
    off_beat_offsets = []
    
    for pos, data in swing_data.items():
        if pos % 2 == 0:  # On-beat (0, 2, 4, 6)
            on_beat_offsets.append(data['mean_offset'])
        else:  # Off-beat (1, 3, 5, 7)
            off_beat_offsets.append(data['mean_offset'])
    
    swing_ratio = None
    if on_beat_offsets and off_beat_offsets:
        # Swing ratio: how much later the off-beats are
        on_mean = statistics.mean(on_beat_offsets)
        off_mean = statistics.mean(off_beat_offsets)
        
        # Convert to swing percentage (50% = straight, 66% = triplet)
        # Offset difference as fraction of eighth note
        offset_diff = off_mean - on_mean
        swing_ratio = 50 + (offset_diff / ticks_per_eighth) * 50
    
    return {
        'positions': swing_data,
        'swing_ratio': swing_ratio
    }

def extract_instrument_stagger(instruments_data, ppq, grid_division=16):
    """
    Calculate timing relationships between instruments.
    Returns stagger data for each instrument pair.
    """
    ticks_per_grid = (ppq * 4) / grid_division
    bar_length = ppq * 4
    
    # Build grid-aligned hit maps for each instrument
    instrument_grids = {}
    
    for inst, notes in instruments_data.items():
        grid_map = defaultdict(list)
        for note in notes:
            tick = note['tick']
            nearest_grid, offset = quantize_to_grid(tick, ppq, grid_division)
            grid_in_bar = int((nearest_grid % bar_length) / ticks_per_grid)
            grid_map[grid_in_bar].append(offset)
        instrument_grids[inst] = grid_map
    
    # Calculate stagger between instrument pairs
    stagger_data = {}
    instruments = list(instrument_grids.keys())
    
    for i, inst_a in enumerate(instruments):
        for inst_b in instruments[i+1:]:
            pair_key = f"{inst_a}_vs_{inst_b}"
            pair_staggers = []
            
            # Find grid positions where both instruments play
            common_grids = set(instrument_grids[inst_a].keys()) & set(instrument_grids[inst_b].keys())
            
            for grid in common_grids:
                offsets_a = instrument_grids[inst_a][grid]
                offsets_b = instrument_grids[inst_b][grid]
                
                # Calculate mean offset difference
                mean_a = statistics.mean(offsets_a)
                mean_b = statistics.mean(offsets_b)
                stagger = mean_b - mean_a  # Positive = B is later
                
                pair_staggers.append({
                    'grid': grid,
                    'stagger': stagger,
                    'count_a': len(offsets_a),
                    'count_b': len(offsets_b)
                })
            
            if pair_staggers:
                staggers = [p['stagger'] for p in pair_staggers]
                stagger_data[pair_key] = {
                    'mean_stagger': statistics.mean(staggers),
                    'std_stagger': statistics.stdev(staggers) if len(staggers) > 1 else 0,
                    'by_grid': pair_staggers
                }
    
    return stagger_data

def extract_velocity_curve(notes, ppq):
    """
    Extract velocity patterns by beat position.
    """
    bar_length = ppq * 4
    ticks_per_sixteenth = ppq / 4
    
    position_velocities = defaultdict(list)
    
    for note in notes:
        tick = note['tick']
        tick_in_bar = tick % bar_length
        position = int(tick_in_bar / ticks_per_sixteenth)  # 0-15 for 16ths
        position_velocities[position].append(note['velocity'])
    
    velocity_curve = {}
    for pos, velocities in position_velocities.items():
        if velocities:
            velocity_curve[pos] = {
                'mean': statistics.mean(velocities),
                'std': statistics.stdev(velocities) if len(velocities) > 1 else 0,
                'min': min(velocities),
                'max': max(velocities),
                'count': len(velocities)
            }
    
    return velocity_curve

# ============================================================================
# Full Extraction Pipeline
# ============================================================================

def extract_groove_template(filepath, name=None, genre=None, subgenre=None):
    """
    Extract complete groove template from MIDI file.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    print(f"Extracting groove from: {filepath.name}")
    
    # Load MIDI
    mid = load_midi(str(filepath))
    ppq = get_ppq(mid)
    bpm = get_tempo_from_midi(mid)
    
    # Extract notes by instrument
    instruments_data, ppq = extract_notes_by_instrument(mid)
    
    print(f"  PPQ: {ppq}, BPM: {bpm:.1f}")
    print(f"  Instruments found: {list(instruments_data.keys())}")
    
    # Calculate total bars
    max_tick = 0
    for notes in instruments_data.values():
        if notes:
            max_tick = max(max_tick, max(n['tick'] for n in notes))
    total_bars = (max_tick // (ppq * 4)) + 1
    
    # Extract groove data for each instrument
    groove_data = {
        'metadata': {
            'name': name or filepath.stem,
            'source_file': str(filepath),
            'genre': genre,
            'subgenre': subgenre,
            'bpm': bpm,
            'ppq': ppq,
            'bars': total_bars,
            'time_signature': '4/4',
            'date_extracted': datetime.now().isoformat()
        },
        'push_pull': {},
        'swing': {},
        'velocity_curves': {},
        'instrument_stagger': {}
    }
    
    # Extract per-instrument data
    for inst, notes in instruments_data.items():
        if len(notes) < 4:  # Skip sparse instruments
            continue
            
        print(f"  Analyzing: {inst} ({len(notes)} notes)")
        
        # Push/pull signature
        groove_data['push_pull'][inst] = extract_push_pull_signature(notes, ppq)
        
        # Swing curve
        groove_data['swing'][inst] = extract_swing_curve(notes, ppq)
        
        # Velocity curve
        groove_data['velocity_curves'][inst] = extract_velocity_curve(notes, ppq)
    
    # Cross-instrument stagger
    groove_data['instrument_stagger'] = extract_instrument_stagger(instruments_data, ppq)
    
    return groove_data

def save_groove_template(groove_data, output_path=None):
    """Save groove template to JSON file."""
    if output_path is None:
        name = groove_data['metadata']['name']
        output_path = TEMPLATES_PATH / f"{name}.json"
    else:
        output_path = Path(output_path)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(groove_data, f, indent=2)
    
    print(f"Saved template: {output_path}")
    return output_path

def save_to_database(groove_data):
    """Save groove template to SQLite database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    meta = groove_data['metadata']
    
    # Insert main template record
    cursor.execute('''
        INSERT INTO groove_templates 
        (name, source_file, genre, subgenre, bpm_original, time_signature, bars, ppq, date_extracted)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        meta['name'],
        meta['source_file'],
        meta['genre'],
        meta['subgenre'],
        meta['bpm'],
        meta['time_signature'],
        meta['bars'],
        meta['ppq'],
        meta['date_extracted']
    ))
    
    template_id = cursor.lastrowid
    
    # Insert push/pull signatures
    for inst, signature in groove_data['push_pull'].items():
        for beat_pos, data in signature.items():
            cursor.execute('''
                INSERT INTO push_pull_signatures
                (template_id, instrument, beat_position, offset_ticks, velocity_mean, velocity_std, sample_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                template_id, inst, float(beat_pos),
                data['offset_mean'], data['velocity_mean'], data['velocity_std'], data['count']
            ))
    
    # Insert swing curves
    for inst, swing_data in groove_data['swing'].items():
        if swing_data['swing_ratio']:
            for pos, data in swing_data['positions'].items():
                cursor.execute('''
                    INSERT INTO swing_curves
                    (template_id, instrument, subdivision, swing_ratio, swing_std, sample_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    template_id, inst, pos,
                    swing_data['swing_ratio'], data['std_offset'], data['count']
                ))
    
    # Insert velocity curves
    for inst, vel_curve in groove_data['velocity_curves'].items():
        for beat_pos, data in vel_curve.items():
            cursor.execute('''
                INSERT INTO velocity_curves
                (template_id, instrument, beat_position, velocity_mean, velocity_std, velocity_min, velocity_max, sample_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                template_id, inst, float(beat_pos),
                data['mean'], data['std'], data['min'], data['max'], data['count']
            ))
    
    # Insert instrument stagger
    for pair, data in groove_data['instrument_stagger'].items():
        parts = pair.split('_vs_')
        if len(parts) == 2:
            cursor.execute('''
                INSERT INTO instrument_stagger
                (template_id, instrument_a, instrument_b, mean_offset_ticks, std_offset_ticks, sample_count)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                template_id, parts[0], parts[1],
                data['mean_stagger'], data['std_stagger'], len(data['by_grid'])
            ))
    
    conn.commit()
    conn.close()
    
    print(f"Saved to database with ID: {template_id}")
    return template_id

# ============================================================================
# Batch Processing
# ============================================================================

def scan_folder(folder_path, genre=None, recursive=True):
    """Scan folder for MIDI files and extract groove templates."""
    folder = Path(folder_path).expanduser().resolve()
    
    if not folder.exists():
        print(f"Error: Folder not found: {folder}")
        return
    
    # Find MIDI files
    pattern = '**/*.mid' if recursive else '*.mid'
    midi_files = list(folder.glob(pattern))
    midi_files.extend(folder.glob(pattern.replace('.mid', '.midi')))
    
    print(f"Found {len(midi_files)} MIDI files in {folder}")
    print("-" * 50)
    
    extracted = 0
    errors = 0
    
    for filepath in midi_files:
        try:
            groove_data = extract_groove_template(
                filepath,
                genre=genre,
                subgenre=filepath.parent.name if filepath.parent != folder else None
            )
            
            save_groove_template(groove_data)
            save_to_database(groove_data)
            extracted += 1
            
        except Exception as e:
            print(f"  Error processing {filepath.name}: {e}")
            errors += 1
    
    print("-" * 50)
    print(f"Extracted: {extracted}")
    print(f"Errors: {errors}")

# ============================================================================
# Query Functions
# ============================================================================

def list_templates(genre=None, limit=50):
    """List all groove templates."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if genre:
        cursor.execute('''
            SELECT id, name, genre, subgenre, bpm_original, bars
            FROM groove_templates
            WHERE genre LIKE ?
            ORDER BY name
            LIMIT ?
        ''', (f'%{genre}%', limit))
    else:
        cursor.execute('''
            SELECT id, name, genre, subgenre, bpm_original, bars
            FROM groove_templates
            ORDER BY name
            LIMIT ?
        ''', (limit,))
    
    results = cursor.fetchall()
    conn.close()
    
    print(f"\n{'ID':<6} {'Name':<30} {'Genre':<15} {'BPM':<8} {'Bars':<6}")
    print("-" * 70)
    
    for row in results:
        id_, name, genre, subgenre, bpm, bars = row
        name_display = name[:28] + '..' if len(name) > 30 else name
        genre_display = f"{genre or ''}/{subgenre or ''}"[:13]
        print(f"{id_:<6} {name_display:<30} {genre_display:<15} {bpm or '?':<8} {bars or '?':<6}")

def get_template_detail(template_id):
    """Get detailed groove template data."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get main template info
    cursor.execute('SELECT * FROM groove_templates WHERE id = ?', (template_id,))
    template = cursor.fetchone()
    
    if not template:
        print(f"Template {template_id} not found")
        return
    
    print(f"\n{'='*60}")
    print(f"Template: {template[1]}")
    print(f"Genre: {template[3] or 'Unknown'} / {template[4] or ''}")
    print(f"BPM: {template[5]}, Bars: {template[7]}")
    print(f"{'='*60}")
    
    # Get push/pull signatures
    cursor.execute('''
        SELECT instrument, beat_position, offset_ticks, velocity_mean
        FROM push_pull_signatures
        WHERE template_id = ?
        ORDER BY instrument, beat_position
    ''', (template_id,))
    
    push_pull = cursor.fetchall()
    
    print(f"\nPush/Pull Signatures:")
    print(f"{'Instrument':<20} {'Beat':<8} {'Offset':<12} {'Velocity':<10}")
    print("-" * 50)
    
    for inst, beat, offset, vel in push_pull:
        print(f"{inst:<20} {beat:<8.2f} {offset:+.1f} ticks  {vel:.0f}")
    
    # Get swing data
    cursor.execute('''
        SELECT instrument, swing_ratio
        FROM swing_curves
        WHERE template_id = ?
        GROUP BY instrument
    ''', (template_id,))
    
    swing = cursor.fetchall()
    
    print(f"\nSwing Ratios:")
    for inst, ratio in swing:
        print(f"  {inst}: {ratio:.1f}%")
    
    # Get instrument stagger
    cursor.execute('''
        SELECT instrument_a, instrument_b, mean_offset_ticks
        FROM instrument_stagger
        WHERE template_id = ?
    ''', (template_id,))
    
    stagger = cursor.fetchall()
    
    print(f"\nInstrument Stagger:")
    for inst_a, inst_b, offset in stagger:
        direction = "ahead" if offset < 0 else "behind"
        print(f"  {inst_b} is {abs(offset):.1f} ticks {direction} {inst_a}")
    
    conn.close()

def export_template(template_id, output_path):
    """Export template to JSON file."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Fetch all data and rebuild JSON structure
    cursor.execute('SELECT * FROM groove_templates WHERE id = ?', (template_id,))
    template = cursor.fetchone()
    
    if not template:
        print(f"Template {template_id} not found")
        return
    
    # Build export structure
    export_data = {
        'metadata': {
            'id': template[0],
            'name': template[1],
            'source_file': template[2],
            'genre': template[3],
            'subgenre': template[4],
            'bpm': template[5],
            'time_signature': template[6],
            'bars': template[7],
            'ppq': template[8],
            'date_extracted': template[9]
        },
        'push_pull': {},
        'swing': {},
        'velocity_curves': {},
        'instrument_stagger': {}
    }
    
    # Add push/pull data
    cursor.execute('''
        SELECT instrument, beat_position, offset_ticks, velocity_mean, velocity_std, sample_count
        FROM push_pull_signatures WHERE template_id = ?
    ''', (template_id,))
    
    for row in cursor.fetchall():
        inst = row[0]
        if inst not in export_data['push_pull']:
            export_data['push_pull'][inst] = {}
        export_data['push_pull'][inst][row[1]] = {
            'offset_mean': row[2],
            'velocity_mean': row[3],
            'velocity_std': row[4],
            'count': row[5]
        }
    
    conn.close()
    
    output_path = Path(output_path)
    with open(output_path, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"Exported to: {output_path}")

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Groove Template Extractor - Extract timing and feel from MIDI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s extract song.mid --genre jazz
  %(prog)s scan ~/MIDI/DrumLoops --genre hiphop
  %(prog)s list --genre rock
  %(prog)s detail 5
  %(prog)s export 5 --output groove.json
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract groove from MIDI file')
    extract_parser.add_argument('file', help='MIDI file path')
    extract_parser.add_argument('--name', help='Template name')
    extract_parser.add_argument('--genre', help='Genre tag')
    extract_parser.add_argument('--subgenre', help='Subgenre tag')
    extract_parser.add_argument('--output', help='Output JSON path')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan folder for MIDI files')
    scan_parser.add_argument('folder', help='Folder path')
    scan_parser.add_argument('--genre', help='Genre tag for all files')
    scan_parser.add_argument('--no-recursive', action='store_true')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List templates')
    list_parser.add_argument('--genre', help='Filter by genre')
    list_parser.add_argument('--limit', type=int, default=50)
    
    # Detail command
    detail_parser = subparsers.add_parser('detail', help='Show template details')
    detail_parser.add_argument('id', type=int, help='Template ID')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export template to JSON')
    export_parser.add_argument('id', type=int, help='Template ID')
    export_parser.add_argument('--output', required=True, help='Output file path')
    
    # Init command
    subparsers.add_parser('init', help='Initialize database')
    
    args = parser.parse_args()
    
    if args.command == 'extract':
        groove_data = extract_groove_template(
            args.file,
            name=args.name,
            genre=args.genre,
            subgenre=args.subgenre
        )
        if args.output:
            save_groove_template(groove_data, args.output)
        else:
            save_groove_template(groove_data)
        save_to_database(groove_data)
    
    elif args.command == 'scan':
        scan_folder(args.folder, genre=args.genre, recursive=not args.no_recursive)
    
    elif args.command == 'list':
        list_templates(genre=args.genre, limit=args.limit)
    
    elif args.command == 'detail':
        get_template_detail(args.id)
    
    elif args.command == 'export':
        export_template(args.id, args.output)
    
    elif args.command == 'init':
        init_database()
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
