#!/usr/bin/env python3
"""
Structural Pattern Extractor
Extract chord progressions, melody shapes, phrase lengths, and harmonic rhythm from MIDI.

Part of the Music Brain system.
Complements groove extraction with harmonic and melodic structure analysis.
"""

import argparse
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
import statistics
import itertools

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False
    print("Error: mido required. Install with: pip install mido")

# ============================================================================
# Configuration
# ============================================================================

DB_PATH = Path.home() / "Music-Brain" / "structure-library" / "structure_patterns.db"
PATTERNS_PATH = Path.home() / "Music-Brain" / "structure-library" / "patterns"

STANDARD_PPQ = 480

# Note names
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Chord templates (intervals from root)
CHORD_TEMPLATES = {
    'maj': [0, 4, 7],
    'min': [0, 3, 7],
    'dim': [0, 3, 6],
    'aug': [0, 4, 8],
    'maj7': [0, 4, 7, 11],
    'min7': [0, 3, 7, 10],
    'dom7': [0, 4, 7, 10],
    'dim7': [0, 3, 6, 9],
    'hdim7': [0, 3, 6, 10],  # half-diminished
    'sus2': [0, 2, 7],
    'sus4': [0, 5, 7],
    'add9': [0, 4, 7, 14],
    'min9': [0, 3, 7, 10, 14],
    'maj9': [0, 4, 7, 11, 14],
    '6': [0, 4, 7, 9],
    'min6': [0, 3, 7, 9],
}

# Chord families by function
CHORD_FAMILIES = {
    'tonic': ['I', 'i', 'vi', 'VI', 'iii', 'III'],
    'subdominant': ['IV', 'iv', 'ii', 'II'],
    'dominant': ['V', 'v', 'vii°', 'VII'],
}

# Common progressions to detect
COMMON_PROGRESSIONS = {
    'I-IV-V-I': [0, 5, 7, 0],
    'I-V-vi-IV': [0, 7, 9, 5],
    'ii-V-I': [2, 7, 0],
    'I-vi-IV-V': [0, 9, 5, 7],
    'vi-IV-I-V': [9, 5, 0, 7],
    'I-IV-vi-V': [0, 5, 9, 7],
    'i-VII-VI-VII': [0, 10, 8, 10],  # Minor
    'i-iv-VII-III': [0, 5, 10, 3],
    'I-V-vi-iii-IV-I-IV-V': [0, 7, 9, 4, 5, 0, 5, 7],  # Canon
    '12-bar-blues': [0, 0, 0, 0, 5, 5, 0, 0, 7, 5, 0, 7],
}

# Melody shape categories
MELODY_SHAPES = {
    'ascending': 'Notes generally rise',
    'descending': 'Notes generally fall',
    'arch': 'Rise then fall',
    'inverted_arch': 'Fall then rise',
    'flat': 'Stays in narrow range',
    'zigzag': 'Alternating up/down',
    'stepwise': 'Mostly small intervals',
    'leapy': 'Many large intervals',
}

# ============================================================================
# Database Setup
# ============================================================================

def init_database():
    """Initialize SQLite database for structural patterns."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    PATTERNS_PATH.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Main structure analysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS structure_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            source_file TEXT,
            genre TEXT,
            key_detected TEXT,
            mode_detected TEXT,
            time_signature TEXT DEFAULT '4/4',
            bpm REAL,
            total_bars INTEGER,
            date_analyzed TEXT
        )
    ''')
    
    # Chord progressions found
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chord_progressions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            progression_name TEXT,
            progression_numerals TEXT,
            occurrence_count INTEGER,
            bar_positions TEXT,
            confidence REAL,
            FOREIGN KEY (analysis_id) REFERENCES structure_analysis(id)
        )
    ''')
    
    # Individual chords
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            bar_number INTEGER,
            beat_position REAL,
            root_note TEXT,
            chord_type TEXT,
            chord_symbol TEXT,
            duration_beats REAL,
            notes_in_chord TEXT,
            FOREIGN KEY (analysis_id) REFERENCES structure_analysis(id)
        )
    ''')
    
    # Melody statistics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS melody_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            track_index INTEGER,
            range_semitones INTEGER,
            lowest_note TEXT,
            highest_note TEXT,
            average_interval REAL,
            interval_distribution TEXT,
            predominant_shape TEXT,
            phrase_count INTEGER,
            avg_phrase_length_beats REAL,
            FOREIGN KEY (analysis_id) REFERENCES structure_analysis(id)
        )
    ''')
    
    # Phrase boundaries
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS phrases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            track_index INTEGER,
            phrase_number INTEGER,
            start_bar REAL,
            end_bar REAL,
            length_beats REAL,
            note_count INTEGER,
            shape TEXT,
            contour TEXT,
            FOREIGN KEY (analysis_id) REFERENCES structure_analysis(id)
        )
    ''')
    
    # Harmonic rhythm
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS harmonic_rhythm (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            avg_chord_duration_beats REAL,
            changes_per_bar REAL,
            rhythm_pattern TEXT,
            pattern_variance REAL,
            FOREIGN KEY (analysis_id) REFERENCES structure_analysis(id)
        )
    ''')
    
    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_structure_genre ON structure_analysis(genre)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chords_analysis ON chords(analysis_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_progressions_analysis ON chord_progressions(analysis_id)')
    
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
    """Load MIDI file."""
    if not MIDO_AVAILABLE:
        raise ImportError("mido required")
    return mido.MidiFile(filepath)

def get_tempo(mid):
    """Extract tempo from MIDI."""
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                return mido.tempo2bpm(msg.tempo)
    return 120.0

def extract_notes_with_timing(mid):
    """
    Extract all notes with absolute timing.
    Returns list of (tick, note, velocity, duration, channel, track_idx)
    """
    ppq = mid.ticks_per_beat
    all_notes = []
    
    for track_idx, track in enumerate(mid.tracks):
        current_tick = 0
        active_notes = {}  # (channel, note) -> (start_tick, velocity)
        
        for msg in track:
            current_tick += msg.time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                key = (msg.channel, msg.note)
                active_notes[key] = (current_tick, msg.velocity)
            
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                key = (msg.channel, msg.note)
                if key in active_notes:
                    start_tick, velocity = active_notes.pop(key)
                    duration = current_tick - start_tick
                    
                    all_notes.append({
                        'tick': start_tick,
                        'note': msg.note,
                        'velocity': velocity,
                        'duration': duration,
                        'channel': msg.channel,
                        'track': track_idx
                    })
    
    return sorted(all_notes, key=lambda x: x['tick']), ppq

def note_to_name(midi_note):
    """Convert MIDI note number to name."""
    octave = (midi_note // 12) - 1
    note = NOTE_NAMES[midi_note % 12]
    return f"{note}{octave}"

def note_to_pitch_class(midi_note):
    """Get pitch class (0-11) from MIDI note."""
    return midi_note % 12

# ============================================================================
# Chord Detection
# ============================================================================

def detect_chord(notes_playing):
    """
    Detect chord from a set of notes.
    Returns (root, chord_type, confidence)
    """
    if len(notes_playing) < 2:
        return None, None, 0
    
    # Get pitch classes
    pitch_classes = sorted(set(n % 12 for n in notes_playing))
    
    if len(pitch_classes) < 2:
        return None, None, 0
    
    best_match = None
    best_score = 0
    
    # Try each pitch class as potential root
    for root in range(12):
        # Normalize intervals relative to this root
        intervals = sorted([(pc - root) % 12 for pc in pitch_classes])
        
        # Compare to chord templates
        for chord_type, template in CHORD_TEMPLATES.items():
            template_set = set(template)
            intervals_set = set(intervals)
            
            # Calculate match score
            matches = len(template_set & intervals_set)
            extras = len(intervals_set - template_set)
            missing = len(template_set - intervals_set)
            
            # Score: matches are good, extras are okay, missing is bad
            score = matches - (missing * 0.5) - (extras * 0.2)
            
            # Bonus for exact match
            if intervals_set == template_set:
                score += 1
            
            if score > best_score:
                best_score = score
                best_match = (root, chord_type)
    
    if best_match and best_score > 0.5:
        root, chord_type = best_match
        confidence = min(1.0, best_score / len(CHORD_TEMPLATES[chord_type]))
        return NOTE_NAMES[root], chord_type, confidence
    
    return None, None, 0

def extract_chords_by_beat(notes, ppq, beats_per_bar=4):
    """
    Extract chords at each beat position.
    Returns list of (bar, beat, chord_symbol, notes)
    """
    ticks_per_beat = ppq
    ticks_per_bar = ppq * beats_per_bar
    
    # Group notes by beat
    beat_notes = defaultdict(list)
    
    for note in notes:
        if note['channel'] == 9:  # Skip drums
            continue
        
        start_beat = note['tick'] / ticks_per_beat
        duration_beats = note['duration'] / ticks_per_beat
        
        # Note is active during these beats
        for beat in range(int(start_beat), int(start_beat + duration_beats) + 1):
            beat_notes[beat].append(note['note'])
    
    # Detect chord at each beat
    chords = []
    current_chord = None
    chord_start_beat = 0
    
    for beat in sorted(beat_notes.keys()):
        notes_at_beat = beat_notes[beat]
        root, chord_type, confidence = detect_chord(notes_at_beat)
        
        if root and chord_type:
            chord_symbol = f"{root}{chord_type}" if chord_type != 'maj' else root
            
            if chord_symbol != current_chord:
                if current_chord:
                    # Save previous chord
                    bar = chord_start_beat // beats_per_bar
                    beat_in_bar = chord_start_beat % beats_per_bar
                    duration = beat - chord_start_beat
                    chords.append({
                        'bar': bar,
                        'beat': beat_in_bar,
                        'symbol': current_chord,
                        'duration_beats': duration,
                        'confidence': confidence
                    })
                
                current_chord = chord_symbol
                chord_start_beat = beat
    
    # Don't forget last chord
    if current_chord:
        bar = chord_start_beat // beats_per_bar
        beat_in_bar = chord_start_beat % beats_per_bar
        chords.append({
            'bar': bar,
            'beat': beat_in_bar,
            'symbol': current_chord,
            'duration_beats': 1,
            'confidence': confidence
        })
    
    return chords

def detect_key(chords):
    """
    Detect likely key from chord progression.
    Returns (key, mode, confidence)
    """
    if not chords:
        return None, None, 0
    
    # Count chord roots
    root_counts = Counter()
    for chord in chords:
        symbol = chord['symbol']
        # Extract root (first 1-2 characters)
        if len(symbol) > 1 and symbol[1] == '#':
            root = symbol[:2]
        else:
            root = symbol[0]
        root_counts[root] += 1
    
    # Most common root is likely tonic
    if not root_counts:
        return None, None, 0
    
    likely_tonic = root_counts.most_common(1)[0][0]
    
    # Determine mode by looking at chord qualities
    major_count = 0
    minor_count = 0
    
    for chord in chords:
        symbol = chord['symbol']
        if 'min' in symbol or 'm' in symbol.lower():
            minor_count += 1
        else:
            major_count += 1
    
    mode = 'major' if major_count >= minor_count else 'minor'
    confidence = root_counts[likely_tonic] / sum(root_counts.values())
    
    return likely_tonic, mode, confidence

def find_progressions(chords, beats_per_bar=4):
    """
    Find recurring chord progressions.
    Returns dict of {progression: count, bar_positions}
    """
    if len(chords) < 2:
        return {}
    
    # Get sequence of chord symbols by bar
    bar_chords = defaultdict(list)
    for chord in chords:
        bar_chords[chord['bar']].append(chord['symbol'])
    
    # Simplify to one chord per bar (most prominent)
    chord_sequence = []
    for bar in sorted(bar_chords.keys()):
        if bar_chords[bar]:
            # Take first chord of bar
            chord_sequence.append(bar_chords[bar][0])
    
    # Find recurring patterns (2-8 bar lengths)
    patterns = defaultdict(lambda: {'count': 0, 'positions': []})
    
    for length in range(2, min(9, len(chord_sequence))):
        for i in range(len(chord_sequence) - length + 1):
            pattern = tuple(chord_sequence[i:i+length])
            pattern_str = '-'.join(pattern)
            patterns[pattern_str]['count'] += 1
            patterns[pattern_str]['positions'].append(i)
    
    # Filter to patterns that occur more than once
    recurring = {k: v for k, v in patterns.items() if v['count'] > 1}
    
    return recurring

def get_chord_family(chord_symbol, key):
    """
    Determine chord family (tonic, subdominant, dominant) relative to key.
    """
    # This is a simplified version
    # Full implementation would need proper roman numeral analysis
    
    if not key or not chord_symbol:
        return 'unknown'
    
    # Extract root from chord symbol
    if len(chord_symbol) > 1 and chord_symbol[1] == '#':
        root = chord_symbol[:2]
    else:
        root = chord_symbol[0]
    
    # Get interval from key
    key_idx = NOTE_NAMES.index(key) if key in NOTE_NAMES else 0
    root_idx = NOTE_NAMES.index(root) if root in NOTE_NAMES else 0
    interval = (root_idx - key_idx) % 12
    
    # Classify by interval
    if interval in [0]:  # I
        return 'tonic'
    elif interval in [5]:  # IV
        return 'subdominant'
    elif interval in [7]:  # V
        return 'dominant'
    elif interval in [9]:  # vi
        return 'tonic'  # Relative minor
    elif interval in [2]:  # ii
        return 'subdominant'
    elif interval in [11, 10]:  # vii
        return 'dominant'
    else:
        return 'other'

# ============================================================================
# Melody Analysis
# ============================================================================

def extract_melody_track(notes, track_idx=None):
    """
    Extract melody notes (highest non-drum notes or specific track).
    """
    # Filter out drums
    melodic_notes = [n for n in notes if n['channel'] != 9]
    
    if track_idx is not None:
        melodic_notes = [n for n in melodic_notes if n['track'] == track_idx]
    
    if not melodic_notes:
        return []
    
    # Sort by time
    return sorted(melodic_notes, key=lambda x: x['tick'])

def calculate_intervals(melody_notes):
    """Calculate intervals between consecutive melody notes."""
    intervals = []
    for i in range(1, len(melody_notes)):
        interval = melody_notes[i]['note'] - melody_notes[i-1]['note']
        intervals.append(interval)
    return intervals

def analyze_melody_shape(intervals):
    """
    Analyze overall melody shape from intervals.
    """
    if not intervals:
        return 'flat', []
    
    # Calculate contour (simplified)
    contour = []
    for interval in intervals:
        if interval > 0:
            contour.append('U')  # Up
        elif interval < 0:
            contour.append('D')  # Down
        else:
            contour.append('S')  # Same
    
    # Determine predominant shape
    up_count = contour.count('U')
    down_count = contour.count('D')
    same_count = contour.count('S')
    total = len(contour)
    
    # Check for arch patterns
    midpoint = len(contour) // 2
    first_half_ups = contour[:midpoint].count('U')
    second_half_downs = contour[midpoint:].count('D')
    
    if total == 0:
        return 'flat', contour
    
    if same_count / total > 0.6:
        return 'flat', contour
    elif up_count / total > 0.6:
        return 'ascending', contour
    elif down_count / total > 0.6:
        return 'descending', contour
    elif first_half_ups > midpoint * 0.5 and second_half_downs > (total - midpoint) * 0.5:
        return 'arch', contour
    elif contour[:midpoint].count('D') > midpoint * 0.5 and contour[midpoint:].count('U') > (total - midpoint) * 0.5:
        return 'inverted_arch', contour
    else:
        # Check interval sizes
        avg_interval = statistics.mean([abs(i) for i in intervals]) if intervals else 0
        if avg_interval < 3:
            return 'stepwise', contour
        elif avg_interval > 5:
            return 'leapy', contour
        else:
            return 'zigzag', contour

def detect_phrases(melody_notes, ppq, min_gap_beats=1.0):
    """
    Detect phrase boundaries based on gaps in melody.
    """
    if not melody_notes:
        return []
    
    gap_threshold = ppq * min_gap_beats
    phrases = []
    current_phrase = [melody_notes[0]]
    
    for i in range(1, len(melody_notes)):
        prev_note = melody_notes[i-1]
        curr_note = melody_notes[i]
        
        # Gap between notes
        gap = curr_note['tick'] - (prev_note['tick'] + prev_note['duration'])
        
        if gap > gap_threshold:
            # New phrase
            if current_phrase:
                phrases.append(current_phrase)
            current_phrase = [curr_note]
        else:
            current_phrase.append(curr_note)
    
    if current_phrase:
        phrases.append(current_phrase)
    
    return phrases

def analyze_phrases(phrases, ppq, beats_per_bar=4):
    """
    Analyze phrase characteristics.
    """
    phrase_analysis = []
    
    for i, phrase in enumerate(phrases):
        if not phrase:
            continue
        
        start_tick = phrase[0]['tick']
        end_tick = phrase[-1]['tick'] + phrase[-1]['duration']
        length_ticks = end_tick - start_tick
        length_beats = length_ticks / ppq
        
        # Get phrase intervals and shape
        intervals = calculate_intervals(phrase)
        shape, contour = analyze_melody_shape(intervals)
        
        phrase_analysis.append({
            'phrase_number': i + 1,
            'start_bar': start_tick / (ppq * beats_per_bar),
            'end_bar': end_tick / (ppq * beats_per_bar),
            'length_beats': length_beats,
            'note_count': len(phrase),
            'shape': shape,
            'contour': ''.join(contour)
        })
    
    return phrase_analysis

def get_interval_distribution(intervals):
    """Get distribution of interval sizes."""
    if not intervals:
        return {}
    
    # Categorize intervals
    distribution = {
        'unison': 0,      # 0
        'step': 0,        # 1-2
        'third': 0,       # 3-4
        'fourth_fifth': 0, # 5-7
        'large': 0,       # 8+
    }
    
    for interval in intervals:
        abs_int = abs(interval)
        if abs_int == 0:
            distribution['unison'] += 1
        elif abs_int <= 2:
            distribution['step'] += 1
        elif abs_int <= 4:
            distribution['third'] += 1
        elif abs_int <= 7:
            distribution['fourth_fifth'] += 1
        else:
            distribution['large'] += 1
    
    # Convert to percentages
    total = sum(distribution.values())
    if total > 0:
        distribution = {k: round(v / total * 100, 1) for k, v in distribution.items()}
    
    return distribution

# ============================================================================
# Harmonic Rhythm Analysis
# ============================================================================

def analyze_harmonic_rhythm(chords, beats_per_bar=4):
    """
    Analyze how often chords change.
    """
    if not chords:
        return None
    
    durations = [c['duration_beats'] for c in chords]
    
    if not durations:
        return None
    
    avg_duration = statistics.mean(durations)
    variance = statistics.variance(durations) if len(durations) > 1 else 0
    
    # Calculate changes per bar
    total_bars = max(c['bar'] for c in chords) + 1 if chords else 1
    changes_per_bar = len(chords) / total_bars
    
    # Determine rhythm pattern
    if avg_duration >= beats_per_bar:
        pattern = 'whole_note'  # One chord per bar or slower
    elif avg_duration >= beats_per_bar / 2:
        pattern = 'half_note'  # Two chords per bar
    elif avg_duration >= beats_per_bar / 4:
        pattern = 'quarter_note'  # Four chords per bar
    else:
        pattern = 'fast'  # Faster than quarter notes
    
    return {
        'avg_duration_beats': round(avg_duration, 2),
        'changes_per_bar': round(changes_per_bar, 2),
        'pattern': pattern,
        'variance': round(variance, 3)
    }

# ============================================================================
# Full Analysis Pipeline
# ============================================================================

def analyze_structure(filepath, name=None, genre=None):
    """
    Complete structural analysis of MIDI file.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    print(f"Analyzing structure: {filepath.name}")
    
    # Load MIDI
    mid = load_midi(str(filepath))
    ppq = mid.ticks_per_beat
    bpm = get_tempo(mid)
    
    # Extract all notes
    notes, ppq = extract_notes_with_timing(mid)
    
    print(f"  PPQ: {ppq}, BPM: {bpm:.1f}, Notes: {len(notes)}")
    
    # Calculate total bars
    max_tick = max(n['tick'] + n['duration'] for n in notes) if notes else 0
    total_bars = int(max_tick / (ppq * 4)) + 1
    
    # Extract chords
    print("  Detecting chords...")
    chords = extract_chords_by_beat(notes, ppq)
    print(f"    Found {len(chords)} chord changes")
    
    # Detect key
    key, mode, key_confidence = detect_key(chords)
    print(f"    Key: {key} {mode} (confidence: {key_confidence:.0%})")
    
    # Find progressions
    print("  Finding progressions...")
    progressions = find_progressions(chords)
    print(f"    Found {len(progressions)} recurring patterns")
    
    # Analyze harmonic rhythm
    harmonic_rhythm = analyze_harmonic_rhythm(chords)
    if harmonic_rhythm:
        print(f"    Harmonic rhythm: {harmonic_rhythm['pattern']} ({harmonic_rhythm['changes_per_bar']:.1f} changes/bar)")
    
    # Analyze melody
    print("  Analyzing melody...")
    melody_notes = extract_melody_track(notes)
    
    melody_stats = None
    phrase_analysis = []
    
    if melody_notes:
        intervals = calculate_intervals(melody_notes)
        shape, contour = analyze_melody_shape(intervals)
        interval_dist = get_interval_distribution(intervals)
        
        # Get range
        pitches = [n['note'] for n in melody_notes]
        lowest = min(pitches)
        highest = max(pitches)
        range_semitones = highest - lowest
        
        # Detect phrases
        phrases = detect_phrases(melody_notes, ppq)
        phrase_analysis = analyze_phrases(phrases, ppq)
        
        melody_stats = {
            'range_semitones': range_semitones,
            'lowest_note': note_to_name(lowest),
            'highest_note': note_to_name(highest),
            'average_interval': round(statistics.mean([abs(i) for i in intervals]), 2) if intervals else 0,
            'interval_distribution': interval_dist,
            'predominant_shape': shape,
            'phrase_count': len(phrases),
            'avg_phrase_length_beats': round(statistics.mean([p['length_beats'] for p in phrase_analysis]), 2) if phrase_analysis else 0
        }
        
        print(f"    Range: {range_semitones} semitones ({melody_stats['lowest_note']} to {melody_stats['highest_note']})")
        print(f"    Shape: {shape}, Phrases: {len(phrases)}")
    
    # Build result
    result = {
        'metadata': {
            'name': name or filepath.stem,
            'source_file': str(filepath),
            'genre': genre,
            'key': key,
            'mode': mode,
            'key_confidence': key_confidence,
            'time_signature': '4/4',
            'bpm': bpm,
            'total_bars': total_bars,
            'date_analyzed': datetime.now().isoformat()
        },
        'chords': chords,
        'progressions': progressions,
        'harmonic_rhythm': harmonic_rhythm,
        'melody_stats': melody_stats,
        'phrases': phrase_analysis,
        'chord_families': {}
    }
    
    # Add chord family analysis
    if key:
        for chord in chords:
            family = get_chord_family(chord['symbol'], key)
            if family not in result['chord_families']:
                result['chord_families'][family] = 0
            result['chord_families'][family] += 1
    
    return result

def save_analysis(analysis, output_path=None):
    """Save analysis to JSON file."""
    if output_path is None:
        name = analysis['metadata']['name']
        output_path = PATTERNS_PATH / f"{name}_structure.json"
    else:
        output_path = Path(output_path)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"Saved: {output_path}")
    return output_path

def save_to_database(analysis):
    """Save analysis to SQLite database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    meta = analysis['metadata']
    
    # Insert main record
    cursor.execute('''
        INSERT INTO structure_analysis
        (name, source_file, genre, key_detected, mode_detected, time_signature, bpm, total_bars, date_analyzed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        meta['name'], meta['source_file'], meta['genre'],
        meta['key'], meta['mode'], meta['time_signature'],
        meta['bpm'], meta['total_bars'], meta['date_analyzed']
    ))
    
    analysis_id = cursor.lastrowid
    
    # Insert chords
    for chord in analysis.get('chords', []):
        cursor.execute('''
            INSERT INTO chords
            (analysis_id, bar_number, beat_position, chord_symbol, duration_beats)
            VALUES (?, ?, ?, ?, ?)
        ''', (analysis_id, chord['bar'], chord['beat'], chord['symbol'], chord['duration_beats']))
    
    # Insert progressions
    for prog_name, prog_data in analysis.get('progressions', {}).items():
        cursor.execute('''
            INSERT INTO chord_progressions
            (analysis_id, progression_numerals, occurrence_count, bar_positions)
            VALUES (?, ?, ?, ?)
        ''', (analysis_id, prog_name, prog_data['count'], json.dumps(prog_data['positions'])))
    
    # Insert melody stats
    melody = analysis.get('melody_stats')
    if melody:
        cursor.execute('''
            INSERT INTO melody_stats
            (analysis_id, range_semitones, lowest_note, highest_note, average_interval,
             interval_distribution, predominant_shape, phrase_count, avg_phrase_length_beats)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_id, melody['range_semitones'], melody['lowest_note'], melody['highest_note'],
            melody['average_interval'], json.dumps(melody['interval_distribution']),
            melody['predominant_shape'], melody['phrase_count'], melody['avg_phrase_length_beats']
        ))
    
    # Insert phrases
    for phrase in analysis.get('phrases', []):
        cursor.execute('''
            INSERT INTO phrases
            (analysis_id, phrase_number, start_bar, end_bar, length_beats, note_count, shape, contour)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_id, phrase['phrase_number'], phrase['start_bar'], phrase['end_bar'],
            phrase['length_beats'], phrase['note_count'], phrase['shape'], phrase['contour']
        ))
    
    # Insert harmonic rhythm
    hr = analysis.get('harmonic_rhythm')
    if hr:
        cursor.execute('''
            INSERT INTO harmonic_rhythm
            (analysis_id, avg_chord_duration_beats, changes_per_bar, rhythm_pattern, pattern_variance)
            VALUES (?, ?, ?, ?, ?)
        ''', (analysis_id, hr['avg_duration_beats'], hr['changes_per_bar'], hr['pattern'], hr['variance']))
    
    conn.commit()
    conn.close()
    
    print(f"Saved to database with ID: {analysis_id}")
    return analysis_id

# ============================================================================
# Batch Processing
# ============================================================================

def scan_folder(folder_path, genre=None, recursive=True):
    """Scan folder for MIDI files and analyze structure."""
    folder = Path(folder_path).expanduser().resolve()
    
    if not folder.exists():
        print(f"Error: Folder not found: {folder}")
        return
    
    pattern = '**/*.mid' if recursive else '*.mid'
    midi_files = list(folder.glob(pattern))
    midi_files.extend(folder.glob(pattern.replace('.mid', '.midi')))
    
    print(f"Found {len(midi_files)} MIDI files")
    print("-" * 50)
    
    analyzed = 0
    errors = 0
    
    for filepath in midi_files:
        try:
            analysis = analyze_structure(filepath, genre=genre)
            save_analysis(analysis)
            save_to_database(analysis)
            analyzed += 1
        except Exception as e:
            print(f"  Error: {e}")
            errors += 1
    
    print("-" * 50)
    print(f"Analyzed: {analyzed}, Errors: {errors}")

# ============================================================================
# Query Functions
# ============================================================================

def list_analyses(genre=None, key=None, limit=50):
    """List all structure analyses."""
    conn = get_connection()
    cursor = conn.cursor()
    
    conditions = ["1=1"]
    params = []
    
    if genre:
        conditions.append("genre LIKE ?")
        params.append(f"%{genre}%")
    if key:
        conditions.append("key_detected LIKE ?")
        params.append(f"%{key}%")
    
    cursor.execute(f'''
        SELECT id, name, genre, key_detected, mode_detected, bpm, total_bars
        FROM structure_analysis
        WHERE {" AND ".join(conditions)}
        ORDER BY name
        LIMIT ?
    ''', params + [limit])
    
    results = cursor.fetchall()
    conn.close()
    
    print(f"\n{'ID':<6} {'Name':<30} {'Genre':<12} {'Key':<8} {'BPM':<8} {'Bars':<6}")
    print("-" * 75)
    
    for row in results:
        id_, name, genre, key, mode, bpm, bars = row
        name_display = name[:28] + '..' if len(name) > 30 else name
        key_display = f"{key or '?'} {mode[0] if mode else ''}"
        print(f"{id_:<6} {name_display:<30} {genre or '':<12} {key_display:<8} {bpm or '?':<8} {bars or '?':<6}")

def get_analysis_detail(analysis_id):
    """Get detailed analysis."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM structure_analysis WHERE id = ?', (analysis_id,))
    analysis = cursor.fetchone()
    
    if not analysis:
        print(f"Analysis {analysis_id} not found")
        return
    
    print(f"\n{'='*60}")
    print(f"Analysis: {analysis[1]}")
    print(f"Key: {analysis[4]} {analysis[5]}")
    print(f"BPM: {analysis[7]}, Bars: {analysis[8]}")
    print(f"{'='*60}")
    
    # Get progressions
    cursor.execute('''
        SELECT progression_numerals, occurrence_count
        FROM chord_progressions
        WHERE analysis_id = ?
        ORDER BY occurrence_count DESC
        LIMIT 10
    ''', (analysis_id,))
    
    progressions = cursor.fetchall()
    
    if progressions:
        print(f"\nRecurring Progressions:")
        for prog, count in progressions:
            print(f"  {prog}: {count}x")
    
    # Get harmonic rhythm
    cursor.execute('SELECT * FROM harmonic_rhythm WHERE analysis_id = ?', (analysis_id,))
    hr = cursor.fetchone()
    
    if hr:
        print(f"\nHarmonic Rhythm:")
        print(f"  Pattern: {hr[4]} ({hr[3]:.1f} changes/bar)")
        print(f"  Avg chord duration: {hr[2]:.1f} beats")
    
    # Get melody stats
    cursor.execute('SELECT * FROM melody_stats WHERE analysis_id = ?', (analysis_id,))
    melody = cursor.fetchone()
    
    if melody:
        print(f"\nMelody:")
        print(f"  Range: {melody[3]} semitones ({melody[4]} to {melody[5]})")
        print(f"  Shape: {melody[8]}")
        print(f"  Phrases: {melody[9]}, Avg length: {melody[10]:.1f} beats")
    
    conn.close()

def find_similar(analysis_id, limit=10):
    """Find analyses with similar characteristics."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get reference analysis
    cursor.execute('SELECT key_detected, mode_detected, bpm FROM structure_analysis WHERE id = ?', (analysis_id,))
    ref = cursor.fetchone()
    
    if not ref:
        print(f"Analysis {analysis_id} not found")
        return
    
    ref_key, ref_mode, ref_bpm = ref
    
    # Find similar
    cursor.execute('''
        SELECT id, name, key_detected, mode_detected, bpm,
               ABS(bpm - ?) as bpm_diff
        FROM structure_analysis
        WHERE id != ?
        AND (key_detected = ? OR mode_detected = ?)
        ORDER BY bpm_diff
        LIMIT ?
    ''', (ref_bpm, analysis_id, ref_key, ref_mode, limit))
    
    results = cursor.fetchall()
    conn.close()
    
    print(f"\nSimilar to {analysis_id} (Key: {ref_key} {ref_mode}, BPM: {ref_bpm}):\n")
    
    for row in results:
        id_, name, key, mode, bpm, diff = row
        print(f"  [{id_}] {name[:30]} - {key} {mode}, BPM: {bpm}")

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Structural Pattern Extractor - Analyze harmony and melody in MIDI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s analyze song.mid --genre jazz
  %(prog)s scan ~/MIDI/Songs --genre pop
  %(prog)s list --key C
  %(prog)s detail 5
  %(prog)s similar 5
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze MIDI file structure')
    analyze_parser.add_argument('file', help='MIDI file path')
    analyze_parser.add_argument('--name', help='Analysis name')
    analyze_parser.add_argument('--genre', help='Genre tag')
    analyze_parser.add_argument('--output', help='Output JSON path')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan folder for MIDI files')
    scan_parser.add_argument('folder', help='Folder path')
    scan_parser.add_argument('--genre', help='Genre tag')
    scan_parser.add_argument('--no-recursive', action='store_true')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List analyses')
    list_parser.add_argument('--genre', help='Filter by genre')
    list_parser.add_argument('--key', help='Filter by key')
    list_parser.add_argument('--limit', type=int, default=50)
    
    # Detail command
    detail_parser = subparsers.add_parser('detail', help='Show analysis details')
    detail_parser.add_argument('id', type=int, help='Analysis ID')
    
    # Similar command
    similar_parser = subparsers.add_parser('similar', help='Find similar analyses')
    similar_parser.add_argument('id', type=int, help='Reference analysis ID')
    similar_parser.add_argument('--limit', type=int, default=10)
    
    # Init command
    subparsers.add_parser('init', help='Initialize database')
    
    args = parser.parse_args()
    
    if args.command == 'analyze':
        analysis = analyze_structure(args.file, name=args.name, genre=args.genre)
        if args.output:
            save_analysis(analysis, args.output)
        else:
            save_analysis(analysis)
        save_to_database(analysis)
    
    elif args.command == 'scan':
        scan_folder(args.folder, genre=args.genre, recursive=not args.no_recursive)
    
    elif args.command == 'list':
        list_analyses(genre=args.genre, key=args.key, limit=args.limit)
    
    elif args.command == 'detail':
        get_analysis_detail(args.id)
    
    elif args.command == 'similar':
        find_similar(args.id, limit=args.limit)
    
    elif args.command == 'init':
        init_database()
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
