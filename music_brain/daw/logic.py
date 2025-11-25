# music_brain/daw/logic.py
"""
Logic Pro Project Abstraction
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import mido

LOGIC_CHANNELS = {
    "keys": 0,
    "bass": 1,
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

    def add_track(self, name: str, channel: int, instrument: Optional[str], notes: List[Dict]):
        """
        Adds a track with notes.

        notes: list of dicts:
            {
                "pitch": int,
                "velocity": int,
                "start_tick": int,
                "duration_ticks": int
            }
        """
        self.tracks.append(
            {
                "name": name,
                "channel": int(channel),
                "instrument": instrument,
                "notes": notes,
            }
        )

    def export_midi(self, output_path: str) -> str:
        mid = mido.MidiFile(ticks_per_beat=self.ppq)

        # Meta track
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
        meta_track.append(mido.MetaMessage("track_name", name=self.name, time=0))

        # Instrument tracks
        for track_data in self.tracks:
            track = mido.MidiTrack()
            mid.tracks.append(track)
            track.append(mido.MetaMessage("track_name", name=track_data["name"], time=0))

            events = []
            for note in track_data["notes"]:
                start = int(note["start_tick"])
                end = int(note["start_tick"] + note["duration_ticks"])
                pitch = int(note["pitch"])
                vel = max(0, min(127, int(note["velocity"])))
                ch = int(track_data["channel"])

                events.append(
                    {
                        "type": "note_on",
                        "time": start,
                        "note": pitch,
                        "velocity": vel,
                        "channel": ch,
                    }
                )
                events.append(
                    {
                        "type": "note_off",
                        "time": end,
                        "note": pitch,
                        "velocity": 0,
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
