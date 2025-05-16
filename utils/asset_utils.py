
"""
utils/asset_utils.py - Centralized asset path handling
"""
import sys
import os

def get_asset_path(*path_parts):
    """
    Get correct path for assets in both dev and bundled app
    
    Args:
        *path_parts: Path components (e.g., 'images', 'logo.png')
        
    Returns:
        str: Full path to the asset
    """
    if hasattr(sys, '_MEIPASS'):
        # Running in PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in development
        # Get the directory containing this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # If we're in utils/ or games/, go up one level to project root
        if os.path.basename(current_dir) in ['utils', 'games']:
            base_path = os.path.dirname(current_dir)
        else:
            # We're already at project root
            base_path = current_dir
    
    # Join with assets directory and provided path parts
    return os.path.join(base_path, 'assets', *path_parts)