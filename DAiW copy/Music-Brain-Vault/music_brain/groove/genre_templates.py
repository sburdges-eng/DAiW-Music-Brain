"""
Genre Templates - Pre-built groove templates with documented semantics.

SEMANTICS:
- ppq: Pulses per quarter note (standard: 480)
- grid: Subdivisions per bar (16 = 16th notes)
- swing_ratio: Timing ratio for off-beat 8ths
    - 0.50 = straight (equal spacing)
    - 0.58 = subtle swing
    - 0.62 = light swing
    - 0.66 = triplet feel
    - 0.72 = heavy swing
    Range: 0.50 to 0.75 (beyond is unplayable)
    
- timing_density: Likelihood of note on each 16th (0.0-1.0)
    - 1.0 = always a note
    - 0.0 = never a note
    - Used for probability-based pattern generation
    
- timing_offset: Push/pull from grid in ticks (at 480 PPQ)
    - Positive = behind beat (laid back)
    - Negative = ahead of beat (pushing)
    - Range typically -20 to +20 ticks
    
- velocity_curve: Per-position velocity (0-127)
    - Indexed by 16th note position in bar
    
- instrument_pocket: Per-instrument timing offsets
    - Defines the "pocket" relationship between instruments
"""

from typing import Dict, Any, Tuple
from ..utils.ppq import STANDARD_PPQ


# Instrument pocket offsets (ticks at 480 PPQ)
# Positive = behind, Negative = ahead
POCKET_OFFSETS = {
    "hiphop": {
        "kick": 0,
        "snare": 8,      # Slightly behind
        "hihat": -5,     # Slightly ahead
        "bass": 5,       # With the kick, slightly back
    },
    "funk": {
        "kick": 0,
        "snare": -3,     # On top / slightly ahead (tight)
        "hihat": -8,     # Pushing
        "bass": 2,
    },
    "jazz": {
        "kick": 5,       # Relaxed
        "snare": 10,     # Behind (laid back)
        "hihat": 0,      # Ride on grid
        "ride": 0,
        "bass": 8,       # Walking bass behind
    },
    "rock": {
        "kick": 0,       # On grid
        "snare": 0,      # On grid (tight)
        "hihat": 0,
        "bass": 0,
    },
    "edm": {
        "kick": 0,       # Perfectly quantized
        "snare": 0,
        "hihat": 0,
        "bass": 0,
    },
    "reggae": {
        "kick": 0,
        "snare": 15,     # Way behind (the skank)
        "hihat": 0,
        "bass": 10,      # Behind with snare
    },
    "gospel": {
        "kick": 0,
        "snare": 12,     # Behind (churchy feel)
        "hihat": -5,
        "bass": 8,
    },
    "rnb": {
        "kick": 0,
        "snare": 10,
        "hihat": -3,
        "bass": 6,
    },
    "latin": {
        "kick": 0,
        "snare": 0,      # Tight
        "hihat": -5,
        "conga": 3,
        "bass": 0,
    },
    "country": {
        "kick": 0,
        "snare": 5,
        "hihat": 0,
        "bass": 3,
    },
    "metal": {
        "kick": 0,       # Tight
        "snare": 0,
        "hihat": 0,
        "bass": 0,
    },
    "soul": {
        "kick": 0,
        "snare": 12,
        "hihat": -5,
        "bass": 8,
    },
    "afrobeat": {
        "kick": 0,
        "snare": 5,
        "hihat": -8,     # Driving hats
        "shaker": -10,
        "bass": 3,
    },
}


GENRE_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "hiphop": {
        "ppq": STANDARD_PPQ,
        "grid": 16,
        "swing_ratio": 0.58,  # Light swing
        
        # 16th note timing density (probability of note)
        # Pattern: kick-heavy on 1, snare on 3, hats throughout
        "timing_density": [
            0.95, 0.30, 0.40, 0.35,  # Beat 1
            0.50, 0.35, 0.45, 0.40,  # Beat 2
            0.90, 0.35, 0.50, 0.40,  # Beat 3 (snare)
            0.50, 0.40, 0.45, 0.35,  # Beat 4
        ],
        
        # Timing offsets from grid (ticks at 480 PPQ)
        "timing_offset": [
            0, -3, 5, -2,
            0, -2, 6, -3,
            0, -3, 5, -2,
            0, -2, 4, -3,
        ],
        
        # Velocity curve
        "velocity_curve": [
            100, 65, 75, 60,
            85, 70, 80, 65,
            105, 70, 85, 65,
            85, 68, 78, 62,
        ],
        
        # Per-instrument pocket
        "pocket": POCKET_OFFSETS["hiphop"],
        
        # Characteristics
        "ghost_density": 0.15,  # 15% ghost notes
        "accent_strength": 1.2,  # 20% louder accents
    },
    
    "funk": {
        "ppq": STANDARD_PPQ,
        "grid": 16,
        "swing_ratio": 0.52,  # Nearly straight but with micro-timing
        
        "timing_density": [
            0.90, 0.50, 0.60, 0.55,  # Beat 1
            0.85, 0.55, 0.65, 0.60,  # Beat 2
            0.90, 0.55, 0.70, 0.55,  # Beat 3
            0.85, 0.60, 0.65, 0.55,  # Beat 4
        ],
        
        "timing_offset": [
            0, -5, -3, -5,   # Pushing
            0, -4, -2, -5,
            0, -5, -3, -4,
            0, -4, -2, -5,
        ],
        
        "velocity_curve": [
            110, 75, 95, 70,
            105, 78, 98, 72,
            112, 80, 100, 75,
            105, 78, 95, 70,
        ],
        
        "pocket": POCKET_OFFSETS["funk"],
        "ghost_density": 0.25,  # Lots of ghost notes
        "accent_strength": 1.3,
    },
    
    "jazz": {
        "ppq": STANDARD_PPQ,
        "grid": 16,  # But swing makes it feel like triplets
        "swing_ratio": 0.66,  # Triplet feel
        
        "timing_density": [
            0.80, 0.20, 0.70, 0.15,  # Ride pattern
            0.75, 0.20, 0.70, 0.15,
            0.80, 0.25, 0.75, 0.20,
            0.75, 0.20, 0.70, 0.15,
        ],
        
        "timing_offset": [
            5, 0, 8, 0,    # Laid back
            6, 0, 10, 0,
            5, 0, 8, 0,
            6, 0, 9, 0,
        ],
        
        "velocity_curve": [
            85, 55, 75, 50,
            82, 55, 75, 52,
            88, 58, 78, 55,
            82, 55, 75, 50,
        ],
        
        "pocket": POCKET_OFFSETS["jazz"],
        "ghost_density": 0.20,
        "accent_strength": 1.15,
    },
    
    "rock": {
        "ppq": STANDARD_PPQ,
        "grid": 16,
        "swing_ratio": 0.50,  # Straight
        
        "timing_density": [
            0.95, 0.30, 0.45, 0.30,
            0.90, 0.30, 0.45, 0.30,
            0.95, 0.30, 0.45, 0.30,
            0.90, 0.30, 0.45, 0.30,
        ],
        
        "timing_offset": [
            0, 0, 0, 0,  # On grid
            0, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
        ],
        
        "velocity_curve": [
            115, 70, 100, 68,
            110, 72, 102, 70,
            118, 75, 105, 72,
            110, 72, 100, 68,
        ],
        
        "pocket": POCKET_OFFSETS["rock"],
        "ghost_density": 0.05,
        "accent_strength": 1.25,
    },
    
    "edm": {
        "ppq": STANDARD_PPQ,
        "grid": 16,
        "swing_ratio": 0.50,  # Perfectly straight
        
        "timing_density": [
            1.00, 0.50, 0.80, 0.50,  # Four on floor
            1.00, 0.50, 0.80, 0.50,
            1.00, 0.50, 0.80, 0.50,
            1.00, 0.50, 0.80, 0.50,
        ],
        
        "timing_offset": [
            0, 0, 0, 0,  # Perfect grid
            0, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
        ],
        
        "velocity_curve": [
            120, 85, 110, 82,
            120, 85, 110, 82,
            122, 88, 112, 85,
            120, 85, 110, 82,
        ],
        
        "pocket": POCKET_OFFSETS["edm"],
        "ghost_density": 0.0,
        "accent_strength": 1.1,
    },
    
    "reggae": {
        "ppq": STANDARD_PPQ,
        "grid": 16,
        "swing_ratio": 0.54,  # Slight shuffle
        
        "timing_density": [
            0.90, 0.20, 0.30, 0.80,  # Off-beat emphasis
            0.30, 0.20, 0.30, 0.85,
            0.85, 0.20, 0.30, 0.80,
            0.30, 0.20, 0.30, 0.85,
        ],
        
        "timing_offset": [
            0, 0, 0, 15,   # Off-beats way behind
            0, 0, 0, 18,
            0, 0, 0, 15,
            0, 0, 0, 18,
        ],
        
        "velocity_curve": [
            95, 60, 65, 90,
            70, 58, 65, 92,
            95, 62, 68, 90,
            70, 58, 65, 92,
        ],
        
        "pocket": POCKET_OFFSETS["reggae"],
        "ghost_density": 0.10,
        "accent_strength": 1.1,
    },
    
    "gospel": {
        "ppq": STANDARD_PPQ,
        "grid": 16,
        "swing_ratio": 0.62,  # Medium swing
        
        "timing_density": [
            0.90, 0.35, 0.55, 0.40,
            0.70, 0.40, 0.60, 0.45,
            0.95, 0.40, 0.65, 0.45,
            0.70, 0.45, 0.60, 0.40,
        ],
        
        "timing_offset": [
            0, 5, 10, 5,  # Behind the beat
            0, 6, 12, 6,
            0, 5, 10, 5,
            0, 6, 11, 5,
        ],
        
        "velocity_curve": [
            105, 70, 85, 68,
            90, 72, 88, 70,
            108, 75, 90, 72,
            90, 72, 85, 68,
        ],
        
        "pocket": POCKET_OFFSETS["gospel"],
        "ghost_density": 0.18,
        "accent_strength": 1.25,
    },
    
    "rnb": {
        "ppq": STANDARD_PPQ,
        "grid": 16,
        "swing_ratio": 0.58,
        
        "timing_density": [
            0.92, 0.35, 0.50, 0.38,
            0.60, 0.40, 0.55, 0.42,
            0.95, 0.38, 0.55, 0.40,
            0.60, 0.42, 0.52, 0.38,
        ],
        
        "timing_offset": [
            0, 3, 8, 3,
            0, 4, 10, 4,
            0, 3, 8, 3,
            0, 4, 9, 3,
        ],
        
        "velocity_curve": [
            100, 68, 82, 65,
            88, 70, 85, 68,
            102, 72, 88, 70,
            88, 70, 82, 65,
        ],
        
        "pocket": POCKET_OFFSETS["rnb"],
        "ghost_density": 0.20,
        "accent_strength": 1.15,
    },
    
    "latin": {
        "ppq": STANDARD_PPQ,
        "grid": 16,
        "swing_ratio": 0.50,  # Straight but syncopated
        
        "timing_density": [
            0.85, 0.45, 0.55, 0.75,  # Tresillo pattern
            0.50, 0.45, 0.80, 0.50,
            0.85, 0.45, 0.55, 0.75,
            0.50, 0.45, 0.80, 0.50,
        ],
        
        "timing_offset": [
            0, -3, -2, 0,  # Tight
            0, -3, 0, -2,
            0, -3, -2, 0,
            0, -3, 0, -2,
        ],
        
        "velocity_curve": [
            105, 75, 85, 95,
            80, 72, 100, 78,
            105, 75, 85, 95,
            80, 72, 100, 78,
        ],
        
        "pocket": POCKET_OFFSETS["latin"],
        "ghost_density": 0.12,
        "accent_strength": 1.2,
    },
    
    "country": {
        "ppq": STANDARD_PPQ,
        "grid": 16,
        "swing_ratio": 0.54,  # Slight shuffle
        
        "timing_density": [
            0.90, 0.25, 0.40, 0.30,
            0.85, 0.25, 0.45, 0.30,
            0.90, 0.25, 0.40, 0.30,
            0.85, 0.28, 0.45, 0.30,
        ],
        
        "timing_offset": [
            0, 2, 5, 2,
            0, 3, 6, 3,
            0, 2, 5, 2,
            0, 3, 5, 2,
        ],
        
        "velocity_curve": [
            108, 68, 95, 65,
            100, 70, 98, 68,
            110, 72, 100, 70,
            100, 68, 95, 65,
        ],
        
        "pocket": POCKET_OFFSETS["country"],
        "ghost_density": 0.08,
        "accent_strength": 1.2,
    },
    
    "metal": {
        "ppq": STANDARD_PPQ,
        "grid": 16,
        "swing_ratio": 0.50,  # Dead straight
        
        "timing_density": [
            1.00, 0.70, 0.80, 0.70,  # Constant 16ths
            1.00, 0.70, 0.80, 0.70,
            1.00, 0.70, 0.80, 0.70,
            1.00, 0.70, 0.80, 0.70,
        ],
        
        "timing_offset": [
            0, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
        ],
        
        "velocity_curve": [
            120, 95, 115, 92,
            118, 95, 115, 92,
            122, 98, 118, 95,
            118, 95, 115, 92,
        ],
        
        "pocket": POCKET_OFFSETS["metal"],
        "ghost_density": 0.02,
        "accent_strength": 1.15,
    },
    
    "soul": {
        "ppq": STANDARD_PPQ,
        "grid": 16,
        "swing_ratio": 0.60,
        
        "timing_density": [
            0.88, 0.35, 0.52, 0.40,
            0.65, 0.40, 0.58, 0.45,
            0.92, 0.40, 0.60, 0.42,
            0.65, 0.42, 0.55, 0.38,
        ],
        
        "timing_offset": [
            0, 5, 10, 5,
            0, 6, 12, 6,
            0, 5, 10, 5,
            0, 6, 11, 5,
        ],
        
        "velocity_curve": [
            102, 68, 85, 65,
            88, 70, 88, 68,
            105, 72, 90, 70,
            88, 70, 85, 65,
        ],
        
        "pocket": POCKET_OFFSETS["soul"],
        "ghost_density": 0.22,
        "accent_strength": 1.2,
    },
    
    "afrobeat": {
        "ppq": STANDARD_PPQ,
        "grid": 16,
        "swing_ratio": 0.52,
        
        "timing_density": [
            0.85, 0.55, 0.65, 0.60,  # Polyrhythmic density
            0.70, 0.55, 0.70, 0.60,
            0.85, 0.58, 0.68, 0.62,
            0.70, 0.55, 0.68, 0.58,
        ],
        
        "timing_offset": [
            0, -5, -3, -5,
            0, -4, -2, -5,
            0, -5, -3, -4,
            0, -4, -2, -5,
        ],
        
        "velocity_curve": [
            105, 78, 92, 75,
            95, 80, 95, 78,
            108, 82, 95, 80,
            95, 78, 92, 75,
        ],
        
        "pocket": POCKET_OFFSETS["afrobeat"],
        "ghost_density": 0.18,
        "accent_strength": 1.15,
    },
}


def get_genre_template(genre: str) -> Dict[str, Any]:
    """
    Get template for genre with validation.
    
    Args:
        genre: Genre name (case-insensitive)
    
    Returns:
        Template dict
    
    Raises:
        KeyError: If genre not found
    """
    genre_lower = genre.lower()
    if genre_lower not in GENRE_TEMPLATES:
        available = ", ".join(sorted(GENRE_TEMPLATES.keys()))
        raise KeyError(f"Unknown genre '{genre}'. Available: {available}")
    return GENRE_TEMPLATES[genre_lower]


def list_genres() -> list:
    """Return list of available genres."""
    return sorted(GENRE_TEMPLATES.keys())


def validate_template(template: Dict[str, Any]) -> list:
    """
    Validate a template and return list of issues.
    
    Returns:
        List of issue strings (empty if valid)
    """
    issues = []
    
    # Required fields
    required = ["ppq", "grid", "swing_ratio"]
    for field in required:
        if field not in template:
            issues.append(f"Missing required field: {field}")
    
    # Swing ratio bounds
    if "swing_ratio" in template:
        sr = template["swing_ratio"]
        if not (0.50 <= sr <= 0.75):
            issues.append(f"swing_ratio {sr} out of range [0.50, 0.75]")
    
    # Array lengths
    grid = template.get("grid", 16)
    for field in ["timing_density", "timing_offset", "velocity_curve"]:
        if field in template:
            if len(template[field]) != grid:
                issues.append(f"{field} length {len(template[field])} != grid {grid}")
    
    # Timing density bounds
    if "timing_density" in template:
        for i, v in enumerate(template["timing_density"]):
            if not (0.0 <= v <= 1.0):
                issues.append(f"timing_density[{i}] = {v} out of range [0, 1]")
    
    # Velocity bounds
    if "velocity_curve" in template:
        for i, v in enumerate(template["velocity_curve"]):
            if not (0 <= v <= 127):
                issues.append(f"velocity_curve[{i}] = {v} out of range [0, 127]")
    
    return issues


# === Accessor Functions (unified from pocket_rules.py) ===

def get_pocket(genre: str) -> Dict[str, int]:
    """Get pocket timing offsets for a genre."""
    return POCKET_OFFSETS.get(genre.lower(), POCKET_OFFSETS.get('rock', {}))


def get_push_pull(genre: str, instrument: str) -> int:
    """Get push/pull offset for instrument in genre (ticks at 480 PPQ)."""
    pocket = get_pocket(genre)
    return pocket.get(instrument, 0)


def get_swing(genre: str) -> float:
    """Get swing ratio for genre (0.5 = straight, 0.66 = triplet)."""
    template = GENRE_TEMPLATES.get(genre.lower())
    if template:
        return template.get('swing_ratio', 0.50)
    return 0.50


def get_velocity_range(genre: str, instrument: str) -> Tuple[int, int]:
    """Get typical velocity range for instrument in genre."""
    # Default ranges by instrument
    defaults = {
        'kick': (90, 115),
        'snare': (85, 110),
        'hihat': (60, 95),
        'bass': (80, 105),
    }
    return defaults.get(instrument, (80, 110))


def scale_pocket_to_ppq(pocket: Dict[str, int], target_ppq: int) -> Dict[str, int]:
    """Scale all tick values in pocket to target PPQ."""
    if target_ppq == STANDARD_PPQ:
        return pocket.copy()
    
    scale = target_ppq / STANDARD_PPQ
    return {k: int(v * scale) for k, v in pocket.items()}
