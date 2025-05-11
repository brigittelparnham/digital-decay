"""
game1.py - Grid block rejuvenation game with individual decay rates (slower version)
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
        # SLOWER: Reduce decay speed range by 4x
        self.decay_speed = random.uniform(0.05, 0.1)  # Individual decay rate per second (was 0.05-0.2)
        
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
        Handle click on this block
        
        Returns:
            float: Amount of decay reduced (for affecting global decay)
        """
        self.last_click_time = pygame.time.get_ticks()
        
        # Calculate how much decay was removed
        old_decay = self.decay_value
        self.decay_value = 0.0  # Reset to fully healthy
        self.current_stage = 0  # Reset to first stage
        
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
        # SLOWER: Apply a global slowdown factor of 0.5 to all decay
        slowdown_factor = 0.2  # Global slowdown (new)
        self.decay_value += self.decay_speed * delta_time * global_decay_factor * slowdown_factor
        self.decay_value = max(0.0, min(1.0, self.decay_value))
        
        # Update discrete stage based on decay value
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
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 1)
        
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
        self.decay_engine = decay_engine
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Grid Rejuvenation")
        self.clock = pygame.time.Clock()
        
        # Grid dimensions to match Excel sheet
        self.grid_rows = 7
        self.grid_cols = 13
        
        # Get initial decay percentage from decay engine
        initial_decay = 1.0 - (self.decay_engine.decay_percentage / 100.0)
        
        # Create a loading indicator
        loading_font = load_jetbrains_mono_font(24)
        loading_text = loading_font.render("Creating Grid Blocks...", True, (0, 255, 0))
        loading_rect = loading_text.get_rect(center=(screen_width // 2, screen_height // 2))
        
        # Show initial loading message
        self.screen.fill((0, 0, 0))
        self.screen.blit(loading_text, loading_rect)
        pygame.display.flip()
        
        # Create blocks - create rows incrementally to avoid freezing
        self.blocks = []
        
        # Calculate block size based on screen dimensions
        margin_horizontal = 50  # Margin from screen edges
        margin_top = 50  # Margin from top
        margin_bottom = 80  # Extra margin from bottom to avoid decay bar
        
        grid_width = self.screen_width - 2 * margin_horizontal
        grid_height = self.screen_height - margin_top - margin_bottom
        
        block_width = grid_width / self.grid_cols
        block_height = grid_height / self.grid_rows
        
        # Create blocks with loading bar updates
        total_blocks = self.grid_rows * self.grid_cols
        blocks_created = 0
        
        # Create a loading bar
        bar_width = 400
        bar_height = 20
        bar_x = (self.screen_width - bar_width) // 2
        bar_y = self.screen_height // 2 + 40
        
        for row in range(self.grid_rows):
            # Update loading progress bar
            progress = (row / self.grid_rows) * 100
            bar_fill_width = int(bar_width * (row / self.grid_rows))
            
            # Draw progress bar
            self.screen.fill((0, 0, 0))
            self.screen.blit(loading_text, loading_rect)
            pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.screen, (0, 255, 0), (bar_x, bar_y, bar_fill_width, bar_height))
            pygame.display.flip()
            
            for col in range(self.grid_cols):
                x = margin_horizontal + col * block_width
                y = margin_top + row * block_height
                rect = pygame.Rect(x, y, block_width, block_height)
                
                # Calculate individual initial decay with some randomness
                block_initial_decay = initial_decay * random.uniform(0.7, 1.3)
                block_initial_decay = max(0.0, min(1.0, block_initial_decay))
                
                self.blocks.append(Block(rect, row, col, block_initial_decay))
                blocks_created += 1
                
                # Update very frequently would slow things down, so we update every column
                if col % 4 == 0:  # Update every 4 columns
                    bar_fill_width = int(bar_width * (blocks_created / total_blocks))
                    pygame.draw.rect(self.screen, (0, 255, 0), (bar_x, bar_y, bar_fill_width, bar_height))
                    pygame.display.flip()
                    
        # Finish loading UI
        self.screen.fill((0, 0, 0))
        finished_text = loading_font.render("Grid Ready!", True, (0, 255, 0))
        finished_rect = finished_text.get_rect(center=(screen_width // 2, screen_height // 2))
        self.screen.blit(finished_text, finished_rect)
        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, (0, 255, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.display.flip()
        pygame.time.delay(300)  # Brief pause to show completion
        
        # Create decay bar - full width at bottom
        self.decay_bar = DecayBar(pygame.Rect(0, screen_height - 40, screen_width, 30), decay_engine, full_width=True)
        
        # Font for text
        self.font = load_jetbrains_mono_font(24)
        
        # Game state
        self.click_count = 0
        
        # For calculating delta time
        self.last_time = pygame.time.get_ticks()
        
        # Back button
        self.back_button = None
        
        # Timer for updating global decay
        self.update_timer = 0
        # SLOWER: Less frequent updates to global decay
        self.update_interval = 2.0  # Update global decay every 2 seconds
    
    def create_grid(self, initial_decay):
        """
        Create the grid of blocks
        
        Args:
            initial_decay (float): Initial decay value (0.0 to 1.0)
            
        Returns:
            list: List of Block objects
        """
        blocks = []
        
        # Calculate block size based on screen dimensions
        margin_horizontal = 50  # Margin from screen edges
        margin_top = 50  # Margin from top
        margin_bottom = 80  # Extra margin from bottom to avoid decay bar
        
        grid_width = self.screen_width - 2 * margin_horizontal
        grid_height = self.screen_height - margin_top - margin_bottom
        
        block_width = grid_width / self.grid_cols
        block_height = grid_height / self.grid_rows
        
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                x = margin_horizontal + col * block_width
                y = margin_top + row * block_height
                rect = pygame.Rect(x, y, block_width, block_height)
                
                # Calculate individual initial decay with some randomness
                block_initial_decay = initial_decay * random.uniform(0.7, 1.3)
                block_initial_decay = max(0.0, min(1.0, block_initial_decay))
                
                blocks.append(Block(rect, row, col, block_initial_decay))
        
        return blocks
    
    def calculate_grid_decay(self):
        """
        Calculate the overall grid decay percentage
        
        Returns:
            float: Grid decay percentage (0.0 to 100.0)
        """
        if not self.blocks:
            return 0.0
            
        # Calculate average decay across all blocks
        total_decay = sum(block.decay_value for block in self.blocks)
        avg_decay = total_decay / len(self.blocks)
        
        # Convert to percentage (0.0 to 100.0)
        # 0.0 decay = 100% health, 1.0 decay = 0% health
        return (1.0 - avg_decay) * 100.0
    
    def handle_click(self, pos):
        """
        Handle a mouse click
        
        Args:
            pos (tuple): Mouse position (x, y)
            
        Returns:
            bool: True if a block was clicked, False otherwise
        """
        for block in self.blocks:
            if block.rect.collidepoint(pos):
                self.click_count += 1
                decay_removed = block.rejuvenate()
                
                # Calculate how much this affects global decay
                # Each block represents a fraction of the total grid
                fraction_of_grid = 1.0 / len(self.blocks)
                
                # Convert block decay to global decay percentage points
                # More decayed blocks give more points when rejuvenated
                # SLOWER: Increase the effect of rejuvenation by 50%
                boost_factor = 1.5  # Increase rejuvenation effect (new)
                decay_percentage_change = decay_removed * fraction_of_grid * 100.0 * boost_factor
                
                # Apply to global decay
                self.decay_engine.modify_decay(decay_percentage_change)
                
                return True
        
        return False
    
    def sync_decay_with_grid(self):
        """Synchronize the global decay engine with the grid state"""
        grid_decay_percentage = self.calculate_grid_decay()
        current_decay_percentage = self.decay_engine.decay_percentage
        
        # Only update if there's a significant difference
        if abs(grid_decay_percentage - current_decay_percentage) > 1.0:
            # Calculate change needed
            change = grid_decay_percentage - current_decay_percentage
            
            # Apply change gradually for smoother transition
            # SLOWER: More gradual synchronization
            change_to_apply = change * 0.05  # Apply 5% of the difference (was 10%)
            
            # Update decay engine
            self.decay_engine.modify_decay(change_to_apply)
    
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
    
    def draw_stats(self, surface):
        """Draw game statistics"""
        # Calculate average decay across all blocks
        total_decay = sum(block.decay_value for block in self.blocks)
        avg_decay = total_decay / len(self.blocks)
        
        # Count blocks in different decay stages
        stage_counts = [0] * 6
        for block in self.blocks:
            stage_counts[block.current_stage] += 1
        
        # Draw statistics
        stats_text = f"Clicks: {self.click_count} | Grid Decay: {(avg_decay * 100.0):.1f}% | System Health: {self.decay_engine.decay_percentage:.1f}%"
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
        
        # Update timer for syncing with grid
        self.update_timer += delta_time
        if self.update_timer >= self.update_interval:
            self.update_timer = 0
            self.sync_decay_with_grid()
        
        # Update decay naturally over time
        # SLOWER: Apply a time scaling factor to make natural decay slower
        time_scale = 0.5  # Half speed (new)
        self.decay_engine.update(delta_time * time_scale)
        
        # Calculate global decay factor for block updates
        # As global decay increases (health decreases), blocks decay faster
        # Global decay percentage: 100 = fully healthy, 0 = fully decayed
        global_decay_factor = 1.0 - (self.decay_engine.decay_percentage / 100.0)
        # SLOWER: Limit the maximum decay factor to slow down late-game decay
        global_decay_factor = max(0.1, min(1.5, global_decay_factor))  # Limit range (was 2.0)
        
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
        self.draw_stats(self.screen)
    
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