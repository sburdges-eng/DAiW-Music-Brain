#!/usr/bin/env python3
"""
MIDI Generator for Kelly Song Project
Generates reference MIDI tracks for guitar parts

Requirements: pip3 install mido
"""

import os

try:
    import mido
    from mido import Message, MidiFile, MidiTrack, MetaMessage
except ImportError:
    print("Installing mido...")
    os.system("pip3 install mido")
    import mido
    from mido import Message, MidiFile, MidiTrack, MetaMessage

# Configuration
BPM = 72
TICKS_PER_BEAT = 480
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Note mappings (MIDI note numbers)
NOTES = {
    'C2': 36, 'D2': 38, 'E2': 40, 'F2': 41, 'G2': 43, 'A2': 45, 'B2': 47,
    'C3': 48, 'C#3': 49, 'D3': 50, 'D#3': 51, 'E3': 52, 'F3': 53, 'F#3': 54, 'G3': 55, 'G#3': 56, 'A3': 57, 'A#3': 58, 'B3': 59,
    'C4': 60, 'C#4': 61, 'D4': 62, 'D#4': 63, 'E4': 64, 'F4': 65, 'F#4': 66, 'G4': 67, 'G#4': 68, 'A4': 69, 'A#4': 70, 'B4': 71,
    'C5': 72, 'D5': 74, 'E5': 76, 'F5': 77, 'G5': 79, 'A5': 81, 'B5': 83,
}

# Chord definitions (guitar voicings as MIDI notes, low to high)
CHORDS = {
    'Am':     [NOTES['A2'], NOTES['E3'], NOTES['A3'], NOTES['C4'], NOTES['E4']],
    'Am/G':   [NOTES['G2'], NOTES['E3'], NOTES['A3'], NOTES['C4'], NOTES['E4']],
    'Fmaj7':  [NOTES['F2'], NOTES['A2'], NOTES['C3'], NOTES['E3'], NOTES['A3'], NOTES['C4']],
    'E':      [NOTES['E2'], NOTES['B2'], NOTES['E3'], NOTES['G#3'], NOTES['B3'], NOTES['E4']],
    'Esus4':  [NOTES['E2'], NOTES['B2'], NOTES['E3'], NOTES['A3'], NOTES['B3'], NOTES['E4']],
    'C':      [NOTES['C3'], NOTES['E3'], NOTES['G3'], NOTES['C4'], NOTES['E4']],
    'G':      [NOTES['G2'], NOTES['B2'], NOTES['D3'], NOTES['G3'], NOTES['B3'], NOTES['G4']],
    'Em':     [NOTES['E2'], NOTES['B2'], NOTES['E3'], NOTES['G3'], NOTES['B3'], NOTES['E4']],
    'Dm':     [NOTES['D3'], NOTES['A3'], NOTES['D4'], NOTES['F4']],
    'Bdim':   [NOTES['B2'], NOTES['F3'], NOTES['A3'], NOTES['D4']],
    'C#dim':  [NOTES['C#3'], NOTES['G3'], NOTES['A#3'], NOTES['E4']],
}

def tempo_to_microseconds(bpm):
    """Convert BPM to microseconds per beat"""
    return int(60000000 / bpm)

def bars_to_ticks(bars):
    """Convert bars to MIDI ticks (4/4 time)"""
    return bars * 4 * TICKS_PER_BEAT

def beats_to_ticks(beats):
    """Convert beats to MIDI ticks"""
    return int(beats * TICKS_PER_BEAT)

def add_chord_strum(track, chord_name, duration_beats, velocity=70, strum_delay=15):
    """Add a strummed chord with slight delay between notes"""
    if chord_name not in CHORDS:
        print(f"Warning: Unknown chord {chord_name}")
        return
    
    notes = CHORDS[chord_name]
    duration_ticks = beats_to_ticks(duration_beats)
    
    # Strum down - slight delay between each note
    for i, note in enumerate(notes):
        delay = strum_delay if i > 0 else 0
        track.append(Message('note_on', note=note, velocity=velocity, time=delay))
    
    # Note offs
    for i, note in enumerate(notes):
        if i == 0:
            track.append(Message('note_off', note=note, velocity=0, time=duration_ticks - (strum_delay * (len(notes)-1))))
        else:
            track.append(Message('note_off', note=note, velocity=0, time=0))

def add_arpeggio(track, chord_name, pattern_beats, velocity=60):
    """Add an arpeggiated chord pattern"""
    if chord_name not in CHORDS:
        print(f"Warning: Unknown chord {chord_name}")
        return
    
    notes = CHORDS[chord_name]
    note_duration = beats_to_ticks(pattern_beats / len(notes) / 2)  # Each note gets portion of the beat
    
    # Fingerpicking pattern: bass, then ascending
    # Pattern: T (bass) - i - m - a - m - i for 6/8 feel
    if len(notes) >= 4:
        pattern = [0, 2, 3, 4 if len(notes) > 4 else 3, 3, 2]  # indices into chord notes
    else:
        pattern = [0, 1, 2, 1]
    
    for idx in pattern:
        if idx < len(notes):
            note = notes[idx]
            track.append(Message('note_on', note=note, velocity=velocity, time=0))
            track.append(Message('note_off', note=note, velocity=0, time=note_duration))

def add_rest(track, beats):
    """Add a rest (silence) for specified beats"""
    track.append(Message('note_on', note=60, velocity=0, time=beats_to_ticks(beats)))
    track.append(Message('note_off', note=60, velocity=0, time=0))

def create_full_song_midi():
    """Create the complete song MIDI file"""
    mid = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    track = MidiTrack()
    mid.tracks.append(track)
    
    # Set tempo
    track.append(MetaMessage('set_tempo', tempo=tempo_to_microseconds(BPM)))
    track.append(MetaMessage('time_signature', numerator=4, denominator=4))
    track.append(MetaMessage('key_signature', key='A'))
    
    # Track name
    track.append(MetaMessage('track_name', name='Guitar Reference'))
    
    # INTRO - 8 bars fingerpicked
    # | Am | Am/G | Fmaj7 | E | Am | Am/G | Dm | E |
    track.append(MetaMessage('marker', text='INTRO'))
    intro_chords = ['Am', 'Am/G', 'Fmaj7', 'E', 'Am', 'Am/G', 'Dm', 'E']
    for chord in intro_chords:
        add_arpeggio(track, chord, 4, velocity=55)
        add_arpeggio(track, chord, 4, velocity=50)
    
    # VERSE 1 - 8 bars strummed
    # | Am | C | G | Em | Am | C | Fmaj7 | E |
    track.append(MetaMessage('marker', text='VERSE 1'))
    verse_chords = ['Am', 'C', 'G', 'Em', 'Am', 'C', 'Fmaj7', 'E']
    for chord in verse_chords:
        add_chord_strum(track, chord, 4, velocity=65)
    
    # VERSE 2 - 8 bars strummed (slightly louder)
    track.append(MetaMessage('marker', text='VERSE 2'))
    for chord in verse_chords:
        add_chord_strum(track, chord, 4, velocity=72)
    
    # CHORUS - 8 bars fuller
    # | Fmaj7 | C | Am | G | Dm | Am | Esus4 | E |
    track.append(MetaMessage('marker', text='CHORUS'))
    chorus_chords = ['Fmaj7', 'C', 'Am', 'G', 'Dm', 'Am', 'Esus4', 'E']
    for chord in chorus_chords:
        add_chord_strum(track, chord, 4, velocity=78)
    
    # INSTRUMENTAL BREAK - 4 bars arpeggiated with diminished
    # | Am | Bdim | C | C#dim |
    track.append(MetaMessage('marker', text='INSTRUMENTAL'))
    break_chords = ['Am', 'Bdim', 'C', 'C#dim']
    for chord in break_chords:
        add_arpeggio(track, chord, 4, velocity=60)
        add_arpeggio(track, chord, 4, velocity=55)
    
    # VERSE 3 - 8 bars pulled back
    track.append(MetaMessage('marker', text='VERSE 3'))
    for chord in verse_chords:
        add_chord_strum(track, chord, 4, velocity=58)
    
    # BRIDGE - 4 bars sustained
    # | Dm | Am | Dm | E (let ring) |
    track.append(MetaMessage('marker', text='BRIDGE'))
    bridge_chords = ['Dm', 'Am', 'Dm', 'E']
    for i, chord in enumerate(bridge_chords):
        vel = 65 if i < 3 else 70
        add_chord_strum(track, chord, 4, velocity=vel, strum_delay=30)
    
    # FINAL REVEAL - 5 bars devastating
    # | Am | Fmaj7 | Dm | E | Am (hold) |
    track.append(MetaMessage('marker', text='FINAL - REVEAL'))
    final_chords = ['Am', 'Fmaj7', 'Dm', 'E', 'Am']
    for chord in final_chords:
        add_chord_strum(track, chord, 4, velocity=55, strum_delay=40)
    
    # OUTRO - 4 bars fingerpicked fade
    track.append(MetaMessage('marker', text='OUTRO'))
    outro_chords = ['Am', 'Am/G', 'Fmaj7', 'E']
    for i, chord in enumerate(outro_chords):
        vel = 50 - (i * 8)  # Fade out
        add_arpeggio(track, chord, 4, velocity=max(vel, 30))
        add_arpeggio(track, chord, 4, velocity=max(vel-5, 25))
    
    # End of track
    track.append(MetaMessage('end_of_track'))
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, 'kelly_song_reference.mid')
    mid.save(output_path)
    print(f"Created: {output_path}")
    return output_path

def create_intro_only():
    """Create just the intro for practice"""
    mid = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    track = MidiTrack()
    mid.tracks.append(track)
    
    track.append(MetaMessage('set_tempo', tempo=tempo_to_microseconds(BPM)))
    track.append(MetaMessage('track_name', name='Intro - Fingerpicked'))
    
    intro_chords = ['Am', 'Am/G', 'Fmaj7', 'E', 'Am', 'Am/G', 'Dm', 'E']
    for chord in intro_chords:
        add_arpeggio(track, chord, 4, velocity=55)
        add_arpeggio(track, chord, 4, velocity=50)
    
    track.append(MetaMessage('end_of_track'))
    
    output_path = os.path.join(OUTPUT_DIR, 'kelly_intro.mid')
    mid.save(output_path)
    print(f"Created: {output_path}")
    return output_path

def create_chord_chart_midi():
    """Create a simple chord reference - one bar of each chord used"""
    mid = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    track = MidiTrack()
    mid.tracks.append(track)
    
    track.append(MetaMessage('set_tempo', tempo=tempo_to_microseconds(60)))  # Slow for reference
    track.append(MetaMessage('track_name', name='Chord Reference'))
    
    all_chords = ['Am', 'Am/G', 'Fmaj7', 'E', 'Esus4', 'C', 'G', 'Em', 'Dm', 'Bdim', 'C#dim']
    for chord in all_chords:
        track.append(MetaMessage('marker', text=chord))
        add_chord_strum(track, chord, 4, velocity=70, strum_delay=25)
    
    track.append(MetaMessage('end_of_track'))
    
    output_path = os.path.join(OUTPUT_DIR, 'kelly_chords_reference.mid')
    mid.save(output_path)
    print(f"Created: {output_path}")
    return output_path

if __name__ == '__main__':
    print("=" * 50)
    print("Kelly Song Project - MIDI Generator")
    print("=" * 50)
    print()
    
    create_full_song_midi()
    create_intro_only()
    create_chord_chart_midi()
    
    print()
    print("Done! Import these MIDI files into Logic Pro as reference tracks.")
    print("They provide timing and chord structure - record your real guitar over them.")
