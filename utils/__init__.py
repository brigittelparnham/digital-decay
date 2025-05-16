"""
Updated utils/__init__.py - Fixed import issues
"""
# Import the centralized asset function first
from .asset_utils import get_asset_path

# Import utility functions for easy access
from .color_utils import *
from .blender_loader import *
from .decay_bar import *

# Make get_asset_path available to other modules
__all__ = ['get_asset_path', 'load_jetbrains_mono_font', 'DecayBar', 'BlenderModel', 'AnimationLoader']