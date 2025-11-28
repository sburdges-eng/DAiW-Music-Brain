"""
Pocket Rules - Backward Compatibility Shim
Import from genre_templates instead.
"""

from .genre_templates import (
    POCKET_OFFSETS as GENRE_POCKETS,
    POCKET_OFFSETS,
    get_pocket,
    get_push_pull,
    get_swing,
    get_velocity_range,
    scale_pocket_to_ppq,
    list_genres,
)
from ..utils.ppq import STANDARD_PPQ

list_pocket_genres = list_genres

__all__ = [
    'GENRE_POCKETS', 'POCKET_OFFSETS', 
    'get_pocket', 'get_push_pull', 'get_swing',
    'get_velocity_range', 'scale_pocket_to_ppq',
    'list_genres', 'list_pocket_genres', 'STANDARD_PPQ',
]
