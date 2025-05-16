"""
end_screen.py - End screen with PNG images and original intense glitchy effects
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
        # Get the directory of the current file
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
    """Class for PNG images that show glitch effects and movement - same style as start screen"""
    
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
        
        # Glitch effect parameters - SAME AS START SCREEN
        self.last_glitch = 0
        self.glitch_interval = random.randint(50, 200)  # ms
        self.glitch_duration = 0
        self.glitch_active = False
        
        # Movement parameters for glittering - SAME AS START SCREEN
        self.base_offset = [0, 0]
        self.jitter_amount = 2  # Maximum pixels to jitter
        
        # Time tracking
        self.time = 0
        
        # Color shift parameters - SAME AS START SCREEN
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
        Update the glitch effect and movement - SAME AS START SCREEN
        
        Args:
            delta_time (float): Time in seconds since last update
            decay_level (float): Current decay level (0.0 to 1.0)
        """
        self.time += delta_time
        
        # Adjust glitch intensity based on decay level - SAME AS START SCREEN
        current_intensity = self.glitch_intensity * (0.5 + decay_level * 0.5)
        
        # Update glitch state - SAME AS START SCREEN
        current_time = pygame.time.get_ticks()
        if current_time - self.last_glitch > self.glitch_interval:
            self.last_glitch = current_time
            self.glitch_interval = random.randint(50, 300)
            
            # Start glitch effect - SAME AS START SCREEN
            if random.random() < current_intensity:
                self.glitch_active = True
                self.glitch_duration = random.randint(50, 150)
                self.color_shift_intensity = random.uniform(0.1, 0.3) * current_intensity
                self.color_shift_direction = random.choice([(1, 0, 0), (0, 1, 0), (0, 0, 1)])
        
        # Apply glitch effects if active - SAME AS START SCREEN
        if self.glitch_active:
            self.glitch_duration -= delta_time * 1000
            if self.glitch_duration <= 0:
                self.glitch_active = False
                self.current_image = self.original_image.copy()
            else:
                self.apply_glitch_effect()
        
        # Update jitter movement - SAME AS START SCREEN
        jitter_intensity = current_intensity * self.jitter_amount
        self.base_offset[0] = random.uniform(-jitter_intensity, jitter_intensity)
        self.base_offset[1] = random.uniform(-jitter_intensity, jitter_intensity)
    
    def apply_glitch_effect(self):
        """Apply various glitch effects to the image - EXACT SAME AS START SCREEN"""
        if not self.original_image:
            return
            
        # Start with original image
        self.current_image = self.original_image.copy()
        
        # Apply color channel shift - SAME AS START SCREEN
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
        
        # Apply scanline effect - SAME AS START SCREEN
        if random.random() < 0.3:
            scanline_surface = pygame.Surface(self.current_image.get_size(), pygame.SRCALPHA)
            for y in range(0, self.current_image.get_height(), random.randint(2, 5)):
                pygame.draw.line(scanline_surface, (0, 0, 0, 100), 
                               (0, y), (self.current_image.get_width(), y))
            self.current_image.blit(scanline_surface, (0, 0))
        
        # Apply random pixel corruption - SAME AS START SCREEN
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
        Draw the glitchy image - SAME AS START SCREEN
        
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

def run_end_screen():
    """Display the end screen with PNG images and ORIGINAL intense glitchy background effects"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Digital Decay - DECAYED")
    clock = pygame.time.Clock()
    
    # Load decay colors
    healthy_color, warning_color, decay_color = load_decay_colors()
    
    # Load PNG images for end screen - EXACT SAME POSITIONS AS START SCREEN
    images = []
    
    # Calculate center positions for the layout (exactly like start screen)
    title_y = SCREEN_HEIGHT // 3  # Main title line
    game_y = title_y + 80  # GAME below the main title
    cubes_y = title_y + 20  # Cubes slightly below title line but behind text
    
    image_configs = [
        {
            'path': get_asset_path('images', 'cubes.png'),
            'pos': (SCREEN_WIDTH // 2, title_y),  # Same as start screen
            'glitch_intensity': 0.2,  # SAME AS START SCREEN
            'scale': 1.2,  # Same scale as start
            'max_width': 450,
            'max_height': 180
        },
        {
            'path': get_asset_path('images', 'digital.png'),
            'pos': (SCREEN_WIDTH // 2 - 160, title_y),  # Same as start screen
            'glitch_intensity': 0.15,  # SAME AS START SCREEN
            'scale': 0.9,  # Same scale as start
            'max_width': 220,
            'max_height': 120
        },
        {
            'path': get_asset_path('images', 'shape_around_decay.png'),
            'pos': (SCREEN_WIDTH // 2, title_y),  # Same as start screen
            'glitch_intensity': 0.1,  # SAME AS START SCREEN
            'scale': 1.3,  # Same scale as start
            'max_width': 270,
            'max_height': 140
        },
        {
            'path': get_asset_path('images', 'decay.png'),
            'pos': (SCREEN_WIDTH // 2 - 5, title_y),  # Same as start screen
            'glitch_intensity': 0.15,  # SAME AS START SCREEN
            'scale': 1.3,  # Same scale as start
            'max_width': 200,
            'max_height': 120
        },
        {
            'path': get_asset_path('images', 'game.png'),
            'pos': (SCREEN_WIDTH // 2 + 140, title_y + 5),  # Same as start screen
            'glitch_intensity': 0.1,  # SAME AS START SCREEN
            'scale': 0.9,  # Same scale as start
            'max_width': 180,
            'max_height': 100
        },
        {
            'path': get_asset_path('images', 'shape_around_enter.png'),
            'pos': (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3 - 5),  # Same as start screen
            'glitch_intensity': 0.05,  # SAME AS START SCREEN
            'scale': 0.8,  # Same scale as start
            'max_width': 240,
            'max_height': 100
        },
        {
            'path': get_asset_path('images', 'press_enter.png'),  # KEEP PRESS ENTER for now
            'pos': (SCREEN_WIDTH // 2 - 7, SCREEN_HEIGHT * 2 // 3),  # Same position as press_enter
            'glitch_intensity': 0.1,  # SAME AS START SCREEN
            'scale': 1.1,  # Same scale as start
            'max_width': 320,
            'max_height': 90
        }
    ]
    
    # Create GlitchyPNGImage objects with SAME glitch style as start screen
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
    
    # Set up auto-reset timer (30 seconds)
    start_time = time.time()
    auto_reset_time = 30  # seconds
    
    # Create ORIGINAL end screen particles for background distortion
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
    
    # Blinking effect for press enter - more erratic for end screen
    blink_timer = 0
    show_press_enter = True
    
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
        
        # Update all images
        for image in images:
            image.update(delta_time, 1.0)  # Full decay for end screen
        
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
        
        # Update blinking for press enter - make the prompt text blink at an irregular rate
        if int(current_time * 0.001) % 2 == 0:
            show_press_enter = True
        else:
            show_press_enter = False
        
        # Draw very dark background based on decay color
        r, g, b = decay_color
        dark_bg = (max(0, r//6), max(0, g//6), max(0, b//6))  # Very dark version of decay color
        screen.fill(dark_bg)
        
        # Add digital noise (static) - ORIGINAL INTENSE EFFECT
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
        
        # Add horizontal scan lines - ORIGINAL EFFECT
        scan_y_offset = int(current_time / 50) % 20
        for y in range(scan_y_offset, SCREEN_HEIGHT, 20):
            pygame.draw.line(
                screen,
                (*decay_color, 128),
                (0, y),
                (SCREEN_WIDTH, y),
                1
            )
        
        # Draw glitchy blocks - ORIGINAL INTENSE EFFECT
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
        
        # Draw PNG images in exact same order as start screen
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
    
    # Brief pause
    pygame.time.delay(500)
    
    # Return to start screen
    return True

if __name__ == "__main__":
    run_end_screen()