"""
decay_bar.py - Decay progress bar implementation with colors from decay_grids.json
"""
import pygame
import os
import json
from utils.color_utils import load_jetbrains_mono_font

# Load colors from decay_grids.json
def load_decay_colors():
    """Load color scheme from decay_grids.json"""
    try:
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Path to the decay_grids.json file - need to go up one level to get to the project root
        json_path = os.path.join(current_dir, '..', 'assets', 'decay_grids.json')
        
        with open(json_path, 'r') as f:
            decay_grids = json.load(f)
            
        # Use the selected Option 2 colors from the grid
        begin_hex = "#adb47d"  # Muted Green from Stage 1
        middle_hex = "#dce4aa"  # Pale Yellow from Stage 3
        end_hex = "#799f96"    # Teal from Stage 6
        
        # Convert hex to RGB
        begin_rgb = tuple(int(begin_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        middle_rgb = tuple(int(middle_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        end_rgb = tuple(int(end_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        return begin_rgb, middle_rgb, end_rgb
    except Exception as e:
        print(f"Error loading decay colors: {e}")
        # Default fallback colors
        return (173, 180, 125), (220, 228, 170), (121, 159, 150)

class DecayBar:
    """
    A visual bar representing decay progress
    
    This class provides a customizable progress bar that visually 
    represents the decay percentage, changing colors as decay progresses.
    """
    
    def __init__(self, rect, decay_engine=None, full_width=False):
        """
        Initialize the decay bar
        
        Args:
            rect (pygame.Rect): Rectangle defining position and size
            decay_engine (DecayEngine, optional): Reference to decay engine
            full_width (bool): If True, the bar will span the full width of the screen
        """
        self.rect = rect
        self.decay_engine = decay_engine
        self.full_width = full_width
        
        # Load colors from decay_grids.json
        self.healthy_color, self.warning_color, self.decay_color = load_decay_colors()
        
        # Consistent styling across all screens
        self.bg_color = (0, 0, 0)  # Black background
        self.border_color = (50, 50, 50)  # Dark gray border
        self.text_color = (255, 255, 255)  # White text - more visible
        
        # Load JetBrains Mono font - using local function to avoid circular imports
        self.font = load_jetbrains_mono_font(16)
    
    def draw(self, surface):
        """
        Draw the decay bar with consistent styling
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        if not surface:
            return
            
        # Get current decay percentage from engine if available
        percentage = 100
        if self.decay_engine:
            percentage = self.decay_engine.decay_percentage
            
        # Adjust rect if full width is enabled
        if self.full_width:
            rect = pygame.Rect(0, self.rect.y, surface.get_width(), self.rect.height)
        else:
            rect = self.rect
        
        # Draw background (black)
        pygame.draw.rect(surface, self.bg_color, rect)
        
        # Calculate fill width based on percentage
        fill_width = int(rect.width * (percentage / 100.0))
        fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)
        
        # Determine bar color based on percentage using our decay colors
        if percentage > 66:
            bar_color = self.healthy_color  # Healthy (green)
        elif percentage > 33:
            bar_color = self.warning_color  # Warning (yellow)
        else:
            bar_color = self.decay_color  # Decayed (teal)
        
        # Draw filled portion with appropriate color
        pygame.draw.rect(surface, bar_color, fill_rect)
        
        # Draw border
        pygame.draw.rect(surface, self.border_color, rect, 1)
        
        # Format text
        if self.font:
            # Format percentage with one decimal place
            percentage_text = f"{percentage:.1f}%"
            percentage_surface = self.font.render(percentage_text, True, self.text_color)
            
            # Position text in center of bar
            percentage_rect = percentage_surface.get_rect(center=rect.center)
            surface.blit(percentage_surface, percentage_rect)
            
            # Add time remaining text if decay engine is available
            if self.decay_engine:
                # Calculate time based on decay percentage
                total_time = self.decay_engine.decay_time  # Total time in seconds
                time_remaining = int(total_time * percentage / 100.0)
                
                # Format as MM:SS
                minutes = time_remaining // 60
                seconds = time_remaining % 60
                time_text = f"Time: {minutes:02d}:{seconds:02d}"
                
                # Render time text
                time_surface = self.font.render(time_text, True, self.text_color)
                
                # Position time text to the right
                time_rect = time_surface.get_rect(
                    midright=(rect.right - 10, rect.centery)
                )
                surface.blit(time_surface, time_rect)