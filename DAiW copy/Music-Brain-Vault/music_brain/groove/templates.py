"""
Templates - Backward Compatibility Shim
Import from template_storage instead.
"""

from .template_storage import (
    TemplateStore as TemplateStorage,
    TemplateStore,
    TemplateMerger,
    get_store as get_storage,
    get_store,
    TemplateMetadata,
)

__all__ = [
    'TemplateStorage', 'TemplateStore',
    'TemplateMerger', 
    'get_storage', 'get_store',
    'TemplateMetadata',
]
