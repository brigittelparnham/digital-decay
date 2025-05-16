"""
game1.py - Grid block rejuvenation game with slower decay (1:45 minute target)
"""
import pygame
import random
import math
import json
import os
import sys
from utils.decay_bar import DecayBar
from utils.color_utils import load_jetbrains_mono_font
from utils.asset_utils import get_asset_path


# Load the decay grids JSON
json_path = get_asset_path('decay_grids.json')
with open(json_path, 'r') as f:
    DECAY_GRIDS = json.load(f)


class Block:
    """Represents a single block in the grid"""
    
    def __init__(self, rect, row, col, initial_decay=0.0):
        """
        Initialize a block
        
        Args:
            rect (pygame.Rect): Rectangle defining position and size
            row (int): Row index in the grid
            col (int): Column index in the grid
            initial_decay (float): Initial decay value (0.0 to 1.0)
        """
        self.rect = rect
        self.row = row
        self.col = col
        self.last_click_time = 0
        
        # Get the 6 color stages for this block position
        self.color_stages = self._get_block_colors()
        
        # Individual decay state - each block has its own decay rate
        self.decay_value = initial_decay  # Initialize based on incoming value
        
        # SLOWER DECAY: Reduce decay speed range by ~50%
        self.decay_speed = random.uniform(0.02, 0.06)  # Reduced from (0.05, 0.12)
        
        # Current discrete stage (0-5)
        self.current_stage = min(5, int(self.decay_value * 6))
    
    def _get_block_colors(self):
        """Get the 6 color stages for this block position"""
        colors = []
        for stage in DECAY_GRIDS["stages"]:
            hex_color = stage["grid"][self.row][self.col]
            # Convert hex to RGB
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            colors.append((r, g, b))
        return colors
    
    def rejuvenate(self):
        """
        Handle click on this block - reset to healthy state
        
        Returns:
            float: Amount of decay removed (0.0 to 1.0)
        """
        self.last_click_time = pygame.time.get_ticks()
        
        # Store old decay for return value
        old_decay = self.decay_value
        
        # Reset to fully healthy
        self.decay_value = 0.0
        self.current_stage = 0
        
        # Return how much decay was removed (0.0 to 1.0)
        return old_decay
    
    def update_decay(self, delta_time, global_decay_factor):
        """
        Update this block's individual decay
        
        Args:
            delta_time (float): Time since last update in seconds
            global_decay_factor (float): Factor affecting decay speed (0.0 to 1.0)
                                        Higher means faster decay
                                        
        Returns:
            bool: True if the stage changed, False otherwise
        """
        # Store old stage for comparison
        old_stage = self.current_stage
        
        # Individual decay progression
        # SLOWER DECAY: Reduce the slowdown factor to slow overall decay
        slowdown_factor = 0.3  # Reduced from 0.6 (lower = slower decay)
        
        self.decay_value += self.decay_speed * delta_time * global_decay_factor * slowdown_factor
        self.decay_value = max(0.0, min(1.0, self.decay_value))
        
        # Update discrete stage based on decay value (0-5)
        self.current_stage = min(5, int(self.decay_value * 6))
        
        # Return whether the stage changed
        return self.current_stage != old_stage
    
    def update(self, delta_time, global_decay_factor):
        """
        Update color based on decay level
        
        Args:
            delta_time (float): Time since last update in seconds
            global_decay_factor (float): Factor affecting decay speed
            
        Returns:
            bool: True if the stage changed, False otherwise
        """
        # Update individual decay value
        return self.update_decay(delta_time, global_decay_factor)
    
    def draw(self, surface):
        """Draw the block"""
        # Draw main block with current stage color
        pygame.draw.rect(surface, self.color_stages[self.current_stage], self.rect)
        
        # Draw border
        pygame.draw.rect(surface, (150, 150, 150), self.rect, 2)  # 2-pixel border for better visibility
        
        # Add highlight effect if recently clicked
        current_time = pygame.time.get_ticks()
        if current_time - self.last_click_time < 500:  # 500ms highlight effect
            highlight_alpha = 255 - int(255 * (current_time - self.last_click_time) / 500)
            highlight = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            highlight.fill((255, 255, 255, highlight_alpha))
            surface.blit(highlight, self.rect)

class Game1:
    """Grid block rejuvenation game"""
    
    def __init__(self, decay_engine, screen_width, screen_height):
        """
        Initialize the game
        
        Args:
            decay_engine (DecayEngine): Reference to the decay engine
            screen_width (int): Width of the screen
            screen_height (int): Height of the screen
        """
        # Debug options - initialize this first so it can be used throughout initialization
        self.debug = False  # Set to True for verbose console output
        
        self.decay_engine = decay_engine
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Grid Rejuvenation")
        self.clock = pygame.time.Clock()
        
        # Grid dimensions to match Excel sheet
        self.grid_rows = 7
        self.grid_cols = 13
        
        # Load font for text early
        self.font = load_jetbrains_mono_font(24)
        
        # Show loading message
        loading_text = self.font.render("Creating Grid Blocks...", True, (173, 180, 125))
        loading_rect = loading_text.get_rect(center=(screen_width // 2, screen_height // 2))
        self.screen.fill((0, 0, 0))
        self.screen.blit(loading_text, loading_rect)
        pygame.display.flip()
        
        # Get initial decay percentage from decay engine
        initial_decay = 1.0 - (self.decay_engine.decay_percentage / 100.0)
        
        # Calculate block size based on screen dimensions
        margin_horizontal = 50  # Margin from screen edges
        margin_top = 50  # Margin from top
        margin_bottom = 80  # Extra margin from bottom to avoid decay bar
        
        grid_width = self.screen_width - 2 * margin_horizontal
        grid_height = self.screen_height - margin_top - margin_bottom
        
        # Calculate exact block dimensions (use integer division to avoid float issues)
        block_width = grid_width // self.grid_cols
        block_height = grid_height // self.grid_rows
        
        # Create a loading bar
        bar_width = 400
        bar_height = 20
        bar_x = (self.screen_width - bar_width) // 2
        bar_y = self.screen_height // 2 + 40
        
        # Create blocks
        self.blocks = []
        total_blocks = self.grid_rows * self.grid_cols
        blocks_created = 0
        
        if self.debug:
            print(f"Creating {self.grid_rows}x{self.grid_cols} grid with blocks of size {block_width}x{block_height}")
        
        for row in range(self.grid_rows):
            # Update loading progress
            progress = (row / self.grid_rows) * 100
            bar_fill_width = int(bar_width * (row / self.grid_rows))
            
            # Draw progress bar
            self.screen.fill((0, 0, 0))
            self.screen.blit(loading_text, loading_rect)
            pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.screen, (173, 180, 125), (bar_x, bar_y, bar_fill_width, bar_height))
            pygame.display.flip()
            
            for col in range(self.grid_cols):
                # Calculate block position (use integers for precision)
                x = margin_horizontal + (col * block_width)
                y = margin_top + (row * block_height)
                
                # Create rectangle with integer coordinates
                rect = pygame.Rect(int(x), int(y), int(block_width), int(block_height))
                
                # SLOWER DECAY: Start with less initial decay for longer gameplay
                block_initial_decay = max(0.1, initial_decay * random.uniform(0.6, 1.2))
                block_initial_decay = min(0.85, block_initial_decay)  # Cap at 0.85 (reduced from 0.95)
                
                # Create and add the block
                block = Block(rect, row, col, block_initial_decay)
                self.blocks.append(block)
                blocks_created += 1
                
                # Update progress bar (but not too frequently)
                if col % 4 == 0:
                    bar_fill_width = int(bar_width * (blocks_created / total_blocks))
                    pygame.draw.rect(self.screen, (173, 180, 125), (bar_x, bar_y, bar_fill_width, bar_height))
                    pygame.display.flip()
        
        # Show completion message
        finished_text = self.font.render("Grid Ready!", True, (173, 180, 125))
        finished_rect = finished_text.get_rect(center=(screen_width // 2, screen_height // 2))
        self.screen.fill((0, 0, 0))
        self.screen.blit(finished_text, finished_rect)
        pygame.draw.rect(self.screen, (173, 180, 125), (bar_x, bar_y, bar_width, bar_height))
        pygame.display.flip()
        pygame.time.delay(300)
        
        # Create decay bar
        self.decay_bar = DecayBar(pygame.Rect(0, screen_height - 40, screen_width, 30), 
                                decay_engine, full_width=True)
        
        # Game state initialization
        self.click_count = 0
        self.last_time = pygame.time.get_ticks()
        self.back_button = None
        
        # Start time for game duration tracking
        self.start_time = pygame.time.get_ticks()
        
        # Force initial sync to set the decay bar to match the grid state
        self.sync_decay_with_grid(force=True)
    
    def handle_click(self, pos):
        """
        Handle a mouse click
        
        Args:
            pos (tuple): Mouse position (x, y)
            
        Returns:
            bool: True if a block was clicked, False otherwise
        """
        if self.debug:
            print(f"Click detected at position: {pos}")
        
        for block in self.blocks:
            if block.rect.collidepoint(pos):
                self.click_count += 1
                
                # Store old decay for calculating change
                old_decay = block.decay_value
                old_stage = block.current_stage
                
                # Reset the block to healthy state
                block.rejuvenate()
                
                if self.debug:
                    print(f"Block at row {block.row}, col {block.col} rejuvenated from stage {old_stage+1} to 1")
                
                # SLOWER DECAY: Provide a slight bonus to global health when clicking
                # This makes the game more forgiving
                rejuvenation_bonus = 0.2  # Added bonus
                fraction_of_grid = 1.0 / len(self.blocks)
                bonus_health = (old_decay + rejuvenation_bonus) * fraction_of_grid * 100.0
                self.decay_engine.modify_decay(bonus_health)
                
                # Update global decay to reflect this change immediately
                self.sync_decay_with_grid()
                
                return True
        
        return False
    
    def calculate_grid_health(self):
        """
        Calculate the overall grid health percentage
        
        Returns:
            float: Grid health percentage (0.0 to 100.0)
        """
        if not self.blocks:
            return 100.0  # Default to healthy if no blocks
                
        # Calculate average decay across all blocks
        total_decay = sum(block.decay_value for block in self.blocks)
        avg_decay = total_decay / len(self.blocks)
        
        # Convert to percentage (0.0 to 100.0)
        # 0.0 decay = 100% health, 1.0 decay = 0% health
        health_percentage = (1.0 - avg_decay) * 100.0
        
        return health_percentage
    
    def sync_decay_with_grid(self, force=False):
        """
        Synchronize the global decay engine with the grid state
        
        Args:
            force (bool): If True, force sync regardless of difference
        """
        # Calculate grid health percentage
        grid_health = self.calculate_grid_health()
        current_health = self.decay_engine.decay_percentage
        
        # Only update if there's a significant difference or forced
        if force or abs(grid_health - current_health) > 1.0:
            # SLOWER DECAY: Make sync more gradual for smoother experience
            change_amount = (grid_health - current_health) * 0.4  # More gradual change
            self.decay_engine.modify_decay(change_amount)
            
            # Debug output if enabled
            if self.debug:
                print(f"Updated global health toward grid: {grid_health:.1f}%")
    
    def draw_back_button(self, surface):
        """Draw the back button with green outline, black middle and green text"""
        button_rect = pygame.Rect(self.screen_width - 100, 20, 80, 30)
        
        # Black background
        pygame.draw.rect(surface, (0, 0, 0), button_rect)
        
        # Green outline (2 pixels thick)
        pygame.draw.rect(surface, (255, 255, 255), button_rect, 2)
        
        # Green text
        text = self.font.render("Back", True, (255, 255, 255))
        text_rect = text.get_rect(center=button_rect.center)
        surface.blit(text, text_rect)
        
        return button_rect
    
    def draw_stats(self, surface):
        """Draw game statistics"""
        # Calculate average decay across all blocks
        total_decay = sum(block.decay_value for block in self.blocks)
        avg_decay = total_decay / len(self.blocks)
        
        # Count blocks in different decay stages
        stage_counts = [0] * 6
        for block in self.blocks:
            stage_counts[block.current_stage] += 1
        
        # Calculate elapsed time
        elapsed_seconds = (pygame.time.get_ticks() - self.start_time) / 1000
        minutes = int(elapsed_seconds / 60)
        seconds = int(elapsed_seconds % 60)
        
        # Draw statistics with time
        stats_text = f"Clicks: {self.click_count} | Grid Health: {(100.0 - avg_decay * 100.0):.1f}% | Time: {minutes}:{seconds:02d}"
        text = self.font.render(stats_text, True, (255, 255, 255))
        surface.blit(text, (20, self.screen_height - 30))
        
        # Draw block stage distribution
        for i, count in enumerate(stage_counts):
            if count > 0:
                color = (0, 255, 0) if i == 0 else (255, 165, 0) if i < 3 else (255, 0, 0)
                stage_text = f"Stage {i+1}: {count}"
                stage_surface = self.font.render(stage_text, True, color)
                surface.blit(stage_surface, (20 + i * 100, 20))
    
    def update(self):
        """Update game state and handle events"""
        # Calculate delta time
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - self.last_time) / 1000.0  # Convert to seconds
        self.last_time = current_time
        
        # SLOWER DECAY: Reduce global decay factor acceleration
        # This creates a more manageable decay curve that targets ~1:45 gameplay
        global_decay_factor = 1.4 - (self.decay_engine.decay_percentage / 150.0)  # Reduced from 2.0
        global_decay_factor = max(0.5, min(1.3, global_decay_factor))  # Capped at 1.3 (was 1.8)
        
        # Update all blocks with their individual decay rates
        stages_changed = False
        for block in self.blocks:
            if block.update(delta_time, global_decay_factor):
                stages_changed = True
        
        # If any stages changed, update the global decay
        if stages_changed:
            self.sync_decay_with_grid()
        
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
                        print("Back button clicked in Game1")
                        return "main_menu"
                    
                    # Handle click on a block
                    self.handle_click(event.pos)
        
        return True
    
    def draw(self):
        """Draw all game elements"""
        # Fill background with black
        self.screen.fill((0, 0, 0))
        
        # Draw all blocks
        for block in self.blocks:
            block.draw(self.screen)
        
        # Draw UI elements
        self.decay_bar.draw(self.screen)
        self.back_button = self.draw_back_button(self.screen)
       # self.draw_stats(self.screen)
    
    def run(self):
        """Run the game loop"""
        running = True
        while running:
            result = self.update()
            
            # Check for 0% decay
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