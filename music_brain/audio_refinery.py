# music_brain/audio_refinery.py
"""
Audio Refinery - Sample management and AudioVault integration.

Handles:
- Kit and sample discovery from AudioVault
- Sample metadata extraction
- Reference track analysis preparation
- Sample categorization and organization

Philosophy: Audio samples are creative building blocks. The refinery
organizes and prepares them for use in the emotional workflow.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import json
import os

from music_brain.config import get_audio_vault_path


# =================================================================
# DATA CLASSES
# =================================================================

@dataclass
class Sample:
    """Represents a single audio sample."""
    path: Path
    name: str
    category: str = "unknown"
    bpm: Optional[float] = None
    key: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": str(self.path),
            "name": self.name,
            "category": self.category,
            "bpm": self.bpm,
            "key": self.key,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Sample":
        return cls(
            path=Path(data["path"]),
            name=data.get("name", ""),
            category=data.get("category", "unknown"),
            bpm=data.get("bpm"),
            key=data.get("key"),
            tags=data.get("tags", []),
        )


@dataclass
class Kit:
    """Represents a collection of samples for a specific mood/genre."""
    name: str
    samples: List[Sample] = field(default_factory=list)
    mood: Optional[str] = None
    genre: Optional[str] = None
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "samples": [s.to_dict() for s in self.samples],
            "mood": self.mood,
            "genre": self.genre,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Kit":
        return cls(
            name=data.get("name", "Unnamed Kit"),
            samples=[Sample.from_dict(s) for s in data.get("samples", [])],
            mood=data.get("mood"),
            genre=data.get("genre"),
            description=data.get("description", ""),
        )


# =================================================================
# CATEGORY DETECTION
# =================================================================

# Common audio extensions
AUDIO_EXTENSIONS = {".wav", ".mp3", ".aiff", ".flac", ".ogg", ".m4a"}

# Keywords for categorization
CATEGORY_KEYWORDS = {
    "kick": ["kick", "bd", "bassdrum", "bass_drum"],
    "snare": ["snare", "sd", "snr"],
    "hihat": ["hihat", "hh", "hat", "hi-hat"],
    "tom": ["tom", "floor"],
    "cymbal": ["cymbal", "crash", "ride", "china"],
    "perc": ["perc", "percussion", "shaker", "tambourine", "conga", "bongo"],
    "bass": ["bass", "sub", "808"],
    "synth": ["synth", "lead", "pad", "keys", "keyboard"],
    "guitar": ["guitar", "gtr", "acoustic", "electric"],
    "vocal": ["vocal", "vox", "voice", "choir"],
    "fx": ["fx", "sfx", "effect", "riser", "impact", "sweep"],
    "loop": ["loop", "beat", "groove"],
    "one_shot": ["one_shot", "oneshot", "one-shot", "hit"],
}


def detect_category(filename: str) -> str:
    """
    Detect sample category from filename.

    Args:
        filename: Name of the audio file

    Returns:
        Category string
    """
    name_lower = filename.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category

    return "unknown"


def extract_bpm_from_name(filename: str) -> Optional[float]:
    """
    Try to extract BPM from filename patterns like 'beat_120bpm.wav'.

    Args:
        filename: Name of the audio file

    Returns:
        BPM as float or None
    """
    import re

    # Common patterns: 120bpm, 120_bpm, 120-bpm, bpm120, etc.
    patterns = [
        r'(\d{2,3})[\s_-]?bpm',
        r'bpm[\s_-]?(\d{2,3})',
        r'(\d{2,3})[\s_-]?tempo',
    ]

    name_lower = filename.lower()
    for pattern in patterns:
        match = re.search(pattern, name_lower)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass

    return None


def extract_key_from_name(filename: str) -> Optional[str]:
    """
    Try to extract musical key from filename.

    Args:
        filename: Name of the audio file

    Returns:
        Key string (e.g., "Am", "Cmaj") or None
    """
    import re

    # Remove extension
    name = filename.rsplit(".", 1)[0] if "." in filename else filename

    # Pattern for key: C, Dm, F#m, Bbmaj, etc.
    # Must be preceded by underscore, hyphen, space, or start of string
    # Quality suffix is optional but must match specific patterns
    pattern = r'(?:^|[_\-\s])([A-G][#b]?)(m|min|maj|major|minor)?(?:$|[_\-\s\.])'

    match = re.search(pattern, name, re.IGNORECASE)
    if match:
        root = match.group(1)
        # Capitalize root note, preserve sharp/flat
        if len(root) > 1:
            root = root[0].upper() + root[1]
        else:
            root = root.upper()

        quality = match.group(2) or ""

        # Normalize quality
        if quality.lower() in ["m", "min", "minor"]:
            quality = "m"
        elif quality.lower() in ["maj", "major"]:
            quality = ""

        return f"{root}{quality}"

    return None


# =================================================================
# AUDIO VAULT OPERATIONS
# =================================================================

def scan_audio_vault(
    vault_path: Optional[Path] = None,
    recursive: bool = True,
) -> List[Sample]:
    """
    Scan AudioVault directory for audio samples.

    Args:
        vault_path: Path to AudioVault (uses config default if None)
        recursive: Whether to scan subdirectories

    Returns:
        List of Sample objects
    """
    if vault_path is None:
        vault_path = get_audio_vault_path()

    if isinstance(vault_path, str):
        vault_path = Path(vault_path)

    if not vault_path.exists():
        return []

    samples = []

    if recursive:
        files = vault_path.rglob("*")
    else:
        files = vault_path.glob("*")

    for file_path in files:
        if file_path.is_file() and file_path.suffix.lower() in AUDIO_EXTENSIONS:
            sample = Sample(
                path=file_path,
                name=file_path.stem,
                category=detect_category(file_path.name),
                bpm=extract_bpm_from_name(file_path.name),
                key=extract_key_from_name(file_path.name),
                tags=_extract_tags_from_path(file_path, vault_path),
            )
            samples.append(sample)

    return samples


def _extract_tags_from_path(file_path: Path, vault_path: Path) -> List[str]:
    """
    Extract tags from the directory structure.

    E.g., AudioVault/Drums/Kicks/acoustic_kick.wav -> ["drums", "kicks"]
    """
    try:
        relative = file_path.relative_to(vault_path)
        parts = relative.parts[:-1]  # Exclude filename
        return [p.lower().replace("_", " ") for p in parts]
    except ValueError:
        return []


def find_samples_by_category(
    category: str,
    vault_path: Optional[Path] = None,
) -> List[Sample]:
    """
    Find all samples of a specific category.

    Args:
        category: Category to search for
        vault_path: AudioVault path

    Returns:
        Filtered list of samples
    """
    all_samples = scan_audio_vault(vault_path)
    return [s for s in all_samples if s.category == category]


def find_samples_by_tag(
    tag: str,
    vault_path: Optional[Path] = None,
) -> List[Sample]:
    """
    Find samples containing a specific tag.

    Args:
        tag: Tag to search for
        vault_path: AudioVault path

    Returns:
        Filtered list of samples
    """
    tag_lower = tag.lower()
    all_samples = scan_audio_vault(vault_path)
    return [s for s in all_samples if tag_lower in [t.lower() for t in s.tags]]


# =================================================================
# KIT MANAGEMENT
# =================================================================

def load_kit(kit_path: Path) -> Kit:
    """
    Load a kit definition from JSON file.

    Args:
        kit_path: Path to kit JSON file

    Returns:
        Kit object
    """
    with open(kit_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Kit.from_dict(data)


def save_kit(kit: Kit, output_path: Path) -> str:
    """
    Save a kit definition to JSON file.

    Args:
        kit: Kit object to save
        output_path: Path for output file

    Returns:
        Path to saved file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(kit.to_dict(), f, indent=2)

    return str(output_path)


def discover_kits(vault_path: Optional[Path] = None) -> List[Kit]:
    """
    Discover all kit definitions in AudioVault.

    Args:
        vault_path: AudioVault path

    Returns:
        List of Kit objects
    """
    if vault_path is None:
        vault_path = get_audio_vault_path()

    if isinstance(vault_path, str):
        vault_path = Path(vault_path)

    kits_dir = vault_path / "kits"
    if not kits_dir.exists():
        return []

    kits = []
    for kit_file in kits_dir.glob("*.json"):
        try:
            kits.append(load_kit(kit_file))
        except (json.JSONDecodeError, KeyError):
            pass

    return kits


def build_kit_from_samples(
    name: str,
    samples: List[Sample],
    mood: Optional[str] = None,
    genre: Optional[str] = None,
    description: str = "",
) -> Kit:
    """
    Build a kit from a list of samples.

    Args:
        name: Kit name
        samples: List of Sample objects
        mood: Associated mood
        genre: Associated genre
        description: Kit description

    Returns:
        Kit object
    """
    return Kit(
        name=name,
        samples=samples,
        mood=mood,
        genre=genre,
        description=description,
    )


def build_basic_drum_kit(vault_path: Optional[Path] = None) -> Kit:
    """
    Build a basic drum kit by finding one sample of each drum category.

    Args:
        vault_path: AudioVault path

    Returns:
        Kit with basic drum samples
    """
    all_samples = scan_audio_vault(vault_path)

    drum_categories = ["kick", "snare", "hihat", "tom", "cymbal", "perc"]
    kit_samples = []

    for category in drum_categories:
        matching = [s for s in all_samples if s.category == category]
        if matching:
            kit_samples.append(matching[0])

    return Kit(
        name="Basic Drums",
        samples=kit_samples,
        description="Auto-generated basic drum kit",
    )


# =================================================================
# MOOD-BASED KIT SELECTION
# =================================================================

# Map moods to preferred sample characteristics
MOOD_PREFERENCES = {
    "grief": {"categories": ["pad", "synth"], "prefer_minor": True, "bpm_range": (60, 90)},
    "rage": {"categories": ["kick", "perc", "fx"], "prefer_distorted": True, "bpm_range": (120, 160)},
    "nostalgia": {"categories": ["loop", "vocal"], "prefer_vintage": True, "bpm_range": (80, 110)},
    "defiance": {"categories": ["bass", "kick"], "prefer_minor": True, "bpm_range": (100, 140)},
    "hope": {"categories": ["synth", "pad"], "prefer_major": True, "bpm_range": (90, 120)},
    "anxiety": {"categories": ["hihat", "perc", "fx"], "prefer_odd_time": True, "bpm_range": (100, 130)},
    "peace": {"categories": ["pad", "synth"], "prefer_major": True, "bpm_range": (60, 80)},
}


def suggest_samples_for_mood(
    mood: str,
    vault_path: Optional[Path] = None,
    max_samples: int = 10,
) -> List[Sample]:
    """
    Suggest samples appropriate for a given mood.

    Args:
        mood: Emotional mood (grief, rage, nostalgia, etc.)
        vault_path: AudioVault path
        max_samples: Maximum samples to return

    Returns:
        List of suggested samples
    """
    all_samples = scan_audio_vault(vault_path)

    prefs = MOOD_PREFERENCES.get(mood.lower(), {})
    preferred_categories = prefs.get("categories", [])
    bpm_range = prefs.get("bpm_range", (0, 999))

    # Score and sort samples
    scored_samples = []
    for sample in all_samples:
        score = 0

        # Boost for matching category
        if sample.category in preferred_categories:
            score += 10

        # Boost for matching BPM range
        if sample.bpm and bpm_range[0] <= sample.bpm <= bpm_range[1]:
            score += 5

        # Boost for matching key preference
        if prefs.get("prefer_minor") and sample.key and "m" in sample.key:
            score += 3
        elif prefs.get("prefer_major") and sample.key and "m" not in sample.key:
            score += 3

        scored_samples.append((score, sample))

    # Sort by score descending
    scored_samples.sort(key=lambda x: x[0], reverse=True)

    return [s for _, s in scored_samples[:max_samples]]


# =================================================================
# REFERENCE TRACK ANALYSIS
# =================================================================

def prepare_reference_analysis(
    reference_path: Path,
    output_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Prepare a reference track for DNA analysis.

    This creates a workspace with the reference track and
    prepares metadata for analysis by the audio module.

    Args:
        reference_path: Path to reference audio file
        output_dir: Output directory (uses AudioVault/references if None)

    Returns:
        Dict with analysis preparation info
    """
    reference_path = Path(reference_path)

    if output_dir is None:
        output_dir = get_audio_vault_path() / "references"

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Basic metadata
    result = {
        "reference_path": str(reference_path),
        "reference_name": reference_path.stem,
        "output_dir": str(output_dir),
        "status": "prepared",
    }

    # Extract info from filename
    result["detected_bpm"] = extract_bpm_from_name(reference_path.name)
    result["detected_key"] = extract_key_from_name(reference_path.name)

    return result


# =================================================================
# EXPORTS
# =================================================================

__all__ = [
    # Data classes
    "Sample",
    "Kit",
    # Category detection
    "detect_category",
    "extract_bpm_from_name",
    "extract_key_from_name",
    # AudioVault operations
    "scan_audio_vault",
    "find_samples_by_category",
    "find_samples_by_tag",
    # Kit management
    "load_kit",
    "save_kit",
    "discover_kits",
    "build_kit_from_samples",
    "build_basic_drum_kit",
    # Mood-based selection
    "suggest_samples_for_mood",
    "MOOD_PREFERENCES",
    # Reference analysis
    "prepare_reference_analysis",
]
