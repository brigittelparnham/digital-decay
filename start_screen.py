"""
start_screen.py - Start screen with PNG images and glitchy effects
"""
import os
import sys
import pygame
import random
import math
import time
import json
from decay_engine import DecayEngine
from utils.color_utils import load_jetbrains_mono_font
from utils.asset_utils import get_asset_path

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Load colors from decay_grids.json
def load_decay_colors():
    """Load color scheme from decay_grids.json"""
    try:
        json_path = get_asset_path('decay_grids.json')
        
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

class GlitchyPNGImage:
    """Class for PNG images that show glitch effects and movement"""
    
    def __init__(self, image_path, pos, glitch_intensity=0.1, scale=1.0, max_width=None, max_height=None):
        """
        Initialize the glitchy PNG image
        
        Args:
            image_path (str): Path to PNG file
            pos (tuple): (x, y) position on screen (center position)
            glitch_intensity (float): How intense the glitch effects should be (0.0 to 1.0)
            scale (float): Scale factor for the image (1.0 = original size)
            max_width (int, optional): Maximum width in pixels
            max_height (int, optional): Maximum height in pixels
        """
        self.original_image = None
        self.current_image = None
        self.pos = pos
        self.base_pos = pos  # Store original position
        self.glitch_intensity = glitch_intensity
        self.scale = scale
        self.max_width = max_width
        self.max_height = max_height
        
        # Load the image
        try:
            loaded_image = pygame.image.load(image_path)
            print(f"Loaded image: {image_path} - Original size: {loaded_image.get_size()}")
            
            # Scale the image if needed
            self.original_image = self._scale_image(loaded_image)
            self.current_image = self.original_image.copy()
            print(f"Final size after scaling: {self.original_image.get_size()}")
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            # Create a placeholder surface
            self.original_image = pygame.Surface((200, 50))
            self.original_image.fill((255, 0, 255))  # Magenta placeholder
            self.current_image = self.original_image.copy()
        
        # Glitch effect parameters
        self.last_glitch = 0
        self.glitch_interval = random.randint(50, 200)  # ms
        self.glitch_duration = 0
        self.glitch_active = False
        
        # Movement parameters for glittering
        self.base_offset = [0, 0]
        self.jitter_amount = 2  # Maximum pixels to jitter
        
        # Time tracking
        self.time = 0
        
        # Color shift parameters
        self.color_shift_intensity = 0
        self.color_shift_direction = random.choice([(1, 0, 0), (0, 1, 0), (0, 0, 1)])
    
    def _scale_image(self, image):
        """
        Scale the image based on scale factor and size constraints
        
        Args:
            image (pygame.Surface): Original image to scale
            
        Returns:
            pygame.Surface: Scaled image
        """
        original_width, original_height = image.get_size()
        
        # Apply scale factor
        new_width = int(original_width * self.scale)
        new_height = int(original_height * self.scale)
        
        # Apply max width/height constraints if specified
        if self.max_width and new_width > self.max_width:
            scale_factor = self.max_width / new_width
            new_width = self.max_width
            new_height = int(new_height * scale_factor)
        
        if self.max_height and new_height > self.max_height:
            scale_factor = self.max_height / new_height
            new_height = self.max_height
            new_width = int(new_width * scale_factor)
        
        # Only scale if size changed
        if (new_width, new_height) != (original_width, original_height):
            return pygame.transform.scale(image, (new_width, new_height))
        else:
            return image
    
    def update(self, delta_time, decay_level):
        """
        Update the glitch effect and movement
        
        Args:
            delta_time (float): Time in seconds since last update
            decay_level (float): Current decay level (0.0 to 1.0)
        """
        self.time += delta_time
        
        # Adjust glitch intensity based on decay level
        current_intensity = self.glitch_intensity * (0.5 + decay_level * 0.5)
        
        # Update glitch state
        current_time = pygame.time.get_ticks()
        if current_time - self.last_glitch > self.glitch_interval:
            self.last_glitch = current_time
            self.glitch_interval = random.randint(50, 300)
            
            # Start glitch effect
            if random.random() < current_intensity:
                self.glitch_active = True
                self.glitch_duration = random.randint(50, 150)
                self.color_shift_intensity = random.uniform(0.1, 0.3) * current_intensity
                self.color_shift_direction = random.choice([(1, 0, 0), (0, 1, 0), (0, 0, 1)])
        
        # Apply glitch effects if active
        if self.glitch_active:
            self.glitch_duration -= delta_time * 1000
            if self.glitch_duration <= 0:
                self.glitch_active = False
                self.current_image = self.original_image.copy()
            else:
                self.apply_glitch_effect()
        
        # Update jitter movement
        jitter_intensity = current_intensity * self.jitter_amount
        self.base_offset[0] = random.uniform(-jitter_intensity, jitter_intensity)
        self.base_offset[1] = random.uniform(-jitter_intensity, jitter_intensity)
    
    def apply_glitch_effect(self):
        """Apply various glitch effects to the image"""
        if not self.original_image:
            return
            
        # Start with original image
        self.current_image = self.original_image.copy()
        
        # Apply color channel shift
        if self.color_shift_intensity > 0:
            # Create color-shifted versions
            red_shift = pygame.Surface(self.original_image.get_size(), pygame.SRCALPHA)
            green_shift = pygame.Surface(self.original_image.get_size(), pygame.SRCALPHA)
            blue_shift = pygame.Surface(self.original_image.get_size(), pygame.SRCALPHA)
            
            # Extract color channels
            pixels = pygame.surfarray.array3d(self.original_image)
            
            # Create shifted versions
            shift_amount = int(self.color_shift_intensity * 10)
            if shift_amount > 0:
                # Red channel shift
                red_pixels = pixels.copy()
                red_pixels[:, :, 1] = 0  # Remove green
                red_pixels[:, :, 2] = 0  # Remove blue
                pygame.surfarray.blit_array(red_shift, red_pixels)
                
                # Shift position slightly
                red_offset = (random.randint(-shift_amount, shift_amount), 
                             random.randint(-shift_amount, shift_amount))
                self.current_image.blit(red_shift, red_offset, special_flags=pygame.BLEND_ADD)
        
        # Apply scanline effect
        if random.random() < 0.3:
            scanline_surface = pygame.Surface(self.current_image.get_size(), pygame.SRCALPHA)
            for y in range(0, self.current_image.get_height(), random.randint(2, 5)):
                pygame.draw.line(scanline_surface, (0, 0, 0, 100), 
                               (0, y), (self.current_image.get_width(), y))
            self.current_image.blit(scanline_surface, (0, 0))
        
        # Apply random pixel corruption
        if random.random() < 0.2:
            corrupt_surface = pygame.Surface(self.current_image.get_size(), pygame.SRCALPHA)
            for _ in range(random.randint(5, 20)):
                x = random.randint(0, self.current_image.get_width() - 1)
                y = random.randint(0, self.current_image.get_height() - 1)
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                pygame.draw.rect(corrupt_surface, color, (x, y, random.randint(1, 5), random.randint(1, 5)))
            self.current_image.blit(corrupt_surface, (0, 0))
    
    def draw(self, surface):
        """
        Draw the glitchy image
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        if not self.current_image:
            return
        
        # Calculate final position with offsets
        final_x = self.base_pos[0] + self.base_offset[0] - self.current_image.get_width() // 2
        final_y = self.base_pos[1] + self.base_offset[1] - self.current_image.get_height() // 2
        
        # Draw the image
        surface.blit(self.current_image, (final_x, final_y))

def run_start_screen():
    """Display the start screen with PNG images and glitchy effects"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Digital Decay")
    clock = pygame.time.Clock()
    
    # Create decay engine for visuals
    decay_engine = DecayEngine(decay_time=30)  # Faster decay for visual effect
    
    # Load decay colors
    healthy_color, warning_color, decay_color = load_decay_colors()
    
    # Load PNG images with their positions
    images = []
    
    # Define positions for each image (center positions)
    # Layout: DIGITAL [DECAY] on one line, GAME below, centered
    # Cubes positioned behind from start of DIGITAL to end of GAME
    # All elements made bigger and properly centered
    
    # Calculate center positions for the layout
    title_y = SCREEN_HEIGHT // 3  # Main title line
    game_y = title_y + 80  # GAME below the main title
    cubes_y = title_y + 20  # Cubes slightly below title line but behind text
    
    image_configs = [
        {
            'path': get_asset_path('images', 'cubes.png'),
            'pos': (SCREEN_WIDTH // 2, title_y),  # Behind and spanning the text area
            'glitch_intensity': 0.2,
            'scale': 1.2,  # Make cubes bigger
            'max_width': 450,  # Wider to span behind text
            'max_height': 180
        },
        {
            'path': get_asset_path('images', 'digital.png'),
            'pos': (SCREEN_WIDTH // 2 - 160, title_y),  # Left part of title
            'glitch_intensity': 0.15,
            'scale': 0.9,  # Make text bigger
            'max_width': 220,
            'max_height': 120
        },
        {
            'path': get_asset_path('images', 'shape_around_decay.png'),
            'pos': (SCREEN_WIDTH // 2, title_y),  # Background for DECAY
            'glitch_intensity': 0.1,
            'scale': 1.3,  # Make shape bigger to fit DECAY
            'max_width': 270,
            'max_height': 140
        },
        {
            'path': get_asset_path('images', 'decay.png'),
            'pos': (SCREEN_WIDTH // 2 - 5, title_y),  # Right part of title (inside shape)
            'glitch_intensity': 0.15,
            'scale': 1.3,  # Make text bigger
            'max_width': 200,
            'max_height': 120
        },
        {
            'path': get_asset_path('images', 'game.png'),
            'pos': (SCREEN_WIDTH // 2 + 140, title_y + 5),  # Below main title, centered
            'glitch_intensity': 0.1,
            'scale': 0.9,  # Make GAME text bigger
            'max_width': 180,
            'max_height': 100
        },
        {
            'path': get_asset_path('images', 'shape_around_enter.png'),
            'pos': (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3 - 5),  # Background for press enter
            'glitch_intensity': 0.05,
            'scale': 0.8,  # Make shape bigger than the text inside
            'max_width': 240,  # Much wider than press_enter text
            'max_height': 100  # Taller than press_enter text
        },
        {
            'path': get_asset_path('images', 'press_enter.png'),
            'pos': (SCREEN_WIDTH // 2 - 7, SCREEN_HEIGHT * 2 // 3),  # Press enter text (inside shape)
            'glitch_intensity': 0.1,
            'scale': 1.1,  # Slightly bigger text but smaller than the shape
            'max_width': 320,
            'max_height': 90
        }
    ]
    
    # Create GlitchyPNGImage objects
    for config in image_configs:
        image = GlitchyPNGImage(
            config['path'], 
            config['pos'], 
            config['glitch_intensity'],
            config.get('scale', 1.0),
            config.get('max_width'),
            config.get('max_height')
        )
        images.append(image)
    
    # Create particles for background
    particles = []
    for _ in range(100):
        particle = {
            'x': random.randint(0, SCREEN_WIDTH),
            'y': random.randint(0, SCREEN_HEIGHT),
            'size': random.randint(1, 3),
            'speed': random.uniform(10, 50),
            'direction': random.uniform(0, math.pi * 2),
            'color': healthy_color,  # Use healthy color for particles
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
    
    # Blinking effect for press enter
    blink_timer = 0
    show_press_enter = True
    
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
        decay_level = 1.0 - (decay_engine.decay_percentage / 100.0)
        
        # Update all images
        for image in images:
            image.update(delta_time, decay_level)
        
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
        
        # Update blinking for press enter
        blink_timer += delta_time
        if blink_timer >= 1.0:  # Blink every second
            show_press_enter = not show_press_enter
            blink_timer = 0
        
        # Draw background
        screen.fill((0, 0, 0))
        
        # Draw grid pattern using healthy color
        grid_size = 50
        # Fixed grid alpha calculation - was based on decay_level (1 - decay_percentage/100) which made it disappear
        # Now based on fade-in progress and time for a nice appearing effect
        if not fade_in and fade_alpha <= 0:
            # Grid slowly appears after initial fade-in
            time_since_start = current_time - start_time
            grid_appearance_factor = min(1.0, time_since_start / 3.0)  # Takes 3 seconds to fully appear
            grid_alpha = int(60 * grid_appearance_factor)  # Increased from 30 to 60 for better visibility
        else:
            grid_alpha = 0  # Hidden during fade-in
            
        if grid_alpha > 0:
            grid_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            
            for x in range(0, SCREEN_WIDTH, grid_size):
                pygame.draw.line(grid_surface, (*healthy_color, grid_alpha), (x, 0), (x, SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, grid_size):
                pygame.draw.line(grid_surface, (*healthy_color, grid_alpha), (0, y), (SCREEN_WIDTH, y))
            
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
        
        # Draw PNG images in order
        # Draw in specific order to ensure proper layering
        image_order = [0, 1, 2, 3, 4, 5, 6]  # cubes, digital, shape_decay, decay, game, shape_enter, press_enter
        
        for i in image_order:
            if i < len(images):
                # Skip press_enter if blinking and should be hidden
                if i == 6 and not show_press_enter:  # press_enter.png
                    continue
                    
                images[i].draw(screen)
        
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