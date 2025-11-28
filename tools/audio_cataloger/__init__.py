"""
Audio Cataloger Module

Scan, catalog, and search audio files with automatic key/tempo detection.
Part of the Music Brain system.
"""

from .audio_cataloger import (
    init_database,
    scan_folder,
    search_catalog,
    show_stats,
    list_all,
    export_results,
    analyze_audio_file,
)

__all__ = [
    'init_database',
    'scan_folder',
    'search_catalog',
    'show_stats',
    'list_all',
    'export_results',
    'analyze_audio_file',
]
