"""
decay_engine.py - Core decay functionality and state management
"""
import time
import pygame
import numpy as np
from utils.color_utils import get_decay_palette, apply_decay_to_color
from utils.color_utils import load_jetbrains_mono_font

class DecayEngine:
    """Manages the decay state and provides color transformations based on decay level"""
    
    def __init__(self, decay_time=60):
        """
        Initialize the decay engine
        
        Args:
            decay_time (int): Time in seconds for decay to go from 100% to 0%
        """
        self.decay_percentage = 100.0
        self.decay_time = decay_time
        self.last_update = time.time()
        self.reached_zero = False  # Flag to track if we've hit zero
    
    def update(self, delta_time=None):
        """
        Update the decay percentage based on elapsed time
        
        Args:
            delta_time (float, optional): Time in seconds since last update.
                                        If None, calculated automatically.
        
        Returns:
            float: Current decay percentage
        """
        current_time = time.time()
        
        if delta_time is None:
            delta_time = current_time - self.last_update
        
        # Calculate decay rate (percentage points per second)
        decay_rate = 100.0 / self.decay_time
        
        # Apply decay
        self.decay_percentage -= decay_rate * delta_time
        
        # CRITICAL: Detect crossing the 0% threshold
        # This exact comparison helps catch the transition to 0
        if self.decay_percentage <= 0.0:
            if not self.reached_zero:
                self.reached_zero = True
                print("CRITICAL: DECAY HAS REACHED EXACT 0%")
            
            # Ensure it stays exactly at 0.0 for reliable detection
            self.decay_percentage = 0.0
        else:
            # Still ensure upper bound is respected
            self.decay_percentage = min(100.0, self.decay_percentage)
            self.reached_zero = False
        
        self.last_update = current_time
        return self.decay_percentage
    
    def modify_decay(self, amount):
        """
        Modify the decay percentage by a given amount
        
        Args:
            amount (float): Amount to change decay percentage (positive increases, negative decreases)
        
        Returns:
            float: New decay percentage
        """
        # Update percentage
        self.decay_percentage += amount
        
        # CRITICAL: Handle 0% threshold with explicit check
        if self.decay_percentage <= 0.0:
            if not self.reached_zero:
                self.reached_zero = True
                print("CRITICAL: DECAY HAS REACHED EXACT 0% THROUGH MODIFICATION")
            
            # Set to exactly 0.0 for reliable detection
            self.decay_percentage = 0.0
        else:
            # Still ensure upper bound is respected
            self.decay_percentage = min(100.0, self.decay_percentage)
            self.reached_zero = False
        
        return self.decay_percentage
    
    def get_current_palette(self):
        """
        Get the color palette based on current decay level
        
        Returns:
            dict: Color palette with primary, secondary, background and text colors
        """
        return get_decay_palette(self.decay_percentage)
    
    def get_decay_color(self, base_color=(255, 255, 255)):
        """
        Transform a color based on current decay level
        
        Args:
            base_color (tuple): RGB color tuple to transform
        
        Returns:
            tuple: Transformed RGB color tuple
        """
        # Ensure base_color is valid and contains integers
        try:
            base_color = tuple(int(c) for c in base_color[:3])
        except (ValueError, TypeError):
            # Fallback to white if there's any issue
            base_color = (255, 255, 255)
        
        # Calculate decay factor (1.0 = no decay, 0.0 = full decay)
        decay_factor = self.decay_percentage / 100.0
        
        # Apply decay to color
        return apply_decay_to_color(base_color, 1.0 - decay_factor)


