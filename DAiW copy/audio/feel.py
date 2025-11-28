#!/usr/bin/env python3
"""
Audio Feel Extractor
Extract production feel characteristics from audio files.

Analyzes:
- Transient drift (timing looseness)
- RMS swing (dynamic groove)
- Spectral movement (tonal changes over time)
- Frequency balance (mix fingerprint)
- Stereo characteristics

Part of the Music Brain system.
"""

import argparse
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import warnings

# Suppress librosa warnings
warnings.filterwarnings('ignore')

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Error: numpy required. Install with: pip install numpy")

try:
    import librosa
    import librosa.display
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("Error: librosa required. Install with: pip install librosa")

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    print("Warning: soundfile not available")

# ============================================================================
# Configuration
# ============================================================================

DB_PATH = Path.home() / "Music-Brain" / "audio-feel" / "audio_feel.db"
FINGERPRINTS_PATH = Path.home() / "Music-Brain" / "audio-feel" / "fingerprints"

# Frequency bands for analysis
FREQ_BANDS = {
    'sub': (20, 60),
    'bass': (60, 250),
    'low_mid': (250, 500),
    'mid': (500, 2000),
    'high_mid': (2000, 4000),
    'presence': (4000, 6000),
    'brilliance': (6000, 12000),
    'air': (12000, 20000)
}

# Genre reference fingerprints (typical frequency balance in dB relative to mid)
GENRE_FINGERPRINTS = {
    'hiphop': {
        'sub': 6, 'bass': 4, 'low_mid': -2, 'mid': 0,
        'high_mid': -1, 'presence': 1, 'brilliance': -2, 'air': -4,
        'description': 'Heavy sub, scooped low-mids, crisp highs'
    },
    'rock': {
        'sub': -2, 'bass': 2, 'low_mid': 1, 'mid': 0,
        'high_mid': 2, 'presence': 3, 'brilliance': 1, 'air': -1,
        'description': 'Guitar presence, punchy mids'
    },
    'pop': {
        'sub': 0, 'bass': 1, 'low_mid': -1, 'mid': 0,
        'high_mid': 2, 'presence': 3, 'brilliance': 2, 'air': 1,
        'description': 'Bright, polished, vocal-forward'
    },
    'jazz': {
        'sub': -3, 'bass': 1, 'low_mid': 2, 'mid': 0,
        'high_mid': 0, 'presence': -1, 'brilliance': -2, 'air': -3,
        'description': 'Warm, natural, less hyped'
    },
    'electronic': {
        'sub': 8, 'bass': 5, 'low_mid': -3, 'mid': 0,
        'high_mid': 2, 'presence': 3, 'brilliance': 4, 'air': 2,
        'description': 'Heavy sub, scooped mids, bright tops'
    },
    'classical': {
        'sub': -4, 'bass': 0, 'low_mid': 1, 'mid': 0,
        'high_mid': 0, 'presence': 0, 'brilliance': -1, 'air': 1,
        'description': 'Natural, balanced, room sound'
    },
    'metal': {
        'sub': 2, 'bass': 3, 'low_mid': -2, 'mid': 0,
        'high_mid': 4, 'presence': 5, 'brilliance': 2, 'air': 0,
        'description': 'Scooped mids, aggressive presence'
    },
    'rnb': {
        'sub': 5, 'bass': 3, 'low_mid': 0, 'mid': 0,
        'high_mid': 1, 'presence': 2, 'brilliance': 1, 'air': 0,
        'description': 'Warm low end, smooth highs'
    },
    'lofi': {
        'sub': -2, 'bass': 2, 'low_mid': 3, 'mid': 0,
        'high_mid': -3, 'presence': -4, 'brilliance': -6, 'air': -8,
        'description': 'Muffled, warm, rolled-off highs'
    },
    'country': {
        'sub': -3, 'bass': 1, 'low_mid': 0, 'mid': 0,
        'high_mid': 2, 'presence': 3, 'brilliance': 2, 'air': 0,
        'description': 'Acoustic clarity, bright guitars'
    }
}

# ============================================================================
# Database Setup
# ============================================================================

def init_database():
    """Initialize SQLite database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    FINGERPRINTS_PATH.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Main analysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audio_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            source_file TEXT,
            genre TEXT,
            duration_seconds REAL,
            sample_rate INTEGER,
            channels INTEGER,
            estimated_bpm REAL,
            estimated_key TEXT,
            date_analyzed TEXT
        )
    ''')
    
    # Transient analysis
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transient_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            onset_count INTEGER,
            avg_onset_interval_ms REAL,
            onset_interval_std_ms REAL,
            transient_drift_ms REAL,
            attack_sharpness REAL,
            FOREIGN KEY (analysis_id) REFERENCES audio_analyses(id)
        )
    ''')
    
    # RMS/dynamics analysis
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dynamics_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            rms_mean REAL,
            rms_std REAL,
            rms_swing_ratio REAL,
            dynamic_range_db REAL,
            crest_factor_db REAL,
            loudness_lufs REAL,
            FOREIGN KEY (analysis_id) REFERENCES audio_analyses(id)
        )
    ''')
    
    # Spectral analysis
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spectral_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            spectral_centroid_mean REAL,
            spectral_centroid_std REAL,
            spectral_bandwidth_mean REAL,
            spectral_rolloff_mean REAL,
            spectral_flux_mean REAL,
            brightness REAL,
            FOREIGN KEY (analysis_id) REFERENCES audio_analyses(id)
        )
    ''')
    
    # Frequency balance (mix fingerprint)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frequency_balance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            band_name TEXT,
            energy_db REAL,
            relative_to_mid_db REAL,
            FOREIGN KEY (analysis_id) REFERENCES audio_analyses(id)
        )
    ''')
    
    # Stereo analysis
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stereo_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            stereo_width REAL,
            mid_side_ratio REAL,
            correlation REAL,
            FOREIGN KEY (analysis_id) REFERENCES audio_analyses(id)
        )
    ''')
    
    # Genre match scores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS genre_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER,
            genre TEXT,
            match_score REAL,
            FOREIGN KEY (analysis_id) REFERENCES audio_analyses(id)
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
# Audio Loading
# ============================================================================

def load_audio(filepath, sr=22050, mono=True, duration=None):
    """Load audio file."""
    if not LIBROSA_AVAILABLE:
        raise ImportError("librosa required")
    
    y, sr = librosa.load(filepath, sr=sr, mono=mono, duration=duration)
    return y, sr

def load_audio_stereo(filepath, sr=22050, duration=None):
    """Load audio in stereo."""
    if not LIBROSA_AVAILABLE:
        raise ImportError("librosa required")
    
    y, sr = librosa.load(filepath, sr=sr, mono=False, duration=duration)
    return y, sr

# ============================================================================
# Transient Analysis
# ============================================================================

def analyze_transients(y, sr):
    """
    Analyze transient characteristics.
    Returns timing drift, attack sharpness, onset patterns.
    """
    # Detect onsets
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, units='frames')
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    
    if len(onset_times) < 2:
        return {
            'onset_count': len(onset_times),
            'avg_interval_ms': 0,
            'interval_std_ms': 0,
            'transient_drift_ms': 0,
            'attack_sharpness': 0
        }
    
    # Calculate inter-onset intervals
    intervals = np.diff(onset_times) * 1000  # Convert to ms
    
    avg_interval = np.mean(intervals)
    interval_std = np.std(intervals)
    
    # Transient drift: variation from expected grid
    # Higher = more human/loose, Lower = more quantized
    if avg_interval > 0:
        drift_ratio = interval_std / avg_interval
        transient_drift = interval_std
    else:
        drift_ratio = 0
        transient_drift = 0
    
    # Attack sharpness via onset strength
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_peaks = onset_env[onset_frames] if len(onset_frames) > 0 else [0]
    attack_sharpness = np.mean(onset_peaks)
    
    return {
        'onset_count': len(onset_times),
        'avg_interval_ms': float(avg_interval),
        'interval_std_ms': float(interval_std),
        'transient_drift_ms': float(transient_drift),
        'drift_ratio': float(drift_ratio),
        'attack_sharpness': float(attack_sharpness),
        'onset_times': onset_times.tolist()[:100]  # First 100 for reference
    }

def analyze_transient_drift_by_beat(y, sr, bpm=None):
    """
    Analyze how transients drift from the beat grid.
    """
    # Estimate tempo if not provided
    if bpm is None:
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        bpm = float(tempo)
    
    # Get beat frames
    _, beat_frames = librosa.beat.beat_track(y=y, sr=sr, bpm=bpm)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    
    # Get onset times
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    
    if len(beat_times) < 2 or len(onset_times) < 2:
        return {'beat_drift_ms': 0, 'on_beat_ratio': 0}
    
    # Calculate drift from nearest beat for each onset
    beat_interval = 60000 / bpm  # ms per beat
    drifts = []
    on_beat_count = 0
    threshold_ms = beat_interval * 0.1  # 10% of beat = "on beat"
    
    for onset in onset_times:
        # Find nearest beat
        nearest_beat_idx = np.argmin(np.abs(beat_times - onset))
        nearest_beat = beat_times[nearest_beat_idx]
        drift = (onset - nearest_beat) * 1000  # ms
        drifts.append(drift)
        
        if abs(drift) < threshold_ms:
            on_beat_count += 1
    
    return {
        'beat_drift_mean_ms': float(np.mean(drifts)),
        'beat_drift_std_ms': float(np.std(drifts)),
        'on_beat_ratio': on_beat_count / len(onset_times) if onset_times.size > 0 else 0,
        'bpm_used': bpm
    }

# ============================================================================
# RMS / Dynamics Analysis
# ============================================================================

def analyze_dynamics(y, sr, frame_length=2048, hop_length=512):
    """
    Analyze dynamic characteristics.
    Returns RMS swing, dynamic range, crest factor.
    """
    # Calculate RMS
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    
    # RMS statistics
    rms_mean = np.mean(rms)
    rms_std = np.std(rms)
    rms_max = np.max(rms)
    rms_min = np.min(rms[rms > 0]) if np.any(rms > 0) else 0
    
    # RMS swing ratio (variation in loudness)
    # Higher = more dynamic, Lower = more compressed
    rms_swing = rms_std / rms_mean if rms_mean > 0 else 0
    
    # Dynamic range in dB
    if rms_min > 0 and rms_max > 0:
        dynamic_range = 20 * np.log10(rms_max / rms_min)
    else:
        dynamic_range = 0
    
    # Crest factor (peak to RMS ratio)
    peak = np.max(np.abs(y))
    if rms_mean > 0:
        crest_factor = 20 * np.log10(peak / rms_mean)
    else:
        crest_factor = 0
    
    # Approximate LUFS (simplified)
    # Real LUFS requires ITU-R BS.1770-4 implementation
    rms_db = 20 * np.log10(rms_mean) if rms_mean > 0 else -100
    approx_lufs = rms_db - 0.691  # Rough approximation
    
    return {
        'rms_mean': float(rms_mean),
        'rms_std': float(rms_std),
        'rms_swing_ratio': float(rms_swing),
        'dynamic_range_db': float(dynamic_range),
        'crest_factor_db': float(crest_factor),
        'approx_lufs': float(approx_lufs),
        'rms_curve': rms.tolist()[:500]  # First 500 frames
    }

def analyze_rms_swing_pattern(y, sr, bpm=None):
    """
    Analyze RMS patterns relative to beat grid.
    Reveals groove in dynamics.
    """
    if bpm is None:
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        bpm = float(tempo)
    
    # Calculate RMS
    hop_length = 512
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    rms_times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)
    
    # Get beat times
    _, beat_frames = librosa.beat.beat_track(y=y, sr=sr, bpm=bpm)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    
    if len(beat_times) < 4:
        return {'rms_by_beat_position': {}}
    
    # Analyze RMS at each beat subdivision (16th notes)
    beat_interval = 60 / bpm
    subdivisions = 16
    sub_interval = beat_interval / (subdivisions / 4)
    
    rms_by_position = defaultdict(list)
    
    for i, rms_time in enumerate(rms_times):
        if rms_time > beat_times[-1]:
            break
        
        # Find position within beat cycle
        beat_idx = np.searchsorted(beat_times, rms_time) - 1
        if beat_idx < 0:
            continue
        
        time_in_bar = (rms_time - beat_times[beat_idx]) % (beat_interval * 4)
        position = int((time_in_bar / (beat_interval * 4)) * subdivisions) % subdivisions
        
        rms_by_position[position].append(rms[i])
    
    # Calculate average RMS at each position
    rms_pattern = {}
    for pos in range(subdivisions):
        if rms_by_position[pos]:
            rms_pattern[pos] = {
                'mean': float(np.mean(rms_by_position[pos])),
                'std': float(np.std(rms_by_position[pos]))
            }
    
    return {
        'rms_by_beat_position': rms_pattern,
        'subdivisions': subdivisions,
        'bpm': bpm
    }

# ============================================================================
# Spectral Analysis
# ============================================================================

def analyze_spectrum(y, sr):
    """
    Analyze spectral characteristics.
    """
    # Spectral centroid (brightness indicator)
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    
    # Spectral bandwidth
    bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
    
    # Spectral rolloff (frequency below which 85% of energy)
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    
    # Spectral flux (rate of spectral change)
    spec = np.abs(librosa.stft(y))
    flux = np.sqrt(np.sum(np.diff(spec, axis=1)**2, axis=0))
    
    # Brightness: ratio of high freq to total energy
    # Using spectral centroid relative to Nyquist
    brightness = np.mean(centroid) / (sr / 2)
    
    return {
        'centroid_mean': float(np.mean(centroid)),
        'centroid_std': float(np.std(centroid)),
        'bandwidth_mean': float(np.mean(bandwidth)),
        'bandwidth_std': float(np.std(bandwidth)),
        'rolloff_mean': float(np.mean(rolloff)),
        'flux_mean': float(np.mean(flux)),
        'flux_std': float(np.std(flux)),
        'brightness': float(brightness),
        'spectral_movement': float(np.std(centroid) / np.mean(centroid)) if np.mean(centroid) > 0 else 0
    }

def analyze_spectral_movement(y, sr, n_segments=16):
    """
    Analyze how spectrum changes over time.
    High movement = more variation, Low = more static.
    """
    # Split into segments
    segment_length = len(y) // n_segments
    
    centroids = []
    bandwidths = []
    
    for i in range(n_segments):
        start = i * segment_length
        end = start + segment_length
        segment = y[start:end]
        
        if len(segment) > 2048:
            c = librosa.feature.spectral_centroid(y=segment, sr=sr)[0]
            b = librosa.feature.spectral_bandwidth(y=segment, sr=sr)[0]
            centroids.append(np.mean(c))
            bandwidths.append(np.mean(b))
    
    if len(centroids) < 2:
        return {'centroid_movement': 0, 'bandwidth_movement': 0}
    
    # Calculate movement as coefficient of variation
    centroid_movement = np.std(centroids) / np.mean(centroids) if np.mean(centroids) > 0 else 0
    bandwidth_movement = np.std(bandwidths) / np.mean(bandwidths) if np.mean(bandwidths) > 0 else 0
    
    return {
        'centroid_movement': float(centroid_movement),
        'bandwidth_movement': float(bandwidth_movement),
        'centroids_over_time': centroids,
        'bandwidths_over_time': bandwidths
    }

# ============================================================================
# Frequency Balance (Mix Fingerprint)
# ============================================================================

def analyze_frequency_balance(y, sr):
    """
    Analyze energy in different frequency bands.
    Returns mix fingerprint.
    """
    # Compute power spectrum
    D = np.abs(librosa.stft(y))**2
    freqs = librosa.fft_frequencies(sr=sr)
    
    band_energies = {}
    
    for band_name, (low, high) in FREQ_BANDS.items():
        # Find frequency bin indices for this band
        band_mask = (freqs >= low) & (freqs < high)
        
        if np.any(band_mask):
            band_energy = np.mean(D[band_mask, :])
            band_energies[band_name] = band_energy
        else:
            band_energies[band_name] = 0
    
    # Convert to dB
    band_db = {}
    for band, energy in band_energies.items():
        if energy > 0:
            band_db[band] = 10 * np.log10(energy)
        else:
            band_db[band] = -100
    
    # Calculate relative to mid band
    mid_db = band_db.get('mid', 0)
    relative_db = {}
    for band, db in band_db.items():
        relative_db[band] = db - mid_db
    
    return {
        'absolute_db': band_db,
        'relative_to_mid_db': relative_db
    }

def match_genre_fingerprint(frequency_balance):
    """
    Match frequency balance against genre fingerprints.
    Returns similarity scores.
    """
    relative_db = frequency_balance.get('relative_to_mid_db', {})
    
    if not relative_db:
        return {}
    
    matches = {}
    
    for genre, fingerprint in GENRE_FINGERPRINTS.items():
        total_diff = 0
        band_count = 0
        
        for band in FREQ_BANDS.keys():
            if band in relative_db and band in fingerprint:
                diff = abs(relative_db[band] - fingerprint[band])
                total_diff += diff
                band_count += 1
        
        if band_count > 0:
            avg_diff = total_diff / band_count
            # Convert to similarity score (0-1, higher = better match)
            similarity = max(0, 1 - (avg_diff / 10))
            matches[genre] = {
                'score': float(similarity),
                'avg_diff_db': float(avg_diff),
                'description': fingerprint.get('description', '')
            }
    
    return dict(sorted(matches.items(), key=lambda x: x[1]['score'], reverse=True))

# ============================================================================
# Stereo Analysis
# ============================================================================

def analyze_stereo(y_stereo, sr):
    """
    Analyze stereo characteristics.
    """
    if y_stereo.ndim != 2 or y_stereo.shape[0] != 2:
        return {'stereo': False}
    
    left = y_stereo[0]
    right = y_stereo[1]
    
    # Mid/Side calculation
    mid = (left + right) / 2
    side = (left - right) / 2
    
    # Stereo width (side energy relative to mid)
    mid_energy = np.mean(mid**2)
    side_energy = np.mean(side**2)
    
    if mid_energy > 0:
        stereo_width = side_energy / mid_energy
    else:
        stereo_width = 0
    
    # Correlation between channels
    if np.std(left) > 0 and np.std(right) > 0:
        correlation = np.corrcoef(left, right)[0, 1]
    else:
        correlation = 1.0
    
    # Mid/Side ratio in dB
    if side_energy > 0 and mid_energy > 0:
        ms_ratio_db = 10 * np.log10(mid_energy / side_energy)
    else:
        ms_ratio_db = 100  # Essentially mono
    
    return {
        'stereo': True,
        'stereo_width': float(stereo_width),
        'mid_side_ratio_db': float(ms_ratio_db),
        'correlation': float(correlation),
        'is_mono': correlation > 0.99,
        'is_wide': stereo_width > 0.5,
        'phase_issues': correlation < 0.3
    }

# ============================================================================
# Full Analysis Pipeline
# ============================================================================

def analyze_audio_feel(filepath, name=None, genre=None, duration=60):
    """
    Full audio feel analysis.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    print(f"Analyzing: {filepath.name}")
    
    # Load audio (mono for most analysis)
    y, sr = load_audio(str(filepath), duration=duration)
    
    # Try to load stereo for stereo analysis
    try:
        y_stereo, _ = load_audio_stereo(str(filepath), sr=sr, duration=duration)
        has_stereo = y_stereo.ndim == 2
    except:
        y_stereo = None
        has_stereo = False
    
    # Get basic info
    full_duration = librosa.get_duration(path=str(filepath))
    
    # Estimate tempo and key
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    bpm = float(tempo)
    
    # Key estimation via chroma
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    key_idx = int(np.argmax(np.mean(chroma, axis=1)))
    key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    estimated_key = key_names[key_idx]
    
    print(f"  Duration: {full_duration:.1f}s, BPM: {bpm:.1f}, Key: {estimated_key}")
    
    # Build analysis result
    analysis = {
        'metadata': {
            'name': name or filepath.stem,
            'source_file': str(filepath),
            'genre': genre,
            'duration_seconds': full_duration,
            'sample_rate': sr,
            'channels': 2 if has_stereo else 1,
            'estimated_bpm': bpm,
            'estimated_key': estimated_key,
            'date_analyzed': datetime.now().isoformat()
        }
    }
    
    # Transient analysis
    print("  Analyzing transients...")
    analysis['transients'] = analyze_transients(y, sr)
    analysis['beat_drift'] = analyze_transient_drift_by_beat(y, sr, bpm)
    print(f"    Drift: {analysis['transients']['transient_drift_ms']:.1f}ms")
    
    # Dynamics analysis
    print("  Analyzing dynamics...")
    analysis['dynamics'] = analyze_dynamics(y, sr)
    analysis['rms_pattern'] = analyze_rms_swing_pattern(y, sr, bpm)
    print(f"    RMS swing: {analysis['dynamics']['rms_swing_ratio']:.3f}")
    print(f"    Dynamic range: {analysis['dynamics']['dynamic_range_db']:.1f}dB")
    
    # Spectral analysis
    print("  Analyzing spectrum...")
    analysis['spectrum'] = analyze_spectrum(y, sr)
    analysis['spectral_movement'] = analyze_spectral_movement(y, sr)
    print(f"    Brightness: {analysis['spectrum']['brightness']:.3f}")
    print(f"    Spectral movement: {analysis['spectrum']['spectral_movement']:.3f}")
    
    # Frequency balance
    print("  Analyzing frequency balance...")
    analysis['frequency_balance'] = analyze_frequency_balance(y, sr)
    analysis['genre_matches'] = match_genre_fingerprint(analysis['frequency_balance'])
    
    top_match = list(analysis['genre_matches'].items())[0] if analysis['genre_matches'] else ('unknown', {'score': 0})
    print(f"    Best genre match: {top_match[0]} ({top_match[1]['score']:.2f})")
    
    # Stereo analysis
    if has_stereo:
        print("  Analyzing stereo field...")
        analysis['stereo'] = analyze_stereo(y_stereo, sr)
        print(f"    Stereo width: {analysis['stereo']['stereo_width']:.3f}")
        print(f"    Correlation: {analysis['stereo']['correlation']:.3f}")
    else:
        analysis['stereo'] = {'stereo': False}
    
    # Summary
    analysis['summary'] = {
        'transient_drift_ms': analysis['transients']['transient_drift_ms'],
        'rms_swing_ratio': analysis['dynamics']['rms_swing_ratio'],
        'dynamic_range_db': analysis['dynamics']['dynamic_range_db'],
        'spectral_movement': analysis['spectrum']['spectral_movement'],
        'brightness': analysis['spectrum']['brightness'],
        'top_genre_match': top_match[0],
        'genre_match_score': top_match[1]['score'],
        'stereo_width': analysis['stereo'].get('stereo_width', 0)
    }
    
    return analysis

def save_analysis(analysis, output_path=None):
    """Save analysis to JSON."""
    if output_path is None:
        name = analysis['metadata']['name']
        output_path = FINGERPRINTS_PATH / f"{name}_feel.json"
    else:
        output_path = Path(output_path)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Remove large arrays for storage
    clean_analysis = {}
    for key, value in analysis.items():
        if isinstance(value, dict):
            clean_value = {}
            for k, v in value.items():
                if isinstance(v, list) and len(v) > 100:
                    continue  # Skip large arrays
                clean_value[k] = v
            clean_analysis[key] = clean_value
        else:
            clean_analysis[key] = value
    
    with open(output_path, 'w') as f:
        json.dump(clean_analysis, f, indent=2)
    
    print(f"Saved: {output_path}")
    return output_path

def save_to_database(analysis):
    """Save to SQLite database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    meta = analysis['metadata']
    
    # Main record
    cursor.execute('''
        INSERT INTO audio_analyses
        (name, source_file, genre, duration_seconds, sample_rate, channels, estimated_bpm, estimated_key, date_analyzed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        meta['name'], meta['source_file'], meta['genre'],
        meta['duration_seconds'], meta['sample_rate'], meta['channels'],
        meta['estimated_bpm'], meta['estimated_key'], meta['date_analyzed']
    ))
    
    analysis_id = cursor.lastrowid
    
    # Transient data
    trans = analysis.get('transients', {})
    cursor.execute('''
        INSERT INTO transient_analysis
        (analysis_id, onset_count, avg_onset_interval_ms, onset_interval_std_ms, transient_drift_ms, attack_sharpness)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        analysis_id, trans.get('onset_count', 0), trans.get('avg_interval_ms', 0),
        trans.get('interval_std_ms', 0), trans.get('transient_drift_ms', 0),
        trans.get('attack_sharpness', 0)
    ))
    
    # Dynamics data
    dyn = analysis.get('dynamics', {})
    cursor.execute('''
        INSERT INTO dynamics_analysis
        (analysis_id, rms_mean, rms_std, rms_swing_ratio, dynamic_range_db, crest_factor_db, loudness_lufs)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        analysis_id, dyn.get('rms_mean', 0), dyn.get('rms_std', 0),
        dyn.get('rms_swing_ratio', 0), dyn.get('dynamic_range_db', 0),
        dyn.get('crest_factor_db', 0), dyn.get('approx_lufs', 0)
    ))
    
    # Spectral data
    spec = analysis.get('spectrum', {})
    cursor.execute('''
        INSERT INTO spectral_analysis
        (analysis_id, spectral_centroid_mean, spectral_centroid_std, spectral_bandwidth_mean, spectral_rolloff_mean, spectral_flux_mean, brightness)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        analysis_id, spec.get('centroid_mean', 0), spec.get('centroid_std', 0),
        spec.get('bandwidth_mean', 0), spec.get('rolloff_mean', 0),
        spec.get('flux_mean', 0), spec.get('brightness', 0)
    ))
    
    # Frequency balance
    freq = analysis.get('frequency_balance', {})
    relative = freq.get('relative_to_mid_db', {})
    absolute = freq.get('absolute_db', {})
    for band in FREQ_BANDS.keys():
        if band in relative:
            cursor.execute('''
                INSERT INTO frequency_balance
                (analysis_id, band_name, energy_db, relative_to_mid_db)
                VALUES (?, ?, ?, ?)
            ''', (analysis_id, band, absolute.get(band, 0), relative.get(band, 0)))
    
    # Stereo
    stereo = analysis.get('stereo', {})
    if stereo.get('stereo'):
        cursor.execute('''
            INSERT INTO stereo_analysis
            (analysis_id, stereo_width, mid_side_ratio, correlation)
            VALUES (?, ?, ?, ?)
        ''', (
            analysis_id, stereo.get('stereo_width', 0),
            stereo.get('mid_side_ratio_db', 0), stereo.get('correlation', 0)
        ))
    
    # Genre matches
    for genre, match_data in analysis.get('genre_matches', {}).items():
        cursor.execute('''
            INSERT INTO genre_matches
            (analysis_id, genre, match_score)
            VALUES (?, ?, ?)
        ''', (analysis_id, genre, match_data['score']))
    
    conn.commit()
    conn.close()
    
    print(f"Saved to database with ID: {analysis_id}")
    return analysis_id

# ============================================================================
# Batch Processing
# ============================================================================

def scan_folder(folder_path, genre=None, recursive=True):
    """Scan folder for audio files."""
    folder = Path(folder_path).expanduser().resolve()
    
    if not folder.exists():
        print(f"Error: Folder not found: {folder}")
        return
    
    extensions = ['*.wav', '*.mp3', '*.flac', '*.aiff', '*.aif', '*.m4a', '*.ogg']
    audio_files = []
    
    for ext in extensions:
        if recursive:
            audio_files.extend(folder.glob(f'**/{ext}'))
        else:
            audio_files.extend(folder.glob(ext))
    
    print(f"Found {len(audio_files)} audio files")
    print("-" * 50)
    
    analyzed = 0
    errors = 0
    
    for filepath in audio_files:
        try:
            analysis = analyze_audio_feel(filepath, genre=genre)
            save_analysis(analysis)
            save_to_database(analysis)
            analyzed += 1
        except Exception as e:
            print(f"  Error: {e}")
            errors += 1
    
    print("-" * 50)
    print(f"Analyzed: {analyzed}")
    print(f"Errors: {errors}")

# ============================================================================
# Query Functions
# ============================================================================

def list_analyses(genre=None, limit=50):
    """List analyses."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if genre:
        cursor.execute('''
            SELECT a.id, a.name, a.genre, a.estimated_bpm, d.rms_swing_ratio, t.transient_drift_ms
            FROM audio_analyses a
            LEFT JOIN dynamics_analysis d ON a.id = d.analysis_id
            LEFT JOIN transient_analysis t ON a.id = t.analysis_id
            WHERE a.genre LIKE ?
            ORDER BY a.name LIMIT ?
        ''', (f'%{genre}%', limit))
    else:
        cursor.execute('''
            SELECT a.id, a.name, a.genre, a.estimated_bpm, d.rms_swing_ratio, t.transient_drift_ms
            FROM audio_analyses a
            LEFT JOIN dynamics_analysis d ON a.id = d.analysis_id
            LEFT JOIN transient_analysis t ON a.id = t.analysis_id
            ORDER BY a.name LIMIT ?
        ''', (limit,))
    
    results = cursor.fetchall()
    conn.close()
    
    print(f"\n{'ID':<6} {'Name':<30} {'Genre':<10} {'BPM':<6} {'RMS Swing':<10} {'Drift(ms)':<10}")
    print("-" * 80)
    
    for row in results:
        id_, name, genre, bpm, rms_swing, drift = row
        name_display = name[:28] + '..' if len(name) > 30 else name
        print(f"{id_:<6} {name_display:<30} {genre or '':<10} {bpm or 0:.0f}  {rms_swing or 0:.3f}     {drift or 0:.1f}")

def get_analysis_detail(analysis_id):
    """Get detailed analysis."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM audio_analyses WHERE id = ?', (analysis_id,))
    analysis = cursor.fetchone()
    
    if not analysis:
        print(f"Analysis {analysis_id} not found")
        return
    
    print(f"\n{'='*60}")
    print(f"Analysis: {analysis[1]}")
    print(f"File: {analysis[2]}")
    print(f"Genre: {analysis[3] or 'Unknown'}")
    print(f"BPM: {analysis[7]:.1f}, Key: {analysis[8]}")
    print(f"Duration: {analysis[4]:.1f}s")
    print(f"{'='*60}")
    
    # Transients
    cursor.execute('SELECT * FROM transient_analysis WHERE analysis_id = ?', (analysis_id,))
    trans = cursor.fetchone()
    if trans:
        print(f"\nTransients:")
        print(f"  Onset count: {trans[2]}")
        print(f"  Transient drift: {trans[5]:.1f}ms")
        print(f"  Attack sharpness: {trans[6]:.3f}")
    
    # Dynamics
    cursor.execute('SELECT * FROM dynamics_analysis WHERE analysis_id = ?', (analysis_id,))
    dyn = cursor.fetchone()
    if dyn:
        print(f"\nDynamics:")
        print(f"  RMS swing ratio: {dyn[4]:.3f}")
        print(f"  Dynamic range: {dyn[5]:.1f}dB")
        print(f"  Crest factor: {dyn[6]:.1f}dB")
    
    # Spectral
    cursor.execute('SELECT * FROM spectral_analysis WHERE analysis_id = ?', (analysis_id,))
    spec = cursor.fetchone()
    if spec:
        print(f"\nSpectral:")
        print(f"  Brightness: {spec[7]:.3f}")
        print(f"  Centroid: {spec[2]:.0f}Hz")
    
    # Frequency balance
    cursor.execute('SELECT band_name, relative_to_mid_db FROM frequency_balance WHERE analysis_id = ?', (analysis_id,))
    bands = cursor.fetchall()
    if bands:
        print(f"\nFrequency Balance (relative to mid):")
        for band, rel_db in bands:
            bar = '+' * int(max(0, rel_db + 5)) + '-' * int(max(0, -rel_db + 5))
            print(f"  {band:<12} {rel_db:+.1f}dB")
    
    # Genre matches
    cursor.execute('SELECT genre, match_score FROM genre_matches WHERE analysis_id = ? ORDER BY match_score DESC LIMIT 5', (analysis_id,))
    matches = cursor.fetchall()
    if matches:
        print(f"\nGenre Matches:")
        for genre, score in matches:
            bar = '█' * int(score * 20)
            print(f"  {genre:<12} {score:.2f} {bar}")
    
    # Stereo
    cursor.execute('SELECT * FROM stereo_analysis WHERE analysis_id = ?', (analysis_id,))
    stereo = cursor.fetchone()
    if stereo:
        print(f"\nStereo:")
        print(f"  Width: {stereo[2]:.3f}")
        print(f"  Correlation: {stereo[4]:.3f}")
    
    conn.close()

def compare_analyses(id1, id2):
    """Compare two analyses."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get both analyses
    cursor.execute('''
        SELECT a.name, d.rms_swing_ratio, d.dynamic_range_db, t.transient_drift_ms, s.brightness
        FROM audio_analyses a
        LEFT JOIN dynamics_analysis d ON a.id = d.analysis_id
        LEFT JOIN transient_analysis t ON a.id = t.analysis_id
        LEFT JOIN spectral_analysis s ON a.id = s.analysis_id
        WHERE a.id IN (?, ?)
    ''', (id1, id2))
    
    results = cursor.fetchall()
    conn.close()
    
    if len(results) != 2:
        print("Could not find both analyses")
        return
    
    a1, a2 = results
    
    print(f"\n{'Metric':<20} {a1[0][:15]:<18} {a2[0][:15]:<18} {'Diff':<10}")
    print("-" * 70)
    print(f"{'RMS Swing':<20} {a1[1]:.3f}            {a2[1]:.3f}            {a2[1]-a1[1]:+.3f}")
    print(f"{'Dynamic Range':<20} {a1[2]:.1f}dB           {a2[2]:.1f}dB           {a2[2]-a1[2]:+.1f}dB")
    print(f"{'Transient Drift':<20} {a1[3]:.1f}ms           {a2[3]:.1f}ms           {a2[3]-a1[3]:+.1f}ms")
    print(f"{'Brightness':<20} {a1[4]:.3f}            {a2[4]:.3f}            {a2[4]-a1[4]:+.3f}")

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Audio Feel Extractor - Analyze production characteristics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s analyze song.wav --genre hiphop
  %(prog)s scan ~/Music/References --genre pop
  %(prog)s list --genre rock
  %(prog)s detail 5
  %(prog)s compare 3 7
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze audio file')
    analyze_parser.add_argument('file', help='Audio file path')
    analyze_parser.add_argument('--name', help='Analysis name')
    analyze_parser.add_argument('--genre', help='Genre tag')
    analyze_parser.add_argument('--duration', type=int, default=60, help='Max duration to analyze (seconds)')
    analyze_parser.add_argument('--output', help='Output JSON path')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan folder')
    scan_parser.add_argument('folder', help='Folder path')
    scan_parser.add_argument('--genre', help='Genre tag')
    scan_parser.add_argument('--no-recursive', action='store_true')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List analyses')
    list_parser.add_argument('--genre', help='Filter by genre')
    list_parser.add_argument('--limit', type=int, default=50)
    
    # Detail command
    detail_parser = subparsers.add_parser('detail', help='Show analysis detail')
    detail_parser.add_argument('id', type=int, help='Analysis ID')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare two analyses')
    compare_parser.add_argument('id1', type=int, help='First analysis ID')
    compare_parser.add_argument('id2', type=int, help='Second analysis ID')
    
    # Init command
    subparsers.add_parser('init', help='Initialize database')
    
    # Genres command
    subparsers.add_parser('genres', help='List genre fingerprints')
    
    args = parser.parse_args()
    
    if args.command == 'analyze':
        analysis = analyze_audio_feel(args.file, name=args.name, genre=args.genre, duration=args.duration)
        if args.output:
            save_analysis(analysis, args.output)
        else:
            save_analysis(analysis)
        save_to_database(analysis)
    
    elif args.command == 'scan':
        scan_folder(args.folder, genre=args.genre, recursive=not args.no_recursive)
    
    elif args.command == 'list':
        list_analyses(genre=args.genre, limit=args.limit)
    
    elif args.command == 'detail':
        get_analysis_detail(args.id)
    
    elif args.command == 'compare':
        compare_analyses(args.id1, args.id2)
    
    elif args.command == 'init':
        init_database()
    
    elif args.command == 'genres':
        print("\nGenre Fingerprints:")
        print("-" * 50)
        for genre, data in GENRE_FINGERPRINTS.items():
            print(f"\n{genre}:")
            print(f"  {data['description']}")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
