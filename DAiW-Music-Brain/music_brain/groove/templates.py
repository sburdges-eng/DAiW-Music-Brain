"""
Genre Groove Templates - Pre-defined groove patterns by genre.

Each template contains:
- Timing characteristics (swing, push/pull, pocket)
- Velocity patterns (accent structure)
- Common deviations for the genre
"""

from music_brain.groove.extractor import GrooveTemplate


# Genre timing characteristics
# Swing: 0.0=straight, 0.5=moderate swing, 0.67=triplet swing
# Timing deviations: positive=late (laid back), negative=early (pushed)

GENRE_TEMPLATES = {
    "funk": {
        "name": "Funk Pocket",
        "description": "Deep pocket with emphasis on 2 and 4, slight push on 16ths",
        "swing_factor": 0.15,
        "tempo_range": (90, 120),
        # Per-16th-note deviations in ticks (at 480 PPQ)
        "timing_deviations": [
            0, -8, 5, -5,   # Beat 1: slight push on 16th notes
            12, -6, 8, -4,  # Beat 2: laid back snare
            0, -10, 6, -6,  # Beat 3
            15, -5, 10, -3, # Beat 4: laid back snare
        ],
        # Velocity pattern per 16th note (0-127)
        "velocity_curve": [
            110, 60, 85, 55,  # Beat 1: strong downbeat
            95, 55, 75, 50,   # Beat 2: snare accent
            85, 50, 70, 45,   # Beat 3
            100, 60, 80, 55,  # Beat 4: snare accent
        ],
    },
    
    "jazz": {
        "name": "Jazz Swing",
        "description": "Classic triplet swing feel with brush-like dynamics",
        "swing_factor": 0.67,
        "tempo_range": (100, 200),
        "timing_deviations": [
            0, 20, 0, 25,     # Heavy swing on off-beats
            -5, 22, 0, 28,
            0, 18, -3, 24,
            -8, 20, 0, 26,
        ],
        "velocity_curve": [
            90, 50, 75, 55,
            85, 55, 70, 60,
            80, 50, 72, 58,
            88, 52, 78, 62,
        ],
    },
    
    "rock": {
        "name": "Rock Drive",
        "description": "Straight feel with strong backbeat, slight push",
        "swing_factor": 0.0,
        "tempo_range": (100, 140),
        "timing_deviations": [
            0, -5, 0, -8,     # Slight push throughout
            -3, -6, -2, -7,
            0, -4, 0, -6,
            -2, -5, -3, -8,
        ],
        "velocity_curve": [
            115, 70, 90, 65,  # Strong kick
            120, 80, 95, 70,  # Heavy snare
            100, 65, 85, 60,
            118, 75, 92, 68,  # Heavy snare
        ],
    },
    
    "hiphop": {
        "name": "Hip-Hop Pocket",
        "description": "Deep laid-back pocket with heavy ghost notes",
        "swing_factor": 0.25,
        "tempo_range": (75, 100),
        "timing_deviations": [
            0, 15, 8, 18,     # Very laid back
            20, 12, 15, 20,
            5, 18, 10, 22,
            25, 15, 18, 25,
        ],
        "velocity_curve": [
            120, 35, 45, 30,  # Strong kick, lots of ghosts
            60, 30, 40, 35,
            100, 38, 48, 32,
            55, 32, 42, 38,
        ],
    },
    
    "edm": {
        "name": "EDM Quantized",
        "description": "Machine-tight with subtle humanization",
        "swing_factor": 0.0,
        "tempo_range": (120, 150),
        "timing_deviations": [
            0, 0, 0, 0,       # Tight to grid
            1, -1, 1, -1,     # Micro variations
            0, 0, 0, 0,
            -1, 1, -1, 1,
        ],
        "velocity_curve": [
            127, 95, 110, 90,
            125, 92, 108, 88,
            127, 93, 112, 91,
            124, 94, 106, 89,
        ],
    },
    
    "latin": {
        "name": "Latin Clave",
        "description": "Syncopated feel based on 3-2 clave",
        "swing_factor": 0.1,
        "tempo_range": (90, 130),
        "timing_deviations": [
            0, 5, -5, 8,      # Clave-based
            -8, 6, 0, 10,
            5, -5, 8, 5,
            -6, 8, -3, 12,
        ],
        "velocity_curve": [
            100, 70, 95, 65,
            85, 75, 80, 70,
            90, 68, 98, 72,
            88, 73, 85, 68,
        ],
    },
    
    "blues": {
        "name": "Blues Shuffle",
        "description": "12/8 shuffle feel with expressive dynamics",
        "swing_factor": 0.6,
        "tempo_range": (70, 120),
        "timing_deviations": [
            0, 18, 0, 20,     # Shuffle swing
            -5, 22, 0, 25,
            0, 16, -3, 18,
            -8, 24, 0, 22,
        ],
        "velocity_curve": [
            105, 55, 85, 60,
            95, 60, 80, 55,
            90, 52, 82, 58,
            98, 58, 88, 62,
        ],
    },
    
    "bedroom_lofi": {
        "name": "Lo-Fi Bedroom",
        "description": "Intentionally imperfect, organic feel",
        "swing_factor": 0.35,
        "tempo_range": (70, 95),
        "timing_deviations": [
            5, 20, -8, 25,    # Deliberately inconsistent
            -12, 30, 8, 22,
            15, -5, 28, 10,
            -10, 35, -5, 28,
        ],
        "velocity_curve": [
            95, 45, 70, 40,
            50, 42, 55, 38,
            80, 48, 65, 42,
            52, 40, 58, 35,
        ],
    },
}


def get_genre_template(genre: str) -> GrooveTemplate:
    """
    Get a pre-defined groove template for a genre.
    
    Args:
        genre: Genre name (funk, jazz, rock, hiphop, edm, latin, blues, bedroom_lofi)
    
    Returns:
        GrooveTemplate with genre characteristics
    """
    genre_lower = genre.lower().replace("-", "_").replace(" ", "_")
    
    if genre_lower not in GENRE_TEMPLATES:
        available = ", ".join(GENRE_TEMPLATES.keys())
        raise ValueError(f"Unknown genre: {genre}. Available: {available}")
    
    data = GENRE_TEMPLATES[genre_lower]
    
    return GrooveTemplate(
        name=data["name"],
        source_file=f"preset:{genre_lower}",
        ppq=480,
        tempo_bpm=sum(data["tempo_range"]) / 2,  # Middle of range
        swing_factor=data["swing_factor"],
        timing_deviations=data["timing_deviations"],
        velocity_curve=data["velocity_curve"],
        timing_stats={
            "mean_deviation_ms": sum(abs(d) for d in data["timing_deviations"]) / len(data["timing_deviations"]) * 0.5,
            "description": data["description"],
        },
        velocity_stats={
            "min": min(data["velocity_curve"]),
            "max": max(data["velocity_curve"]),
            "mean": sum(data["velocity_curve"]) / len(data["velocity_curve"]),
        },
    )


def list_genres() -> list:
    """Return list of available genre templates."""
    return list(GENRE_TEMPLATES.keys())


def get_genre_info(genre: str) -> dict:
    """Get info about a genre template without creating full template."""
    genre_lower = genre.lower().replace("-", "_").replace(" ", "_")
    if genre_lower not in GENRE_TEMPLATES:
        return None
    return GENRE_TEMPLATES[genre_lower]
