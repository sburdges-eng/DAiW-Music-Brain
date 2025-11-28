"""
Auto-Application Pipeline

The complete workflow:
1. Audio feel → template selection
2. Section detection → per-section groove maps
3. Per-instrument velocity application
4. Smart groove transfer

This is the "assistant" layer that makes intelligent decisions.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import random

from ..utils.ppq import STANDARD_PPQ, scale_template
from ..utils.midi_io import load_midi, save_midi, modify_notes_safe, MidiData
from ..utils.instruments import classify_note, get_drum_category, is_drum_channel
from .feel_matching import (
    TemplateMatcher, FeelProfile, TemplateScore,
    SectionGrooveMap, InstrumentVelocityPattern,
    INSTRUMENT_VELOCITY_PATTERNS
)
from .genre_templates import GENRE_TEMPLATES, POCKET_OFFSETS
from .applicator import ApplicationStats


@dataclass
class AutoApplicationConfig:
    """Configuration for auto-application."""
    
    # Template selection
    genre_override: Optional[str] = None  # Force specific genre
    min_match_score: float = 40.0         # Minimum acceptable score
    
    # Application intensity
    timing_intensity: float = 0.7         # How much timing to apply (0-1)
    velocity_intensity: float = 0.8       # How much velocity to apply (0-1)
    swing_intensity: float = 0.6          # How much swing to apply (0-1)
    
    # Humanization
    randomness: float = 0.2               # Random variation (0-1)
    
    # Section handling
    section_aware: bool = True            # Use section-specific grooves
    fill_enabled: bool = True             # Add fills at section boundaries
    
    # Per-instrument handling
    per_instrument_velocity: bool = True  # Use per-instrument patterns
    respect_existing_dynamics: float = 0.3  # Blend with existing velocities (0-1)


@dataclass
class SectionApplication:
    """Application results for a single section."""
    section_name: str
    start_bar: int
    end_bar: int
    notes_modified: int
    groove_map: SectionGrooveMap


@dataclass
class AutoApplicationResult:
    """Complete results from auto-application."""
    
    # Input info
    source_audio: Optional[str]
    target_midi: str
    output_midi: str
    
    # Template selection
    selected_genre: str
    match_score: float
    match_reasons: List[str]
    alternative_genres: List[Tuple[str, float]]  # (genre, score)
    
    # Application stats
    total_notes_modified: int
    timing_shifts: int
    velocity_changes: int
    swing_adjustments: int
    
    # Section breakdown
    sections_processed: List[SectionApplication]
    
    # Per-instrument stats
    instrument_stats: Dict[str, Dict[str, int]]  # instrument → {metric: count}
    
    # Warnings/notes
    warnings: List[str] = field(default_factory=list)


class AutoGrooveApplicator:
    """
    Intelligent groove application pipeline.
    
    Flow:
    1. Analyze source (audio or MIDI)
    2. Select best-matching template
    3. Detect sections in target
    4. Apply per-section, per-instrument grooves
    """
    
    def __init__(self, config: AutoApplicationConfig = None):
        self.config = config or AutoApplicationConfig()
        self.matcher = TemplateMatcher()
    
    def apply_from_audio(
        self,
        audio_path: str,
        midi_path: str,
        output_path: str,
        audio_feel: Dict[str, Any] = None
    ) -> AutoApplicationResult:
        """
        Apply groove from audio reference to MIDI.
        
        Args:
            audio_path: Source audio file
            midi_path: Target MIDI file
            output_path: Output MIDI path
            audio_feel: Pre-computed audio analysis (optional)
        
        Returns:
            AutoApplicationResult with full details
        """
        # Step 1: Get audio feel (or use provided)
        if audio_feel is None:
            try:
                from ..audio.analyzer import analyze_audio_feel
                audio_feel = analyze_audio_feel(audio_path)
            except ImportError:
                from ..audio.feel import analyze_audio_feel as legacy_analyze
                audio_feel = legacy_analyze(audio_path)
        
        # Step 2: Create feel profile
        profile = self.matcher.profile_from_audio_feel(audio_feel)
        profile.source_file = audio_path
        
        # Step 3: Apply to MIDI
        return self._apply_with_profile(profile, midi_path, output_path, audio_path)
    
    def apply_from_midi_reference(
        self,
        reference_midi: str,
        target_midi: str,
        output_path: str
    ) -> AutoApplicationResult:
        """
        Transfer groove from one MIDI to another.
        
        Args:
            reference_midi: Source MIDI with desired groove
            target_midi: Target MIDI to modify
            output_path: Output MIDI path
        
        Returns:
            AutoApplicationResult
        """
        # Load reference and extract groove
        from .extractor import GrooveExtractor
        
        ref_data = load_midi(reference_midi)
        extractor = GrooveExtractor()
        groove_template = extractor.extract(reference_midi, genre=None)
        
        # Create profile from MIDI
        profile = self.matcher.profile_from_midi(ref_data, groove_template.__dict__)
        profile.source_file = reference_midi
        
        return self._apply_with_profile(profile, target_midi, output_path, None)
    
    def apply_genre(
        self,
        genre: str,
        midi_path: str,
        output_path: str
    ) -> AutoApplicationResult:
        """
        Apply a specific genre's groove to MIDI.
        
        Args:
            genre: Genre name (hiphop, funk, jazz, etc.)
            midi_path: Target MIDI file
            output_path: Output MIDI path
        
        Returns:
            AutoApplicationResult
        """
        # Create a "neutral" profile that will match the requested genre
        profile = FeelProfile(
            tempo_bpm=120,
            source_type="genre_override"
        )
        
        # Override genre selection
        original_override = self.config.genre_override
        self.config.genre_override = genre
        
        try:
            result = self._apply_with_profile(profile, midi_path, output_path, None)
        finally:
            self.config.genre_override = original_override
        
        return result
    
    def _apply_with_profile(
        self,
        profile: FeelProfile,
        midi_path: str,
        output_path: str,
        audio_source: Optional[str]
    ) -> AutoApplicationResult:
        """
        Core application logic with a feel profile.
        """
        warnings = []
        
        # Step 1: Select template
        if self.config.genre_override:
            genre = self.config.genre_override
            score = TemplateScore(
                genre=genre,
                total_score=100,
                tempo_score=20, energy_score=25, swing_score=25,
                density_score=15, brightness_score=15,
                match_reasons=["Genre manually selected"],
                mismatch_reasons=[]
            )
            alternatives = []
        else:
            all_scores = self.matcher.rank_templates(profile, top_n=5)
            if not all_scores or all_scores[0].total_score < self.config.min_match_score:
                warnings.append(f"No good template match (best: {all_scores[0].total_score:.0f})")
                # Fall back to most neutral template
                genre = "rock"
                score = all_scores[0] if all_scores else TemplateScore(
                    "rock", 50, 10, 10, 10, 10, 10, [], ["Fallback"]
                )
            else:
                genre = all_scores[0].genre
                score = all_scores[0]
            alternatives = [(s.genre, s.total_score) for s in all_scores[1:]]
        
        template = GENRE_TEMPLATES.get(genre, GENRE_TEMPLATES["rock"])
        
        # Step 2: Load target MIDI
        data = load_midi(midi_path, normalize_ppq=False)  # Keep original PPQ
        
        # Step 3: Detect sections (if enabled)
        if self.config.section_aware:
            from ..structure.sections import SectionDetector
            detector = SectionDetector(ppq=data.ppq)
            sections = detector.detect_sections(data)
        else:
            # Treat entire file as one section
            from ..structure.sections import Section
            total_bars = int(max(n.onset_ticks for n in data.all_notes) / data.ticks_per_bar) + 1
            sections = [Section(
                name="full",
                start_bar=0,
                end_bar=total_bars,
                length_bars=total_bars,
                energy=0.5,
                density=0.5,
                characteristics={},
                confidence=1.0
            )]
        
        # Step 4: Scale template to target PPQ if needed
        if template.get('ppq', STANDARD_PPQ) != data.ppq:
            template = scale_template(template, template['ppq'], data.ppq)
        
        # Step 5: Apply section by section
        section_results = []
        total_modified = 0
        total_timing = 0
        total_velocity = 0
        total_swing = 0
        instrument_stats = {}
        
        for section in sections:
            section_result = self._apply_to_section(
                data, template, genre, section
            )
            section_results.append(section_result)
            total_modified += section_result.notes_modified
        
        # Step 6: Aggregate instrument stats
        for note in data.all_notes:
            inst = classify_note(note.pitch, note.channel)
            if inst not in instrument_stats:
                instrument_stats[inst] = {"notes": 0, "timing_shifts": 0, "velocity_changes": 0}
            instrument_stats[inst]["notes"] += 1
        
        # Step 7: Save output
        save_midi(data, output_path)
        
        return AutoApplicationResult(
            source_audio=audio_source,
            target_midi=midi_path,
            output_midi=output_path,
            selected_genre=genre,
            match_score=score.total_score,
            match_reasons=score.match_reasons,
            alternative_genres=alternatives,
            total_notes_modified=total_modified,
            timing_shifts=total_timing,
            velocity_changes=total_velocity,
            swing_adjustments=total_swing,
            sections_processed=section_results,
            instrument_stats=instrument_stats,
            warnings=warnings
        )
    
    def _apply_to_section(
        self,
        data: MidiData,
        template: Dict,
        genre: str,
        section
    ) -> SectionApplication:
        """
        Apply groove to a specific section.
        """
        # Get section-specific groove map
        groove_map = self.matcher.get_section_groove_map(genre, section.name)
        
        # Calculate tick range for this section
        tpb = data.ticks_per_bar
        start_tick = section.start_bar * tpb
        end_tick = section.end_bar * tpb
        
        notes_modified = 0
        
        # Get per-instrument velocity patterns
        inst_patterns = INSTRUMENT_VELOCITY_PATTERNS.get(genre.lower(), {})
        
        # Apply groove to notes in this section
        def modify_note(note):
            nonlocal notes_modified
            
            # Check if note is in this section
            if not (start_tick <= note.onset_ticks < end_tick):
                return note
            
            # Get instrument
            if is_drum_channel(note.channel):
                inst = get_drum_category(note.pitch)
            else:
                inst = classify_note(note.pitch, note.channel)
            
            # Calculate position in bar
            position_in_bar = (note.onset_ticks - start_tick) % tpb
            grid_ticks = tpb // 16
            grid_idx = int(position_in_bar // grid_ticks) % 16
            
            new_onset = note.onset_ticks
            new_velocity = note.velocity
            
            # === Timing Application ===
            
            # 1. Pocket offset (per-instrument)
            pocket_offset = groove_map.instrument_pocket.get(inst, 0)
            pocket_offset = int(pocket_offset * self.config.timing_intensity)
            
            # 2. Grid timing offset
            timing_offsets = groove_map.timing_offset
            if grid_idx < len(timing_offsets):
                grid_offset = int(timing_offsets[grid_idx] * self.config.timing_intensity)
            else:
                grid_offset = 0
            
            # 3. Swing (for off-beat 8ths)
            swing_offset = 0
            eighth_pos = grid_idx // 2
            is_offbeat_eighth = grid_idx % 2 == 1 and grid_idx % 4 in (1, 3)
            
            if is_offbeat_eighth and groove_map.swing_ratio > 0.52:
                # Calculate swing offset
                eighth_ticks = tpb // 2
                swing_amount = (groove_map.swing_ratio - 0.5) * eighth_ticks
                swing_offset = int(swing_amount * self.config.swing_intensity)
            
            # 4. Randomization
            if self.config.randomness > 0:
                random_offset = int(random.gauss(0, self.config.randomness * 10))
            else:
                random_offset = 0
            
            # Apply timing
            total_offset = pocket_offset + grid_offset + swing_offset + random_offset
            new_onset = max(0, note.onset_ticks + total_offset)
            
            # === Velocity Application ===
            
            if self.config.per_instrument_velocity and inst in inst_patterns:
                pattern = inst_patterns[inst]
                
                # Get target velocity for this position
                if grid_idx < len(pattern.velocity_curve):
                    target_vel = pattern.velocity_curve[grid_idx]
                else:
                    target_vel = pattern.base_velocity
                
                # Check for accent/ghost
                if grid_idx in pattern.accent_positions:
                    target_vel = min(127, target_vel + pattern.accent_boost)
                elif grid_idx in pattern.ghost_positions:
                    target_vel = max(1, target_vel - pattern.ghost_reduction)
                
                # Apply energy modifier
                target_vel = int(target_vel * groove_map.energy_modifier)
                target_vel = max(1, min(127, target_vel))
                
                # Blend with existing velocity
                blend = self.config.respect_existing_dynamics
                new_velocity = int(
                    note.velocity * blend + 
                    target_vel * (1 - blend) * self.config.velocity_intensity +
                    note.velocity * (1 - self.config.velocity_intensity) * (1 - blend)
                )
                new_velocity = max(1, min(127, new_velocity))
            else:
                # Use template velocity curve
                vel_curve = template.get('velocity_curve', [90]*16)
                if grid_idx < len(vel_curve):
                    target_vel = vel_curve[grid_idx]
                    blend = self.config.respect_existing_dynamics
                    new_velocity = int(
                        note.velocity * blend +
                        target_vel * self.config.velocity_intensity * (1 - blend) +
                        note.velocity * (1 - self.config.velocity_intensity) * (1 - blend)
                    )
                    new_velocity = max(1, min(127, new_velocity))
            
            # Add variation
            if self.config.randomness > 0:
                vel_variation = int(random.gauss(0, self.config.randomness * 8))
                new_velocity = max(1, min(127, new_velocity + vel_variation))
            
            # Check if modified
            if new_onset != note.onset_ticks or new_velocity != note.velocity:
                notes_modified += 1
            
            # Return modified note
            return type(note)(
                pitch=note.pitch,
                velocity=new_velocity,
                onset_ticks=new_onset,
                duration_ticks=note.duration_ticks,
                channel=note.channel,
                track_index=note.track_index,
                onset_beats=note.onset_beats,
                onset_bars=note.onset_bars,
                grid_position=note.grid_position
            )
        
        # Apply modifications
        modify_notes_safe(data, modify_note)
        
        return SectionApplication(
            section_name=section.name,
            start_bar=section.start_bar,
            end_bar=section.end_bar,
            notes_modified=notes_modified,
            groove_map=groove_map
        )


# === High-Level Convenience Functions ===

def auto_apply_groove(
    source: str,
    target_midi: str,
    output_path: str,
    **config_kwargs
) -> AutoApplicationResult:
    """
    Auto-apply groove from source to target MIDI.
    
    Source can be:
    - Audio file (.wav, .mp3, etc.) → analyze feel → match template
    - MIDI file (.mid) → extract groove → transfer
    - Genre name (string like "hiphop") → use built-in template
    
    Args:
        source: Audio file, MIDI file, or genre name
        target_midi: MIDI file to modify
        output_path: Where to save result
        **config_kwargs: Override AutoApplicationConfig settings
    
    Returns:
        AutoApplicationResult with full details
    """
    config = AutoApplicationConfig(**config_kwargs)
    applicator = AutoGrooveApplicator(config)
    
    source_path = Path(source)
    
    # Determine source type
    if source_path.suffix.lower() in ('.wav', '.mp3', '.aiff', '.flac', '.ogg'):
        return applicator.apply_from_audio(source, target_midi, output_path)
    elif source_path.suffix.lower() in ('.mid', '.midi'):
        return applicator.apply_from_midi_reference(source, target_midi, output_path)
    elif source.lower() in GENRE_TEMPLATES:
        return applicator.apply_genre(source, target_midi, output_path)
    else:
        # Assume it's a genre name
        raise ValueError(
            f"Unknown source type: {source}. "
            f"Must be audio file, MIDI file, or genre name "
            f"({', '.join(GENRE_TEMPLATES.keys())})"
        )


def preview_template_match(
    audio_path: str,
    top_n: int = 5
) -> List[Dict[str, Any]]:
    """
    Preview which templates would match an audio file.
    
    Args:
        audio_path: Audio file to analyze
        top_n: Number of matches to return
    
    Returns:
        List of match info dicts
    """
    # Analyze audio
    try:
        from ..audio.analyzer import analyze_audio_feel
        audio_feel = analyze_audio_feel(audio_path)
    except ImportError:
        from ..audio.feel import analyze_audio_feel as legacy_analyze
        audio_feel = legacy_analyze(audio_path)
    
    # Get matches
    matcher = TemplateMatcher()
    profile = matcher.profile_from_audio_feel(audio_feel)
    scores = matcher.rank_templates(profile, top_n)
    
    return [
        {
            "genre": s.genre,
            "score": s.total_score,
            "match_reasons": s.match_reasons,
            "mismatch_reasons": s.mismatch_reasons,
            "components": {
                "tempo": s.tempo_score,
                "energy": s.energy_score,
                "swing": s.swing_score,
                "density": s.density_score,
            }
        }
        for s in scores
    ]


def get_section_grooves(
    genre: str,
    sections: List[str] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Get groove parameters for each section type.
    
    Args:
        genre: Base genre
        sections: List of section names (default: standard set)
    
    Returns:
        Dict mapping section name to groove parameters
    """
    if sections is None:
        sections = ["intro", "verse", "pre_chorus", "chorus", "bridge", "outro"]
    
    matcher = TemplateMatcher()
    
    result = {}
    for section in sections:
        groove_map = matcher.get_section_groove_map(genre, section)
        result[section] = {
            "swing_ratio": groove_map.swing_ratio,
            "energy_modifier": groove_map.energy_modifier,
            "tightness_modifier": groove_map.tightness_modifier,
            "fill_probability": groove_map.fill_probability,
            "instruments": list(groove_map.instrument_velocities.keys()),
            "pocket": groove_map.instrument_pocket,
        }
    
    return result
