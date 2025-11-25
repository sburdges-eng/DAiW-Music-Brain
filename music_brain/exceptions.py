"""
DAiW Exceptions
===============

Domain-specific exceptions for clear error handling.
Use these instead of bare prints for user-facing errors.
"""


class DAiWError(Exception):
    """Base exception for all DAiW errors."""

    pass


# =============================================================================
# GROOVE ENGINE ERRORS
# =============================================================================


class GrooveEngineError(DAiWError):
    """Errors in the groove/humanization engine."""

    pass


class InvalidGrooveTemplate(GrooveEngineError):
    """Raised when a groove template is invalid or not found."""

    def __init__(self, template_name: str, available: list = None):
        self.template_name = template_name
        self.available = available or []
        msg = f"Unknown groove template: '{template_name}'"
        if self.available:
            msg += f". Available: {', '.join(self.available)}"
        super().__init__(msg)


class InvalidGrooveSettings(GrooveEngineError):
    """Raised when groove settings are invalid."""

    pass


# =============================================================================
# STRUCTURE/HARMONY ERRORS
# =============================================================================


class StructureError(DAiWError):
    """Errors in structure/harmony analysis."""

    pass


class ChordParseError(StructureError):
    """Raised when a chord string cannot be parsed."""

    def __init__(self, chord_string: str, reason: str = None):
        self.chord_string = chord_string
        self.reason = reason
        msg = f"Could not parse chord: '{chord_string}'"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


class ProgressionParseError(StructureError):
    """Raised when a progression string cannot be parsed."""

    def __init__(self, progression_string: str, reason: str = None):
        self.progression_string = progression_string
        self.reason = reason
        msg = f"Could not parse progression: '{progression_string}'"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


class EmptyProgressionError(StructureError):
    """Raised when a progression is empty after parsing."""

    def __init__(self, original_input: str = None):
        self.original_input = original_input
        msg = "Chord progression is empty"
        if original_input:
            msg += f" (input was: '{original_input}')"
        super().__init__(msg)


# =============================================================================
# THERAPY/INTENT ERRORS
# =============================================================================


class TherapyError(DAiWError):
    """Errors in the therapy/intent engine."""

    pass


class InvalidIntentError(TherapyError):
    """Raised when an intent file or object is invalid."""

    def __init__(self, reason: str, field: str = None):
        self.reason = reason
        self.field = field
        msg = f"Invalid intent: {reason}"
        if field:
            msg = f"Invalid intent field '{field}': {reason}"
        super().__init__(msg)


class MissingPhaseError(TherapyError):
    """Raised when a required phase is missing from intent."""

    def __init__(self, phase: str):
        self.phase = phase
        super().__init__(f"Missing required phase: {phase}")


# =============================================================================
# MIDI/DAW ERRORS
# =============================================================================


class MidiError(DAiWError):
    """Errors in MIDI generation or processing."""

    pass


class MidiRenderError(MidiError):
    """Raised when MIDI rendering fails."""

    def __init__(self, reason: str, output_path: str = None):
        self.reason = reason
        self.output_path = output_path
        msg = f"Failed to render MIDI: {reason}"
        if output_path:
            msg += f" (target: {output_path})"
        super().__init__(msg)


class MidiImportError(MidiError):
    """Raised when a MIDI file cannot be imported."""

    def __init__(self, file_path: str, reason: str = None):
        self.file_path = file_path
        self.reason = reason
        msg = f"Could not import MIDI file: '{file_path}'"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


# =============================================================================
# AUDIO VAULT ERRORS
# =============================================================================


class AudioVaultError(DAiWError):
    """Errors related to the audio vault."""

    pass


class SampleNotFoundError(AudioVaultError):
    """Raised when a sample file is not found."""

    def __init__(self, sample_path: str, vault_path: str = None):
        self.sample_path = sample_path
        self.vault_path = vault_path
        msg = f"Sample not found: '{sample_path}'"
        if vault_path:
            msg += f" (in vault: {vault_path})"
        super().__init__(msg)


class KitNotFoundError(AudioVaultError):
    """Raised when a kit definition is not found."""

    def __init__(self, kit_name: str, available: list = None):
        self.kit_name = kit_name
        self.available = available or []
        msg = f"Kit not found: '{kit_name}'"
        if self.available:
            msg += f". Available: {', '.join(self.available)}"
        super().__init__(msg)


class InvalidKitError(AudioVaultError):
    """Raised when a kit definition file is invalid."""

    def __init__(self, kit_path: str, reason: str = None):
        self.kit_path = kit_path
        self.reason = reason
        msg = f"Invalid kit definition: '{kit_path}'"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


# =============================================================================
# CONFIGURATION ERRORS
# =============================================================================


class ConfigError(DAiWError):
    """Errors in configuration."""

    pass


class InvalidConfigError(ConfigError):
    """Raised when a configuration value is invalid."""

    def __init__(self, key: str, value, reason: str = None):
        self.key = key
        self.value = value
        self.reason = reason
        msg = f"Invalid config value for '{key}': {value}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)
