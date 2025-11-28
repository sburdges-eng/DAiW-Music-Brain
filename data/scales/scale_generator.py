#!/usr/bin/env python3
"""
Scale Generator Utility
=======================
Generates notes for any scale in any key from the scale_emotional_map.json database.

Usage:
    CLI:
        python scale_generator.py Dorian C
        python scale_generator.py "Harmonic Minor" F#
        python scale_generator.py --list                    # List all scale types
        python scale_generator.py --list --category "Blues" # List scales in category
        python scale_generator.py --search "exotic"         # Search by keyword
        python scale_generator.py --all C                   # All scales in key of C
        python scale_generator.py --export C --format csv   # Export all scales in C to CSV
    
    Programmatic:
        from scale_generator import ScaleGenerator
        sg = ScaleGenerator()
        notes = sg.get_notes("Dorian", "C")
        scale_data = sg.get_scale("Dorian", "C")  # Full data with notes
"""

import json
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Any

# Note names for sharp and flat representations
NOTES_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTES_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

# Enharmonic equivalents
ENHARMONIC = {
    'C#': 'Db', 'Db': 'C#',
    'D#': 'Eb', 'Eb': 'D#',
    'F#': 'Gb', 'Gb': 'F#',
    'G#': 'Ab', 'Ab': 'G#',
    'A#': 'Bb', 'Bb': 'A#',
    'E#': 'F', 'Fb': 'E',
    'B#': 'C', 'Cb': 'B'
}

# Keys that conventionally use flats
FLAT_KEYS = ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb']
SHARP_KEYS = ['G', 'D', 'A', 'E', 'B', 'F#', 'C#']


class ScaleGenerator:
    """Generate scale notes for any root from the scale emotional map database."""
    
    def __init__(self, json_path: Optional[str] = None):
        """
        Initialize the scale generator.
        
        Args:
            json_path: Path to scale_emotional_map.json. If None, looks in same directory.
        """
        if json_path is None:
            # Look in same directory as this script
            json_path = Path(__file__).parent / "scale_emotional_map.json"
        
        self.json_path = Path(json_path)
        self._load_data()
    
    def _load_data(self):
        """Load the scale database from JSON."""
        if not self.json_path.exists():
            raise FileNotFoundError(f"Scale database not found: {self.json_path}")
        
        with open(self.json_path, 'r') as f:
            data = json.load(f)
        
        self.metadata = data.get('metadata', {})
        self.scales = {s['scale_type']: s for s in data.get('scales', [])}
    
    def _normalize_root(self, root: str) -> str:
        """Normalize root note to standard format."""
        root = root.strip().capitalize()
        if len(root) > 1:
            root = root[0].upper() + root[1].lower()
        return root
    
    def _get_root_index(self, root: str) -> int:
        """Get the semitone index (0-11) for a root note."""
        root = self._normalize_root(root)
        
        # Check sharps first
        if root in NOTES_SHARP:
            return NOTES_SHARP.index(root)
        
        # Check flats
        if root in NOTES_FLAT:
            return NOTES_FLAT.index(root)
        
        # Check enharmonic
        if root in ENHARMONIC:
            equiv = ENHARMONIC[root]
            if equiv in NOTES_SHARP:
                return NOTES_SHARP.index(equiv)
            if equiv in NOTES_FLAT:
                return NOTES_FLAT.index(equiv)
        
        raise ValueError(f"Invalid root note: {root}")
    
    def _use_flats(self, root: str) -> bool:
        """Determine whether to use flats or sharps for a given root."""
        root = self._normalize_root(root)
        
        # Convert enharmonic if needed
        if root in ENHARMONIC and root not in NOTES_SHARP and root not in FLAT_KEYS:
            root = ENHARMONIC.get(root, root)
        
        return root in FLAT_KEYS or 'b' in root
    
    def _interval_to_note_name(self, interval_name: str, root: str, semitones: int) -> str:
        """
        Convert interval + root + semitones to proper note name.
        Attempts to use correct enharmonic spelling based on interval.
        """
        use_flats = self._use_flats(root)
        root_idx = self._get_root_index(root)
        note_idx = (root_idx + semitones) % 12
        
        # Get base note name
        if use_flats:
            note = NOTES_FLAT[note_idx]
        else:
            note = NOTES_SHARP[note_idx]
        
        return note
    
    def get_notes(self, scale_type: str, root: str) -> List[str]:
        """
        Get the notes of a scale in a specific key.
        
        Args:
            scale_type: Name of the scale (e.g., "Dorian", "Harmonic Minor")
            root: Root note (e.g., "C", "F#", "Bb")
        
        Returns:
            List of note names
        
        Example:
            >>> sg = ScaleGenerator()
            >>> sg.get_notes("Dorian", "C")
            ['C', 'D', 'Eb', 'F', 'G', 'A', 'Bb']
        """
        if scale_type not in self.scales:
            # Try case-insensitive exact match
            matches = [s for s in self.scales if s.lower() == scale_type.lower()]
            if not matches:
                # Try partial match (scale name contains or starts with input)
                matches = [s for s in self.scales if scale_type.lower() in s.lower()]
            if not matches:
                # Try matching just the first word
                matches = [s for s in self.scales if s.lower().startswith(scale_type.lower())]
            if matches:
                if len(matches) == 1:
                    scale_type = matches[0]
                else:
                    # Return first match but could be ambiguous
                    scale_type = matches[0]
            else:
                raise ValueError(f"Unknown scale type: {scale_type}. Use --list to see available scales.")
        
        scale = self.scales[scale_type]
        intervals = scale['intervals_semitones']
        interval_names = scale.get('intervals_names', [])
        
        root = self._normalize_root(root)
        root_idx = self._get_root_index(root)
        use_flats = self._use_flats(root)
        
        notes = []
        for i, semitone in enumerate(intervals):
            note_idx = (root_idx + semitone) % 12
            if use_flats:
                notes.append(NOTES_FLAT[note_idx])
            else:
                notes.append(NOTES_SHARP[note_idx])
        
        return notes
    
    def get_scale(self, scale_type: str, root: str) -> Dict[str, Any]:
        """
        Get full scale data with notes for a specific key.
        
        Args:
            scale_type: Name of the scale
            root: Root note
        
        Returns:
            Dictionary with all scale data plus generated notes
        """
        if scale_type not in self.scales:
            # Try case-insensitive exact match
            matches = [s for s in self.scales if s.lower() == scale_type.lower()]
            if not matches:
                # Try partial match
                matches = [s for s in self.scales if scale_type.lower() in s.lower()]
            if not matches:
                # Try matching just the first word
                matches = [s for s in self.scales if s.lower().startswith(scale_type.lower())]
            if matches:
                scale_type = matches[0]
            else:
                raise ValueError(f"Unknown scale type: {scale_type}")
        
        scale = self.scales[scale_type].copy()
        scale['root'] = self._normalize_root(root)
        scale['notes'] = self.get_notes(scale_type, root)
        
        return scale
    
    def list_scales(self, category: Optional[str] = None) -> List[str]:
        """
        List all available scale types.
        
        Args:
            category: Optional category filter
        
        Returns:
            List of scale type names
        """
        if category:
            return [
                name for name, data in self.scales.items()
                if data.get('category', '').lower() == category.lower()
            ]
        return list(self.scales.keys())
    
    def list_categories(self) -> List[str]:
        """Get all unique categories."""
        return list(set(s.get('category', 'Uncategorized') for s in self.scales.values()))
    
    def search(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Search scales by keyword in name, category, emotional quality, or genre.
        
        Args:
            keyword: Search term
        
        Returns:
            List of matching scale data
        """
        keyword = keyword.lower()
        results = []
        
        for name, data in self.scales.items():
            searchable = [
                name.lower(),
                data.get('category', '').lower(),
                ' '.join(data.get('emotional_quality', [])).lower(),
                ' '.join(data.get('genre_associations', [])).lower()
            ]
            
            if any(keyword in text for text in searchable):
                results.append(data)
        
        return results
    
    def get_all_scales_in_key(self, root: str) -> List[Dict[str, Any]]:
        """Get all scales transposed to a specific key."""
        return [self.get_scale(name, root) for name in self.scales]
    
    def export_csv(self, root: str, output_path: Optional[str] = None) -> str:
        """
        Export all scales in a key to CSV format.
        
        Args:
            root: Root note
            output_path: Optional file path to save CSV
        
        Returns:
            CSV string
        """
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Scale Type', 'Category', 'Root', 'Notes', 
            'Intervals (Semitones)', 'Intervals (Names)',
            'Emotional Quality', 'Genre Associations'
        ])
        
        for scale_type in self.scales:
            scale = self.get_scale(scale_type, root)
            writer.writerow([
                scale['scale_type'],
                scale.get('category', ''),
                scale['root'],
                ' - '.join(scale['notes']),
                ', '.join(map(str, scale['intervals_semitones'])),
                ', '.join(scale.get('intervals_names', [])),
                ', '.join(scale.get('emotional_quality', [])),
                ', '.join(scale.get('genre_associations', []))
            ])
        
        csv_str = output.getvalue()
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(csv_str)
        
        return csv_str
    
    def get_scales_by_emotion(self, emotion: str) -> List[Dict[str, Any]]:
        """Find scales that match an emotional quality."""
        emotion = emotion.lower()
        return [
            data for data in self.scales.values()
            if any(emotion in eq.lower() for eq in data.get('emotional_quality', []))
        ]
    
    def get_scales_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """Find scales commonly used in a genre."""
        genre = genre.lower()
        return [
            data for data in self.scales.values()
            if any(genre in g.lower() for g in data.get('genre_associations', []))
        ]
    
    def compare_scales(self, scale1: str, scale2: str, root: str = 'C') -> Dict[str, Any]:
        """
        Compare two scales showing common and different notes.
        
        Args:
            scale1: First scale name
            scale2: Second scale name
            root: Root note for comparison
        
        Returns:
            Dictionary with comparison data
        """
        notes1 = set(self.get_notes(scale1, root))
        notes2 = set(self.get_notes(scale2, root))
        
        return {
            'scale1': scale1,
            'scale2': scale2,
            'root': root,
            'notes1': sorted(notes1, key=lambda n: self._get_root_index(n)),
            'notes2': sorted(notes2, key=lambda n: self._get_root_index(n)),
            'common': sorted(notes1 & notes2, key=lambda n: self._get_root_index(n)),
            'only_in_scale1': sorted(notes1 - notes2, key=lambda n: self._get_root_index(n)),
            'only_in_scale2': sorted(notes2 - notes1, key=lambda n: self._get_root_index(n)),
            'similarity': len(notes1 & notes2) / len(notes1 | notes2)
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate scale notes from the emotional scale map database.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s Dorian C                    # Get C Dorian notes
  %(prog)s "Harmonic Minor" F#         # Get F# Harmonic Minor
  %(prog)s --list                      # List all scale types
  %(prog)s --list --category Blues     # List scales in Blues category
  %(prog)s --categories                # List all categories
  %(prog)s --search exotic             # Search for "exotic" scales
  %(prog)s --emotion melancholy        # Find melancholy scales
  %(prog)s --genre jazz                # Find jazz scales
  %(prog)s --all C                     # All scales in key of C
  %(prog)s --compare Dorian Aeolian C  # Compare two scales
  %(prog)s --export C --format csv     # Export all C scales to CSV
        """
    )
    
    parser.add_argument('scale', nargs='?', help='Scale type name')
    parser.add_argument('root', nargs='?', help='Root note (C, C#, Db, etc.)')
    parser.add_argument('--list', '-l', action='store_true', help='List available scales')
    parser.add_argument('--category', '-c', help='Filter by category')
    parser.add_argument('--categories', action='store_true', help='List all categories')
    parser.add_argument('--search', '-s', help='Search scales by keyword')
    parser.add_argument('--emotion', '-e', help='Find scales by emotional quality')
    parser.add_argument('--genre', '-g', help='Find scales by genre')
    parser.add_argument('--all', '-a', metavar='ROOT', help='Get all scales in a key')
    parser.add_argument('--compare', nargs=3, metavar=('SCALE1', 'SCALE2', 'ROOT'), 
                        help='Compare two scales')
    parser.add_argument('--export', metavar='ROOT', help='Export all scales in key')
    parser.add_argument('--format', choices=['csv', 'json'], default='json', 
                        help='Export format')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--full', '-f', action='store_true', 
                        help='Show full scale data (not just notes)')
    parser.add_argument('--json-path', help='Path to scale_emotional_map.json')
    
    args = parser.parse_args()
    
    try:
        sg = ScaleGenerator(args.json_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure scale_emotional_map.json is in the same directory.")
        return 1
    
    # Handle different modes
    if args.categories:
        print("Categories:")
        for cat in sorted(sg.list_categories()):
            count = len(sg.list_scales(cat))
            print(f"  {cat} ({count} scales)")
        return 0
    
    if args.list:
        scales = sg.list_scales(args.category)
        if args.category:
            print(f"Scales in '{args.category}':")
        else:
            print(f"All scales ({len(scales)} total):")
        for name in sorted(scales):
            print(f"  {name}")
        return 0
    
    if args.search:
        results = sg.search(args.search)
        print(f"Scales matching '{args.search}' ({len(results)} found):")
        for scale in results:
            print(f"  {scale['scale_type']} ({scale.get('category', 'N/A')})")
            print(f"    Mood: {', '.join(scale.get('emotional_quality', [])[:3])}")
        return 0
    
    if args.emotion:
        results = sg.get_scales_by_emotion(args.emotion)
        print(f"Scales with '{args.emotion}' quality ({len(results)} found):")
        for scale in results:
            print(f"  {scale['scale_type']}")
        return 0
    
    if args.genre:
        results = sg.get_scales_by_genre(args.genre)
        print(f"Scales used in '{args.genre}' ({len(results)} found):")
        for scale in results:
            print(f"  {scale['scale_type']}")
        return 0
    
    if args.all:
        scales = sg.get_all_scales_in_key(args.all)
        print(f"All scales in {args.all}:")
        for scale in scales:
            notes = ' - '.join(scale['notes'])
            print(f"  {scale['scale_type']}: {notes}")
        return 0
    
    if args.compare:
        scale1, scale2, root = args.compare
        result = sg.compare_scales(scale1, scale2, root)
        print(f"Comparing {scale1} vs {scale2} in {root}:")
        print(f"  {scale1}: {' - '.join(result['notes1'])}")
        print(f"  {scale2}: {' - '.join(result['notes2'])}")
        print(f"  Common: {' - '.join(result['common'])}")
        print(f"  Only in {scale1}: {' - '.join(result['only_in_scale1']) or 'none'}")
        print(f"  Only in {scale2}: {' - '.join(result['only_in_scale2']) or 'none'}")
        print(f"  Similarity: {result['similarity']:.0%}")
        return 0
    
    if args.export:
        if args.format == 'csv':
            output = sg.export_csv(args.export, args.output)
            if args.output:
                print(f"Exported to {args.output}")
            else:
                print(output)
        else:
            scales = sg.get_all_scales_in_key(args.export)
            output = json.dumps(scales, indent=2)
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Exported to {args.output}")
            else:
                print(output)
        return 0
    
    # Default: get specific scale in key
    if args.scale and args.root:
        if args.full:
            scale = sg.get_scale(args.scale, args.root)
            print(json.dumps(scale, indent=2))
        else:
            notes = sg.get_notes(args.scale, args.root)
            print(f"{args.scale} in {args.root}:")
            print(f"  {' - '.join(notes)}")
        return 0
    
    # No valid arguments
    parser.print_help()
    return 1


if __name__ == '__main__':
    exit(main())
