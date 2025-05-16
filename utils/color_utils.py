"""
Fixed color_utils.py - Utility functions for color manipulation
"""
import sys
import os
import math
import random
from .asset_utils import get_asset_path

def interpolate_color(color1, color2, factor):
    """
    Interpolate between two colors
    
    Args:
        color1 (tuple): RGB color tuple (start)
        color2 (tuple): RGB color tuple (end)
        factor (float): Interpolation factor (0.0 to 1.0)
    
    Returns:
        tuple: Interpolated RGB color tuple
    """
    # Ensure factor is between 0 and 1
    factor = max(0.0, min(1.0, factor))
    
    # Interpolate each component
    r = int(color1[0] + (color2[0] - color1[0]) * factor)
    g = int(color1[1] + (color2[1] - color1[1]) * factor)
    b = int(color1[2] + (color2[2] - color1[2]) * factor)
    
    # Ensure valid RGB values
    return (
        max(0, min(255, r)),
        max(0, min(255, g)),
        max(0, min(255, b))
    )

def get_decay_palette(decay_percentage):
    """
    Get a color palette based on decay percentage
    
    Args:
        decay_percentage (float): Decay percentage (0.0 to 100.0)
    
    Returns:
        dict: Color palette with primary, secondary, background and text colors
    """
    # Define color palettes for different decay states
    palettes = {
        "healthy": {
            "primary": (0, 255, 0),     # Bright green
            "secondary": (100, 255, 100),
            "background": (0, 40, 0),
            "text": (200, 255, 200)
        },
        "warning": {
            "primary": (255, 255, 0),    # Yellow
            "secondary": (255, 255, 100),
            "background": (40, 40, 0),
            "text": (255, 255, 200)
        },
        "critical": {
            "primary": (255, 0, 0),      # Red
            "secondary": (255, 100, 100),
            "background": (40, 0, 0),
            "text": (255, 200, 200)
        },
        "decayed": {
            "primary": (100, 0, 0),      # Dark red/brown
            "secondary": (50, 0, 0),
            "background": (20, 0, 0),
            "text": (150, 50, 50)
        }
    }
    
    # Select palette based on decay percentage
    if decay_percentage > 66:
        return palettes["healthy"]
    elif decay_percentage > 33:
        return palettes["warning"]
    elif decay_percentage > 10:
        return palettes["critical"]
    else:
        return palettes["decayed"]

def apply_decay_to_color(color, decay_factor, noise=True):
    """
    Apply decay effect to a color
    
    Args:
        color (tuple): RGB color tuple
        decay_factor (float): Decay factor (0.0 to 1.0, where 1.0 is fully decayed)
        noise (bool): Whether to add noise effect
    
    Returns:
        tuple: Decayed RGB color tuple
    """
    # Ensure valid input
    decay_factor = max(0.0, min(1.0, decay_factor))
    
    # Decay the color by reducing brightness and adding a red tint
    r = int(color[0] * (1 - decay_factor * 0.5) + decay_factor * 50)
    g = int(color[1] * (1 - decay_factor * 0.7))
    b = int(color[2] * (1 - decay_factor * 0.7))
    
    # Add noise for a "damaged" effect
    if noise and decay_factor > 0.3:
        noise_amount = int(decay_factor * 30)
        r = max(0, min(255, r + random.randint(-noise_amount, noise_amount)))
        g = max(0, min(255, g + random.randint(-noise_amount, noise_amount)))
        b = max(0, min(255, b + random.randint(-noise_amount, noise_amount)))
    
    return (r, g, b)

def hsv_to_rgb(h, s, v):
    """
    Convert HSV color to RGB
    
    Args:
        h (float): Hue (0.0 to 360.0)
        s (float): Saturation (0.0 to 1.0)
        v (float): Value (0.0 to 1.0)
    
    Returns:
        tuple: RGB color tuple
    """
    h = float(h % 360)
    s = float(max(0.0, min(1.0, s)))
    v = float(max(0.0, min(1.0, v)))
    
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    r = int((r + m) * 255)
    g = int((g + m) * 255)
    b = int((b + m) * 255)
    
    return (r, g, b)

def rgb_to_hsv(r, g, b):
    """
    Convert RGB color to HSV
    
    Args:
        r (int): Red component (0 to 255)
        g (int): Green component (0 to 255)
        b (int): Blue component (0 to 255)
    
    Returns:
        tuple: HSV color tuple (h: 0-360, s: 0-1, v: 0-1)
    """
    r = r / 255.0
    g = g / 255.0
    b = b / 255.0
    
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    diff = cmax - cmin
    
    # Hue calculation
    if diff == 0:
        h = 0
    elif cmax == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif cmax == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else:  # cmax == b
        h = (60 * ((r - g) / diff) + 240) % 360
    
    # Saturation calculation
    if cmax == 0:
        s = 0
    else:
        s = diff / cmax
    
    # Value calculation
    v = cmax
    
    return (h, s, v)

# font loader
def load_jetbrains_mono_font(size=16):
    """
    Load the JetBrains Mono font with improved path handling
    
    Args:
        size (int): Font size to load
        
    Returns:
        pygame.font.Font: Loaded font object
    """
    import pygame
    
    # Get font path using centralized asset function
    font_path = get_asset_path("fonts", "JetBrainsMono-Regular.ttf")
    
    # Try to load the font
    if os.path.exists(font_path):
        try:
            print(f"Successfully loaded font from: {font_path}")
            return pygame.font.Font(font_path, size)
        except Exception as e:
            print(f"Error loading font from {font_path}: {e}")
    
    # If font loading fails, use default font
    print("Warning: Could not find JetBrains Mono font, using default font")
    return pygame.font.Font(None, size)