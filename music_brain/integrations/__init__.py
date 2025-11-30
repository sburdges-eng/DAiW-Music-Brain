"""
Integrations module for DAiW-Music-Brain.

This module provides integration interfaces with external systems while
maintaining the core philosophy of "Interrogate Before Generate" -
emotional intent should drive technical decisions.
"""

from music_brain.integrations.penta_core import PentaCoreIntegration

__all__ = [
    "PentaCoreIntegration",
]
