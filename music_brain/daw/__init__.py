"""
DAW Integration - Logic Pro and other DAW integration utilities.

Provides bridges for working with different DAW file formats,
MIDI export/import, DAW-specific features, and timeline markers.
"""

from music_brain.daw.logic import (
    LogicProject,
    export_to_logic,
    import_from_logic,
)
from music_brain.daw.markers import (
    MarkerEvent,
    EmotionalSection,
    export_markers_midi,
    export_sections_midi,
    merge_markers_with_midi,
    get_standard_structure,
    get_emotional_structure,
)

__all__ = [
    # Logic integration
    "LogicProject",
    "export_to_logic",
    "import_from_logic",
    # Markers
    "MarkerEvent",
    "EmotionalSection",
    "export_markers_midi",
    "export_sections_midi",
    "merge_markers_with_midi",
    "get_standard_structure",
    "get_emotional_structure",
]
