"""
Groove extractor - minimal stub.

The full extractor is not needed in this phase. This provides
the GrooveTemplate dataclass for templates.py compatibility.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple


@dataclass
class GrooveTemplate:
    """Minimal groove template for genre templates compatibility."""
    name: str = "Untitled Groove"
    source_file: str = ""
    ppq: int = 480
    tempo_bpm: float = 120.0
    time_signature: Tuple[int, int] = (4, 4)
    timing_deviations: List[float] = field(default_factory=list)
    swing_factor: float = 0.0
    velocity_curve: List[int] = field(default_factory=list)
    velocity_stats: Dict = field(default_factory=dict)
    timing_stats: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Serialize to dictionary for JSON export."""
        return {
            "name": self.name,
            "source_file": self.source_file,
            "ppq": self.ppq,
            "tempo_bpm": self.tempo_bpm,
            "time_signature": list(self.time_signature),
            "timing_deviations": self.timing_deviations,
            "swing_factor": self.swing_factor,
            "velocity_curve": self.velocity_curve,
            "velocity_stats": self.velocity_stats,
            "timing_stats": self.timing_stats,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "GrooveTemplate":
        """Deserialize from dictionary."""
        return cls(
            name=data.get("name", "Untitled"),
            source_file=data.get("source_file", ""),
            ppq=data.get("ppq", 480),
            tempo_bpm=data.get("tempo_bpm", 120.0),
            time_signature=tuple(data.get("time_signature", [4, 4])),
            timing_deviations=data.get("timing_deviations", []),
            swing_factor=data.get("swing_factor", 0.0),
            velocity_curve=data.get("velocity_curve", []),
            velocity_stats=data.get("velocity_stats", {}),
            timing_stats=data.get("timing_stats", {}),
        )
