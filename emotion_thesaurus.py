"""
DAiW Emotion Thesaurus
======================
A comprehensive 6×6×6 emotion taxonomy with intensity tiers for music therapy.

This module provides loading and querying capabilities for the emotion thesaurus
JSON data files, designed to integrate with the DAiW-Music-Brain interrogation system.

Usage:
    from emotion_thesaurus import EmotionThesaurus
    
    thesaurus = EmotionThesaurus()
    
    # Find emotions by synonym
    matches = thesaurus.find_by_synonym("melancholy")
    
    # Get intensity synonyms
    synonyms = thesaurus.get_intensity_synonyms("SAD", "GRIEF", "bereaved", tier=4)
    
    # Find blends
    blend = thesaurus.find_blend("guilt")
"""

import json
from pathlib import Path
from typing import Optional, Union
from dataclasses import dataclass


@dataclass
class EmotionMatch:
    """Represents a matched emotion from the thesaurus."""
    base_emotion: str
    sub_emotion: str
    sub_sub_emotion: str
    intensity_tier: int
    matched_synonym: str
    all_tier_synonyms: list[str]
    emotion_id: str
    description: str


@dataclass 
class BlendMatch:
    """Represents a matched emotional blend."""
    blend_id: str
    name: str
    components: list[str]
    ratio: list[float]
    description: str
    intensity_tier: int
    matched_synonym: str
    all_tier_synonyms: list[str]


class EmotionThesaurus:
    """
    Main interface for the DAiW Emotion Thesaurus.
    
    Loads and queries the 6×6×6 emotion taxonomy with intensity tiers
    and emotional blends.
    """
    
    BASE_EMOTIONS = ["happy", "sad", "angry", "fear", "surprise", "disgust"]
    INTENSITY_TIERS = ["1_subtle", "2_mild", "3_moderate", "4_strong", "5_intense", "6_overwhelming"]
    
    def __init__(self, data_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the thesaurus.
        
        Args:
            data_dir: Path to the emotion_thesaurus directory containing JSON files.
                     Defaults to looking in standard locations.
        """
        self.data_dir = self._resolve_data_dir(data_dir)
        self.emotions: dict = {}
        self.blends: dict = {}
        self.metadata: dict = {}
        self._synonym_index: dict[str, list] = {}
        self._blend_synonym_index: dict[str, list] = {}
        
        self._load_all()
        self._build_indices()
    
    def _resolve_data_dir(self, data_dir: Optional[Union[str, Path]]) -> Path:
        """Find the data directory."""
        if data_dir:
            return Path(data_dir)
        
        # Check standard locations
        candidates = [
            Path(__file__).parent / "data" / "emotion_thesaurus",
            Path(__file__).parent.parent / "data" / "emotion_thesaurus",
            Path("music_brain/data/emotion_thesaurus"),
            Path("data/emotion_thesaurus"),
            Path("emotion_thesaurus"),
        ]
        
        for candidate in candidates:
            if candidate.exists() and (candidate / "metadata.json").exists():
                return candidate
        
        raise FileNotFoundError(
            f"Could not find emotion_thesaurus data directory. "
            f"Searched: {[str(c) for c in candidates]}"
        )
    
    def _load_all(self) -> None:
        """Load all JSON data files."""
        # Load metadata
        with open(self.data_dir / "metadata.json") as f:
            self.metadata = json.load(f)
        
        # Load base emotions
        for emotion in self.BASE_EMOTIONS:
            filepath = self.data_dir / f"{emotion}.json"
            if filepath.exists():
                with open(filepath) as f:
                    self.emotions[emotion.upper()] = json.load(f)
        
        # Load blends
        blends_path = self.data_dir / "blends.json"
        if blends_path.exists():
            with open(blends_path) as f:
                self.blends = json.load(f)
    
    def _build_indices(self) -> None:
        """Build reverse lookup indices for synonyms."""
        # Index base emotions
        for base_name, base_data in self.emotions.items():
            for sub_name, sub_data in base_data.get("sub_emotions", {}).items():
                for subsub_name, subsub_data in sub_data.get("sub_sub_emotions", {}).items():
                    for tier, synonyms in subsub_data.get("intensity_tiers", {}).items():
                        for syn in synonyms:
                            key = syn.lower().strip()
                            if key not in self._synonym_index:
                                self._synonym_index[key] = []
                            self._synonym_index[key].append({
                                "base": base_name,
                                "sub": sub_name,
                                "subsub": subsub_name,
                                "tier": tier,
                                "id": subsub_data.get("id", ""),
                                "description": subsub_data.get("description", ""),
                                "all_synonyms": synonyms
                            })
        
        # Index blends
        for category in ["dyadic_blends", "triadic_blends", "therapeutic_blends", 
                        "musical_blends", "situational_blends"]:
            if category not in self.blends:
                continue
            
            blends_list = self.blends[category]
            if isinstance(blends_list, dict):
                blends_list = blends_list.get("blends", [])
            
            for blend in blends_list:
                for tier, synonyms in blend.get("synonyms", {}).items():
                    for syn in synonyms:
                        key = syn.lower().strip()
                        if key not in self._blend_synonym_index:
                            self._blend_synonym_index[key] = []
                        self._blend_synonym_index[key].append({
                            "blend": blend,
                            "tier": tier,
                            "all_synonyms": synonyms
                        })
    
    def find_by_synonym(self, word: str, fuzzy: bool = False) -> list[EmotionMatch]:
        """
        Find emotions matching a synonym.
        
        Args:
            word: The word/phrase to search for
            fuzzy: If True, also match partial/similar words
            
        Returns:
            List of EmotionMatch objects for all matching emotions
        """
        word = word.lower().strip()
        matches = []
        
        # Exact match
        if word in self._synonym_index:
            for entry in self._synonym_index[word]:
                tier_num = int(entry["tier"].split("_")[0])
                matches.append(EmotionMatch(
                    base_emotion=entry["base"],
                    sub_emotion=entry["sub"],
                    sub_sub_emotion=entry["subsub"],
                    intensity_tier=tier_num,
                    matched_synonym=word,
                    all_tier_synonyms=entry["all_synonyms"],
                    emotion_id=entry["id"],
                    description=entry["description"]
                ))
        
        # Fuzzy matching
        if fuzzy and not matches:
            for key in self._synonym_index:
                if word in key or key in word:
                    for entry in self._synonym_index[key]:
                        tier_num = int(entry["tier"].split("_")[0])
                        matches.append(EmotionMatch(
                            base_emotion=entry["base"],
                            sub_emotion=entry["sub"],
                            sub_sub_emotion=entry["subsub"],
                            intensity_tier=tier_num,
                            matched_synonym=key,
                            all_tier_synonyms=entry["all_synonyms"],
                            emotion_id=entry["id"],
                            description=entry["description"]
                        ))
        
        return matches
    
    def find_blend(self, word: str, fuzzy: bool = False) -> list[BlendMatch]:
        """
        Find emotional blends matching a synonym.
        
        Args:
            word: The word/phrase to search for
            fuzzy: If True, also match partial/similar words
            
        Returns:
            List of BlendMatch objects
        """
        word = word.lower().strip()
        matches = []
        
        # Also check blend names directly
        for category in ["dyadic_blends", "triadic_blends", "therapeutic_blends",
                        "musical_blends", "situational_blends"]:
            if category not in self.blends:
                continue
            
            blends_list = self.blends[category]
            if isinstance(blends_list, dict):
                blends_list = blends_list.get("blends", [])
            
            for blend in blends_list:
                if blend.get("name", "").lower() == word:
                    # Return moderate tier by default
                    tier = "3_moderate"
                    synonyms = blend.get("synonyms", {}).get(tier, [])
                    matches.append(BlendMatch(
                        blend_id=blend.get("id", ""),
                        name=blend.get("name", ""),
                        components=blend.get("components", []),
                        ratio=blend.get("ratio", []),
                        description=blend.get("description", ""),
                        intensity_tier=3,
                        matched_synonym=word,
                        all_tier_synonyms=synonyms
                    ))
        
        # Check synonym index
        if word in self._blend_synonym_index:
            for entry in self._blend_synonym_index[word]:
                blend = entry["blend"]
                tier_num = int(entry["tier"].split("_")[0])
                matches.append(BlendMatch(
                    blend_id=blend.get("id", ""),
                    name=blend.get("name", ""),
                    components=blend.get("components", []),
                    ratio=blend.get("ratio", []),
                    description=blend.get("description", ""),
                    intensity_tier=tier_num,
                    matched_synonym=word,
                    all_tier_synonyms=entry["all_synonyms"]
                ))
        
        return matches
    
    def get_intensity_synonyms(
        self, 
        base_emotion: str, 
        sub_emotion: str, 
        sub_sub_emotion: str,
        tier: int = 3
    ) -> list[str]:
        """
        Get synonyms for a specific emotion at a given intensity tier.
        
        Args:
            base_emotion: e.g., "SAD"
            sub_emotion: e.g., "GRIEF"  
            sub_sub_emotion: e.g., "bereaved"
            tier: 1-6 intensity level
            
        Returns:
            List of synonyms for that intensity tier
        """
        tier_key = self.INTENSITY_TIERS[tier - 1] if 1 <= tier <= 6 else "3_moderate"
        
        try:
            base = self.emotions.get(base_emotion.upper(), {})
            sub = base.get("sub_emotions", {}).get(sub_emotion.upper(), {})
            subsub = sub.get("sub_sub_emotions", {}).get(sub_sub_emotion.lower(), {})
            return subsub.get("intensity_tiers", {}).get(tier_key, [])
        except (KeyError, AttributeError):
            return []
    
    def get_emotion_path(self, emotion_id: str) -> Optional[dict]:
        """
        Get full emotion data by ID (e.g., "IIia" for SAD > GRIEF > bereaved).
        
        Args:
            emotion_id: The hierarchical ID string
            
        Returns:
            Dict with base, sub, subsub data or None if not found
        """
        for base_name, base_data in self.emotions.items():
            if base_data.get("id") == emotion_id[0:len(base_data.get("id", ""))]:
                for sub_name, sub_data in base_data.get("sub_emotions", {}).items():
                    sub_id = sub_data.get("id", "")
                    if emotion_id.startswith(sub_id):
                        for subsub_name, subsub_data in sub_data.get("sub_sub_emotions", {}).items():
                            if subsub_data.get("id") == emotion_id:
                                return {
                                    "base": {"name": base_name, **base_data},
                                    "sub": {"name": sub_name, **sub_data},
                                    "subsub": {"name": subsub_name, **subsub_data}
                                }
        return None
    
    def get_all_base_emotions(self) -> list[str]:
        """Get list of all base emotion names."""
        return list(self.emotions.keys())
    
    def get_sub_emotions(self, base_emotion: str) -> list[str]:
        """Get sub-emotions for a base emotion."""
        base = self.emotions.get(base_emotion.upper(), {})
        return list(base.get("sub_emotions", {}).keys())
    
    def get_sub_sub_emotions(self, base_emotion: str, sub_emotion: str) -> list[str]:
        """Get sub-sub-emotions for a sub-emotion."""
        base = self.emotions.get(base_emotion.upper(), {})
        sub = base.get("sub_emotions", {}).get(sub_emotion.upper(), {})
        return list(sub.get("sub_sub_emotions", {}).keys())
    
    def suggest_intensity(self, words: list[str]) -> int:
        """
        Analyze a list of emotion words and suggest an overall intensity tier.
        
        Args:
            words: List of emotional words/phrases
            
        Returns:
            Suggested intensity tier (1-6)
        """
        if not words:
            return 3
        
        tiers = []
        for word in words:
            matches = self.find_by_synonym(word)
            if matches:
                tiers.append(max(m.intensity_tier for m in matches))
        
        if not tiers:
            return 3
        
        # Return the mode or median
        return round(sum(tiers) / len(tiers))
    
    def get_musical_hints(self, base_emotion: str) -> dict:
        """
        Get musical mapping hints for a base emotion.
        
        Args:
            base_emotion: e.g., "SAD"
            
        Returns:
            Dict with valence, arousal_range, and musical suggestions
        """
        base = self.emotions.get(base_emotion.upper(), {})
        hints = self.metadata.get("musical_mapping_hints", {})
        
        valence = base.get("valence", "mixed")
        arousal = base.get("arousal_range", [0.3, 0.7])
        
        return {
            "valence": valence,
            "arousal_range": arousal,
            "suggested_mode": hints.get("valence_to_mode", {}).get(valence, ""),
            "tempo_range": self._arousal_to_tempo(arousal),
        }
    
    def _arousal_to_tempo(self, arousal_range: list[float]) -> str:
        """Convert arousal range to tempo suggestion."""
        avg = sum(arousal_range) / 2
        if avg < 0.4:
            return "40-70 BPM (slow)"
        elif avg < 0.7:
            return "70-120 BPM (moderate)"
        else:
            return "120-180+ BPM (fast)"
    
    def stats(self) -> dict:
        """Return statistics about the loaded thesaurus."""
        total_synonyms = len(self._synonym_index)
        total_blend_synonyms = len(self._blend_synonym_index)
        
        emotion_counts = {}
        for base_name, base_data in self.emotions.items():
            sub_count = len(base_data.get("sub_emotions", {}))
            subsub_count = sum(
                len(sub.get("sub_sub_emotions", {}))
                for sub in base_data.get("sub_emotions", {}).values()
            )
            emotion_counts[base_name] = {"sub": sub_count, "subsub": subsub_count}
        
        blend_count = 0
        for category in ["dyadic_blends", "triadic_blends", "therapeutic_blends",
                        "musical_blends", "situational_blends"]:
            if category in self.blends:
                blends_list = self.blends[category]
                if isinstance(blends_list, dict):
                    blend_count += len(blends_list.get("blends", []))
                else:
                    blend_count += len(blends_list)
        
        return {
            "base_emotions": len(self.emotions),
            "emotion_hierarchy": emotion_counts,
            "total_unique_synonyms": total_synonyms,
            "total_blend_synonyms": total_blend_synonyms,
            "blend_count": blend_count,
            "data_directory": str(self.data_dir)
        }


# Convenience function for quick lookups
def lookup(word: str, data_dir: Optional[str] = None) -> list[EmotionMatch]:
    """
    Quick synonym lookup without instantiating the full thesaurus.
    
    Args:
        word: The emotion word to look up
        data_dir: Optional path to data directory
        
    Returns:
        List of matching EmotionMatch objects
    """
    thesaurus = EmotionThesaurus(data_dir)
    return thesaurus.find_by_synonym(word, fuzzy=True)


if __name__ == "__main__":
    # Demo usage
    print("DAiW Emotion Thesaurus Demo")
    print("=" * 40)
    
    try:
        thesaurus = EmotionThesaurus()
        print(f"\nLoaded from: {thesaurus.data_dir}")
        print(f"\nStats: {json.dumps(thesaurus.stats(), indent=2)}")
        
        # Test synonym lookup
        test_words = ["melancholy", "furious", "anxious", "joyful", "betrayed"]
        print("\n\nSynonym Lookups:")
        print("-" * 40)
        for word in test_words:
            matches = thesaurus.find_by_synonym(word)
            if matches:
                m = matches[0]
                print(f"  '{word}' -> {m.base_emotion} > {m.sub_emotion} > {m.sub_sub_emotion} (tier {m.intensity_tier})")
            else:
                # Try blend
                blend_matches = thesaurus.find_blend(word)
                if blend_matches:
                    b = blend_matches[0]
                    print(f"  '{word}' -> BLEND: {b.name} ({' + '.join(b.components)})")
                else:
                    print(f"  '{word}' -> No match")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nTo use this module, ensure the JSON data files are in the expected location.")
