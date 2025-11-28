"""
Template Storage with Versioning

Features:
- Automatic version history
- Template validation before save
- Rollback capability
- Merge multiple templates
- Thread-safe file operations

This consolidates templates.py and template_storage.py.
"""

import os
import json
import hashlib
import fcntl
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from .genre_templates import GENRE_TEMPLATES, validate_template
from ..utils.ppq import STANDARD_PPQ, scale_template

# Try numpy for better merging
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


@dataclass
class TemplateMetadata:
    """Metadata for a saved template."""
    version: int
    created_at: str
    source_file: Optional[str]
    genre: str
    ppq: int
    bars_analyzed: int
    notes_analyzed: int
    checksum: str


class TemplateMerger:
    """
    Merge multiple templates into a statistically averaged template.
    """
    
    def merge(self, templates: List[dict]) -> dict:
        """
        Merge multiple templates into one averaged template.
        
        Args:
            templates: List of template dicts
        
        Returns:
            Merged template with averaged values
        """
        if not templates:
            raise ValueError("No templates to merge")
        
        if len(templates) == 1:
            return templates[0].copy()
        
        merged = {}
        
        # Copy non-mergeable fields from first template
        for key in ['ppq', 'grid']:
            if key in templates[0]:
                merged[key] = templates[0][key]
        
        # Merge timing arrays
        for key in ['timing_map', 'timing_density', 'timing_offset', 'velocity_map', 'velocity_curve']:
            if key in templates[0]:
                merged[key] = self._merge_arrays([t.get(key, []) for t in templates])
        
        # Merge swing (weighted average)
        swing_key = 'swing_ratio' if 'swing_ratio' in templates[0] else 'swing'
        swings = [t.get(swing_key, 0.5) for t in templates]
        merged[swing_key] = self._mean(swings)
        
        # Merge push_pull offsets
        if 'push_pull' in templates[0]:
            merged['push_pull'] = self._merge_nested_dicts([t.get('push_pull', {}) for t in templates])
        
        # Merge pocket offsets
        if 'pocket' in templates[0]:
            merged['pocket'] = self._merge_dicts([t.get('pocket', {}) for t in templates])
        
        # Add merge metadata
        merged['_merged'] = {
            'count': len(templates),
            'timestamp': datetime.now().isoformat()
        }
        
        return merged
    
    def _merge_arrays(self, arrays: List[list]) -> list:
        """Merge arrays by averaging."""
        arrays = [a for a in arrays if a]
        if not arrays:
            return []
        
        max_len = max(len(a) for a in arrays)
        
        if HAS_NUMPY:
            normalized = []
            for arr in arrays:
                if len(arr) < max_len:
                    mean_val = np.mean(arr) if arr else 0
                    padded = list(arr) + [mean_val] * (max_len - len(arr))
                    normalized.append(padded)
                else:
                    normalized.append(arr[:max_len])
            return np.mean(normalized, axis=0).tolist()
        else:
            result = []
            for i in range(max_len):
                values = [arr[i] for arr in arrays if i < len(arr)]
                result.append(sum(values) / len(values) if values else 0)
            return result
    
    def _merge_dicts(self, dicts: List[dict]) -> dict:
        """Merge dicts by averaging numeric values."""
        all_keys = set()
        for d in dicts:
            all_keys.update(d.keys())
        
        result = {}
        for key in all_keys:
            values = [d.get(key) for d in dicts if key in d]
            if values and isinstance(values[0], (int, float)):
                result[key] = sum(values) / len(values)
            elif values:
                result[key] = values[0]  # Take first non-numeric
        return result
    
    def _merge_nested_dicts(self, dicts: List[dict]) -> dict:
        """Merge nested dicts (e.g., push_pull)."""
        all_keys = set()
        for d in dicts:
            all_keys.update(d.keys())
        
        result = {}
        for key in all_keys:
            sub_dicts = [d.get(key, {}) for d in dicts if key in d]
            if sub_dicts and isinstance(sub_dicts[0], dict):
                result[key] = self._merge_dicts(sub_dicts)
            else:
                result[key] = sub_dicts[0] if sub_dicts else {}
        return result
    
    def _mean(self, values: List[float]) -> float:
        """Calculate mean."""
        if not values:
            return 0.0
        return sum(values) / len(values)


class TemplateStore:
    """
    Versioned template storage with validation.
    
    Storage structure:
        base_dir/
            genre_name/
                latest.json      # Symlink to current version
                v001.json
                v002.json
                metadata.json    # Version history
    """
    
    MAX_VERSIONS = 50  # Keep last 50 versions per genre
    
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            base_dir = os.path.expanduser("~/.music_brain/templates")
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def _genre_dir(self, genre: str) -> Path:
        """Get or create genre directory."""
        path = self.base_dir / genre.lower()
        path.mkdir(exist_ok=True)
        return path
    
    def _compute_checksum(self, template: Dict[str, Any]) -> str:
        """Compute SHA256 checksum of template."""
        # Sort keys for consistent hashing
        json_str = json.dumps(template, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]
    
    def _get_next_version(self, genre_dir: Path) -> int:
        """Get next version number."""
        versions = list(genre_dir.glob("v*.json"))
        if not versions:
            return 1
        
        max_ver = 0
        for v in versions:
            try:
                num = int(v.stem[1:])  # "v001" -> 1
                max_ver = max(max_ver, num)
            except ValueError:
                pass
        return max_ver + 1
    
    def _load_metadata(self, genre_dir: Path) -> Dict:
        """Load or create metadata."""
        meta_file = genre_dir / "metadata.json"
        if meta_file.exists():
            with open(meta_file) as f:
                return json.load(f)
        return {"versions": [], "current": None}
    
    def _save_metadata(self, genre_dir: Path, metadata: Dict):
        """Save metadata with locking."""
        meta_file = genre_dir / "metadata.json"
        with open(meta_file, "w") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            json.dump(metadata, f, indent=2)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    def save(
        self,
        genre: str,
        template: Dict[str, Any],
        source_file: Optional[str] = None,
        bars_analyzed: int = 0,
        notes_analyzed: int = 0
    ) -> str:
        """
        Save template with version history.
        
        Args:
            genre: Genre name
            template: Template dict to save
            source_file: Original MIDI file (for reference)
            bars_analyzed: Number of bars analyzed
            notes_analyzed: Number of notes analyzed
        
        Returns:
            Path to saved file
        
        Raises:
            ValueError: If template validation fails
        """
        # Validate
        issues = validate_template(template)
        if issues:
            raise ValueError(f"Invalid template: {'; '.join(issues)}")
        
        genre_dir = self._genre_dir(genre)
        version = self._get_next_version(genre_dir)
        
        # Create metadata
        meta = TemplateMetadata(
            version=version,
            created_at=datetime.now().isoformat(),
            source_file=source_file,
            genre=genre,
            ppq=template.get("ppq", STANDARD_PPQ),
            bars_analyzed=bars_analyzed,
            notes_analyzed=notes_analyzed,
            checksum=self._compute_checksum(template)
        )
        
        # Save versioned file
        version_file = genre_dir / f"v{version:03d}.json"
        with open(version_file, "w") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            json.dump({
                "metadata": asdict(meta),
                "template": template
            }, f, indent=2)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Update latest symlink
        latest = genre_dir / "latest.json"
        if latest.is_symlink() or latest.exists():
            latest.unlink()
        latest.symlink_to(version_file.name)
        
        # Update metadata
        metadata = self._load_metadata(genre_dir)
        metadata["versions"].append(asdict(meta))
        metadata["current"] = version
        self._save_metadata(genre_dir, metadata)
        
        # Prune old versions
        self._prune_old_versions(genre_dir)
        
        return str(version_file)
    
    def load(
        self,
        genre: str,
        version: Optional[int] = None,
        target_ppq: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Load template, optionally at specific version.
        
        Args:
            genre: Genre name
            version: Specific version (None = latest)
            target_ppq: Scale template to this PPQ if different
        
        Returns:
            Template dict
        
        Raises:
            FileNotFoundError: If genre/version not found
        """
        genre_dir = self._genre_dir(genre)
        
        if version is None:
            # Try latest symlink
            latest = genre_dir / "latest.json"
            if latest.exists():
                with open(latest) as f:
                    data = json.load(f)
                template = data.get("template", data)
            elif genre.lower() in GENRE_TEMPLATES:
                # Fall back to built-in
                template = GENRE_TEMPLATES[genre.lower()].copy()
            else:
                raise FileNotFoundError(
                    f"No template for '{genre}'. "
                    f"Available: {', '.join(self.list_genres())}"
                )
        else:
            version_file = genre_dir / f"v{version:03d}.json"
            if not version_file.exists():
                raise FileNotFoundError(f"Version {version} not found for '{genre}'")
            with open(version_file) as f:
                data = json.load(f)
            template = data.get("template", data)
        
        # Scale to target PPQ if needed
        if target_ppq and template.get("ppq", STANDARD_PPQ) != target_ppq:
            template = scale_template(template, template["ppq"], target_ppq)
        
        return template
    
    def list_genres(self) -> List[str]:
        """List all genres with saved templates."""
        saved = [d.name for d in self.base_dir.iterdir() if d.is_dir()]
        builtin = list(GENRE_TEMPLATES.keys())
        return sorted(set(saved + builtin))
    
    def list_versions(self, genre: str) -> List[Dict]:
        """List all versions for a genre."""
        genre_dir = self._genre_dir(genre)
        metadata = self._load_metadata(genre_dir)
        return metadata.get("versions", [])
    
    def rollback(self, genre: str, version: int) -> str:
        """
        Rollback to a previous version.
        
        Args:
            genre: Genre name
            version: Version number to rollback to
        
        Returns:
            Path to the now-current version
        """
        genre_dir = self._genre_dir(genre)
        version_file = genre_dir / f"v{version:03d}.json"
        
        if not version_file.exists():
            raise FileNotFoundError(f"Version {version} not found for '{genre}'")
        
        # Update latest symlink
        latest = genre_dir / "latest.json"
        if latest.is_symlink() or latest.exists():
            latest.unlink()
        latest.symlink_to(version_file.name)
        
        # Update metadata
        metadata = self._load_metadata(genre_dir)
        metadata["current"] = version
        self._save_metadata(genre_dir, metadata)
        
        return str(version_file)
    
    def delete(self, genre: str, version: Optional[int] = None):
        """
        Delete a version or entire genre.
        
        Args:
            genre: Genre name
            version: Specific version (None = all)
        """
        genre_dir = self._genre_dir(genre)
        
        if version is None:
            # Delete all
            import shutil
            shutil.rmtree(genre_dir)
        else:
            version_file = genre_dir / f"v{version:03d}.json"
            if version_file.exists():
                version_file.unlink()
            
            # Update metadata
            metadata = self._load_metadata(genre_dir)
            metadata["versions"] = [
                v for v in metadata["versions"]
                if v.get("version") != version
            ]
            self._save_metadata(genre_dir, metadata)
    
    def _prune_old_versions(self, genre_dir: Path):
        """Remove versions beyond MAX_VERSIONS."""
        versions = sorted(genre_dir.glob("v*.json"))
        if len(versions) > self.MAX_VERSIONS:
            # Keep newest MAX_VERSIONS
            to_delete = versions[:-self.MAX_VERSIONS]
            for v in to_delete:
                v.unlink()
            
            # Update metadata
            metadata = self._load_metadata(genre_dir)
            kept_versions = [v.stem for v in versions[-self.MAX_VERSIONS:]]
            metadata["versions"] = [
                v for v in metadata["versions"]
                if f"v{v['version']:03d}" in kept_versions
            ]
            self._save_metadata(genre_dir, metadata)
    
    def get_info(self, genre: str) -> Dict:
        """Get info about a genre's templates."""
        genre_dir = self._genre_dir(genre)
        metadata = self._load_metadata(genre_dir)
        
        has_builtin = genre.lower() in GENRE_TEMPLATES
        saved_versions = len(metadata.get("versions", []))
        
        return {
            "genre": genre,
            "has_builtin": has_builtin,
            "saved_versions": saved_versions,
            "current_version": metadata.get("current"),
            "versions": metadata.get("versions", [])[-5:],  # Last 5
        }


# Global instance
_store = None

def get_store(base_dir: Optional[str] = None) -> TemplateStore:
    """Get or create global template store."""
    global _store
    if _store is None or base_dir is not None:
        _store = TemplateStore(base_dir)
    return _store
