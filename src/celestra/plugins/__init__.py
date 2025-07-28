"""
Plugin system for Celestraa DSL.

This module contains the plugin system including plugin management,
base classes for plugin development, and template management.
"""

from .plugin_manager import PluginManager
from .plugin_base import PluginBase, PluginType, PluginMetadata
from .template_manager import TemplateManager, TemplateEngine

__all__ = [
    "PluginManager",
    "PluginBase", 
    "PluginType",
    "PluginMetadata",
    "TemplateManager",
    "TemplateEngine"
] 