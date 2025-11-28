"""
Logic Pro Integration
Automate Logic Pro session creation via AppleScript.

Features:
- Create new sessions with predefined structure
- Set up track routing and buses
- Import MIDI files to tracks
- Add markers for song sections
- Apply groove templates via MIDI import
"""

import subprocess
import os
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass


@dataclass
class LogicTrack:
    """Track configuration for Logic Pro."""
    name: str
    track_type: str  # 'software_instrument', 'audio', 'drummer'
    instrument: Optional[str] = None  # e.g., 'Steinway Grand Piano'
    output_bus: Optional[str] = None
    color: Optional[str] = None
    midi_file: Optional[str] = None


@dataclass 
class LogicSession:
    """Session configuration for Logic Pro."""
    name: str
    bpm: int
    key: str  # e.g., 'C major'
    time_signature: str  # e.g., '4/4'
    tracks: List[LogicTrack]
    markers: List[tuple]  # [(bar, name), ...]
    

# Default track templates by genre
GENRE_TRACK_TEMPLATES = {
    'pop': [
        LogicTrack('Drums', 'drummer', instrument='Pop'),
        LogicTrack('Bass', 'software_instrument', instrument='Fingerstyle Bass'),
        LogicTrack('Piano', 'software_instrument', instrument='Steinway Grand Piano'),
        LogicTrack('Synth Pad', 'software_instrument', instrument='Warm Pad'),
        LogicTrack('Lead Vocal', 'audio'),
        LogicTrack('Harmony Vox', 'audio'),
    ],
    'rock': [
        LogicTrack('Drums', 'drummer', instrument='Rock'),
        LogicTrack('Bass', 'software_instrument', instrument='Classic Electric Bass'),
        LogicTrack('Rhythm Guitar L', 'audio'),
        LogicTrack('Rhythm Guitar R', 'audio'),
        LogicTrack('Lead Guitar', 'audio'),
        LogicTrack('Lead Vocal', 'audio'),
    ],
    'hiphop': [
        LogicTrack('Drums', 'software_instrument', instrument='Hip Hop Drums'),
        LogicTrack('808 Bass', 'software_instrument', instrument='808 Bass'),
        LogicTrack('Keys', 'software_instrument', instrument='Electric Piano'),
        LogicTrack('Synth', 'software_instrument', instrument='Analog Pad'),
        LogicTrack('Lead Vocal', 'audio'),
        LogicTrack('Ad Libs', 'audio'),
    ],
    'jazz': [
        LogicTrack('Drums', 'drummer', instrument='Jazz Brushes'),
        LogicTrack('Upright Bass', 'software_instrument', instrument='Upright Bass'),
        LogicTrack('Piano', 'software_instrument', instrument='Jazz Piano'),
        LogicTrack('Horns', 'software_instrument', instrument='Trumpet Section'),
    ],
    'electronic': [
        LogicTrack('Kick', 'software_instrument', instrument='Electronic Drums'),
        LogicTrack('Snare/Clap', 'software_instrument', instrument='Electronic Drums'),
        LogicTrack('Hi-Hats', 'software_instrument', instrument='Electronic Drums'),
        LogicTrack('Bass', 'software_instrument', instrument='Analog Bass'),
        LogicTrack('Lead Synth', 'software_instrument', instrument='Lead Synth'),
        LogicTrack('Pad', 'software_instrument', instrument='Ambient Pad'),
        LogicTrack('FX', 'software_instrument', instrument='FX'),
    ],
    'lofi': [
        LogicTrack('Drums', 'software_instrument', instrument='Vintage Drums'),
        LogicTrack('Bass', 'software_instrument', instrument='Muted Bass'),
        LogicTrack('Rhodes', 'software_instrument', instrument='Vintage Electric Piano'),
        LogicTrack('Vinyl Noise', 'audio'),
        LogicTrack('Samples', 'audio'),
    ],
}

# Bus routing templates
BUS_TEMPLATES = {
    'standard': [
        ('Drums Bus', ['Drums', 'Kick', 'Snare/Clap', 'Hi-Hats']),
        ('Music Bus', ['Bass', 'Piano', 'Keys', 'Guitar', 'Synth']),
        ('Vocal Bus', ['Lead Vocal', 'Harmony Vox', 'Ad Libs']),
    ],
    'stems': [
        ('Drums', ['Drums', 'Kick', 'Snare/Clap', 'Hi-Hats']),
        ('Bass', ['Bass', '808 Bass']),
        ('Music', ['Piano', 'Keys', 'Guitar', 'Synth', 'Pad']),
        ('Vocals', ['Lead Vocal', 'Harmony Vox', 'Ad Libs']),
        ('FX', ['FX', 'Vinyl Noise']),
    ],
}


class LogicProAutomation:
    """
    Automate Logic Pro X via AppleScript.
    
    Note: Requires Logic Pro X and macOS.
    Some features may require Logic Pro to be open.
    """
    
    def __init__(self):
        self.is_macos = os.uname().sysname == 'Darwin'
    
    def _run_applescript(self, script: str) -> str:
        """Run AppleScript and return result."""
        if not self.is_macos:
            raise RuntimeError("Logic Pro automation requires macOS")
        
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"AppleScript error: {result.stderr}")
        
        return result.stdout.strip()
    
    def is_logic_running(self) -> bool:
        """Check if Logic Pro is running."""
        if not self.is_macos:
            return False
        
        script = '''
        tell application "System Events"
            return (name of processes) contains "Logic Pro X"
        end tell
        '''
        result = self._run_applescript(script)
        return result == 'true'
    
    def launch_logic(self):
        """Launch Logic Pro X."""
        script = '''
        tell application "Logic Pro X"
            activate
        end tell
        '''
        self._run_applescript(script)
    
    def create_new_project(self, name: str, bpm: int = 120):
        """
        Create a new Logic Pro project.
        
        Note: This creates a basic project. For full template support,
        Logic Pro needs to be configured with the template.
        """
        script = f'''
        tell application "Logic Pro X"
            activate
            delay 1
            -- Create new project (Cmd+N)
            tell application "System Events"
                keystroke "n" using command down
            end tell
            delay 2
        end tell
        '''
        self._run_applescript(script)
    
    def set_tempo(self, bpm: int):
        """Set project tempo."""
        script = f'''
        tell application "Logic Pro X"
            activate
            tell application "System Events"
                -- Open tempo dialog
                keystroke "t" using {{command down, option down}}
                delay 0.5
                -- Type tempo
                keystroke "{bpm}"
                keystroke return
            end tell
        end tell
        '''
        self._run_applescript(script)
    
    def add_marker(self, name: str):
        """Add a marker at current position."""
        script = f'''
        tell application "Logic Pro X"
            activate
            tell application "System Events"
                -- Create marker (Option+')
                keystroke "'" using option down
                delay 0.3
                -- Rename marker
                keystroke "{name}"
                keystroke return
            end tell
        end tell
        '''
        self._run_applescript(script)
    
    def import_midi(self, midi_path: str):
        """Import a MIDI file."""
        midi_path = str(Path(midi_path).resolve())
        
        script = f'''
        tell application "Logic Pro X"
            activate
            tell application "System Events"
                -- Import (Cmd+I doesn't work directly, use menu)
                click menu item "Import" of menu "File" of menu bar 1 of process "Logic Pro X"
                delay 0.5
            end tell
        end tell
        
        tell application "System Events"
            tell process "Logic Pro X"
                -- Navigate to file
                keystroke "g" using {{command down, shift down}}
                delay 0.5
                keystroke "{midi_path}"
                keystroke return
                delay 0.5
                keystroke return
            end tell
        end tell
        '''
        self._run_applescript(script)
    
    def generate_session_script(self, session: LogicSession) -> str:
        """
        Generate a complete AppleScript for session creation.
        
        Returns the script as a string that can be saved and run manually.
        """
        lines = [
            '-- Logic Pro Session Setup Script',
            f'-- Project: {session.name}',
            f'-- BPM: {session.bpm}',
            f'-- Key: {session.key}',
            '',
            'tell application "Logic Pro X"',
            '    activate',
            '    delay 2',
            'end tell',
            '',
            'tell application "System Events"',
            '    tell process "Logic Pro X"',
        ]
        
        # Set tempo
        lines.extend([
            f'        -- Set tempo to {session.bpm}',
            '        keystroke "t" using {command down, option down}',
            '        delay 0.5',
            f'        keystroke "{session.bpm}"',
            '        keystroke return',
            '        delay 0.5',
        ])
        
        # Add tracks
        for track in session.tracks:
            track_type_key = {
                'software_instrument': 's',
                'audio': 'a',
                'drummer': 'd'
            }.get(track.track_type, 'a')
            
            lines.extend([
                f'        -- Add track: {track.name}',
                f'        keystroke "{track_type_key}" using {{command down, option down}}',
                '        delay 1',
            ])
        
        # Add markers
        for bar, marker_name in session.markers:
            lines.extend([
                f'        -- Marker: {marker_name} at bar {bar}',
                '        -- (Move playhead to bar position first)',
                f'        keystroke "\'" using option down',
                '        delay 0.3',
                f'        keystroke "{marker_name}"',
                '        keystroke return',
                '        delay 0.3',
            ])
        
        lines.extend([
            '    end tell',
            'end tell',
        ])
        
        return '\n'.join(lines)
    
    def save_session_script(self, session: LogicSession, output_path: str) -> str:
        """Save session setup script to file."""
        script = self.generate_session_script(session)
        
        output_path = Path(output_path)
        output_path.write_text(script)
        
        # Make executable
        os.chmod(output_path, 0o755)
        
        return str(output_path)


def create_logic_session(
    genre: str,
    name: str,
    bpm: int = 120,
    key: str = 'C major',
    markers: Optional[List[tuple]] = None,
    output_script: Optional[str] = None
) -> LogicSession:
    """
    Create a Logic Pro session configuration.
    
    Args:
        genre: Genre for track template
        name: Project name
        bpm: Tempo
        key: Key signature
        markers: List of (bar, name) tuples
        output_script: Path to save AppleScript (optional)
    
    Returns:
        LogicSession object
    """
    # Get track template
    tracks = GENRE_TRACK_TEMPLATES.get(genre, GENRE_TRACK_TEMPLATES['pop'])
    
    session = LogicSession(
        name=name,
        bpm=bpm,
        key=key,
        time_signature='4/4',
        tracks=list(tracks),  # Copy the list
        markers=markers or []
    )
    
    if output_script:
        automation = LogicProAutomation()
        automation.save_session_script(session, output_script)
    
    return session


def get_genre_tracks(genre: str) -> List[LogicTrack]:
    """Get default track list for a genre."""
    return list(GENRE_TRACK_TEMPLATES.get(genre, GENRE_TRACK_TEMPLATES['pop']))
