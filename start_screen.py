"""
start_screen.py - Start screen with decaying Digital Decay logo
"""
import os
import pygame
import random
import math
import time
from decay_engine import DecayEngine
from utils.color_utils import load_jetbrains_mono_font

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

class DecayingText:
    """Class for text that shows progressive decay effects"""
    
    def __init__(self, text, font_size, color, pos):
        """
        Initialize the decaying text
        
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
        self.decay_level = 0.0  # 0.0 to 1.0
        self.target_decay = 0.5  # Target decay level
        
        # Characters decay at different rates
        self.char_decay = [0.0] * len(text)
        
        # Wave animation parameters
        self.wave_amp = 3
        self.wave_freq = 0.1
        self.wave_speed = 2
        self.time = 0
        
        # Glitch effect parameters
        self.last_glitch = 0
        self.glitch_interval = 300  # ms
        self.glitch_chars = "!@#$%^&*()-_=+[]{}|;:,.<>/?`~"
    
    def update(self, delta_time):
        """
        Update the decay effect
        
        Args:
            delta_time (float): Time in seconds since last update
        """
        self.time += delta_time
        
        # Progress toward target decay
        decay_diff = self.target_decay - self.decay_level
        if abs(decay_diff) > 0.01:
            # Approach target decay level
            self.decay_level += decay_diff * 0.01
        else:
            # Randomize target occasionally
            if random.random() < 0.001:
                self.target_decay = random.uniform(0.3, 0.7)
        
        # Update individual character decay
        for i in range(len(self.char_decay)):
            # Characters decay toward global decay level
            diff = self.decay_level - self.char_decay[i]
            self.char_decay[i] += diff * 0.1
            
            # Add some randomness
            if random.random() < 0.02:
                self.char_decay[i] += random.uniform(-0.05, 0.05)
            
            # Clamp values
            self.char_decay[i] = max(0.0, min(1.0, self.char_decay[i]))
    
    def draw(self, surface):
        """
        Draw the decaying text
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        text_width = 0
        rendered_chars = []
        
        # First pass - calculate total width and render characters
        for i, char in enumerate(self.text):
            decay = self.char_decay[i]
            
            # Color effect based on decay
            char_color = (
                min(255, self.color[0] + int(decay * 100)),
                max(0, self.color[1] - int(decay * 150)),
                max(0, self.color[2] - int(decay * 150))
            )
            
            # Render character
            rendered_char = self.font.render(char, True, char_color)
            
            # Apply glitch effect randomly
            if random.random() < decay * 0.2:
                glitch_char = random.choice(self.glitch_chars)
                rendered_char = self.font.render(glitch_char, True, char_color)
            
            # Apply rotation based on decay
            if decay > 0.3:
                angle = math.sin(self.time + i) * decay * 8
                rendered_char = pygame.transform.rotate(rendered_char, angle)
            
            rendered_chars.append(rendered_char)
            text_width += rendered_char.get_width()
        
        # Calculate start position to center the text
        start_x = self.pos[0] - text_width // 2
        current_x = start_x
        
        # Second pass - draw each character with effects
        for i, char_surface in enumerate(rendered_chars):
            decay = self.char_decay[i]
            
            # Wave effect
            wave_y = int(math.sin(self.time * self.wave_speed + i * self.wave_freq) * 
                         self.wave_amp * (1.0 + decay * 2))
            
            # Position for this character
            char_pos = (current_x, self.pos[1] + wave_y)
            
            # Apply alpha based on decay
            alpha = max(0, min(255, int(255 - decay * 100)))
            char_surface.set_alpha(alpha)
            
            # Draw the character
            surface.blit(char_surface, char_pos)
            
            # Add a glow effect for highly decayed characters
            if decay > 0.5:
                glow_surface = pygame.Surface((char_surface.get_width() + 4, 
                                             char_surface.get_height() + 4), pygame.SRCALPHA)
                glow_color = (255, 0, 0, int(100 * decay))
                pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), 0)
                
                # Draw the glow under the character
                glow_pos = (char_pos[0] - 2, char_pos[1] - 2)
                surface.blit(glow_surface, glow_pos, special_flags=pygame.BLEND_ADD)
            
            # Update x position for next character
            current_x += char_surface.get_width()

def run_start_screen():
    """Display the start screen with decaying logo and wait for input"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Digital Decay")
    clock = pygame.time.Clock()
    
    # Create decay engine for visuals
    decay_engine = DecayEngine(decay_time=30)  # Faster decay for visual effect
    
    # Create decaying text elements
    title_text = DecayingText(
        "DIGITAL DECAY",
        72,
        (0, 255, 0),  # Green
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
    )
    
    prompt_text = DecayingText(
        "Press ENTER to start",
        36,
        (200, 200, 200),  # Light gray
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3)
    )
    
    # Create particles for background
    particles = []
    for _ in range(100):
        particle = {
            'x': random.randint(0, SCREEN_WIDTH),
            'y': random.randint(0, SCREEN_HEIGHT),
            'size': random.randint(1, 3),
            'speed': random.uniform(10, 50),
            'direction': random.uniform(0, math.pi * 2),
            'color': (random.randint(0, 100), 
                     random.randint(100, 200), 
                     random.randint(0, 100)),
            'alpha': random.randint(50, 200)
        }
        particles.append(particle)
    
    # Screen transition effect
    fade_alpha = 255  # Start with black screen
    fade_in = True
    fade_out = False
    
    # Keep track of time
    start_time = time.time()
    last_time = start_time
    
    # Main loop
    running = True
    while running:
        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time
        
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
        
        # Update decay values
        decay_engine.update(delta_time)
        title_text.update(delta_time)
        prompt_text.update(delta_time)
        
        # Update particles
        for particle in particles:
            particle['x'] += math.cos(particle['direction']) * particle['speed'] * delta_time
            particle['y'] += math.sin(particle['direction']) * particle['speed'] * delta_time
            
            # Wrap around screen edges
            if particle['x'] < 0:
                particle['x'] = SCREEN_WIDTH
            elif particle['x'] > SCREEN_WIDTH:
                particle['x'] = 0
            if particle['y'] < 0:
                particle['y'] = SCREEN_HEIGHT
            elif particle['y'] > SCREEN_HEIGHT:
                particle['y'] = 0
        
        # Handle fade transitions
        if fade_in:
            fade_alpha = max(0, fade_alpha - 255 * delta_time)
            if fade_alpha <= 0:
                fade_in = False
        
        if fade_out:
            fade_alpha = min(255, fade_alpha + 510 * delta_time)
            if fade_alpha >= 255:
                running = False
        
        # Draw background
        screen.fill((0, 0, 0))
        
        # Draw grid pattern
        grid_size = 50
        grid_alpha = int(30 * (1.0 - decay_engine.decay_percentage / 100.0))
        grid_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        for x in range(0, SCREEN_WIDTH, grid_size):
            pygame.draw.line(grid_surface, (0, 255, 0, grid_alpha), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, grid_size):
            pygame.draw.line(grid_surface, (0, 255, 0, grid_alpha), (0, y), (SCREEN_WIDTH, y))
        
        screen.blit(grid_surface, (0, 0))
        
        # Draw particles
        for particle in particles:
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                particle_surface, 
                (*particle['color'], particle['alpha']), 
                (particle['size'], particle['size']), 
                particle['size']
            )
            screen.blit(particle_surface, (particle['x'] - particle['size'], particle['y'] - particle['size']))
        
        # Draw text elements
        title_text.draw(screen)
        
        # Make the prompt text blink
        if int(current_time * 2) % 2 == 0:
            prompt_text.draw(screen)
        
        # Draw fade overlay
        if fade_alpha > 0:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, int(fade_alpha)))
            screen.blit(fade_surface, (0, 0))
        
        # Update screen
        pygame.display.flip()
        clock.tick(FPS)
    
    # Return to main game
    return True

if __name__ == "__main__":
    run_start_screen()