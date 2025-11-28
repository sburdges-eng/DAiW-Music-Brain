#!/usr/bin/env python3
"""
Music Brain CLI
Unified command-line interface for groove, structure, audio, and session tools.

Usage:
    music-brain groove extract <file> [--genre=<g>] [--save]
    music-brain groove apply <file> <source> [--out=<o>] [--intensity=<i>]
    music-brain groove humanize <file> [--out=<o>] [--timing=<t>] [--velocity=<v>]
    music-brain groove genres
    music-brain groove templates [--genre=<g>]
    
    music-brain structure analyze <file> [--key=<k>]
    music-brain structure progressions <genre>
    
    music-brain sections <file>
    
    music-brain new-song [--genre=<g>] [--bpm=<b>] [--key=<k>] [--title=<t>] [--out=<o>]
    
    music-brain daw setup <genre> <name> [--bpm=<b>] [--script=<s>]
    music-brain daw tracks <genre>
    
    music-brain info <file>
"""

import argparse
import sys
import os


def cmd_groove_extract(args):
    """Extract groove from MIDI file."""
    from .groove.extractor import GrooveExtractor, template_to_dict
    from .groove.templates import get_storage
    
    print(f"\n🎵 Extracting groove from: {args.file}")
    
    extractor = GrooveExtractor()
    template = extractor.extract(args.file, genre=args.genre)
    
    print(f"\n{'='*60}")
    print(f"BPM: {template.bpm:.1f}")
    print(f"Bars analyzed: {template.bars_analyzed}")
    print(f"Notes analyzed: {template.notes_analyzed}")
    print(f"PPQ: {template.ppq}")
    
    # Swing info
    print(f"\n--- Swing ---")
    swing_desc = "straight" if template.swing < 0.52 else \
                 "subtle" if template.swing < 0.56 else \
                 "noticeable" if template.swing < 0.60 else \
                 "heavy" if template.swing < 0.64 else "triplet"
    print(f"Global: {template.swing:.3f} ({swing_desc})")
    print(f"Consistency: {template.swing_consistency:.3f} {'(consistent)' if template.swing_consistency < 0.08 else '(variable)'}")
    
    if template.per_instrument_swing:
        print(f"\nPer-instrument swing:")
        for inst, data in template.per_instrument_swing.items():
            if data.sample_count >= 8:
                print(f"  {inst:<12} {data.ratio:.3f} (n={data.sample_count}, consistency={data.consistency:.3f})")
    
    # Push/pull
    print(f"\n--- Push/Pull (timing offsets) ---")
    for inst, positions in template.push_pull.items():
        if isinstance(positions, dict):
            # Get average offset
            offsets = [v for v in positions.values() if isinstance(v, (int, float))]
            if offsets:
                avg = sum(offsets) / len(offsets)
                direction = "behind" if avg > 0 else "ahead" if avg < 0 else "on grid"
                print(f"  {inst:<12} avg {avg:+.1f} ticks ({direction})")
        else:
            direction = "behind" if positions > 0 else "ahead" if positions < 0 else "on grid"
            print(f"  {inst:<12} {positions:+d} ticks ({direction})")
    
    # Ghost note analysis
    if template.ghost_density:
        print(f"\n--- Ghost Notes ---")
        for inst, count in template.ghost_density.items():
            print(f"  {inst:<12} {count} ghost notes detected")
    
    # Stagger
    if template.stagger:
        print(f"\n--- Instrument Stagger ---")
        for pair, offset in template.stagger.items():
            inst_a, inst_b = pair if isinstance(pair, tuple) else pair.split(':')
            direction = "behind" if offset > 0 else "ahead of"
            print(f"  {inst_b} is {abs(offset)} ticks {direction} {inst_a}")
    
    # Velocity curves
    if template.velocity_curves:
        print(f"\n--- Velocity Patterns ---")
        for inst, curve in template.velocity_curves.items():
            if curve.accent_ratio > 0.1 or curve.ghost_ratio > 0.1:
                print(f"  {inst:<12} accents:{curve.accent_ratio:.0%} ghosts:{curve.ghost_ratio:.0%} range:{curve.dynamic_range:.1f}")
    
    # Save if requested
    if args.save:
        storage = get_storage()
        genre = args.genre or 'extracted'
        storage.save(genre, template_to_dict(template))
        print(f"\n✓ Saved to template storage under '{genre}'")
    
    print()


def cmd_groove_apply(args):
    """Apply groove to MIDI file."""
    from .groove.applicator import apply_groove
    
    output = args.out or args.file.replace('.mid', '_grooved.mid')
    intensity = float(args.intensity) if args.intensity else 1.0
    
    print(f"\n🎵 Applying groove: {args.source}")
    print(f"Input: {args.file}")
    print(f"Output: {output}")
    print(f"Intensity: {intensity:.0%}")
    
    stats = apply_groove(args.file, output, args.source, intensity=intensity)
    
    print(f"\n{'='*60}")
    print(f"Notes modified: {stats.notes_modified}")
    print(f"Timing shifts: {stats.timing_shifts_applied}")
    print(f"Velocity changes: {stats.velocity_changes_applied}")
    print(f"Swing adjustments: {stats.swing_adjustments}")
    print(f"Ghost notes preserved: {stats.ghost_notes_preserved}")
    
    if stats.scale_factor != 1.0:
        print(f"\n⚠️  PPQ scaling applied: {stats.source_ppq} → {stats.target_ppq} (×{stats.scale_factor:.2f})")
    
    print(f"\n✓ Saved: {output}\n")


def cmd_groove_humanize(args):
    """Apply basic humanization."""
    from .groove.applicator import GrooveApplicator
    
    output = args.out or args.file.replace('.mid', '_humanized.mid')
    timing = int(args.timing) if args.timing else 10
    velocity = int(args.velocity) if args.velocity else 15
    
    print(f"\n🎵 Humanizing: {args.file}")
    print(f"Timing range: ±{timing} ticks")
    print(f"Velocity range: ±{velocity}")
    
    applicator = GrooveApplicator()
    stats = applicator.humanize(args.file, output, timing, velocity)
    
    print(f"\n✓ Saved: {output} ({stats.notes_modified} notes modified)\n")


def cmd_groove_genres(args):
    """List available genre pockets."""
    from .groove.pocket_rules import GENRE_POCKETS
    
    print(f"\n🎵 Available Genre Pockets")
    print("=" * 70)
    
    for genre, pocket in GENRE_POCKETS.items():
        bpm = pocket.get('bpm_range', (0, 0))
        swing = pocket.get('swing', 0.5)
        swing_desc = "straight" if swing < 0.52 else \
                     "subtle" if swing < 0.56 else \
                     "groovy" if swing < 0.60 else \
                     "heavy" if swing < 0.64 else "triplet"
        notes = pocket.get('notes', '')[:50]
        
        print(f"\n{genre}")
        print(f"  BPM: {bpm[0]}-{bpm[1]}")
        print(f"  Swing: {swing:.2f} ({swing_desc})")
        print(f"  {notes}...")
    
    print()


def cmd_groove_templates(args):
    """List saved templates."""
    from .groove.templates import get_storage
    
    storage = get_storage()
    
    if args.genre:
        templates = storage.list_templates(args.genre)
        print(f"\n📁 Templates for '{args.genre}': {len(templates)} saved")
        for t in templates:
            print(f"  • {t}")
    else:
        genres = storage.list_genres()
        print(f"\n📁 Saved Templates by Genre")
        print("=" * 40)
        for genre in genres:
            templates = storage.list_templates(genre)
            print(f"  {genre}: {len(templates)} templates")
    
    print()


def cmd_structure_analyze(args):
    """Analyze chords and progressions."""
    from .utils.midi_io import load_midi
    from .structure.chord import ChordAnalyzer
    from .structure.progression import ProgressionMatcher
    
    print(f"\n🎼 Analyzing structure: {args.file}")
    
    data = load_midi(args.file)
    key = int(args.key) if args.key else 0
    
    analyzer = ChordAnalyzer(ppq=data.ppq)
    chords = analyzer.analyze(data.all_notes)
    
    print(f"\n--- Chords (first 20) ---")
    print(f"{'Bar':<6} {'Beat':<6} {'Chord':<12} {'Roman':<8}")
    print("-" * 35)
    
    for chord in chords[:20]:
        roman = analyzer.to_roman_numeral(chord, key)
        print(f"{chord.bar:<6.1f} {chord.beat:<6.1f} {chord.root_name + chord.chord_type:<12} {roman:<8}")
    
    if len(chords) > 20:
        print(f"... and {len(chords) - 20} more")
    
    # Find progressions
    matcher = ProgressionMatcher()
    matches = matcher.find_matches(chords, key)
    
    if matches:
        print(f"\n--- Progression Matches ---")
        for match in matches[:5]:
            print(f"  {match.name}: {' '.join(match.degrees)} (confidence: {match.confidence:.0%})")
    
    # Find recurring patterns
    patterns = matcher.find_recurring_patterns(chords)
    if patterns:
        print(f"\n--- Recurring Patterns ---")
        for pattern, positions in list(patterns.items())[:5]:
            print(f"  {pattern}: appears at bars {positions[:5]}")
    
    print()


def cmd_structure_progressions(args):
    """Show progressions for a genre."""
    from .structure.progression import ProgressionMatcher, COMMON_PROGRESSIONS
    
    matcher = ProgressionMatcher()
    suggestions = matcher.suggest_progressions(args.genre)
    
    print(f"\n🎼 Common progressions for '{args.genre}':")
    print("=" * 50)
    
    if suggestions:
        for name, data in suggestions.items():
            chords = matcher.degrees_to_chords(data['degrees'])
            print(f"\n  {name}")
            print(f"    Degrees: {' - '.join(data['degrees'])}")
            print(f"    Chords (C): {' - '.join(chords)}")
    else:
        print(f"  No specific progressions for '{args.genre}'")
        print(f"\n  Universal progressions:")
        for name in ['I-V-vi-IV', 'I-vi-IV-V', 'ii-V-I']:
            if name in COMMON_PROGRESSIONS:
                data = COMMON_PROGRESSIONS[name]
                print(f"    {name}: {' - '.join(data['degrees'])}")
    
    print()


def cmd_sections(args):
    """Detect song sections."""
    from .utils.midi_io import load_midi
    from .structure.sections import detect_sections
    
    print(f"\n🎵 Detecting sections: {args.file}")
    
    data = load_midi(args.file)
    sections = detect_sections(data)
    
    print(f"\n{'Section':<15} {'Bars':<12} {'Length':<8} {'Energy':<8} {'Density':<8} {'Conf':<6}")
    print("=" * 65)
    
    for section in sections:
        conf_str = f"{section.confidence:.0%}"
        irregular = " ⚠️" if section.is_irregular else ""
        pickup = " 🎵" if section.is_pickup else ""
        
        print(f"{section.name:<15} {section.start_bar:>3}-{section.end_bar:<6} {section.length_bars:<8} "
              f"{section.energy:<8.2f} {section.density:<8.2f} {conf_str:<6}{irregular}{pickup}")
        
        if section.possible_names and len(section.possible_names) > 1:
            alts = ', '.join(section.possible_names[1:3])
            print(f"{'':15} (also: {alts})")
    
    print()


def cmd_new_song(args):
    """Generate a new song."""
    from .session.generator import generate_song
    
    key_map = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4,
               'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9,
               'A#': 10, 'Bb': 10, 'B': 11}
    
    key = key_map.get(args.key, 0) if args.key else 0
    bpm = int(args.bpm) if args.bpm else None
    
    print(f"\n🎵 Generating new {args.genre} song...")
    
    structure, midi_path = generate_song(
        genre=args.genre,
        output_path=args.out,
        key=key,
        bpm=bpm,
        title=args.title,
        humanize=True
    )
    
    key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    print(f"\n{'='*60}")
    print(f"Title: {structure.title}")
    print(f"Genre: {structure.genre}")
    print(f"BPM: {structure.bpm}")
    print(f"Key: {key_names[structure.key]}")
    print(f"{'='*60}")
    
    print(f"\nStructure ({structure.total_bars} bars):")
    bar_pos = 0
    for section in structure.sections:
        energy_bar = '█' * int(section.energy * 10)
        print(f"  Bar {bar_pos:3d}: {section.name:<12} ({section.bars:2d} bars) {energy_bar}")
        bar_pos += section.bars
    
    print(f"\n✓ MIDI saved: {midi_path}\n")


def cmd_daw_setup(args):
    """Create Logic Pro session setup."""
    from .daw.logic_pro import create_logic_session
    
    bpm = int(args.bpm) if args.bpm else 120
    
    session = create_logic_session(
        genre=args.genre,
        name=args.name,
        bpm=bpm,
        output_script=args.script
    )
    
    print(f"\n🎛️  Logic Pro Session: {session.name}")
    print(f"Genre: {args.genre}")
    print(f"BPM: {session.bpm}")
    print("=" * 50)
    
    print(f"\nTracks ({len(session.tracks)}):")
    for track in session.tracks:
        inst = f" → {track.instrument}" if track.instrument else ""
        print(f"  • {track.name} [{track.track_type}]{inst}")
    
    if args.script:
        print(f"\n✓ AppleScript saved: {args.script}")
        print(f"  Run with: osascript {args.script}")
    
    print()


def cmd_daw_tracks(args):
    """Show default tracks for genre."""
    from .daw.logic_pro import get_genre_tracks, GENRE_TRACK_TEMPLATES
    
    if args.genre == 'list':
        print("\n🎛️  Available genre templates:")
        for genre in GENRE_TRACK_TEMPLATES.keys():
            print(f"  • {genre}")
        print()
        return
    
    tracks = get_genre_tracks(args.genre)
    
    print(f"\n🎛️  Default tracks for '{args.genre}':")
    print("-" * 50)
    
    for track in tracks:
        inst = f" → {track.instrument}" if track.instrument else ""
        print(f"  {track.name:<20} [{track.track_type}]{inst}")
    
    print()


def cmd_drums(args):
    """Analyze drum technique."""
    from .utils.midi_io import load_midi
    from .groove.drum_analysis import DrumAnalyzer
    
    print(f"\n🥁 Drum Technique Analysis: {args.file}")
    print("=" * 60)
    
    data = load_midi(args.file)
    analyzer = DrumAnalyzer(ppq=data.ppq, bpm=data.bpm)
    profile = analyzer.analyze(data.all_notes, bpm=data.bpm)
    
    # Snare bounce signature
    snare = profile.snare
    print(f"\n--- Snare Technique ---")
    print(f"Primary style: {snare.primary_technique}")
    print(f"Flams detected: {snare.flam_count}")
    print(f"Drag rudiments: {snare.drag_count}")
    print(f"Buzz roll regions: {len(snare.buzz_roll_regions)}")
    print(f"Total bounces: {snare.total_bounces}")
    
    if snare.avg_flam_gap_ms > 0:
        print(f"Average flam gap: {snare.avg_flam_gap_ms:.1f}ms")
        print(f"Flam velocity ratio: {snare.avg_flam_velocity_ratio:.2f}")
    
    # Hi-hat alternation
    hihat = profile.hihat
    print(f"\n--- Hi-Hat Alternation ---")
    if hihat.is_alternating:
        print(f"Alternating pattern: YES (confidence: {hihat.confidence:.0%})")
        print(f"Dominant hand: {hihat.dominant_hand}")
        print(f"Downbeat avg velocity: {hihat.downbeat_avg_velocity:.0f}")
        print(f"Upbeat avg velocity: {hihat.upbeat_avg_velocity:.0f}")
        print(f"Velocity ratio: {hihat.velocity_alternation_ratio:.2f}")
        print(f"Pattern consistency: {hihat.alternation_consistency:.0%}")
        if hihat.accent_positions:
            print(f"Accent positions: {hihat.accent_positions}")
    else:
        print(f"Alternating pattern: NO or inconsistent")
        print(f"Confidence: {hihat.confidence:.0%}")
    
    # Overall
    print(f"\n--- Overall Profile ---")
    print(f"Tightness: {profile.tightness:.0%}")
    print(f"Dynamics range: {profile.dynamics_range:.0%}")
    print(f"Ghost note density: {profile.ghost_note_density:.0%}")
    
    print()


def cmd_orchestral(args):
    """Validate orchestral template."""
    from .utils.midi_io import load_midi
    from .utils.orchestral import OrchestralAnalyzer, is_orchestral_template
    
    print(f"\n🎻 Orchestral Template Analysis: {args.file}")
    print("=" * 60)
    
    data = load_midi(args.file, normalize_ppq=False)  # Keep original
    
    # Quick check
    if not is_orchestral_template(data):
        print("\n⚠️  This doesn't appear to be an orchestral template.")
        print("   (Fewer than 3 orchestral instrument names detected)")
    
    analyzer = OrchestralAnalyzer()
    result = analyzer.validate(data)
    
    print(f"\n--- Summary ---")
    print(f"Total tracks: {result.total_tracks}")
    print(f"Unique instruments: {result.unique_instruments}")
    
    print(f"\n--- Features Detected ---")
    features = [
        ("Keyswitches", result.has_keyswitches, result.total_keyswitch_notes),
        ("Expression automation", result.has_expression, result.total_cc_events),
        ("Tempo changes", result.has_tempo_changes, len(data.tempo_map)),
        ("Divisi sections", result.has_divisi, None),
    ]
    
    for name, detected, count in features:
        status = "✓" if detected else "✗"
        count_str = f" ({count} events)" if count else ""
        print(f"  {status} {name}{count_str}")
    
    # Articulation tracks
    if result.articulation_tracks:
        print(f"\n--- Articulation Tracks ({len(result.articulation_tracks)}) ---")
        for art in result.articulation_tracks[:10]:
            ks = f" [KS: {art.keyswitch_note}]" if art.keyswitch_note else ""
            print(f"  {art.instrument}: {art.articulation} ({art.note_count} notes){ks}")
        if len(result.articulation_tracks) > 10:
            print(f"  ... and {len(result.articulation_tracks) - 10} more")
    
    # Warnings
    if result.warnings:
        print(f"\n--- Warnings ({len(result.warnings)}) ---")
        for warn in result.warnings[:10]:
            print(f"  ⚠️  {warn}")
    
    # Errors
    if result.errors:
        print(f"\n--- Errors ({len(result.errors)}) ---")
        for err in result.errors:
            print(f"  ❌ {err}")
    
    print()


def cmd_audio(args):
    """Analyze audio file feel."""
    try:
        from .audio.analyzer import analyze_audio_feel
    except ImportError as e:
        print(f"❌ Audio analysis requires librosa: {e}")
        print("   Install with: pip install librosa")
        return
    
    print(f"\n🎵 Audio Feel Analysis: {args.file}")
    print("=" * 60)
    
    try:
        feel = analyze_audio_feel(args.file)
    except FileNotFoundError:
        print(f"❌ File not found: {args.file}")
        return
    except ValueError as e:
        print(f"❌ {e}")
        return
    
    print(f"\n--- Overview ---")
    print(f"Duration: {feel.duration_seconds:.1f}s")
    print(f"Sample rate: {feel.sample_rate} Hz")
    print(f"Feel: {feel.feel_description}")
    
    print(f"\n--- Rhythm ---")
    print(f"Tempo: {feel.rhythm.tempo_bpm:.1f} BPM (confidence: {feel.rhythm.tempo_confidence:.0%})")
    print(f"Beat regularity: {feel.rhythm.beat_regularity:.0%}")
    print(f"Beats detected: {len(feel.rhythm.beat_times)}")
    
    print(f"\n--- Dynamics ---")
    print(f"Dynamic range: {feel.dynamics.dynamic_range_db:.1f} dB")
    print(f"Compression estimate: {feel.dynamics.compression_estimate:.0%}")
    print(f"Peak/Average ratio: {feel.dynamics.peak_to_average:.1f}")
    
    print(f"\n--- Timbre ---")
    print(f"Brightness (centroid): {feel.spectral.centroid_mean:.0f} Hz")
    print(f"Bandwidth: {feel.spectral.bandwidth_mean:.0f} Hz")
    print(f"Noisiness (flatness): {feel.spectral.flatness_mean:.2f}")
    
    print(f"\n--- Classification ---")
    print(f"Energy: {feel.energy_level}")
    print(f"Brightness: {feel.brightness_level}")
    print(f"Texture: {feel.texture}")
    
    print()


def cmd_progression(args):
    """Analyze chord progression."""
    from .utils.midi_io import load_midi
    from .structure.chord import ChordAnalyzer
    from .structure.progression_analysis import ProgressionAnalyzer
    
    print(f"\n🎹 Progression Analysis: {args.file}")
    print("=" * 60)
    
    data = load_midi(args.file)
    
    # Detect chords
    chord_analyzer = ChordAnalyzer(ppq=data.ppq)
    chords = chord_analyzer.detect_chords(data.all_notes)
    
    if not chords:
        print("No chords detected.")
        return
    
    # Get key (from MIDI or estimate)
    key_name = args.key if hasattr(args, 'key') and args.key else "C major"
    
    # Analyze progression
    prog_analyzer = ProgressionAnalyzer()
    result = prog_analyzer.analyze(chords, key_name)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    print(f"\n--- Key ---")
    print(f"Root: {result['key']['root']}")
    print(f"Mode: {result['key']['mode']}")
    
    print(f"\n--- Chord Degrees ---")
    degrees = result['degrees']
    deg_display = []
    for d in degrees[:16]:
        if d.is_chromatic:
            deg_display.append(d.chromatic_name)
        else:
            deg_display.append(str(d.degree))
    print(" ".join(deg_display))
    if len(degrees) > 16:
        print(f"  ... and {len(degrees) - 16} more")
    
    print(f"\n--- Pattern Matches ---")
    matches = result['matches']
    if matches:
        for m in matches[:5]:
            pattern_str = "-".join(str(p) for p in m.pattern)
            print(f"  {m.family}: {pattern_str} ({m.confidence:.0%})")
    else:
        print("  No common patterns detected")
    
    print(f"\n--- Summary ---")
    print(f"Progression: {result['summary']['progression']}")
    print(f"Chromatic chords: {result['summary']['chromatic_count']}")
    
    print()


def cmd_templates(args):
    """Manage groove templates."""
    from .groove.template_storage import get_store
    from .groove.genre_templates import list_genres as list_builtin
    
    store = get_store()
    
    if args.action == "list":
        print("\n📂 Available Templates")
        print("=" * 50)
        
        builtin = list_builtin()
        saved = [g for g in store.list_genres() if g not in builtin]
        
        print(f"\n--- Built-in ({len(builtin)}) ---")
        for g in builtin:
            print(f"  {g}")
        
        if saved:
            print(f"\n--- Saved ({len(saved)}) ---")
            for g in saved:
                info = store.get_info(g)
                print(f"  {g} (v{info['current_version']}, {info['saved_versions']} versions)")
        
        print()
    
    elif args.action == "info":
        if not hasattr(args, 'genre') or not args.genre:
            print("❌ Specify genre with --genre")
            return
        
        info = store.get_info(args.genre)
        
        print(f"\n📋 Template Info: {args.genre}")
        print("=" * 50)
        print(f"Built-in: {'Yes' if info['has_builtin'] else 'No'}")
        print(f"Saved versions: {info['saved_versions']}")
        print(f"Current version: {info['current_version']}")
        
        if info['versions']:
            print(f"\nRecent versions:")
            for v in info['versions']:
                print(f"  v{v['version']:03d} - {v['created_at'][:19]}")
        
        print()
    
    elif args.action == "rollback":
        if not hasattr(args, 'genre') or not args.genre:
            print("❌ Specify genre with --genre")
            return
        if not hasattr(args, 'version') or not args.version:
            print("❌ Specify version with --version")
            return
        
        path = store.rollback(args.genre, args.version)
        print(f"✓ Rolled back {args.genre} to v{args.version}")


def cmd_auto_apply(args):
    """Auto-apply groove from audio/MIDI/genre to target MIDI."""
    from .groove.auto_apply import auto_apply_groove, AutoApplicationConfig
    
    print(f"\n🎯 Auto-Apply Groove")
    print("=" * 60)
    print(f"Source: {args.source}")
    print(f"Target: {args.target}")
    print(f"Output: {args.output}")
    
    # Build config
    config = {}
    if hasattr(args, 'intensity') and args.intensity:
        config['timing_intensity'] = args.intensity
        config['velocity_intensity'] = args.intensity
    if hasattr(args, 'no_sections') and args.no_sections:
        config['section_aware'] = False
    if hasattr(args, 'genre') and args.genre:
        config['genre_override'] = args.genre
    
    try:
        result = auto_apply_groove(
            args.source,
            args.target,
            args.output,
            **config
        )
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return
    
    print(f"\n--- Template Selection ---")
    print(f"Selected: {result.selected_genre} ({result.match_score:.0f}/100)")
    for reason in result.match_reasons[:3]:
        print(f"  ✓ {reason}")
    for reason in result.mismatch_reasons[:2]:
        print(f"  ⚠ {reason}")
    
    if result.alternative_genres:
        alts = ", ".join(f"{g} ({s:.0f})" for g, s in result.alternative_genres[:3])
        print(f"Alternatives: {alts}")
    
    print(f"\n--- Application ---")
    print(f"Notes modified: {result.total_notes_modified}")
    
    if result.sections_processed:
        print(f"\n--- Sections ({len(result.sections_processed)}) ---")
        for sec in result.sections_processed:
            print(f"  {sec.section_name}: bars {sec.start_bar}-{sec.end_bar} ({sec.notes_modified} notes)")
    
    if result.warnings:
        print(f"\n⚠️  Warnings:")
        for w in result.warnings:
            print(f"  {w}")
    
    print(f"\n✓ Saved to: {result.output_midi}")
    print()


def cmd_match_preview(args):
    """Preview which templates match an audio file."""
    from .groove.auto_apply import preview_template_match
    
    print(f"\n🔍 Template Match Preview: {args.file}")
    print("=" * 60)
    
    try:
        matches = preview_template_match(args.file, top_n=args.top if hasattr(args, 'top') else 5)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return
    
    print(f"\n{'Rank':<5} {'Genre':<12} {'Score':<8} {'Reasons'}")
    print("-" * 60)
    
    for i, m in enumerate(matches, 1):
        reasons = ", ".join(m['match_reasons'][:2]) if m['match_reasons'] else "—"
        print(f"{i:<5} {m['genre']:<12} {m['score']:<8.0f} {reasons[:35]}")
    
    # Show best match details
    if matches:
        best = matches[0]
        print(f"\n--- Best Match: {best['genre']} ---")
        print(f"Score breakdown:")
        for comp, score in best['components'].items():
            bar = "█" * int(score / 5) + "░" * (5 - int(score / 5))
            print(f"  {comp:<10} {bar} {score:.0f}")
        
        if best['mismatch_reasons']:
            print(f"\nPotential issues:")
            for r in best['mismatch_reasons']:
                print(f"  ⚠ {r}")
    
    print()


def cmd_section_grooves(args):
    """Show groove parameters for each section type."""
    from .groove.auto_apply import get_section_grooves
    
    genre = args.genre if hasattr(args, 'genre') and args.genre else "hiphop"
    
    print(f"\n📊 Section Groove Map: {genre}")
    print("=" * 60)
    
    grooves = get_section_grooves(genre)
    
    print(f"\n{'Section':<12} {'Swing':<8} {'Energy':<8} {'Tight':<8} {'Fill%':<8}")
    print("-" * 60)
    
    for section, params in grooves.items():
        swing = f"{params['swing_ratio']:.2f}"
        energy = f"×{params['energy_modifier']:.2f}"
        tight = f"×{params['tightness_modifier']:.2f}"
        fill = f"{params['fill_probability']*100:.0f}%"
        print(f"{section:<12} {swing:<8} {energy:<8} {tight:<8} {fill:<8}")
    
    # Show instrument pocket for first section
    first_section = list(grooves.keys())[0]
    pocket = grooves[first_section]['pocket']
    print(f"\n--- Instrument Pocket (ticks from grid) ---")
    for inst, offset in pocket.items():
        direction = "behind" if offset > 0 else "ahead" if offset < 0 else "on grid"
        print(f"  {inst}: {offset:+d} ({direction})")
    
    print()


def cmd_validate(args):
    """Validate MIDI file or template."""
    from .utils.midi_io import load_midi
    from .groove.genre_templates import validate_template
    import json
    
    if args.file.endswith('.json'):
        # Validate template
        print(f"\n🔍 Validating Template: {args.file}")
        print("=" * 50)
        
        with open(args.file) as f:
            data = json.load(f)
        
        template = data.get('template', data)
        issues = validate_template(template)
        
        if issues:
            print(f"\n❌ {len(issues)} issues found:")
            for issue in issues:
                print(f"  • {issue}")
        else:
            print("\n✓ Template is valid")
    
    else:
        # Validate MIDI
        print(f"\n🔍 Validating MIDI: {args.file}")
        print("=" * 50)
        
        try:
            data = load_midi(args.file, normalize_ppq=False)
            print(f"\n✓ Valid MIDI file")
            print(f"  PPQ: {data.ppq}")
            print(f"  Tracks: {len(data.tracks)}")
            print(f"  Notes: {len(data.all_notes)}")
            print(f"  BPM: {data.bpm:.1f}")
        except Exception as e:
            print(f"\n❌ Invalid MIDI: {e}")
    
    print()


def cmd_info(args):
    """Show MIDI file info."""
    from .utils.midi_io import load_midi
    from .utils.instruments import classify_note, is_drum_channel, get_drum_category
    from collections import Counter
    
    print(f"\n📄 MIDI File Info: {args.file}")
    print("=" * 60)
    
    data = load_midi(args.file, normalize_ppq=False)  # Show original PPQ
    
    print(f"PPQ: {data.ppq}")
    print(f"BPM: {data.bpm:.1f}")
    print(f"Time Signature: {data.time_signature[0]}/{data.time_signature[1]}")
    print(f"Tracks: {len(data.tracks)}")
    
    total_notes = len(data.all_notes)
    print(f"Total Notes: {total_notes}")
    
    if total_notes > 0:
        max_tick = max(n.onset_ticks for n in data.all_notes)
        bars = int(max_tick / data.ticks_per_bar) + 1
        print(f"Duration: {bars} bars ({max_tick / data.ppq:.1f} beats)")
        
        # Note distribution
        instruments = Counter()
        for note in data.all_notes:
            if is_drum_channel(note.channel):
                inst = get_drum_category(note.pitch)
            else:
                inst = classify_note(note.channel, note.pitch)
            instruments[inst] += 1
        
        print(f"\nInstrument Distribution:")
        for inst, count in instruments.most_common(10):
            pct = count / total_notes * 100
            bar = '█' * int(pct / 5)
            print(f"  {inst:<12} {count:>5} ({pct:>5.1f}%) {bar}")
    
    if data.tempo_map and len(data.tempo_map) > 1:
        print(f"\nTempo Changes: {len(data.tempo_map)}")
        for tick, tempo in data.tempo_map[:5]:
            import mido
            bpm = mido.tempo2bpm(tempo)
            print(f"  Tick {tick}: {bpm:.1f} BPM")
    
    print(f"\nTracks:")
    for track in data.tracks:
        drum_marker = " [DRUMS]" if track.is_drum else ""
        print(f"  [{track.index}] {track.name}: {len(track.notes)} notes{drum_marker}")
    
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Music Brain - Groove, Structure, and Generation Tools',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Groove commands
    groove_parser = subparsers.add_parser('groove', help='Groove extraction and application')
    groove_sub = groove_parser.add_subparsers(dest='groove_cmd')
    
    # groove extract
    extract_p = groove_sub.add_parser('extract', help='Extract groove from MIDI')
    extract_p.add_argument('file', help='MIDI file')
    extract_p.add_argument('--genre', '-g', help='Genre hint')
    extract_p.add_argument('--save', '-s', action='store_true', help='Save to template storage')
    
    # groove apply
    apply_p = groove_sub.add_parser('apply', help='Apply groove to MIDI')
    apply_p.add_argument('file', help='MIDI file')
    apply_p.add_argument('source', help='Genre name or template path')
    apply_p.add_argument('--out', '-o', help='Output file')
    apply_p.add_argument('--intensity', '-i', default='1.0', help='Intensity 0-1')
    
    # groove humanize
    human_p = groove_sub.add_parser('humanize', help='Basic humanization')
    human_p.add_argument('file', help='MIDI file')
    human_p.add_argument('--out', '-o', help='Output file')
    human_p.add_argument('--timing', '-t', default='10', help='Timing range')
    human_p.add_argument('--velocity', '-v', default='15', help='Velocity range')
    
    # groove genres
    groove_sub.add_parser('genres', help='List genre pockets')
    
    # groove templates
    templates_p = groove_sub.add_parser('templates', help='List saved templates')
    templates_p.add_argument('--genre', '-g', help='Filter by genre')
    
    # Structure commands
    struct_parser = subparsers.add_parser('structure', help='Structural analysis')
    struct_sub = struct_parser.add_subparsers(dest='struct_cmd')
    
    # structure analyze
    analyze_p = struct_sub.add_parser('analyze', help='Analyze chords/progressions')
    analyze_p.add_argument('file', help='MIDI file')
    analyze_p.add_argument('--key', '-k', default='0', help='Key root (0=C)')
    
    # structure progressions
    prog_p = struct_sub.add_parser('progressions', help='Show genre progressions')
    prog_p.add_argument('genre', help='Genre name')
    
    # Sections command
    sections_p = subparsers.add_parser('sections', help='Detect song sections')
    sections_p.add_argument('file', help='MIDI file')
    
    # Drums command
    drums_p = subparsers.add_parser('drums', help='Analyze drum technique')
    drums_p.add_argument('file', help='MIDI file')
    
    # Orchestral command
    orch_p = subparsers.add_parser('orchestral', help='Validate orchestral template')
    orch_p.add_argument('file', help='MIDI file')
    
    # Audio command
    audio_p = subparsers.add_parser('audio', help='Analyze audio file feel')
    audio_p.add_argument('file', help='Audio file (wav, mp3, etc.)')
    
    # Progression command
    prog_p = subparsers.add_parser('progression', help='Analyze chord progression')
    prog_p.add_argument('file', help='MIDI file')
    prog_p.add_argument('--key', '-k', default='C major', help='Key (e.g., "C major", "G minor")')
    
    # Templates command
    tmpl_p = subparsers.add_parser('templates', help='Manage groove templates')
    tmpl_p.add_argument('action', choices=['list', 'info', 'rollback'], help='Action')
    tmpl_p.add_argument('--genre', '-g', help='Genre name')
    tmpl_p.add_argument('--version', '-v', type=int, help='Version number')
    
    # Validate command
    val_p = subparsers.add_parser('validate', help='Validate MIDI or template')
    val_p.add_argument('file', help='File to validate')
    
    # Auto-apply command (THE BIG ONE)
    auto_p = subparsers.add_parser('auto', help='Auto-apply groove from audio/MIDI/genre')
    auto_p.add_argument('source', help='Source: audio file, MIDI file, or genre name')
    auto_p.add_argument('target', help='Target MIDI file to modify')
    auto_p.add_argument('output', help='Output MIDI path')
    auto_p.add_argument('--intensity', '-i', type=float, default=0.7, help='Application intensity (0-1)')
    auto_p.add_argument('--genre', '-g', help='Force specific genre (override auto-selection)')
    auto_p.add_argument('--no-sections', action='store_true', help='Disable section-aware processing')
    
    # Match preview command
    match_p = subparsers.add_parser('match', help='Preview template matches for audio')
    match_p.add_argument('file', help='Audio file to analyze')
    match_p.add_argument('--top', '-n', type=int, default=5, help='Number of matches to show')
    
    # Section grooves command
    secgroove_p = subparsers.add_parser('section-grooves', help='Show section groove parameters')
    secgroove_p.add_argument('--genre', '-g', default='hiphop', help='Genre to show')
    
    # New-song command
    newsong_p = subparsers.add_parser('new-song', help='Generate a new song')
    newsong_p.add_argument('--genre', '-g', default='pop', help='Genre')
    newsong_p.add_argument('--bpm', '-b', help='Tempo')
    newsong_p.add_argument('--key', '-k', default='C', help='Key')
    newsong_p.add_argument('--title', '-t', help='Song title')
    newsong_p.add_argument('--out', '-o', help='Output MIDI path')
    
    # DAW commands
    daw_parser = subparsers.add_parser('daw', help='DAW session automation')
    daw_sub = daw_parser.add_subparsers(dest='daw_cmd')
    
    daw_setup_p = daw_sub.add_parser('setup', help='Create Logic Pro session')
    daw_setup_p.add_argument('genre', help='Genre for track template')
    daw_setup_p.add_argument('name', help='Project name')
    daw_setup_p.add_argument('--bpm', '-b', help='Tempo')
    daw_setup_p.add_argument('--script', '-s', help='Save AppleScript to file')
    
    daw_tracks_p = daw_sub.add_parser('tracks', help='Show genre track templates')
    daw_tracks_p.add_argument('genre', help='Genre name or "list"')
    
    # Info command
    info_p = subparsers.add_parser('info', help='Show MIDI file info')
    info_p.add_argument('file', help='MIDI file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Route commands
    if args.command == 'groove':
        if args.groove_cmd == 'extract':
            cmd_groove_extract(args)
        elif args.groove_cmd == 'apply':
            cmd_groove_apply(args)
        elif args.groove_cmd == 'humanize':
            cmd_groove_humanize(args)
        elif args.groove_cmd == 'genres':
            cmd_groove_genres(args)
        elif args.groove_cmd == 'templates':
            cmd_groove_templates(args)
        else:
            groove_parser.print_help()
    
    elif args.command == 'structure':
        if args.struct_cmd == 'analyze':
            cmd_structure_analyze(args)
        elif args.struct_cmd == 'progressions':
            cmd_structure_progressions(args)
        else:
            struct_parser.print_help()
    
    elif args.command == 'sections':
        cmd_sections(args)
    
    elif args.command == 'drums':
        cmd_drums(args)
    
    elif args.command == 'orchestral':
        cmd_orchestral(args)
    
    elif args.command == 'audio':
        cmd_audio(args)
    
    elif args.command == 'progression':
        cmd_progression(args)
    
    elif args.command == 'templates':
        cmd_templates(args)
    
    elif args.command == 'validate':
        cmd_validate(args)
    
    elif args.command == 'auto':
        cmd_auto_apply(args)
    
    elif args.command == 'match':
        cmd_match_preview(args)
    
    elif args.command == 'section-grooves':
        cmd_section_grooves(args)
    
    elif args.command == 'new-song':
        cmd_new_song(args)
    
    elif args.command == 'daw':
        if args.daw_cmd == 'setup':
            cmd_daw_setup(args)
        elif args.daw_cmd == 'tracks':
            cmd_daw_tracks(args)
        else:
            daw_parser.print_help()
    
    elif args.command == 'info':
        cmd_info(args)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
