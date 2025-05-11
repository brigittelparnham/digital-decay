"""
Modified end_screen.py - Simplified end screen using decay colors
"""
import os
import pygame
import random
import math
import time
import json
from utils.color_utils import load_jetbrains_mono_font

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Load colors from decay_grids.json
def load_decay_colors():
    """Load color scheme from decay_grids.json"""
    try:
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Path to the decay_grids.json file
        json_path = os.path.join(current_dir, 'assets', 'decay_grids.json')
        
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

class GlitchText:
    """Class for text that shows glitch effects"""
    
    def __init__(self, text, font_size, color, pos):
        """
        Initialize the glitchy text
        
        Args:
            text (str): Text to display
            font (str): Font name or path
            size (int): Font size
            color (tuple): RGB color tuple
            pos (tuple): (x, y) position on screen
        """
        self.text = text
        self.font = load_jetbrains_mono_font(font_size)
        self.color = color
        self.pos = pos
        
        # Glitch effect parameters
        self.last_glitch = 0
        self.glitch_interval = 100  # ms
        self.glitch_chars = "!@#$%^&*()-_=+[]{}|;:,.<>/?`~"
        self.glitched_text = self.text
        
        # Time tracking
        self.time = 0
    
    def update(self, delta_time):
        """
        Update the glitch effect
        
        Args:
            delta_time (float): Time in seconds since last update
        """
        self.time += delta_time
        
        # Update glitch effect
        current_time = pygame.time.get_ticks()
        if current_time - self.last_glitch > self.glitch_interval:
            self.last_glitch = current_time
            self.glitch_interval = random.randint(50, 200)
            
            # Create glitched version of text
            self.glitched_text = ""
            for char in self.text:
                # Higher percentage chance of glitches for more broken feel
                if random.random() < 0.3:
                    self.glitched_text += random.choice(self.glitch_chars)
                else:
                    self.glitched_text += char
    
    def draw(self, surface):
        """
        Draw the glitching text
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        # Decide whether to draw normal or glitched text
        text_to_render = self.glitched_text if random.random() < 0.5 else self.text
        
        # Render text
        rendered_text = self.font.render(text_to_render, True, self.color)
        
        # Apply random offset for glitchy feel
        offset_x = random.randint(-3, 3) if random.random() < 0.3 else 0
        offset_y = random.randint(-3, 3) if random.random() < 0.3 else 0
        
        # Calculate position
        text_rect = rendered_text.get_rect(center=(self.pos[0] + offset_x, self.pos[1] + offset_y))
        
        # Draw text
        surface.blit(rendered_text, text_rect)
        
        # Occasionally draw "echo" of text in different color
        if random.random() < 0.2:
            # Use a slightly different tint of decay color
            r, g, b = self.color
            echo_color = (min(255, r + random.randint(-20, 20)), 
                          min(255, g + random.randint(-20, 20)), 
                          min(255, b + random.randint(-20, 20)))
            echo_text = self.font.render(text_to_render, True, echo_color)
            echo_offset = (random.randint(-5, 5), random.randint(-5, 5))
            echo_pos = (text_rect.x + echo_offset[0], text_rect.y + echo_offset[1])
            surface.blit(echo_text, echo_pos)

def run_end_screen():
    """Display the end screen with glitchy effect and auto-reset"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Digital Decay - DECAYED")
    clock = pygame.time.Clock()
    
    # Load decay colors
    healthy_color, warning_color, decay_color = load_decay_colors()
    
    # Create glitching text elements
    title_text = GlitchText(
        "DECAYED",
        92,  # Larger size for impact
        decay_color,  # Use decay color
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
    )
    
    prompt_text = GlitchText(
        "Press ENTER to restart",
        36,
        decay_color,  # Use decay color
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3)
    )
    
    # Set up auto-reset timer (30 seconds)
    start_time = time.time()
    auto_reset_time = 30  # seconds
    
    # Create some basic particles for background distortion
    particles = []
    for _ in range(50):
        particle = {
            'x': random.randint(0, SCREEN_WIDTH),
            'y': random.randint(0, SCREEN_HEIGHT),
            'size': random.randint(1, 4),
            'speed_x': random.uniform(-100, 100),
            'speed_y': random.uniform(-100, 100),
            'color': (*decay_color, random.randint(50, 150))
        }
        particles.append(particle)
    
    # Screen transition effect
    fade_alpha = 255  # Start with black screen
    fade_in = True
    fade_out = False
    
    # Keep track of time
    last_time = pygame.time.get_ticks()
    
    # Main loop
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - last_time) / 1000.0  # Convert to seconds
        last_time = current_time
        
        # Auto-reset check
        elapsed_time = time.time() - start_time
        if elapsed_time >= auto_reset_time:
            fade_out = True
            
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False  # Signal to quit game
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    fade_out = True
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return False  # Signal to quit game
        
        # Update text elements
        title_text.update(delta_time)
        prompt_text.update(delta_time)
        
        # Update particles
        for particle in particles:
            particle['x'] += particle['speed_x'] * delta_time
            particle['y'] += particle['speed_y'] * delta_time
            
            # Bounce off screen edges with direction change
            if particle['x'] < 0 or particle['x'] > SCREEN_WIDTH:
                particle['speed_x'] *= -1
                particle['x'] = max(0, min(SCREEN_WIDTH, particle['x']))
            if particle['y'] < 0 or particle['y'] > SCREEN_HEIGHT:
                particle['speed_y'] *= -1
                particle['y'] = max(0, min(SCREEN_HEIGHT, particle['y']))
                
            # Randomly change direction occasionally
            if random.random() < 0.01:
                particle['speed_x'] = random.uniform(-100, 100)
                particle['speed_y'] = random.uniform(-100, 100)
        
        # Handle fade transitions
        if fade_in:
            fade_alpha = max(0, fade_alpha - 255 * delta_time)
            if fade_alpha <= 0:
                fade_in = False
        
        if fade_out:
            fade_alpha = min(255, fade_alpha + 510 * delta_time)
            if fade_alpha >= 255:
                running = False
        
        # Draw very dark background based on decay color
        r, g, b = decay_color
        dark_bg = (max(0, r//6), max(0, g//6), max(0, b//6))  # Very dark version of decay color
        screen.fill(dark_bg)
        
        # Add digital noise (static)
        for _ in range(200):
            noise_size = random.randint(1, 3)
            noise_x = random.randint(0, SCREEN_WIDTH - noise_size)
            noise_y = random.randint(0, SCREEN_HEIGHT - noise_size)
            noise_color = (
                min(255, decay_color[0] + random.randint(-30, 70)),
                min(255, decay_color[1] + random.randint(-30, 70)),
                min(255, decay_color[2] + random.randint(-30, 70))
            )
            pygame.draw.rect(
                screen,
                noise_color,
                (noise_x, noise_y, noise_size, noise_size)
            )
        
        # Draw particles
        for particle in particles:
            pygame.draw.circle(
                screen,
                particle['color'],
                (int(particle['x']), int(particle['y'])),
                particle['size']
            )
        
        # Add horizontal scan lines
        scan_y_offset = int(current_time / 50) % 20
        for y in range(scan_y_offset, SCREEN_HEIGHT, 20):
            pygame.draw.line(
                screen,
                (*decay_color, 128),
                (0, y),
                (SCREEN_WIDTH, y),
                1
            )
        
        # Draw glitchy blocks
        for _ in range(10):
            if random.random() < 0.3:
                block_width = random.randint(50, 200)
                block_height = random.randint(10, 40)
                block_x = random.randint(0, SCREEN_WIDTH - block_width)
                block_y = random.randint(0, SCREEN_HEIGHT - block_height)
                
                # Use decay color with random variance
                r, g, b = decay_color
                block_color = (
                    min(255, r + random.randint(-30, 50)),
                    min(255, g + random.randint(-30, 50)),
                    min(255, b + random.randint(-30, 50)),
                    random.randint(50, 200)
                )
                
                block_surface = pygame.Surface((block_width, block_height), pygame.SRCALPHA)
                block_surface.fill(block_color)
                screen.blit(block_surface, (block_x, block_y))
        
        # Draw text elements
        title_text.draw(screen)
        
        # Make the prompt text blink at an irregular rate
        if int(current_time * 0.001) % 2 == 0:
            prompt_text.draw(screen)
        
        # Draw fade overlay
        if fade_alpha > 0:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, int(fade_alpha)))
            screen.blit(fade_surface, (0, 0))
        
        # Update screen
        pygame.display.flip()
        clock.tick(FPS)
    
    # Brief pause
    pygame.time.delay(500)
    
    # Return to start screen
    return True

if __name__ == "__main__":
    run_end_screen()