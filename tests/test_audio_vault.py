# tests/test_audio_vault.py
"""
Tests for AudioVault module.

These tests verify:
- Kit loading and GM mapping
- Vault configuration
- Engine → Vault integration (render_phrase_to_vault)
"""

import pytest
from pathlib import Path


class TestKitLoader:
    """Tests for kit_loader module."""

    def test_default_kit_loads(self):
        """Default kit should always be available."""
        from music_brain.audio_vault.kit_loader import load_kit

        kit = load_kit()
        assert "gm_map" in kit
        assert isinstance(kit["gm_map"], dict)
        assert len(kit["gm_map"]) >= 1

    def test_default_kit_has_name(self):
        """Default kit should have a name."""
        from music_brain.audio_vault.kit_loader import load_kit

        kit = load_kit()
        assert "name" in kit
        assert kit["name"] == "DAiW_Default"

    def test_gm_map_returns_dict(self):
        """GM drum map should return a dict of note -> name."""
        from music_brain.audio_vault.kit_loader import get_gm_map

        gm_map = get_gm_map()
        assert isinstance(gm_map, dict)
        assert 36 in gm_map  # Standard kick
        assert 38 in gm_map  # Standard snare

    def test_load_nonexistent_kit_returns_default(self):
        """Loading a nonexistent kit should return default."""
        from music_brain.audio_vault.kit_loader import load_kit

        kit = load_kit("nonexistent_kit_xyz")
        assert kit["name"] == "DAiW_Default"


class TestVaultConfig:
    """Tests for vault configuration."""

    def test_config_paths_are_pathlib(self):
        """All config paths should be Path objects."""
        from music_brain.audio_vault.config import (
            VAULT_ROOT,
            RAW_DIR,
            REFINED_DIR,
            OUTPUT_DIR,
            MANIFESTS_DIR,
        )

        assert isinstance(VAULT_ROOT, Path)
        assert isinstance(RAW_DIR, Path)
        assert isinstance(REFINED_DIR, Path)
        assert isinstance(OUTPUT_DIR, Path)
        assert isinstance(MANIFESTS_DIR, Path)

    def test_get_vault_info(self):
        """get_vault_info should return a dict with expected keys."""
        from music_brain.audio_vault.config import get_vault_info

        info = get_vault_info()
        assert "vault_root" in info
        assert "output_dir" in info
        assert "vault_exists" in info


class TestEngineToVault:
    """Tests for engine → vault integration."""

    def test_render_phrase_to_vault_returns_path(self, tmp_path, monkeypatch):
        """render_phrase_to_vault should return a valid path."""
        # Redirect OUTPUT_DIR to temp directory
        monkeypatch.setattr(
            "music_brain.audio_vault.config.OUTPUT_DIR",
            tmp_path
        )

        from music_brain.structure.comprehensive_engine import render_phrase_to_vault

        midi_path = render_phrase_to_vault(
            "I feel broken",
            motivation=7,
            chaos=0.5,
            vulnerability=0.5,
        )

        assert midi_path is not None
        assert midi_path.endswith(".mid")

    def test_render_phrase_creates_file(self, tmp_path, monkeypatch):
        """render_phrase_to_vault should create a MIDI file."""
        monkeypatch.setattr(
            "music_brain.audio_vault.config.OUTPUT_DIR",
            tmp_path
        )

        from music_brain.structure.comprehensive_engine import render_phrase_to_vault

        midi_path = render_phrase_to_vault(
            "I am furious",
            motivation=9,
            chaos=0.8,
            vulnerability=0.6,
        )

        assert Path(midi_path).exists()

    def test_render_phrase_filename_contains_phrase(self, tmp_path, monkeypatch):
        """Generated filename should contain cleaned version of phrase."""
        monkeypatch.setattr(
            "music_brain.audio_vault.config.OUTPUT_DIR",
            tmp_path
        )

        from music_brain.structure.comprehensive_engine import render_phrase_to_vault

        midi_path = render_phrase_to_vault("I miss you")

        filename = Path(midi_path).name
        assert "i_miss_you" in filename or "miss" in filename

    def test_render_phrase_with_existing_session(self, tmp_path, monkeypatch):
        """Should work with a pre-configured session."""
        monkeypatch.setattr(
            "music_brain.audio_vault.config.OUTPUT_DIR",
            tmp_path
        )

        from music_brain.structure.comprehensive_engine import (
            TherapySession,
            render_phrase_to_vault,
        )

        session = TherapySession()
        session.set_scales(motivation=5, chaos=0.3)

        midi_path = render_phrase_to_vault(
            "Quiet sadness",
            session=session,
        )

        assert Path(midi_path).exists()


class TestRefinery:
    """Tests for refinery module (sample processing)."""

    def test_refinery_imports(self):
        """Refinery module should import without error."""
        from music_brain.audio_vault import refinery
        assert hasattr(refinery, "normalize_sample")
        assert hasattr(refinery, "refine_pack")

    def test_augment_sample_exists(self):
        """augment_sample function should exist."""
        from music_brain.audio_vault.refinery import augment_sample
        assert callable(augment_sample)
