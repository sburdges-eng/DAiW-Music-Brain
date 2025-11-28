#!/usr/bin/env python3
"""
iDAW Instrument Library Integration
====================================
Version: 1.0.02

Integrates with:
- Logic Pro X (Apple Loops, Patches, Alchemy)
- MeldaProduction (Presets, MSoundFactory)
- Vital (Wavetables, Presets)
- User Sample Library (Google Drive)

Author: iDAW Project
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# ============================================================================
# STANDARD PATHS FOR MAC
# ============================================================================

class InstrumentPaths:
    """Standard locations for instrument libraries on macOS."""
    
    # Logic Pro X
    LOGIC_PRO = {
        "app": "/Applications/Logic Pro X.app",
        "apple_loops": Path.home() / "Library/Audio/Apple Loops",
        "apple_loops_system": Path("/Library/Audio/Apple Loops"),
        "patches": Path.home() / "Library/Application Support/Logic/Patches",
        "patches_system": Path("/Library/Application Support/Logic/Patches"),
        "alchemy": Path.home() / "Library/Application Support/Logic/Alchemy",
        "sampler_instruments": Path.home() / "Library/Application Support/Logic/Sampler Instruments",
        "channel_strips": Path.home() / "Library/Application Support/Logic/Channel Strip Settings",
        "impulse_responses": Path.home() / "Library/Audio/Impulse Responses",
    }
    
    # MeldaProduction
    MELDA = {
        "presets_user": Path.home() / "Library/Audio/Presets/MeldaProduction",
        "presets_system": Path("/Library/Audio/Presets/MeldaProduction"),
        "msoundfactory": Path.home() / "Library/Application Support/MeldaProduction/MSoundFactory",
        "mdrummer": Path.home() / "Library/Application Support/MeldaProduction/MDrummer",
        "plugins_au": Path("/Library/Audio/Plug-Ins/Components"),
        "plugins_vst": Path("/Library/Audio/Plug-Ins/VST"),
        "plugins_vst3": Path("/Library/Audio/Plug-Ins/VST3"),
    }
    
    # Vital Synth
    VITAL = {
        "presets_user": Path.home() / "Library/Application Support/Vital/presets",
        "presets_factory": Path("/Library/Application Support/Vital/presets"),
        "wavetables_user": Path.home() / "Library/Application Support/Vital/wavetables",
        "wavetables_factory": Path("/Library/Application Support/Vital/wavetables"),
        "lfo": Path.home() / "Library/Application Support/Vital/LFO",
        "samples": Path.home() / "Library/Application Support/Vital/Samples",
    }
    
    # User Sample Library (from previous conversation)
    USER_SAMPLES = {
        "google_drive": Path.home() / "Google Drive/My Drive",
        "audio_vault": Path.home() / "Google Drive/My Drive/audio_vault",
        "drum_tornado": Path.home() / "Google Drive/My Drive/audio_vault/Drum Tornado 2023",
        "drum_empire": Path.home() / "Google Drive/My Drive/audio_vault/Drum Empire 2020",
        "synthwave": Path.home() / "Google Drive/My Drive/audio_vault/Synthwave",
        "pads_strings": Path.home() / "Google Drive/My Drive/audio_vault/Pads & Strings",
        "plucks_keys": Path.home() / "Google Drive/My Drive/audio_vault/Plucks & Keys",
        "bass": Path.home() / "Google Drive/My Drive/audio_vault/Bass",
        "percussion": Path.home() / "Google Drive/My Drive/audio_vault/Percussion",
    }
    
    # iDAW Output
    OUTPUT = Path.home() / "Music/iDAW_Output"


# ============================================================================
# INSTRUMENT CATEGORIES
# ============================================================================

class InstrumentCategory(Enum):
    """Categories of instruments for emotional mapping."""
    DRUMS_ACOUSTIC = "drums_acoustic"
    DRUMS_ELECTRONIC = "drums_electronic"
    BASS_SYNTH = "bass_synth"
    BASS_ACOUSTIC = "bass_acoustic"
    KEYS_PIANO = "keys_piano"
    KEYS_ELECTRIC = "keys_electric"
    PADS = "pads"
    STRINGS = "strings"
    SYNTH_LEAD = "synth_lead"
    SYNTH_PAD = "synth_pad"
    GUITAR_ACOUSTIC = "guitar_acoustic"
    GUITAR_ELECTRIC = "guitar_electric"
    VOCALS = "vocals"
    FX = "fx"
    PERCUSSION = "percussion"


# ============================================================================
# EMOTIONAL INSTRUMENT MAPPING
# ============================================================================

EMOTION_TO_INSTRUMENTS: Dict[str, Dict[str, List[str]]] = {
    "grief": {
        "primary": ["keys_piano", "pads", "strings", "guitar_acoustic"],
        "drums": ["drums_acoustic"],
        "texture": ["pads"],
        "avoid": ["synth_lead", "drums_electronic"],
        "logic_patches": ["Emotional Piano", "Ethereal Pad", "Melancholy Strings"],
        "vital_presets": ["Soft Pad", "Ambient Wash", "Gentle Keys"],
        "melda_presets": ["Warm Pad", "Soft Synth"],
        "user_samples": ["Drum Tornado 2023/Acoustic", "Pads & Strings"],
    },
    "anxiety": {
        "primary": ["synth_lead", "keys_electric", "bass_synth"],
        "drums": ["drums_electronic"],
        "texture": ["fx", "synth_pad"],
        "avoid": ["pads", "strings"],
        "logic_patches": ["Tense Pulse", "Dark Synth", "Nervous Energy"],
        "vital_presets": ["Harsh Lead", "Distorted Bass", "Glitch Pad"],
        "melda_presets": ["Aggressive Synth", "Tense Atmosphere"],
        "user_samples": ["Drum Empire 2020", "Synthwave"],
    },
    "nostalgia": {
        "primary": ["keys_piano", "keys_electric", "guitar_acoustic"],
        "drums": ["drums_acoustic"],
        "texture": ["pads", "strings"],
        "avoid": ["synth_lead"],
        "logic_patches": ["Vintage Keys", "Warm Rhodes", "Nostalgic Piano"],
        "vital_presets": ["Retro Pad", "Warm Analog", "Vintage Lead"],
        "melda_presets": ["Vintage Warmth", "Retro Synth"],
        "user_samples": ["Plucks & Keys", "Pads & Strings", "Drum Tornado 2023/Acoustic"],
    },
    "anger": {
        "primary": ["bass_synth", "synth_lead", "guitar_electric"],
        "drums": ["drums_electronic", "drums_acoustic"],
        "texture": ["fx"],
        "avoid": ["pads", "strings"],
        "logic_patches": ["Aggressive Bass", "Distorted Lead", "Power Drums"],
        "vital_presets": ["Scream Lead", "Distortion Bass", "Harsh Pad"],
        "melda_presets": ["Brutal Synth", "Aggressive Lead"],
        "user_samples": ["Drum Empire 2020", "Bass"],
    },
    "calm": {
        "primary": ["keys_piano", "pads", "guitar_acoustic"],
        "drums": [],  # Often no drums
        "texture": ["pads", "strings"],
        "avoid": ["synth_lead", "drums_electronic", "bass_synth"],
        "logic_patches": ["Peaceful Piano", "Ambient Pad", "Gentle Strings"],
        "vital_presets": ["Soft Ambient", "Peaceful Pad", "Gentle Wave"],
        "melda_presets": ["Calm Atmosphere", "Soft Pad"],
        "user_samples": ["Pads & Strings", "Plucks & Keys"],
    },
    "hope": {
        "primary": ["keys_piano", "strings", "synth_pad"],
        "drums": ["drums_acoustic"],
        "texture": ["pads"],
        "avoid": [],
        "logic_patches": ["Uplifting Piano", "Bright Strings", "Hopeful Pad"],
        "vital_presets": ["Bright Lead", "Uplifting Pad", "Shimmer"],
        "melda_presets": ["Bright Synth", "Uplifting Atmosphere"],
        "user_samples": ["Plucks & Keys", "Pads & Strings", "Drum Tornado 2023"],
    },
    "intimacy": {
        "primary": ["keys_piano", "guitar_acoustic", "vocals"],
        "drums": ["drums_acoustic"],  # Brushes
        "texture": ["pads"],
        "avoid": ["drums_electronic", "synth_lead"],
        "logic_patches": ["Intimate Piano", "Soft Guitar", "Whisper Pad"],
        "vital_presets": ["Soft Keys", "Gentle Pad", "Warm Texture"],
        "melda_presets": ["Intimate Atmosphere", "Soft Synth"],
        "user_samples": ["Drum Tornado 2023/Acoustic", "Pads & Strings"],
    },
    "defiance": {
        "primary": ["bass_synth", "guitar_electric", "synth_lead"],
        "drums": ["drums_acoustic", "drums_electronic"],
        "texture": ["fx"],
        "avoid": ["pads"],
        "logic_patches": ["Power Bass", "Defiant Lead", "Strong Drums"],
        "vital_presets": ["Aggressive Lead", "Power Bass", "Distorted Pad"],
        "melda_presets": ["Powerful Synth", "Strong Bass"],
        "user_samples": ["Drum Empire 2020", "Bass", "Synthwave"],
    },
}


# ============================================================================
# LIBRARY SCANNER
# ============================================================================

@dataclass
class InstrumentLibrary:
    """Represents a scanned instrument library."""
    name: str
    path: Path
    available: bool
    presets: List[str] = field(default_factory=list)
    samples: List[str] = field(default_factory=list)
    patches: List[str] = field(default_factory=list)
    wavetables: List[str] = field(default_factory=list)


class LibraryScanner:
    """Scans and catalogs available instrument libraries."""
    
    def __init__(self):
        self.libraries: Dict[str, InstrumentLibrary] = {}
        self.scan_results: Dict[str, Any] = {}
        
    def scan_all(self) -> Dict[str, InstrumentLibrary]:
        """Scan all known library locations."""
        print("🔍 Scanning instrument libraries...")
        
        self.scan_logic_pro()
        self.scan_melda()
        self.scan_vital()
        self.scan_user_samples()
        
        return self.libraries
    
    def scan_logic_pro(self) -> Optional[InstrumentLibrary]:
        """Scan Logic Pro X libraries."""
        print("  📁 Logic Pro X...")
        
        logic_app = Path(InstrumentPaths.LOGIC_PRO["app"])
        available = logic_app.exists()
        
        library = InstrumentLibrary(
            name="Logic Pro X",
            path=logic_app,
            available=available,
        )
        
        if available:
            # Scan Apple Loops
            for loops_path in [InstrumentPaths.LOGIC_PRO["apple_loops"], 
                              InstrumentPaths.LOGIC_PRO["apple_loops_system"]]:
                if loops_path.exists():
                    library.samples.extend(self._scan_directory(loops_path, [".aif", ".caf", ".wav"]))
            
            # Scan Patches
            for patches_path in [InstrumentPaths.LOGIC_PRO["patches"],
                                InstrumentPaths.LOGIC_PRO["patches_system"]]:
                if patches_path.exists():
                    library.patches.extend(self._scan_directory(patches_path, [".patch", ".pst"]))
            
            # Scan Alchemy
            alchemy_path = InstrumentPaths.LOGIC_PRO["alchemy"]
            if alchemy_path.exists():
                library.presets.extend(self._scan_directory(alchemy_path, [".alchemy"]))
            
            print(f"    ✓ Found {len(library.samples)} loops, {len(library.patches)} patches")
        else:
            print("    ✗ Not installed")
        
        self.libraries["logic_pro"] = library
        return library
    
    def scan_melda(self) -> Optional[InstrumentLibrary]:
        """Scan MeldaProduction libraries."""
        print("  📁 MeldaProduction...")
        
        # Check if any Melda plugins exist
        melda_exists = any(
            list(InstrumentPaths.MELDA["plugins_au"].glob("M*.component")) if InstrumentPaths.MELDA["plugins_au"].exists() else []
        )
        
        library = InstrumentLibrary(
            name="MeldaProduction",
            path=InstrumentPaths.MELDA["presets_user"],
            available=melda_exists,
        )
        
        if melda_exists or InstrumentPaths.MELDA["presets_user"].exists():
            # Scan presets
            for presets_path in [InstrumentPaths.MELDA["presets_user"],
                                InstrumentPaths.MELDA["presets_system"]]:
                if presets_path.exists():
                    library.presets.extend(self._scan_directory(presets_path, [".mpreset", ".xml"]))
            
            # Scan MSoundFactory
            msf_path = InstrumentPaths.MELDA["msoundfactory"]
            if msf_path.exists():
                library.patches.extend(self._scan_directory(msf_path, [".msf", ".mpreset"]))
            
            # Scan MDrummer
            mdrummer_path = InstrumentPaths.MELDA["mdrummer"]
            if mdrummer_path.exists():
                library.samples.extend(self._scan_directory(mdrummer_path, [".wav", ".aif"]))
            
            print(f"    ✓ Found {len(library.presets)} presets, {len(library.patches)} patches")
            library.available = True
        else:
            print("    ✗ Not installed")
        
        self.libraries["melda"] = library
        return library
    
    def scan_vital(self) -> Optional[InstrumentLibrary]:
        """Scan Vital synthesizer libraries."""
        print("  📁 Vital...")
        
        vital_exists = InstrumentPaths.VITAL["presets_user"].exists() or \
                      InstrumentPaths.VITAL["presets_factory"].exists()
        
        library = InstrumentLibrary(
            name="Vital",
            path=InstrumentPaths.VITAL["presets_user"],
            available=vital_exists,
        )
        
        if vital_exists:
            # Scan presets
            for presets_path in [InstrumentPaths.VITAL["presets_user"],
                                InstrumentPaths.VITAL["presets_factory"]]:
                if presets_path.exists():
                    library.presets.extend(self._scan_directory(presets_path, [".vital"]))
            
            # Scan wavetables
            for wt_path in [InstrumentPaths.VITAL["wavetables_user"],
                           InstrumentPaths.VITAL["wavetables_factory"]]:
                if wt_path.exists():
                    library.wavetables.extend(self._scan_directory(wt_path, [".wav", ".vitaltable"]))
            
            # Scan LFO shapes
            lfo_path = InstrumentPaths.VITAL["lfo"]
            if lfo_path.exists():
                library.patches.extend(self._scan_directory(lfo_path, [".vitallfo"]))
            
            print(f"    ✓ Found {len(library.presets)} presets, {len(library.wavetables)} wavetables")
        else:
            print("    ✗ Not installed")
        
        self.libraries["vital"] = library
        return library
    
    def scan_user_samples(self) -> Optional[InstrumentLibrary]:
        """Scan user's sample library (Google Drive)."""
        print("  📁 User Samples (Google Drive)...")
        
        # Check various possible Google Drive paths
        possible_paths = [
            Path.home() / "Google Drive/My Drive",
            Path.home() / "Google Drive",
            Path.home() / "Library/CloudStorage/GoogleDrive-seanblariat@gmail.com/My Drive",
            Path.home() / "Library/CloudStorage/GoogleDrive/My Drive",
        ]
        
        gdrive_path = None
        for p in possible_paths:
            if p.exists():
                gdrive_path = p
                break
        
        library = InstrumentLibrary(
            name="User Samples",
            path=gdrive_path or Path.home() / "Google Drive",
            available=gdrive_path is not None,
        )
        
        if gdrive_path:
            # Scan known sample folders
            sample_folders = [
                "audio_vault",
                "Drum Tornado 2023",
                "Drum Empire 2020",
                "Synthwave",
                "Pads & Strings",
                "Plucks & Keys",
                "Bass",
                "Percussion",
            ]
            
            for folder in sample_folders:
                folder_path = gdrive_path / folder
                if not folder_path.exists():
                    folder_path = gdrive_path / "audio_vault" / folder
                
                if folder_path.exists():
                    samples = self._scan_directory(folder_path, [".wav", ".aif", ".mp3", ".flac"])
                    library.samples.extend(samples)
            
            print(f"    ✓ Found {len(library.samples)} samples")
        else:
            print("    ✗ Google Drive not found")
            print("      Checked:", possible_paths[0])
        
        self.libraries["user_samples"] = library
        return library
    
    def _scan_directory(self, path: Path, extensions: List[str], max_depth: int = 3) -> List[str]:
        """Recursively scan directory for files with given extensions."""
        results = []
        
        if not path.exists():
            return results
        
        try:
            for ext in extensions:
                results.extend([str(f) for f in path.rglob(f"*{ext}")])
        except PermissionError:
            pass
        
        return results[:500]  # Limit to prevent huge lists
    
    def get_summary(self) -> str:
        """Get a summary of scanned libraries."""
        lines = ["📚 Instrument Library Summary", "=" * 40]
        
        for name, lib in self.libraries.items():
            status = "✓" if lib.available else "✗"
            lines.append(f"\n{status} {lib.name}")
            if lib.available:
                if lib.presets:
                    lines.append(f"   Presets: {len(lib.presets)}")
                if lib.patches:
                    lines.append(f"   Patches: {len(lib.patches)}")
                if lib.samples:
                    lines.append(f"   Samples: {len(lib.samples)}")
                if lib.wavetables:
                    lines.append(f"   Wavetables: {len(lib.wavetables)}")
        
        return "\n".join(lines)


# ============================================================================
# INSTRUMENT SELECTOR
# ============================================================================

@dataclass
class InstrumentSelection:
    """Selected instruments for a track."""
    category: InstrumentCategory
    source: str  # "logic_pro", "melda", "vital", "user_samples"
    preset_path: Optional[str] = None
    sample_paths: List[str] = field(default_factory=list)
    midi_channel: int = 0
    midi_program: int = 0


class InstrumentSelector:
    """Selects appropriate instruments based on emotional state."""
    
    def __init__(self, scanner: LibraryScanner):
        self.scanner = scanner
        self.libraries = scanner.libraries
        
    def select_for_emotion(self, emotion: str, 
                          track_type: str = "full") -> Dict[str, InstrumentSelection]:
        """
        Select instruments for an emotion.
        
        Args:
            emotion: Primary emotion (grief, anxiety, etc.)
            track_type: "full" (all parts), "minimal", "drums_only", etc.
            
        Returns:
            Dict mapping track names to InstrumentSelection
        """
        selections = {}
        
        mapping = EMOTION_TO_INSTRUMENTS.get(emotion, EMOTION_TO_INSTRUMENTS["calm"])
        
        # Primary instrument
        primary_cat = mapping["primary"][0] if mapping["primary"] else "keys_piano"
        selections["lead"] = self._select_instrument(primary_cat, emotion)
        
        # Drums
        if mapping["drums"] and track_type != "no_drums":
            drum_cat = mapping["drums"][0]
            selections["drums"] = self._select_drums(drum_cat, emotion)
        
        # Texture/Pad
        if mapping["texture"] and track_type == "full":
            texture_cat = mapping["texture"][0]
            selections["pad"] = self._select_instrument(texture_cat, emotion)
        
        # Bass
        if track_type == "full":
            bass_cat = "bass_acoustic" if emotion in ["grief", "intimacy", "calm"] else "bass_synth"
            selections["bass"] = self._select_instrument(bass_cat, emotion)
        
        return selections
    
    def _select_instrument(self, category: str, emotion: str) -> InstrumentSelection:
        """Select a specific instrument."""
        selection = InstrumentSelection(
            category=InstrumentCategory(category) if category in [e.value for e in InstrumentCategory] else InstrumentCategory.KEYS_PIANO,
            source="user_samples"
        )
        
        mapping = EMOTION_TO_INSTRUMENTS.get(emotion, {})
        
        # Try Vital first for synths
        if "synth" in category and self.libraries.get("vital", InstrumentLibrary("", Path(), False)).available:
            vital_presets = mapping.get("vital_presets", [])
            if vital_presets:
                selection.source = "vital"
                selection.preset_path = self._find_preset("vital", vital_presets[0])
        
        # Try Logic Pro for acoustic instruments
        elif "acoustic" in category or "piano" in category or "strings" in category:
            if self.libraries.get("logic_pro", InstrumentLibrary("", Path(), False)).available:
                logic_patches = mapping.get("logic_patches", [])
                if logic_patches:
                    selection.source = "logic_pro"
                    selection.preset_path = self._find_preset("logic_pro", logic_patches[0])
        
        # Fallback to user samples
        user_samples = mapping.get("user_samples", [])
        if user_samples and self.libraries.get("user_samples", InstrumentLibrary("", Path(), False)).available:
            selection.sample_paths = self._find_samples("user_samples", user_samples[0])
        
        return selection
    
    def _select_drums(self, category: str, emotion: str) -> InstrumentSelection:
        """Select drum samples."""
        selection = InstrumentSelection(
            category=InstrumentCategory(category),
            source="user_samples",
            midi_channel=9  # GM drum channel
        )
        
        mapping = EMOTION_TO_INSTRUMENTS.get(emotion, {})
        user_samples = mapping.get("user_samples", [])
        
        # Find drum samples from user library
        for sample_hint in user_samples:
            if "Drum" in sample_hint:
                selection.sample_paths = self._find_samples("user_samples", sample_hint)
                break
        
        return selection
    
    def _find_preset(self, library: str, hint: str) -> Optional[str]:
        """Find a preset matching the hint."""
        lib = self.libraries.get(library)
        if not lib or not lib.available:
            return None
        
        hint_lower = hint.lower()
        
        for preset in lib.presets:
            if hint_lower in preset.lower():
                return preset
        
        # Return first preset if no match
        return lib.presets[0] if lib.presets else None
    
    def _find_samples(self, library: str, hint: str) -> List[str]:
        """Find samples matching the hint."""
        lib = self.libraries.get(library)
        if not lib or not lib.available:
            return []
        
        hint_lower = hint.lower().replace(" ", "").replace("/", "")
        
        matches = []
        for sample in lib.samples:
            sample_lower = sample.lower().replace(" ", "").replace("/", "")
            if hint_lower in sample_lower:
                matches.append(sample)
        
        return matches[:50]  # Limit results


# ============================================================================
# LOGIC PRO PROJECT GENERATOR
# ============================================================================

class LogicProExporter:
    """
    Generate files that can be imported into Logic Pro.
    
    Note: Logic Pro doesn't have a direct API, but we can:
    1. Generate MIDI files (import into Logic)
    2. Generate AAF/OMF for exchange
    3. Create Apple Loops
    4. Generate GarageBand projects (Logic can open these)
    """
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or InstrumentPaths.OUTPUT
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def export_for_logic(self, midi_path: Path, 
                        selections: Dict[str, InstrumentSelection],
                        emotion: str,
                        bpm: int) -> Dict[str, Path]:
        """
        Export project files optimized for Logic Pro import.
        
        Returns dict of generated file paths.
        """
        outputs = {}
        
        # 1. Main MIDI file (already exists)
        outputs["midi"] = midi_path
        
        # 2. Create a JSON project file with instrument mappings
        project_data = {
            "idaw_version": "1.0.02",
            "emotion": emotion,
            "bpm": bpm,
            "time_signature": "4/4",
            "tracks": {},
            "logic_pro_hints": {
                "suggested_patches": [],
                "apple_loops_tags": [],
            }
        }
        
        for track_name, selection in selections.items():
            project_data["tracks"][track_name] = {
                "category": selection.category.value,
                "source": selection.source,
                "preset": selection.preset_path,
                "samples": selection.sample_paths[:10],  # Limit
                "midi_channel": selection.midi_channel,
            }
            
            # Add Logic Pro hints
            if selection.source == "logic_pro" and selection.preset_path:
                project_data["logic_pro_hints"]["suggested_patches"].append(selection.preset_path)
        
        project_path = midi_path.with_suffix(".idaw.json")
        with open(project_path, "w") as f:
            json.dump(project_data, f, indent=2)
        outputs["project"] = project_path
        
        # 3. Create a README for Logic Pro import
        readme_content = f"""# iDAW Project - {emotion.title()}

## Import into Logic Pro X

1. Open Logic Pro X
2. Create new project at {bpm} BPM
3. File → Import → MIDI File → select `{midi_path.name}`
4. Assign instruments to tracks:

"""
        for track_name, selection in selections.items():
            readme_content += f"\n### {track_name.title()} Track\n"
            readme_content += f"- Category: {selection.category.value}\n"
            if selection.preset_path:
                readme_content += f"- Suggested Patch: {Path(selection.preset_path).name}\n"
            if selection.sample_paths:
                readme_content += f"- Samples: {len(selection.sample_paths)} available\n"
        
        readme_content += f"""

## Emotional Parameters

- Primary Emotion: {emotion}
- BPM: {bpm}
- Generated by iDAW v1.0.02

## Sample Locations

Your samples are in:
- Google Drive: ~/Google Drive/My Drive/audio_vault/
- Drum Tornado 2023 (Acoustic)
- Drum Empire 2020 (Electronic)
- Pads & Strings
- Plucks & Keys
"""
        
        readme_path = midi_path.with_suffix(".README.md")
        with open(readme_path, "w") as f:
            f.write(readme_content)
        outputs["readme"] = readme_path
        
        return outputs


# ============================================================================
# MAIN INTEGRATION CLASS
# ============================================================================

class iDAWLibraryIntegration:
    """
    Main class for integrating external instrument libraries with iDAW.
    
    Usage:
        integration = iDAWLibraryIntegration()
        integration.scan_libraries()
        
        # Select instruments for emotion
        instruments = integration.select_instruments("grief")
        
        # Export for Logic Pro
        integration.export_for_logic(midi_path, instruments)
    """
    
    def __init__(self):
        self.scanner = LibraryScanner()
        self.selector = None
        self.exporter = LogicProExporter()
        self.scanned = False
        
    def scan_libraries(self) -> str:
        """Scan all libraries and return summary."""
        self.scanner.scan_all()
        self.selector = InstrumentSelector(self.scanner)
        self.scanned = True
        return self.scanner.get_summary()
    
    def select_instruments(self, emotion: str, 
                          track_type: str = "full") -> Dict[str, InstrumentSelection]:
        """Select instruments for an emotion."""
        if not self.scanned:
            self.scan_libraries()
        return self.selector.select_for_emotion(emotion, track_type)
    
    def export_for_logic(self, midi_path: Path,
                        selections: Dict[str, InstrumentSelection],
                        emotion: str,
                        bpm: int) -> Dict[str, Path]:
        """Export project files for Logic Pro."""
        return self.exporter.export_for_logic(midi_path, selections, emotion, bpm)
    
    def get_available_libraries(self) -> Dict[str, bool]:
        """Get which libraries are available."""
        if not self.scanned:
            self.scan_libraries()
        return {name: lib.available for name, lib in self.scanner.libraries.items()}


# ============================================================================
# CLI
# ============================================================================

def main():
    """Command-line interface."""
    print("=" * 50)
    print("iDAW Library Integration v1.0.02")
    print("=" * 50)
    print()
    
    integration = iDAWLibraryIntegration()
    summary = integration.scan_libraries()
    
    print()
    print(summary)
    print()
    
    # Test instrument selection
    print("\n🎹 Testing instrument selection for 'grief'...")
    selections = integration.select_instruments("grief")
    
    for track, sel in selections.items():
        print(f"\n  {track}:")
        print(f"    Source: {sel.source}")
        print(f"    Category: {sel.category.value}")
        if sel.preset_path:
            print(f"    Preset: {Path(sel.preset_path).name}")
        if sel.sample_paths:
            print(f"    Samples: {len(sel.sample_paths)} found")


if __name__ == "__main__":
    main()
