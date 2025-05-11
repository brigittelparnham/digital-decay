"""
game2.py - Bounce game with decay grid color scheme (Modified)
"""
import pygame
import random
import math
import json
import os
from utils.decay_bar import DecayBar
from utils.color_utils import load_jetbrains_mono_font

# Load the decay grids JSON
# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the project root, then into assets
json_path = os.path.join(current_dir, '..', 'assets', 'decay_grids.json')
with open(json_path, 'r') as f:
    DECAY_GRIDS = json.load(f)

class Paddle:
    """Represents the player-controlled paddle"""
    
    def __init__(self, screen_width, screen_height):
        """
        Initialize the paddle
        
        Args:
            screen_width (int): Width of the screen
            screen_height (int): Height of the screen
        """
        self.width = 100
        self.height = 20
        self.x = (screen_width - self.width) / 2
        # Position paddle higher to avoid decay bar
        self.y = screen_height - self.height - 60
        self.speed = 800  # Pixels per second
        
    def update(self, delta_time, keys, screen_width):
        """
        Update the paddle position based on keyboard input
        
        Args:
            delta_time (float): Time in seconds since last update
            keys (pygame.key.ScancodeWrapper): Current keyboard state
            screen_width (int): Width of the screen
        """
        if keys[pygame.K_LEFT]:
            self.x -= self.speed * delta_time
        if keys[pygame.K_RIGHT]:
            self.x += self.speed * delta_time
        
        # Keep paddle within screen bounds
        self.x = max(0, min(screen_width - self.width, self.x))
    
    def draw(self, surface, decay_engine):
        """
        Draw the paddle
        
        Args:
            surface (pygame.Surface): Surface to draw on
            decay_engine (DecayEngine): Reference to the decay engine for color
        """
        # Use paddle color from decay grid (average of middle row, middle column)
        middle_row = 3  # Middle of 7 rows
        middle_col = 6  # Middle of 13 columns
        color = self._get_decay_color(middle_row, middle_col, decay_engine)
        
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (200, 200, 200), rect, 2)  # Border
    
    def _get_decay_color(self, row, col, decay_engine):
        """Get color from decay grid based on global decay"""
        decay_value = 1.0 - (decay_engine.decay_percentage / 100.0)
        stage_index = min(5, int(decay_value * 6))
        
        # Get color from decay grid
        hex_color = DECAY_GRIDS["stages"][stage_index]["grid"][row][col]
        
        # Convert hex to RGB
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        return (r, g, b)

class Block:
    """Represents a falling block"""
    
    def __init__(self, x, y, width, height, decay_level):
        """
        Initialize a falling block
        
        Args:
            x (float): X position
            y (float): Y position
            width (int): Block width
            height (int): Block height
            decay_level (float): Initial decay level (0.0 to 1.0)
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity_y = random.uniform(100, 250)  # Falling speed
        # No horizontal velocity - blocks only move vertically
        self.velocity_x = 0
        self.decay_level = decay_level
        
        # No hit counter since we don't show scores
        
        # Assign random position in decay grid for consistent colors
        self.grid_row = random.randint(0, 6)
        self.grid_col = random.randint(0, 12)
        
    def update(self, delta_time, screen_width):
        """
        Update the block position
        
        Args:
            delta_time (float): Time in seconds since last update
            screen_width (int): Width of the screen
        
        Returns:
            bool: True if block is still on screen, False if it has fallen off
        """
        self.y += self.velocity_y * delta_time
        
        # Bounce off top of screen
        if self.y < 0:
            self.velocity_y *= -0.9  # Reverse and dampen
            self.y = 0
        
        # Check if fallen off bottom of screen
        return self.y < screen_width
    
    def check_collision(self, paddle):
        """
        Check for collision with paddle
        
        Args:
            paddle (Paddle): The player's paddle
            
        Returns:
            bool: True if collision detected, False otherwise
        """
        # Check if any part of the block overlaps with the paddle
        return (self.x < paddle.x + paddle.width and
                self.x + self.width > paddle.x and
                self.y < paddle.y + paddle.height and
                self.y + self.height > paddle.y)
    
    def handle_collision(self):
        """
        Handle collision with paddle - only vertical bounce, no horizontal movement
        
        Returns:
            float: Amount to modify the global decay percentage
        """
        # Stronger upward bounce, with no horizontal movement
        self.velocity_y *= -1.2
        
        # No hit counter increment since we're not showing scores
        
        # Reduce decay level with each hit (block becomes "healthier")
        old_decay = self.decay_level
        self.decay_level = max(0.0, self.decay_level - 0.2)
        
        # Return the amount of decay reduction for the global decay system
        return (old_decay - self.decay_level) * 2.0
    
    def get_color(self, decay_engine):
        """
        Get the block's color based on its decay level using decay grid
        
        Args:
            decay_engine (DecayEngine): Reference to the decay engine
            
        Returns:
            tuple: RGB color tuple
        """
        # Get color based on block's individual decay level
        stage_index = min(5, int(self.decay_level * 6))
        
        # Get color from assigned grid position
        hex_color = DECAY_GRIDS["stages"][stage_index]["grid"][self.grid_row][self.grid_col]
        
        # Convert hex to RGB
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # Apply global decay effect
        color = decay_engine.get_decay_color((r, g, b))
        
        # Ensure color values are integers and within valid range
        return (
            max(0, min(255, int(color[0]))),
            max(0, min(255, int(color[1]))),
            max(0, min(255, int(color[2])))
        )
    
    def draw(self, surface, decay_engine):
        """
        Draw the block - no score display
        
        Args:
            surface (pygame.Surface): Surface to draw on
            decay_engine (DecayEngine): Reference to the decay engine
        """
        color = self.get_color(decay_engine)
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (200, 200, 200), rect, 2)  # Border
        
        # No hit count display

# No custom decay bar

class Game2:
    """Bounce game where you keep blocks from falling with a paddle"""
    
    def __init__(self, decay_engine, screen_width, screen_height):
        """
        Initialize the game with loading screen
        """
        self.decay_engine = decay_engine
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Bounce Game")
        self.clock = pygame.time.Clock()
        
        # Show loading screen
        loading_font = load_jetbrains_mono_font(24)
        loading_text = loading_font.render("Initializing Game Assets...", True, (0, 255, 0))
        loading_rect = loading_text.get_rect(center=(screen_width // 2, screen_height // 2))
        
        # Draw loading screen
        self.screen.fill((0, 0, 0))
        self.screen.blit(loading_text, loading_rect)
        pygame.display.flip()
        
        # Create paddle
        self.paddle = Paddle(screen_width, screen_height)
        
        # Create initial blocks
        self.blocks = []
        self.spawn_timer = 0
        self.spawn_interval = 2.0  # Time between block spawns in seconds
        
        # Create decay bar - full width at bottom
        self.decay_bar = DecayBar(pygame.Rect(0, screen_height - 40, screen_width, 30), decay_engine, full_width=True)
        
        # Font for text
        self.font = load_jetbrains_mono_font(24)
        
        # For calculating delta time
        self.last_time = pygame.time.get_ticks()
        
        # Back button
        self.back_button = None
        
        # Pre-spawn a few blocks for immediate gameplay
        for _ in range(3):
            self.spawn_block()
        
        # Show game ready message
        self.screen.fill((0, 0, 0))
        ready_text = loading_font.render("Game Ready!", True, (0, 255, 0))
        ready_rect = ready_text.get_rect(center=(screen_width // 2, screen_height // 2))
        self.screen.blit(ready_text, ready_rect)
        pygame.display.flip()
        pygame.time.delay(300)  # Brief pause
    
    def spawn_block(self):
        """Spawn a new block at the top of the screen"""
        width = random.randint(30, 80)
        height = random.randint(20, 40)
        x = random.randint(0, self.screen_width - width)
        
        # Initial decay level is related to global decay
        global_decay = 1.0 - (self.decay_engine.decay_percentage / 100.0)
        decay_level = global_decay * random.uniform(0.5, 1.0)
        
        self.blocks.append(Block(x, 0, width, height, decay_level))
    
    def update_blocks(self, delta_time):
        """
        Update all blocks and handle collisions
        
        Args:
            delta_time (float): Time in seconds since last update
            
        Returns:
            float: Total decay change from all collisions
        """
        total_decay_change = 0.0
        keys = pygame.key.get_pressed()
        
        # Update paddle
        self.paddle.update(delta_time, keys, self.screen_width)
        
        # Update blocks and check for collisions
        blocks_to_remove = []
        for block in self.blocks:
            # Update block position
            if not block.update(delta_time, self.screen_width):
                blocks_to_remove.append(block)
                continue
            
            # Check for collision with paddle
            if block.check_collision(self.paddle):
                decay_change = block.handle_collision()
                total_decay_change += decay_change
        
        # Remove blocks that have fallen off screen
        for block in blocks_to_remove:
            if block in self.blocks:
                self.blocks.remove(block)
        
        # Spawn new blocks
        self.spawn_timer += delta_time
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_block()
        
        return total_decay_change
    
    def draw_back_button(self, surface):
        """Draw the back button with green outline, black middle and green text"""
        button_rect = pygame.Rect(self.screen_width - 100, 20, 80, 30)
        
        # Black background
        pygame.draw.rect(surface, (0, 0, 0), button_rect)
        
        # Green outline (2 pixels thick)
        pygame.draw.rect(surface, (0, 255, 0), button_rect, 2)
        
        # Green text
        text = self.font.render("Back", True, (0, 255, 0))
        text_rect = text.get_rect(center=button_rect.center)
        surface.blit(text, text_rect)
        
        return button_rect
    
    def update(self):
        """Update game state and handle events"""
        # Calculate delta time
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - self.last_time) / 1000.0  # Convert to seconds
        self.last_time = current_time
        
        # Update decay naturally over time
        self.decay_engine.update(delta_time)
        
        # Update blocks and apply decay change
        decay_change = self.update_blocks(delta_time)
        self.decay_engine.modify_decay(decay_change * 10)  # Convert to percentage points
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "main_menu"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check if back button was clicked
                    if self.back_button and self.back_button.collidepoint(event.pos):
                        print("Back button clicked in Game2")
                        return "main_menu"
        
        return True
    
    def draw(self):
        """Draw all game elements"""
        # Fill background with black
        self.screen.fill((0, 0, 0))
        
        # Draw all blocks
        for block in self.blocks:
            block.draw(self.screen, self.decay_engine)
        
        # Draw paddle
        self.paddle.draw(self.screen, self.decay_engine)
        
        # Draw UI elements
        self.decay_bar.draw(self.screen)
        self.back_button = self.draw_back_button(self.screen)
        
        # Draw instructions
        instructions = "Use LEFT/RIGHT arrow keys to move paddle"
        text = self.font.render(instructions, True, (255, 255, 255))
        self.screen.blit(text, (self.screen_width // 2 - text.get_width() // 2, 60))
    

    def run(self):
        """Run the game loop"""
        running = True
        while running:
            result = self.update()
            
            # *** CRITICAL ADDITION: Check for 0% decay ***
            # This ensures each game can trigger the end screen
            if self.decay_engine.decay_percentage <= 0.0:
                print(f"DECAY DETECTED AT 0% IN GAME - Ending game")
                return "end_screen"  # Force transition to end screen
            
            if result is False:
                running = False
                return None
            elif isinstance(result, str):
                return result
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        
        return None