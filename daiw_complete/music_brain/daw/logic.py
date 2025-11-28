"""
Logic Pro Project Abstraction
=============================

Minimal MIDI project wrapper used by DAiW to export structured MIDI
that imports cleanly into Logic / any DAW.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import mido

# Channel recommendations (0-based)
LOGIC_CHANNELS = {
    "keys": 0,
    "bass": 1,
    "pads": 2,
    "drums": 9,
}


@dataclass
class LogicProject:
    name: str
    tempo_bpm: int = 120
    time_signature: Tuple[int, int] = (4, 4)
    ppq: int = 480
    tracks: List[Dict] = field(default_factory=list)
    key: str = "C Major"

    def add_track(
        self,
        name: str,
        channel: int,
        instrument: Optional[str],
        notes: List[Dict],
    ) -> None:
        """
        Adds a track with note events (absolute tick times).

        notes format:
            {
                'pitch': int,
                'velocity': int,
                'start_tick': int,
                'duration_ticks': int,
                # optional: 'channel' override, 'bar_index', 'complexity', ...
            }
        """
        self.tracks.append(
            {
                "name": name,
                "channel": channel,
                "instrument": instrument,
                "notes": notes,
            }
        )

    def export_midi(self, output_path: str) -> str:
        """
        Writes a type-1 MIDI file with tempo / time signature meta track
        and one track per logical instrument.
        """
        mid = mido.MidiFile(ticks_per_beat=self.ppq)

        # Tempo / Time signature track
        meta_track = mido.MidiTrack()
        mid.tracks.append(meta_track)

        tempo_us = mido.bpm2tempo(self.tempo_bpm)
        meta_track.append(mido.MetaMessage("set_tempo", tempo=tempo_us, time=0))
        meta_track.append(
            mido.MetaMessage(
                "time_signature",
                numerator=self.time_signature[0],
                denominator=self.time_signature[1],
                time=0,
            )
        )
        
        # Key signature - mido expects lowercase mode format
        # Parse "C Major" -> "C", "C minor" -> "Cm"
        key_parts = self.key.split()
        if len(key_parts) >= 2:
            root = key_parts[0]
            mode = key_parts[1].lower()
            if mode in ("minor", "aeolian", "dorian", "phrygian", "locrian"):
                key_str = f"{root}m"
            else:
                key_str = root
        else:
            key_str = "C"
        
        try:
            meta_track.append(
                mido.MetaMessage("key_signature", key=key_str, time=0)
            )
        except Exception:
            # If key signature fails, skip it - not critical
            pass

        # Instrument tracks
        for track_data in self.tracks:
            base_channel = int(track_data["channel"])
            track = mido.MidiTrack()
            mid.tracks.append(track)
            track.append(
                mido.MetaMessage(
                    "track_name",
                    name=track_data["name"],
                    time=0,
                )
            )

            events: List[Dict] = []
            for note in track_data["notes"]:
                pitch = int(note["pitch"])
                vel = max(0, min(127, int(note["velocity"])))
                start = int(note["start_tick"])
                end = start + int(note["duration_ticks"])
                ch = int(note.get("channel", base_channel))

                events.append(
                    {
                        "type": "note_on",
                        "note": pitch,
                        "velocity": vel,
                        "time": start,
                        "channel": ch,
                    }
                )
                events.append(
                    {
                        "type": "note_off",
                        "note": pitch,
                        "velocity": 0,
                        "time": end,
                        "channel": ch,
                    }
                )

            events.sort(key=lambda e: e["time"])

            last_time = 0
            for event in events:
                delta = max(0, event["time"] - last_time)
                last_time = event["time"]
                track.append(
                    mido.Message(
                        event["type"],
                        note=event["note"],
                        velocity=event["velocity"],
                        time=delta,
                        channel=event["channel"],
                    )
                )

        mid.save(output_path)
        return output_path
