#!/usr/bin/env python3
"""
MIDI Structure Analyzer
Extract chord families, progressions, melody shapes, phrase lengths, and harmonic rhythm.

Complements groove extraction with harmonic and structural DNA.
Part of the Music Brain system.
"""

import argparse
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
import statistics
import math

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False
    print("Error: mido required. Install with: pip install mido")

# ============================================================================
# Configuration
# ============================================================================

DB_PATH = Path.home() / "Music-Brain" / "structure-library" / "structure_analysis.db"
OUTPUT_PATH = Path.home() / "Music-Brain" / "structure-library" / "analyses"

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
    'maj9': [0, 4, 7, 11, 14],
    'min9': [0, 3, 7, 10, 14],
    'dom9': [0, 4, 7, 10, 14],
    'sus2': [0, 2, 7],
    'sus4': [0, 5, 7],
    'add9': [0, 4, 7, 14],
    '6': [0, 4, 7, 9],
    'min6': [0, 3, 7, 9],
}

# Chord families
CHORD_FAMILIES = {
    'major': ['maj', 'maj7', 'maj9', '6', 'add9'],
    'minor': ['min', 'min7', 'min9', 'min6'],
    'dominant': ['dom7', 'dom9'],
    'diminished': ['dim', 'dim7', 'hdim7'],
    'augmented': ['aug'],
    'suspended': ['sus2', 'sus4'],
}

# Common progressions to detect
COMMON_PROGRESSIONS = {
    'I-IV-V-I': [(0, 'maj'), (5, 'maj'), (7, 'maj'), (0, 'maj')],
    'I-V-vi-IV': [(0, 'maj'), (7, 'maj'), (9, 'min'), (5, 'maj')],
    'ii-V-I': [(2, 'min7'), (7, 'dom7'), (0, 'maj7')],
    'I-vi-IV-V': [(0, 'maj'), (9, 'min'), (5, 'maj'), (7, 'maj')],
    'vi-IV-I-V': [(9, 'min'), (5, 'maj'), (0, 'maj'), (7, 'maj')],
    'I-IV-vi-V': [(0, 'maj'), (5, 'maj'), (9, 'min'), (7, 'maj')],
    'i-VI-III-VII': [(0, 'min'), (8, 'maj'), (3, 'maj'), (10, 'maj')],  # Andalusian
    'I-V-IV-I': [(0, 'maj'), (7, 'maj'), (5, 'maj'), (0, 'maj')],
    'I-bVII-IV-I': [(0, 'maj'), (10, 'maj'), (5, 'maj'), (0, 'maj')],  # Rock
    'i-iv-v-i': [(0, 'min'), (5, 'min'), (7, 'min'), (0, 'min')],  # Natural minor
    'i-VII-VI-V': [(0, 'min'), (10, 'maj'), (8, 'maj'), (7, 'maj')],  # Descending
}

# ============================================================================
# Database Setup
# ============================================================================

def init_database():
    """Initialize SQLite database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Main analysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS structure_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            source_file TEXT,
            genre TEXT,
            key_detected TEXT,
            mode_detected TEXT,
            bpm REAL,
            time_signature TEXT,
            total_bars INTEGER,
            date_analyzed TEXT
        )
    ''')
    
    # Chord progressions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chord_progressions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            bar_number INTEGER,
            beat REAL,
            root_note TEXT,
            chord_type TEXT,
            chord_family TEXT,
            duration_beats REAL,
            confidence REAL,
            FOREIGN KEY (analysis_id) REFERENCES structure_analyses(id)
        )
    ''')
    
    # Detected patterns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detected_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            pattern_name TEXT,
            pattern_type TEXT,
            start_bar INTEGER,
            occurrences INTEGER,
            transposition INTEGER,
            confidence REAL,
            FOREIGN KEY (analysis_id) REFERENCES structure_analyses(id)
        )
    ''')
    
    # Melody contours
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS melody_contours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            phrase_number INTEGER,
            start_bar REAL,
            end_bar REAL,
            contour_type TEXT,
            pitch_range INTEGER,
            direction TEXT,
            step_count INTEGER,
            leap_count INTEGER,
            FOREIGN KEY (analysis_id) REFERENCES structure_analyses(id)
        )
    ''')
    
    # Phrase structure
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS phrase_structure (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            phrase_number INTEGER,
            start_bar REAL,
            length_bars REAL,
            note_density REAL,
            avg_velocity REAL,
            pitch_center INTEGER,
            FOREIGN KEY (analysis_id) REFERENCES structure_analyses(id)
        )
    ''')
    
    # Harmonic rhythm
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS harmonic_rhythm (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            avg_chord_duration REAL,
            changes_per_bar REAL,
            rhythm_pattern TEXT,
            consistency REAL,
            FOREIGN KEY (analysis_id) REFERENCES structure_analyses(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized: {DB_PATH}")

def get_connection():
    if not DB_PATH.exists():
        init_database()
    return sqlite3.connect(DB_PATH)

# ============================================================================
# MIDI Loading
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

def extract_notes(mid):
    """
    Extract all notes with timing info.
    Returns list of {tick, note, velocity, duration, channel}
    """
    ppq = mid.ticks_per_beat
    all_notes = []
    
    for track in mid.tracks:
        current_tick = 0
        active_notes = {}
        
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
                        'channel': msg.channel
                    })
    
    all_notes.sort(key=lambda x: x['tick'])
    return all_notes, ppq

def separate_melody_harmony(notes, ppq):
    """
    Separate melody (highest notes) from harmony (chord notes).
    Simple heuristic: notes on channel 9 = drums, highest non-drum = melody
    """
    # Remove drums
    non_drum = [n for n in notes if n['channel'] != 9]
    
    if not non_drum:
        return [], []
    
    # Group by time windows
    window_size = ppq // 4  # 16th note windows
    
    melody_notes = []
    harmony_notes = []
    
    # Group notes by start time
    time_groups = defaultdict(list)
    for note in non_drum:
        window = note['tick'] // window_size
        time_groups[window].append(note)
    
    for window, group in time_groups.items():
        if len(group) == 1:
            melody_notes.append(group[0])
        else:
            # Highest note is melody
            sorted_group = sorted(group, key=lambda x: x['note'], reverse=True)
            melody_notes.append(sorted_group[0])
            harmony_notes.extend(sorted_group[1:])
    
    return melody_notes, harmony_notes

# ============================================================================
# Chord Detection
# ============================================================================

def note_to_pitch_class(note):
    """Convert MIDI note to pitch class (0-11)."""
    return note % 12

def pitch_class_to_name(pc):
    """Convert pitch class to note name."""
    return NOTE_NAMES[pc]

def detect_chord(pitch_classes):
    """
    Detect chord from set of pitch classes.
    Returns (root, chord_type, confidence)
    """
    if len(pitch_classes) < 2:
        return None, None, 0
    
    pitch_set = set(pitch_classes)
    best_match = None
    best_score = 0
    
    # Try each pitch class as potential root
    for root in range(12):
        # Transpose pitch set to root = 0
        transposed = set((p - root) % 12 for p in pitch_set)
        
        # Compare against templates
        for chord_type, template in CHORD_TEMPLATES.items():
            template_set = set(template)
            
            # Calculate match score
            matches = len(transposed & template_set)
            total = len(template_set)
            extras = len(transposed - template_set)
            
            # Score: matches / total, penalized for extra notes
            if total > 0:
                score = (matches / total) - (extras * 0.1)
                
                if score > best_score:
                    best_score = score
                    best_match = (root, chord_type)
    
    if best_match and best_score > 0.5:
        return best_match[0], best_match[1], best_score
    
    return None, None, 0

def get_chord_family(chord_type):
    """Get the family a chord type belongs to."""
    for family, types in CHORD_FAMILIES.items():
        if chord_type in types:
            return family
    return 'other'

def analyze_chords(notes, ppq, beats_per_bar=4):
    """
    Analyze chord progression over time.
    Returns list of chord events with timing.
    """
    if not notes:
        return []
    
    ticks_per_bar = ppq * beats_per_bar
    ticks_per_beat = ppq
    
    # Group notes by beat
    beat_groups = defaultdict(list)
    
    for note in notes:
        beat = note['tick'] // ticks_per_beat
        beat_groups[beat].append(note)
    
    chords = []
    current_chord = None
    current_start = 0
    
    for beat in sorted(beat_groups.keys()):
        notes_in_beat = beat_groups[beat]
        pitch_classes = [note_to_pitch_class(n['note']) for n in notes_in_beat]
        
        root, chord_type, confidence = detect_chord(pitch_classes)
        
        if root is not None:
            chord_key = (root, chord_type)
            
            if chord_key != current_chord:
                # Save previous chord
                if current_chord is not None:
                    prev_root, prev_type = current_chord
                    chords.append({
                        'bar': current_start // beats_per_bar,
                        'beat': current_start % beats_per_bar,
                        'root': pitch_class_to_name(prev_root),
                        'root_pc': prev_root,
                        'type': prev_type,
                        'family': get_chord_family(prev_type),
                        'duration_beats': beat - current_start,
                        'confidence': confidence
                    })
                
                current_chord = chord_key
                current_start = beat
    
    # Add final chord
    if current_chord is not None:
        prev_root, prev_type = current_chord
        final_beat = max(beat_groups.keys()) + 1
        chords.append({
            'bar': current_start // beats_per_bar,
            'beat': current_start % beats_per_bar,
            'root': pitch_class_to_name(prev_root),
            'root_pc': prev_root,
            'type': prev_type,
            'family': get_chord_family(prev_type),
            'duration_beats': final_beat - current_start,
            'confidence': confidence
        })
    
    return chords

# ============================================================================
# Progression Detection
# ============================================================================

def detect_progression_patterns(chords):
    """
    Detect common chord progressions.
    Returns list of detected patterns with confidence.
    """
    if len(chords) < 3:
        return []
    
    detected = []
    
    # Extract chord sequence as (root_pc, type) tuples
    chord_seq = [(c['root_pc'], c['type'].split('7')[0].split('9')[0]) for c in chords]
    
    # Simplify chord types
    def simplify_type(t):
        if t in ['maj', 'maj7', 'maj9', '6', 'add9']:
            return 'maj'
        elif t in ['min', 'min7', 'min9', 'min6']:
            return 'min'
        elif t in ['dom7', 'dom9']:
            return 'dom7'
        elif t in ['dim', 'dim7', 'hdim7']:
            return 'dim'
        return t
    
    chord_seq_simple = [(c[0], simplify_type(c[1])) for c in chord_seq]
    
    # Try to detect patterns at different transpositions
    for pattern_name, pattern_template in COMMON_PROGRESSIONS.items():
        pattern_len = len(pattern_template)
        
        # Simplify template
        template_simple = [(p[0], simplify_type(p[1])) for p in pattern_template]
        
        # Slide window through chord sequence
        for i in range(len(chord_seq_simple) - pattern_len + 1):
            window = chord_seq_simple[i:i + pattern_len]
            
            # Try each transposition
            for trans in range(12):
                transposed_template = [((t[0] + trans) % 12, t[1]) for t in template_simple]
                
                # Check match
                matches = sum(1 for w, t in zip(window, transposed_template) 
                             if w[0] == t[0] and (w[1] == t[1] or t[1] == 'maj' and w[1] in ['maj', 'dom7']))
                
                confidence = matches / pattern_len
                
                if confidence >= 0.75:  # 75% match threshold
                    detected.append({
                        'pattern': pattern_name,
                        'start_index': i,
                        'start_bar': chords[i]['bar'],
                        'transposition': trans,
                        'key': NOTE_NAMES[trans],
                        'confidence': confidence
                    })
    
    # Remove duplicates, keep highest confidence
    unique = {}
    for d in detected:
        key = (d['pattern'], d['start_bar'])
        if key not in unique or d['confidence'] > unique[key]['confidence']:
            unique[key] = d
    
    return list(unique.values())

def analyze_chord_families(chords):
    """Analyze distribution of chord families."""
    family_counts = Counter(c['family'] for c in chords)
    total = sum(family_counts.values())
    
    distribution = {
        family: count / total if total > 0 else 0
        for family, count in family_counts.items()
    }
    
    return distribution

# ============================================================================
# Melody Analysis
# ============================================================================

def analyze_melody_contour(melody_notes, ppq, beats_per_bar=4):
    """
    Analyze melody contour and shape.
    Returns phrase-by-phrase analysis.
    """
    if len(melody_notes) < 2:
        return []
    
    ticks_per_bar = ppq * beats_per_bar
    
    # Detect phrases by gaps
    phrases = []
    current_phrase = [melody_notes[0]]
    gap_threshold = ppq * 2  # Half bar gap = new phrase
    
    for i in range(1, len(melody_notes)):
        gap = melody_notes[i]['tick'] - (melody_notes[i-1]['tick'] + melody_notes[i-1]['duration'])
        
        if gap > gap_threshold:
            if len(current_phrase) >= 2:
                phrases.append(current_phrase)
            current_phrase = []
        
        current_phrase.append(melody_notes[i])
    
    if len(current_phrase) >= 2:
        phrases.append(current_phrase)
    
    # Analyze each phrase
    contours = []
    for i, phrase in enumerate(phrases):
        pitches = [n['note'] for n in phrase]
        
        # Calculate intervals
        intervals = [pitches[j+1] - pitches[j] for j in range(len(pitches)-1)]
        
        # Classify intervals
        steps = sum(1 for iv in intervals if abs(iv) <= 2)
        leaps = sum(1 for iv in intervals if abs(iv) > 2)
        
        # Overall direction
        direction = 'ascending' if pitches[-1] > pitches[0] else 'descending' if pitches[-1] < pitches[0] else 'static'
        
        # Contour type
        max_idx = pitches.index(max(pitches))
        min_idx = pitches.index(min(pitches))
        
        if max_idx < len(pitches) // 3:
            contour_type = 'descending_arch'
        elif max_idx > 2 * len(pitches) // 3:
            contour_type = 'ascending_arch'
        elif min_idx < len(pitches) // 3:
            contour_type = 'ascending_arch'
        elif min_idx > 2 * len(pitches) // 3:
            contour_type = 'descending_arch'
        else:
            contour_type = 'arch' if max_idx < min_idx else 'inverse_arch'
        
        start_bar = phrase[0]['tick'] / ticks_per_bar
        end_bar = (phrase[-1]['tick'] + phrase[-1]['duration']) / ticks_per_bar
        
        contours.append({
            'phrase_number': i + 1,
            'start_bar': round(start_bar, 2),
            'end_bar': round(end_bar, 2),
            'length_bars': round(end_bar - start_bar, 2),
            'note_count': len(phrase),
            'pitch_range': max(pitches) - min(pitches),
            'contour_type': contour_type,
            'direction': direction,
            'step_count': steps,
            'leap_count': leaps,
            'step_ratio': steps / max(1, steps + leaps)
        })
    
    return contours

def calculate_melody_statistics(melody_notes):
    """Calculate overall melody statistics."""
    if not melody_notes:
        return {}
    
    pitches = [n['note'] for n in melody_notes]
    velocities = [n['velocity'] for n in melody_notes]
    durations = [n['duration'] for n in melody_notes]
    
    # Interval statistics
    intervals = [abs(pitches[i+1] - pitches[i]) for i in range(len(pitches)-1)]
    
    return {
        'pitch_mean': statistics.mean(pitches),
        'pitch_std': statistics.stdev(pitches) if len(pitches) > 1 else 0,
        'pitch_range': max(pitches) - min(pitches),
        'pitch_min': min(pitches),
        'pitch_max': max(pitches),
        'velocity_mean': statistics.mean(velocities),
        'velocity_std': statistics.stdev(velocities) if len(velocities) > 1 else 0,
        'avg_interval': statistics.mean(intervals) if intervals else 0,
        'max_interval': max(intervals) if intervals else 0,
        'note_count': len(melody_notes)
    }

# ============================================================================
# Phrase Structure
# ============================================================================

def analyze_phrase_lengths(melody_notes, ppq, beats_per_bar=4):
    """Analyze phrase length patterns."""
    ticks_per_bar = ppq * beats_per_bar
    
    # Detect phrases
    phrases = []
    current_phrase_start = melody_notes[0]['tick'] if melody_notes else 0
    current_phrase_notes = []
    gap_threshold = ppq * 2
    
    for i, note in enumerate(melody_notes):
        if i > 0:
            gap = note['tick'] - (melody_notes[i-1]['tick'] + melody_notes[i-1]['duration'])
            if gap > gap_threshold:
                if current_phrase_notes:
                    phrase_end = current_phrase_notes[-1]['tick'] + current_phrase_notes[-1]['duration']
                    phrases.append({
                        'start': current_phrase_start,
                        'end': phrase_end,
                        'notes': current_phrase_notes
                    })
                current_phrase_start = note['tick']
                current_phrase_notes = []
        
        current_phrase_notes.append(note)
    
    # Add final phrase
    if current_phrase_notes:
        phrase_end = current_phrase_notes[-1]['tick'] + current_phrase_notes[-1]['duration']
        phrases.append({
            'start': current_phrase_start,
            'end': phrase_end,
            'notes': current_phrase_notes
        })
    
    # Calculate phrase lengths in bars
    phrase_lengths = []
    for phrase in phrases:
        length_bars = (phrase['end'] - phrase['start']) / ticks_per_bar
        phrase_lengths.append({
            'start_bar': phrase['start'] / ticks_per_bar,
            'length_bars': round(length_bars, 2),
            'note_count': len(phrase['notes']),
            'note_density': len(phrase['notes']) / max(0.1, length_bars)
        })
    
    # Statistics
    lengths = [p['length_bars'] for p in phrase_lengths]
    
    return {
        'phrases': phrase_lengths,
        'count': len(phrase_lengths),
        'avg_length': statistics.mean(lengths) if lengths else 0,
        'std_length': statistics.stdev(lengths) if len(lengths) > 1 else 0,
        'common_lengths': Counter(round(l, 0) for l in lengths).most_common(3)
    }

# ============================================================================
# Harmonic Rhythm
# ============================================================================

def analyze_harmonic_rhythm(chords, beats_per_bar=4):
    """Analyze harmonic rhythm patterns."""
    if not chords:
        return {}
    
    durations = [c['duration_beats'] for c in chords]
    
    # Calculate changes per bar
    total_beats = sum(durations)
    total_bars = total_beats / beats_per_bar
    changes_per_bar = len(chords) / max(1, total_bars)
    
    # Detect rhythm pattern
    # Round durations to common values
    rounded = [round(d / 0.5) * 0.5 for d in durations]
    pattern_counter = Counter(rounded)
    most_common = pattern_counter.most_common(1)
    
    if most_common:
        dominant_duration = most_common[0][0]
        if dominant_duration >= 4:
            rhythm_pattern = 'whole_note'
        elif dominant_duration >= 2:
            rhythm_pattern = 'half_note'
        elif dominant_duration >= 1:
            rhythm_pattern = 'quarter_note'
        else:
            rhythm_pattern = 'eighth_note'
    else:
        rhythm_pattern = 'irregular'
    
    # Consistency (how regular are the changes)
    if len(durations) > 1:
        consistency = 1 - (statistics.stdev(durations) / statistics.mean(durations))
        consistency = max(0, min(1, consistency))
    else:
        consistency = 1
    
    return {
        'avg_chord_duration': statistics.mean(durations),
        'changes_per_bar': round(changes_per_bar, 2),
        'rhythm_pattern': rhythm_pattern,
        'consistency': round(consistency, 2),
        'duration_distribution': dict(pattern_counter)
    }

# ============================================================================
# Key Detection
# ============================================================================

def detect_key(notes):
    """
    Detect the key of the piece using Krumhansl-Schmuckler algorithm.
    Returns (key_name, mode, confidence)
    """
    if not notes:
        return None, None, 0
    
    # Major and minor key profiles (Krumhansl)
    major_profile = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
    minor_profile = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
    
    # Count pitch classes
    pc_counts = [0] * 12
    for note in notes:
        pc = note['note'] % 12
        pc_counts[pc] += 1
    
    # Normalize
    total = sum(pc_counts)
    if total == 0:
        return None, None, 0
    pc_dist = [c / total for c in pc_counts]
    
    # Correlate with each possible key
    best_key = None
    best_mode = None
    best_corr = -1
    
    for root in range(12):
        # Rotate distribution
        rotated = pc_dist[root:] + pc_dist[:root]
        
        # Correlate with major
        major_corr = sum(r * m for r, m in zip(rotated, major_profile))
        if major_corr > best_corr:
            best_corr = major_corr
            best_key = root
            best_mode = 'major'
        
        # Correlate with minor
        minor_corr = sum(r * m for r, m in zip(rotated, minor_profile))
        if minor_corr > best_corr:
            best_corr = minor_corr
            best_key = root
            best_mode = 'minor'
    
    # Normalize confidence to 0-1 range
    confidence = min(1, max(0, best_corr / 30))
    
    return NOTE_NAMES[best_key], best_mode, confidence

# ============================================================================
# Full Analysis Pipeline
# ============================================================================

def analyze_structure(filepath, name=None, genre=None):
    """
    Run full structural analysis on MIDI file.
    """
    filepath = Path(filepath)
    print(f"Analyzing structure: {filepath.name}")
    
    # Load MIDI
    mid = load_midi(str(filepath))
    ppq = mid.ticks_per_beat
    bpm = get_tempo(mid)
    
    # Extract notes
    all_notes, ppq = extract_notes(mid)
    melody_notes, harmony_notes = separate_melody_harmony(all_notes, ppq)
    
    print(f"  PPQ: {ppq}, BPM: {bpm:.1f}")
    print(f"  Total notes: {len(all_notes)}, Melody: {len(melody_notes)}, Harmony: {len(harmony_notes)}")
    
    # Calculate total bars
    max_tick = max(n['tick'] + n['duration'] for n in all_notes) if all_notes else 0
    total_bars = math.ceil(max_tick / (ppq * 4))
    
    # Detect key
    key, mode, key_confidence = detect_key(all_notes)
    print(f"  Detected key: {key} {mode} (confidence: {key_confidence:.2f})")
    
    # Analyze chords
    print("  Analyzing chords...")
    chords = analyze_chords(harmony_notes + [n for n in melody_notes], ppq)
    chord_families = analyze_chord_families(chords)
    
    # Detect progressions
    print("  Detecting progressions...")
    progressions = detect_progression_patterns(chords)
    
    # Analyze melody
    print("  Analyzing melody...")
    melody_contours = analyze_melody_contour(melody_notes, ppq)
    melody_stats = calculate_melody_statistics(melody_notes)
    
    # Analyze phrases
    print("  Analyzing phrases...")
    phrase_analysis = analyze_phrase_lengths(melody_notes, ppq)
    
    # Analyze harmonic rhythm
    print("  Analyzing harmonic rhythm...")
    harmonic_rhythm = analyze_harmonic_rhythm(chords)
    
    # Compile results
    analysis = {
        'metadata': {
            'name': name or filepath.stem,
            'source_file': str(filepath),
            'genre': genre,
            'key': key,
            'mode': mode,
            'key_confidence': key_confidence,
            'bpm': bpm,
            'ppq': ppq,
            'time_signature': '4/4',
            'total_bars': total_bars,
            'date_analyzed': datetime.now().isoformat()
        },
        'chords': {
            'progression': chords,
            'family_distribution': chord_families,
            'detected_patterns': progressions
        },
        'melody': {
            'statistics': melody_stats,
            'contours': melody_contours
        },
        'phrases': phrase_analysis,
        'harmonic_rhythm': harmonic_rhythm
    }
    
    return analysis

def save_analysis(analysis, output_path=None):
    """Save analysis to JSON."""
    if output_path is None:
        name = analysis['metadata']['name']
        output_path = OUTPUT_PATH / f"{name}_structure.json"
    else:
        output_path = Path(output_path)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"Saved analysis: {output_path}")
    return output_path

def save_to_database(analysis):
    """Save analysis to SQLite database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    meta = analysis['metadata']
    
    # Insert main record
    cursor.execute('''
        INSERT INTO structure_analyses
        (name, source_file, genre, key_detected, mode_detected, bpm, time_signature, total_bars, date_analyzed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        meta['name'], meta['source_file'], meta['genre'],
        meta['key'], meta['mode'], meta['bpm'],
        meta['time_signature'], meta['total_bars'], meta['date_analyzed']
    ))
    
    analysis_id = cursor.lastrowid
    
    # Insert chords
    for chord in analysis['chords']['progression']:
        cursor.execute('''
            INSERT INTO chord_progressions
            (analysis_id, bar_number, beat, root_note, chord_type, chord_family, duration_beats, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_id, chord['bar'], chord['beat'],
            chord['root'], chord['type'], chord['family'],
            chord['duration_beats'], chord['confidence']
        ))
    
    # Insert detected patterns
    for pattern in analysis['chords']['detected_patterns']:
        cursor.execute('''
            INSERT INTO detected_patterns
            (analysis_id, pattern_name, pattern_type, start_bar, transposition, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            analysis_id, pattern['pattern'], 'chord_progression',
            pattern['start_bar'], pattern['transposition'], pattern['confidence']
        ))
    
    # Insert melody contours
    for contour in analysis['melody']['contours']:
        cursor.execute('''
            INSERT INTO melody_contours
            (analysis_id, phrase_number, start_bar, end_bar, contour_type, pitch_range, direction, step_count, leap_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_id, contour['phrase_number'],
            contour['start_bar'], contour['end_bar'],
            contour['contour_type'], contour['pitch_range'],
            contour['direction'], contour['step_count'], contour['leap_count']
        ))
    
    # Insert phrase structure
    for i, phrase in enumerate(analysis['phrases']['phrases']):
        cursor.execute('''
            INSERT INTO phrase_structure
            (analysis_id, phrase_number, start_bar, length_bars, note_density)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            analysis_id, i + 1,
            phrase['start_bar'], phrase['length_bars'], phrase['note_density']
        ))
    
    # Insert harmonic rhythm
    hr = analysis['harmonic_rhythm']
    if hr:
        cursor.execute('''
            INSERT INTO harmonic_rhythm
            (analysis_id, avg_chord_duration, changes_per_bar, rhythm_pattern, consistency)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            analysis_id,
            hr.get('avg_chord_duration', 0),
            hr.get('changes_per_bar', 0),
            hr.get('rhythm_pattern', ''),
            hr.get('consistency', 0)
        ))
    
    conn.commit()
    conn.close()
    
    print(f"Saved to database with ID: {analysis_id}")
    return analysis_id

# ============================================================================
# Query Functions
# ============================================================================

def list_analyses(genre=None, key=None, limit=50):
    """List all analyses."""
    conn = get_connection()
    cursor = conn.cursor()
    
    conditions = []
    params = []
    
    if genre:
        conditions.append("genre LIKE ?")
        params.append(f'%{genre}%')
    
    if key:
        conditions.append("key_detected = ?")
        params.append(key)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    cursor.execute(f'''
        SELECT id, name, genre, key_detected, mode_detected, bpm, total_bars
        FROM structure_analyses
        WHERE {where_clause}
        ORDER BY date_analyzed DESC
        LIMIT ?
    ''', params + [limit])
    
    results = cursor.fetchall()
    conn.close()
    
    print(f"\n{'ID':<6} {'Name':<30} {'Genre':<12} {'Key':<8} {'BPM':<8} {'Bars':<6}")
    print("-" * 75)
    
    for row in results:
        id_, name, genre, key, mode, bpm, bars = row
        name_display = name[:28] + '..' if len(name) > 30 else name
        key_display = f"{key or '?'} {mode or ''}"[:8]
        print(f"{id_:<6} {name_display:<30} {genre or '':<12} {key_display:<8} {bpm or '?':<8} {bars or '?':<6}")

def show_detail(analysis_id):
    """Show detailed analysis."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM structure_analyses WHERE id = ?', (analysis_id,))
    analysis = cursor.fetchone()
    
    if not analysis:
        print(f"Analysis {analysis_id} not found")
        return
    
    print(f"\n{'='*60}")
    print(f"Analysis: {analysis[1]}")
    print(f"Key: {analysis[4]} {analysis[5]}")
    print(f"BPM: {analysis[6]}, Bars: {analysis[8]}")
    print(f"{'='*60}")
    
    # Show chord progression
    cursor.execute('''
        SELECT bar_number, root_note, chord_type, duration_beats
        FROM chord_progressions
        WHERE analysis_id = ?
        ORDER BY bar_number, beat
        LIMIT 20
    ''', (analysis_id,))
    
    print(f"\nChord Progression (first 20):")
    print(f"{'Bar':<6} {'Chord':<12} {'Duration':<10}")
    print("-" * 30)
    
    for bar, root, ctype, dur in cursor.fetchall():
        print(f"{bar:<6} {root}{ctype:<10} {dur:.1f} beats")
    
    # Show detected patterns
    cursor.execute('''
        SELECT pattern_name, start_bar, transposition, confidence
        FROM detected_patterns
        WHERE analysis_id = ?
    ''', (analysis_id,))
    
    patterns = cursor.fetchall()
    if patterns:
        print(f"\nDetected Patterns:")
        for name, bar, trans, conf in patterns:
            print(f"  {name} in {NOTE_NAMES[trans]} (bar {bar}, confidence {conf:.0%})")
    
    # Show harmonic rhythm
    cursor.execute('''
        SELECT avg_chord_duration, changes_per_bar, rhythm_pattern, consistency
        FROM harmonic_rhythm
        WHERE analysis_id = ?
    ''', (analysis_id,))
    
    hr = cursor.fetchone()
    if hr:
        print(f"\nHarmonic Rhythm:")
        print(f"  Average chord duration: {hr[0]:.1f} beats")
        print(f"  Changes per bar: {hr[1]:.2f}")
        print(f"  Pattern: {hr[2]}")
        print(f"  Consistency: {hr[3]:.0%}")
    
    conn.close()

def scan_folder(folder_path, genre=None, recursive=True):
    """Scan folder for MIDI files."""
    folder = Path(folder_path).expanduser().resolve()
    
    pattern = '**/*.mid' if recursive else '*.mid'
    midi_files = list(folder.glob(pattern))
    midi_files.extend(folder.glob(pattern.replace('.mid', '.midi')))
    
    print(f"Found {len(midi_files)} MIDI files")
    print("-" * 50)
    
    for filepath in midi_files:
        try:
            analysis = analyze_structure(filepath, genre=genre)
            save_analysis(analysis)
            save_to_database(analysis)
            print()
        except Exception as e:
            print(f"  Error: {e}\n")

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='MIDI Structure Analyzer - Extract chord progressions, melody shapes, and more',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s analyze song.mid --genre pop
  %(prog)s scan ~/MIDI/Songs --genre jazz
  %(prog)s list --key C
  %(prog)s detail 5
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze MIDI file')
    analyze_parser.add_argument('file', help='MIDI file path')
    analyze_parser.add_argument('--name', help='Analysis name')
    analyze_parser.add_argument('--genre', help='Genre tag')
    analyze_parser.add_argument('--output', help='Output JSON path')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan folder')
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
        show_detail(args.id)
    
    elif args.command == 'init':
        init_database()
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
