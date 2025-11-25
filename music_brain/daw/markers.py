"""
DAW Marker Automation - Export structure markers to MIDI.

Creates a MIDI file with marker meta events that DAWs like
Logic Pro, Ableton, and Reaper can import as timeline markers.

This shows the emotional map in the DAW session:
"Intro - The Wound", "Verse - The Resistance", "Chorus - The Transformation"

Philosophy: The structure should reflect the emotional journey,
not arbitrary form conventions.
"""

from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    mido = None
    MIDO_AVAILABLE = False


# =================================================================
# DATA CLASSES
# =================================================================

@dataclass
class MarkerEvent:
    """A single marker to place on the timeline."""
    bar: int              # 1-indexed bar number
    text: str             # Marker label
    color: Optional[str] = None  # Optional color hint (DAW-specific)


@dataclass
class EmotionalSection:
    """
    A section with emotional context.

    Connects the standard musical sections to the three-phase
    emotional journey of the song.
    """
    start_bar: int
    end_bar: int
    section_type: str     # intro, verse, chorus, bridge, outro
    emotional_label: str  # The Wound, The Resistance, The Transformation
    tension: float = 0.8  # 0-1 tension level


# =================================================================
# PRESET STRUCTURES
# =================================================================

def get_standard_structure(length_bars: int) -> List[MarkerEvent]:
    """
    Generate standard structure markers for a given song length.

    Args:
        length_bars: Total number of bars

    Returns:
        List of MarkerEvent objects
    """
    markers = []

    if length_bars <= 16:
        # Short form: Intro, Main, Outro
        markers = [
            MarkerEvent(bar=1, text="Intro"),
            MarkerEvent(bar=5, text="Main"),
            MarkerEvent(bar=13, text="Outro"),
        ]
    elif length_bars <= 32:
        # Medium form: Intro, Verse, Chorus, Outro
        markers = [
            MarkerEvent(bar=1, text="Intro"),
            MarkerEvent(bar=9, text="Verse"),
            MarkerEvent(bar=17, text="Chorus"),
            MarkerEvent(bar=25, text="Outro"),
        ]
    else:
        # Long form: Full structure
        markers = [
            MarkerEvent(bar=1, text="Intro"),
            MarkerEvent(bar=9, text="Verse 1"),
            MarkerEvent(bar=17, text="Chorus"),
            MarkerEvent(bar=25, text="Verse 2"),
            MarkerEvent(bar=33, text="Chorus"),
            MarkerEvent(bar=41, text="Bridge"),
            MarkerEvent(bar=49, text="Final Chorus"),
            MarkerEvent(bar=57, text="Outro"),
        ]

    return [m for m in markers if m.bar <= length_bars]


def get_emotional_structure(
    length_bars: int,
    mood_profile: str = "neutral",
) -> List[MarkerEvent]:
    """
    Generate emotionally-labeled structure markers.

    Maps the song structure to the therapy phases:
    - The Wound (Phase 0)
    - The Resistance (what holds you back)
    - The Transformation (what you want to become)

    Args:
        length_bars: Total number of bars
        mood_profile: The detected mood (grief, rage, etc.)

    Returns:
        List of emotionally-labeled MarkerEvents
    """
    # Customize labels based on mood
    mood_labels = {
        "grief": ("The Loss", "The Memories", "The Acceptance"),
        "rage": ("The Wound", "The Burning", "The Release"),
        "fear": ("The Threat", "The Running", "The Standing"),
        "nostalgia": ("What Was", "What Changed", "What Remains"),
        "defiance": ("The Challenge", "The Fight", "The Victory"),
        "tenderness": ("The Opening", "The Vulnerability", "The Connection"),
        "dissociation": ("The Numbness", "The Drift", "The Return"),
        "awe": ("The Glimpse", "The Immersion", "The Understanding"),
        "confusion": ("The Chaos", "The Search", "The Clarity"),
        "neutral": ("Beginning", "Development", "Resolution"),
    }

    labels = mood_labels.get(mood_profile, mood_labels["neutral"])

    if length_bars <= 16:
        return [
            MarkerEvent(bar=1, text=f"I: {labels[0]}"),
            MarkerEvent(bar=9, text=f"II: {labels[2]}"),
        ]
    elif length_bars <= 32:
        return [
            MarkerEvent(bar=1, text=f"I: {labels[0]}"),
            MarkerEvent(bar=9, text=f"II: {labels[1]}"),
            MarkerEvent(bar=17, text=f"III: {labels[2]}"),
            MarkerEvent(bar=25, text="Reflection"),
        ]
    else:
        return [
            MarkerEvent(bar=1, text=f"Opening - {labels[0]}"),
            MarkerEvent(bar=17, text=f"Development - {labels[1]}"),
            MarkerEvent(bar=33, text=f"Climax - {labels[2]}"),
            MarkerEvent(bar=49, text="Integration"),
            MarkerEvent(bar=57, text="Closing"),
        ]


# =================================================================
# MIDI EXPORT
# =================================================================

def export_markers_midi(
    markers: List[MarkerEvent],
    ppq: int,
    beats_per_bar: int,
    tempo_bpm: int,
    output_path: str,
) -> str:
    """
    Create a MIDI file containing only marker meta events at given bars.

    DAWs like Logic can import these as timeline markers, showing
    the emotional structure in the session.

    Args:
        markers: List of MarkerEvent objects
        ppq: Pulses per quarter note
        beats_per_bar: Number of beats per bar
        tempo_bpm: Tempo in BPM
        output_path: Path for output MIDI file

    Returns:
        Path to the created file
    """
    if not MIDO_AVAILABLE:
        print("[MARKERS]: mido not installed; skipping marker export.")
        return output_path

    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # Set tempo in microseconds per beat
    tempo = mido.bpm2tempo(tempo_bpm)
    track.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))

    # Sort markers by bar
    sorted_markers = sorted(markers, key=lambda m: m.bar)

    last_tick = 0
    bar_ticks = beats_per_bar * ppq

    for marker in sorted_markers:
        # Convert bar to tick (bars are 1-indexed)
        target_tick = (marker.bar - 1) * bar_ticks
        delta = max(0, target_tick - last_tick)

        track.append(
            mido.MetaMessage("marker", text=marker.text, time=delta)
        )
        last_tick = target_tick

    # End of track
    track.append(mido.MetaMessage("end_of_track", time=0))

    mid.ticks_per_beat = ppq
    mid.save(output_path)

    return output_path


def export_sections_midi(
    sections: List[EmotionalSection],
    ppq: int,
    beats_per_bar: int,
    tempo_bpm: int,
    output_path: str,
) -> str:
    """
    Export sections as markers with start and end points.

    Args:
        sections: List of EmotionalSection objects
        ppq: Pulses per quarter note
        beats_per_bar: Beats per bar
        tempo_bpm: Tempo
        output_path: Output file path

    Returns:
        Path to created file
    """
    markers = []

    for section in sections:
        # Create marker at section start
        label = f"{section.section_type.upper()}: {section.emotional_label}"
        markers.append(MarkerEvent(bar=section.start_bar, text=label))

        # Optionally mark the end
        if section.end_bar > section.start_bar:
            markers.append(MarkerEvent(
                bar=section.end_bar,
                text=f"[End {section.section_type}]"
            ))

    return export_markers_midi(
        markers=markers,
        ppq=ppq,
        beats_per_bar=beats_per_bar,
        tempo_bpm=tempo_bpm,
        output_path=output_path,
    )


def merge_markers_with_midi(
    markers: List[MarkerEvent],
    midi_path: str,
    output_path: str,
) -> str:
    """
    Add markers to an existing MIDI file.

    Args:
        markers: Markers to add
        midi_path: Path to existing MIDI file
        output_path: Path for output file

    Returns:
        Path to the merged file
    """
    if not MIDO_AVAILABLE:
        print("[MARKERS]: mido not installed")
        return midi_path

    path = Path(midi_path)
    if not path.exists():
        print(f"[MARKERS]: MIDI file not found: {midi_path}")
        return midi_path

    mid = mido.MidiFile(str(path))
    ppq = mid.ticks_per_beat

    # Find or create a tempo/marker track
    if mid.tracks:
        meta_track = mid.tracks[0]
    else:
        meta_track = mido.MidiTrack()
        mid.tracks.insert(0, meta_track)

    # Get beats per bar from time signature, default to 4
    beats_per_bar = 4
    for msg in meta_track:
        if msg.type == "time_signature":
            beats_per_bar = msg.numerator
            break

    bar_ticks = beats_per_bar * ppq

    # Sort existing events by absolute time
    events = []
    current_time = 0
    for msg in meta_track:
        current_time += msg.time
        events.append((current_time, msg))

    # Add marker events
    for marker in markers:
        target_tick = (marker.bar - 1) * bar_ticks
        msg = mido.MetaMessage("marker", text=marker.text, time=0)
        events.append((target_tick, msg))

    # Sort by time and rebuild track
    events.sort(key=lambda x: x[0])

    new_track = mido.MidiTrack()
    last_time = 0
    for abs_time, msg in events:
        delta = abs_time - last_time
        new_track.append(msg.copy(time=delta))
        last_time = abs_time

    mid.tracks[0] = new_track
    mid.save(output_path)

    return output_path
