"""
Core module for Celestraa DSL.

This module contains the core classes for the Celestraa DSL including
App, StatefulApp, AppGroup, and base builder functionality.
"""

from .base_builder import BaseBuilder
from .resource_generator import ResourceGenerator
from .app import App
from .stateful_app import StatefulApp
from .app_group import AppGroup

__all__ = [
    "BaseBuilder",
    "ResourceGenerator", 
    "App",
    "StatefulApp",
    "AppGroup"
] 