"""
game3.py - Keyboard Simon Says game with DISSOLVE animation frames synced to decay
"""
import pygame
import random
import os
import sys
import time
import re
import json
from utils.decay_bar import DecayBar
from utils.color_utils import load_jetbrains_mono_font
from utils.asset_utils import get_asset_path


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

class BlenderAnimation:
    """Manages a sequence of Blender animation frames from the DISSOLVE sequence"""
    
    def __init__(self, base_dir=None):
        """
        Initialize the animation with DISSOLVE frames
        
        Args:
            base_dir (str): Base directory containing animation frames
        """
        self.frames = []
        self.current_frame = 0
        
        # If no base directory is specified, use the default path
        if base_dir is None:
           base_dir = get_asset_path("blender", "animation")
        
        # Look for rerender folder
        rerender_dir = os.path.join(base_dir, "rerender")
        if os.path.exists(rerender_dir) and os.path.isdir(rerender_dir):
            self.load_dissolve_frames(rerender_dir)
        else:
            print(f"Warning: Rerender directory not found at {rerender_dir}")
            print("Creating default animation frames instead")
            self.create_default_frames(120)  # Create 120 default frames
    
    def load_dissolve_frames(self, rerender_dir):
        """
        Load DISSOLVE animation frames from the rerender directory
        
        Args:
            rerender_dir (str): Path to the directory with DISSOLVE frames
        """
        # Get all PNG files in the directory
        files = [f for f in os.listdir(rerender_dir) if f.endswith('.png') and f.startswith('DISSOLVE')]
        
        # Define a function to extract the frame number from the filename
        def get_frame_number(filename):
            # Extract the number after the underscore
            match = re.search(r'DISSOLVE\d+_(\d+)', filename)
            if match:
                return int(match.group(1))
            return 0
        
        # Sort files by frame number
        files.sort(key=get_frame_number)
        
        print(f"Found {len(files)} DISSOLVE animation frames")
        
        # Load all frames
        for i, filename in enumerate(files):
            file_path = os.path.join(rerender_dir, filename)
            try:
                surface = pygame.image.load(file_path)
                self.frames.append(surface)
                
                # Print progress every 100 frames
                if i % 100 == 0 or i == len(files) - 1:
                    print(f"Loaded {i+1}/{len(files)} frames...")
            except Exception as e:
                print(f"Error loading frame {file_path}: {e}")
        
        self.num_frames = len(self.frames)
        print(f"Successfully loaded {self.num_frames} DISSOLVE animation frames")
    
    def create_default_frames(self, num_frames):
        """
        Create default animation frames when no image files are available
        
        Args:
            num_frames (int): Number of frames to generate
        """
        self.frames = []
        
        for i in range(num_frames):
            # Create a surface with a gradient color based on frame number
            surface = pygame.Surface((800, 600))
            
            # Calculate color gradient (blue to red)
            normalized = i / (num_frames - 1)
            r = int(255 * normalized)
            b = int(255 * (1 - normalized))
            g = int(100 * (0.5 - abs(0.5 - normalized)))
            
            surface.fill((r, g, b))
            
            # Add frame number text
            font = pygame.font.Font(None, 72)
            text = font.render(f"Frame {i+1}/{num_frames}", True, (255, 255, 255))
            text_rect = text.get_rect(center=(400, 300))
            surface.blit(text, text_rect)
            
            # Add to frame list
            self.frames.append(surface)
        
        self.num_frames = len(self.frames)
        print(f"Created {self.num_frames} default animation frames")
    
    def get_frame(self, frame_index):
        """
        Get a specific frame
        
        Args:
            frame_index (int): Index of the frame to get
            
        Returns:
            pygame.Surface: The frame surface
        """
        if not self.frames:
            return None
            
        # Ensure frame_index is within valid range
        frame_index = max(0, min(len(self.frames) - 1, frame_index))
        return self.frames[frame_index]
    
    def get_current_frame(self):
        """
        Get the current frame
        
        Returns:
            pygame.Surface: The current frame surface
        """
        return self.get_frame(self.current_frame)
    
    def advance(self, amount=1):
        """
        Advance the animation by a given number of frames
        
        Args:
            amount (int): Number of frames to advance (can be negative to rewind)
        """
        if not self.frames:
            return
            
        self.current_frame = (self.current_frame + amount) % self.num_frames
    
    def set_frame(self, frame_index):
        """
        Set the current frame
        
        Args:
            frame_index (int): Index of the frame to set as current
        """
        if not self.frames:
            return
            
        self.current_frame = max(0, min(self.num_frames - 1, frame_index))
    
    def set_frame_by_percentage(self, percentage):
        """
        Set frame based on a percentage (0-100)
        
        Args:
            percentage (float): Percentage value (0-100)
        """
        if not self.frames:
            return
            
        # Convert percentage to frame index
        # 100% decay = frame 0, 0% decay = last frame
        frame_index = int((100 - percentage) / 100 * (self.num_frames - 1))
        self.current_frame = max(0, min(self.num_frames - 1, frame_index))
    
    def get_progress(self):
        """
        Get the current progress through the animation
        
        Returns:
            float: Progress from 0.0 to 1.0
        """
        if not self.frames or self.num_frames <= 1:
            return 0
            
        return self.current_frame / (self.num_frames - 1)

class KeyboardKey:
    """Represents a key in the Keyboard Simon Says game"""
    
    def __init__(self, key, key_name, color, sound_id):
        """
        Initialize a key
        
        Args:
            key (int): Pygame key code
            key_name (str): Display name of the key
            color (tuple): RGB color tuple for the key visualization
            sound_id (int): ID of the sound to play when key is pressed
        """
        self.key = key  # Pygame key code
        self.key_name = key_name  # Name to display
        self.color = color
        self.sound_id = sound_id
        self.is_lit = False
        self.lit_time = 0
        self.lit_duration = 0.5  # Seconds to stay lit
    
    def light_up(self):
        """Light up the key"""
        self.is_lit = True
        self.lit_time = time.time()
    
    def update(self):
        """Update key state"""
        if self.is_lit and time.time() - self.lit_time > self.lit_duration:
            self.is_lit = False
    
    def draw(self, surface, rect, decay_engine):
        """
        Draw the key visualization
        
        Args:
            surface (pygame.Surface): Surface to draw on
            rect (pygame.Rect): Rectangle defining position and size
            decay_engine (DecayEngine): Reference to the decay engine
        """
        # Get base color, modified by global decay
        color = decay_engine.get_decay_color(self.color)
        
        # Ensure valid color values
        color = (
            max(0, min(255, int(color[0]))),
            max(0, min(255, int(color[1]))),
            max(0, min(255, int(color[2])))
        )
        
        # If lit, make brighter
        if self.is_lit:
            color = tuple(min(255, c + 100) for c in color)
        
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (200, 200, 200), rect, 2)  # Border
        
        # Draw key name
        font = pygame.font.Font(None, 36)
        text = font.render(self.key_name, True, (255, 255, 255))
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)

class SequenceItem:
    """Represents an item in the sequence with "Computer says" or "Press" instruction"""
    def __init__(self, key_idx, should_press):
        """
        Initialize a sequence item
        
        Args:
            key_idx (int): Index of the key in the keys list
            should_press (bool): Whether the player should press this key (True for "Computer says")
        """
        self.key_idx = key_idx
        self.should_press = should_press

class Game3:
    """Keyboard Simon Says game with DISSOLVE animation frames synced to decay"""
    
    def __init__(self, decay_engine, screen_width, screen_height):
        """
        Initialize the game with loading animations
        """
        self.decay_engine = decay_engine
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Keyboard Simon Says")
        self.clock = pygame.time.Clock()
        
        # Load decay colors for consistent UI theming
        self.healthy_color, self.warning_color, self.decay_color = load_decay_colors()
        
        # Show loading message
        loading_font = load_jetbrains_mono_font(24)
        loading_text = loading_font.render("Loading Animation Frames...", True, self.healthy_color)
        loading_rect = loading_text.get_rect(center=(screen_width // 2, screen_height // 2))
        
        # Draw loading screen
        self.screen.fill((0, 0, 0))
        self.screen.blit(loading_text, loading_rect)
        pygame.display.flip()
        
        # Create Blender animation with the DISSOLVE frames
        frames_dir = os.path.join("assets", "blender", "animation")
        self.animation = BlenderAnimation(frames_dir)
        
        # Create a loading bar showing animation progress
        bar_width = 400
        bar_height = 20
        bar_x = (self.screen_width - bar_width) // 2
        bar_y = self.screen_height // 2 + 40
        
        # Show loading progress bar without animation preview
        frames_loaded = len(self.animation.frames)
        if frames_loaded > 0:
            self.screen.fill((0, 0, 0))
            loading_text = loading_font.render(f"Animation Loaded! ({frames_loaded} frames)", True, self.healthy_color)
            self.screen.blit(loading_text, loading_rect)
            pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.screen, self.healthy_color, (bar_x, bar_y, bar_width, bar_height))
            pygame.display.flip()
            pygame.time.delay(500)  # Brief pause to show completion
        
        # Load UI and game elements
        self.screen.fill((0, 0, 0))
        loading_text = loading_font.render("Creating Game Elements...", True, self.healthy_color)
        self.screen.blit(loading_text, loading_rect)
        pygame.display.flip()
        
        # Create decay bar - full width at bottom
        self.decay_bar = DecayBar(pygame.Rect(0, screen_height - 40, screen_width, 30), decay_engine, full_width=True)
        
        # Font for text
        self.font = load_jetbrains_mono_font(24)
        self.large_font = load_jetbrains_mono_font(32)
        
        # Create keyboard keys for Simon Says
        self.keys = [
            KeyboardKey(pygame.K_w, "W", (255, 0, 0), 0),    # Red - W
            KeyboardKey(pygame.K_a, "A", (0, 255, 0), 1),    # Green - A
            KeyboardKey(pygame.K_s, "S", (0, 0, 255), 2),    # Blue - S
            KeyboardKey(pygame.K_d, "D", (255, 255, 0), 3)   # Yellow - D
        ]
        
        # Mapping of key codes to indices for easy lookup
        self.key_map = {key.key: i for i, key in enumerate(self.keys)}
        
        # Game states
        self.SHOWING_SEQUENCE = 0
        self.WAITING_FOR_PLAYER = 1
        self.SHOWING_RESULT = 2
        
        # For "Computer says" vs "Press" distinction
        self.correct_prefix = "Computer says press"
        self.wrong_prefix = "Press"  # Changed from "Click" to "Press" to avoid confusion
        self.current_instruction = ""
        
        # Game state initialization
        self.state = self.SHOWING_SEQUENCE
        self.sequence = []  # List of SequenceItem objects
        self.player_keys = []  # List of key indices the player has pressed
        self.expected_player_keys = []  # List of key indices player should press (only "Computer says" ones)
        self.sequence_index = 0
        self.next_item_time = 0
        self.sequence_delay = 0.8  # Seconds between keys in sequence
        self.level = 1
        self.score = 0
        
        # Timeout for player input
        self.last_key_time = 0
        self.player_timeout = 3.0  # Seconds to wait after last key press before checking completion
        self.is_timeout_active = False
        
        # Decay adjustment amounts (percentage points)
        self.correct_decay_bonus = 5.0  # Decrease decay by this much for correct answers
        self.wrong_decay_penalty = -2.0  # Increase decay by this much for wrong answers
        
        # Result message timing
        self.result_message = ""
        self.result_display_time = 0
        self.result_duration = 1.5  # How long to show result message
        
        # For calculating delta time
        self.last_time = pygame.time.get_ticks()
        
        # Back button
        self.back_button = None
        
        # Sync animation with current decay percentage
        self.sync_animation_with_decay()
        
        # Show ready message
        self.screen.fill((0, 0, 0))
        ready_text = loading_font.render("Game Ready!", True, self.healthy_color)
        ready_rect = ready_text.get_rect(center=(screen_width // 2, screen_height // 2))
        self.screen.blit(ready_text, ready_rect)
        pygame.display.flip()
        pygame.time.delay(300)  # Brief pause
    
    def sync_animation_with_decay(self):
        """
        Sync the animation frame with the current decay percentage
        """
        if hasattr(self, 'animation') and self.animation.frames:
            decay_percentage = self.decay_engine.decay_percentage
            self.animation.set_frame_by_percentage(decay_percentage)
            # Only print debug info occasionally to avoid console spam
            if random.random() < 0.01:  # 1% chance to print
                print(f"Synced animation to decay: {decay_percentage}% -> Frame {self.animation.current_frame}")
    
    def start_new_level(self, is_reset=False):
        """
        Start a new level
        
        Args:
            is_reset (bool): If True, reset level and score
        """
        if is_reset:
            self.level = 1
            self.score = 0
            
        # Generate sequence for this level
        self.sequence = []
        self.expected_player_keys = []
        
        # Sequence length based on level (minimum 3 items)
        sequence_length = max(3, self.level + 2)
        
        for _ in range(sequence_length):
            # Random key index
            key_idx = random.randint(0, len(self.keys) - 1)
            # 70% chance of "Computer says" (player should press)
            should_press = random.random() < 0.7
            
            # Create sequence item
            sequence_item = SequenceItem(key_idx, should_press)
            self.sequence.append(sequence_item)
            
            # If this is a "Computer says" item, add to expected keys
            if should_press:
                self.expected_player_keys.append(key_idx)
        
        # Ensure there's at least one key to press
        if not self.expected_player_keys:
            # Add one mandatory "Computer says" item
            key_idx = random.randint(0, len(self.keys) - 1)
            self.sequence.append(SequenceItem(key_idx, True))
            self.expected_player_keys.append(key_idx)
        
        # Reset player keys and sequence index
        self.player_keys = []
        self.sequence_index = 0
        
        # Set state to showing sequence
        self.state = self.SHOWING_SEQUENCE
        self.next_item_time = time.time() + 0.5  # Start after a short delay
        
        # Clear instruction
        self.current_instruction = "Watch the sequence..."
        
        # Debug print
        print(f"New level {self.level} sequence created:")
        for i, item in enumerate(self.sequence):
            prefix = "Computer says" if item.should_press else "Press only"
            print(f"  {i+1}: {prefix} {self.keys[item.key_idx].key_name}")
        print(f"Expected player keys: {[self.keys[idx].key_name for idx in self.expected_player_keys]}")
    
    def update_game(self, delta_time):
        """
        Update the Simon Says game state
        
        Args:
            delta_time (float): Time in seconds since last update
            
        Returns:
            float: Amount to modify the global decay percentage
        """
        decay_change = 0.0
        
        current_time = time.time()
        
        # Update all keys
        for key in self.keys:
            key.update()
        
        # Handle different game states
        if self.state == self.SHOWING_SEQUENCE:
            # Showing the sequence to the player
            if current_time >= self.next_item_time:
                if self.sequence_index < len(self.sequence):
                    # Show next item in sequence
                    sequence_item = self.sequence[self.sequence_index]
                    
                    # Light up the key
                    self.keys[sequence_item.key_idx].light_up()
                    
                    # Show instruction with appropriate prefix
                    prefix = self.correct_prefix if sequence_item.should_press else self.wrong_prefix
                    key_name = self.keys[sequence_item.key_idx].key_name
                    self.current_instruction = f"{prefix} {key_name}"
                    
                    # Move to next item
                    self.sequence_index += 1
                    self.next_item_time = current_time + self.sequence_delay
                else:
                    # Finished showing sequence
                    self.state = self.WAITING_FOR_PLAYER
                    self.current_instruction = "Your turn! Press only the keys that had 'Computer says'"
                    self.is_timeout_active = False
                    
                    # Debug: Print out expected keys for developer reference
                    expected_keys = [self.keys[idx].key_name for idx in self.expected_player_keys]
                    print(f"Expected keys: {expected_keys}")
                    
                    # Add "Done" button instruction if there are expected keys
                    if self.expected_player_keys:
                        self.current_instruction += " or press SPACE when done"
        
        elif self.state == self.WAITING_FOR_PLAYER:
            # Check for timeout after last key press
            if self.is_timeout_active and current_time >= self.last_key_time + self.player_timeout:
                decay_change = self.check_player_completion()
                self.is_timeout_active = False
        
        elif self.state == self.SHOWING_RESULT:
            # Showing result message
            if current_time >= self.result_display_time + self.result_duration:
                # Move to next level or restart
                if "Correct" in self.result_message:
                    # Start next level
                    self.level += 1
                    self.start_new_level(is_reset=False)
                else:
                    # Restart with level 1
                    self.start_new_level(is_reset=True)
        
        # Make sure animation is always synced with decay
        self.sync_animation_with_decay()
        
        return decay_change
        
    def check_player_completion(self):
        """
        Check if the player has completed their turn correctly
        
        Returns:
            float: Amount to modify the global decay percentage
        """
        # If there are no expected keys
        if not self.expected_player_keys:
            if not self.player_keys:
                # Correct - player didn't press any keys
                self.result_message = "Correct! You correctly didn't press any keys."
                self.result_display_time = time.time()
                self.state = self.SHOWING_RESULT
                return self.correct_decay_bonus
            else:
                # Wrong - player pressed keys when they shouldn't have
                self.result_message = "Wrong! You shouldn't have pressed any keys."
                self.result_display_time = time.time()
                self.state = self.SHOWING_RESULT
                return self.wrong_decay_penalty
                
        # If player pressed fewer keys than expected
        if len(self.player_keys) < len(self.expected_player_keys):
            # Check if the keys they did press were correct
            correct_so_far = True
            for i, key_idx in enumerate(self.player_keys):
                if key_idx != self.expected_player_keys[i]:
                    correct_so_far = False
                    break
            
            if correct_so_far:
                # They pressed the right keys, just not all of them
                missed_keys = len(self.expected_player_keys) - len(self.player_keys)
                self.result_message = f"Incorrect! You missed {missed_keys} key(s)."
                self.result_display_time = time.time()
                self.state = self.SHOWING_RESULT
                return self.wrong_decay_penalty / 2  # Smaller penalty
            else:
                # They pressed the wrong keys
                self.result_message = "Wrong! You pressed the wrong keys."
                self.result_display_time = time.time() 
                self.state = self.SHOWING_RESULT
                return self.wrong_decay_penalty
        
        # If player pressed exactly the right keys
        if len(self.player_keys) == len(self.expected_player_keys):
            all_correct = True
            for i, key_idx in enumerate(self.player_keys):
                if key_idx != self.expected_player_keys[i]:
                    all_correct = False
                    break
            
            if all_correct:
                # Player got all keys correct
                self.score += len(self.expected_player_keys) * 10
                self.result_message = "Correct! Level complete!"
                self.result_display_time = time.time()
                self.state = self.SHOWING_RESULT
                return self.correct_decay_bonus
            else:
                # Player pressed wrong keys
                self.result_message = "Wrong! You pressed the wrong keys."
                self.result_display_time = time.time()
                self.state = self.SHOWING_RESULT
                return self.wrong_decay_penalty
        
        return 0.0
    
    def handle_key_press(self, key_code):
        """
        Handle a player pressing a key
        
        Args:
            key_code (int): Pygame key code that was pressed
            
        Returns:
            float: Amount to modify the global decay percentage
        """
        # Only process key presses when waiting for player input
        if self.state != self.WAITING_FOR_PLAYER:
            return 0.0
        
        # Special case for SPACE key: player indicates they're done
        if key_code == pygame.K_SPACE:
            print("Player pressed SPACE to indicate completion")
            return self.check_player_completion()
            
        # Map key to our key index
        if key_code not in self.key_map:
            return 0.0  # Not one of our Simon keys
            
        key_idx = self.key_map[key_code]
        
        # Light up the key
        self.keys[key_idx].light_up()
        
        # Add to player keys
        self.player_keys.append(key_idx)
        
        # Update last key time and activate timeout
        self.last_key_time = time.time()
        self.is_timeout_active = True
        
        # Log for debugging
        current_key_index = len(self.player_keys) - 1
        print(f"Player pressed key: {self.keys[key_idx].key_name}")
        print(f"Current index: {current_key_index}, Total expected: {len(self.expected_player_keys)}")
        
        # Check if there are expected keys to press
        if not self.expected_player_keys:
            self.result_message = "Wrong! There were no keys to press in this sequence."
            self.result_display_time = time.time()
            self.state = self.SHOWING_RESULT
            return self.wrong_decay_penalty
        
        # Check if the player has pressed too many keys
        if len(self.player_keys) > len(self.expected_player_keys):
            self.result_message = "Wrong! You pressed too many keys."
            self.result_display_time = time.time()
            self.state = self.SHOWING_RESULT
            return self.wrong_decay_penalty
        
        # Check if the current key is correct
        current_expected_key = self.expected_player_keys[current_key_index]
        if key_idx != current_expected_key:
            # Wrong key pressed
            print(f"Wrong key! Expected {self.keys[current_expected_key].key_name} but got {self.keys[key_idx].key_name}")
            self.result_message = f"Wrong! You pressed {self.keys[key_idx].key_name} instead of {self.keys[current_expected_key].key_name}."
            self.result_display_time = time.time()
            self.state = self.SHOWING_RESULT
            return self.wrong_decay_penalty
        else:
            print(f"Correct key: {self.keys[key_idx].key_name}")
        
        # If player has pressed all expected keys
        if len(self.player_keys) == len(self.expected_player_keys):
            # Sequence completed correctly
            self.score += len(self.expected_player_keys) * 10
            self.result_message = "Correct! Level complete!"
            self.result_display_time = time.time()
            self.state = self.SHOWING_RESULT
            return self.correct_decay_bonus
        
        # Correct key so far - give a small bonus
        return 1.0  # Small decay improvement for each correct key
    
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
        """
        Draw game statistics
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        stats_text = f"Level: {self.level} | Score: {self.score}"
        
        # Note: For the updated version, we're not showing animation frame stats
        # since it's now directly tied to the decay bar
        
        stats_surface = self.font.render(stats_text, True, (255, 255, 255))
        surface.blit(stats_surface, (20, self.screen_height - 80))
        
        # Draw info about key controls
        info_text = "Keys: W, A, S, D | Press SPACE when done | ESC to exit"
        info_surface = self.font.render(info_text , True, (180, 180, 180))
        surface.blit(info_surface, (self.screen_width - info_surface.get_width() - 20, self.screen_height - 80))
    
    def draw_instruction(self, surface):
        """
        Draw the current instruction or result message at the bottom of the screen
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        # Get the message to display (instruction or result)
        message = self.result_message if self.state == self.SHOWING_RESULT else self.current_instruction
        
        if not message:
            return
            
        # Create a box for the message at the bottom of the screen (above the decay bar)
        box_width = self.screen_width - 40  # Wide box with small margins
        box_height = 60  # Slightly shorter box
        box_x = 20  # Left margin
        box_y = self.screen_height - 110  # Position above decay bar
        
        # Draw box background
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        
        # Get the decay percentage for color selection
        decay_percentage = self.decay_engine.decay_percentage
        
        # Determine background color based on message content and using decay colors
        if "Wrong" in message or "Incorrect" in message:
            # For wrong answers - darker version of decay color (red-tinted)
            r, g, b = self.decay_color
            bg_color = (min(255, r + 80), max(0, g - 70), max(0, b - 70))  # Reddish tint
        elif "Correct" in message:
            # For correct answers - darker version of healthy color (green-tinted)
            r, g, b = self.healthy_color
            bg_color = (max(0, r - 70), min(255, g + 30), max(0, b - 70))  # Greenish tint
        elif self.correct_prefix in message:
            # For "Computer says" - use healthy color (darker)
            r, g, b = self.healthy_color
            bg_color = (max(0, r - 70), max(0, g - 40), max(0, b - 70))  # Darker green
        elif self.wrong_prefix in message:
            # For "Press" - use warning color (darker)
            r, g, b = self.warning_color
            bg_color = (min(255, r - 30), max(0, g - 40), max(0, b - 120))  # Orangish
        else:
            # For normal instructions - use a darker shade of the current decay state
            if decay_percentage > 66:
                r, g, b = self.healthy_color
            elif decay_percentage > 33:
                r, g, b = self.warning_color
            else:
                r, g, b = self.decay_color
            
            # Make it darker for better text contrast
            bg_color = (max(0, r - 100), max(0, g - 100), max(0, b - 50))
        
        pygame.draw.rect(surface, bg_color, box_rect)
        pygame.draw.rect(surface, (200, 200, 200), box_rect, 2)  # Border
        
        # Always use standard font for better fitting and wrap text if needed
        font_to_use = self.font
        
        # Text wrapping for long messages
        if len(message) > 60:
            # Split into two lines
            words = message.split()
            line1 = []
            line2 = []
            
            # Distribute words evenly between lines
            half_len = len(message) // 2
            current_len = 0
            
            for word in words:
                if current_len < half_len:
                    line1.append(word)
                    current_len += len(word) + 1
                else:
                    line2.append(word)
            
            # Render two lines of text
            text1 = font_to_use.render(" ".join(line1), True, (255, 255, 255))
            text2 = font_to_use.render(" ".join(line2), True, (255, 255, 255))
            
            # Position texts
            text1_rect = text1.get_rect(center=(box_rect.centerx, box_rect.centery - 15))
            text2_rect = text2.get_rect(center=(box_rect.centerx, box_rect.centery + 15))
            
            # Draw texts
            surface.blit(text1, text1_rect)
            surface.blit(text2, text2_rect)
        else:
            # Single line text
            text = font_to_use.render(message, True, (255, 255, 255))
            text_rect = text.get_rect(center=box_rect.center)
            surface.blit(text, text_rect)
        
        # Show which keys the player has pressed (positioned above the instruction box)
        if self.state == self.WAITING_FOR_PLAYER and self.player_keys:
            pressed_text = "Keys pressed: " + " ".join([self.keys[idx].key_name for idx in self.player_keys])
            pressed_surface = self.font.render(pressed_text, True, (200, 200, 200))
            pressed_rect = pressed_surface.get_rect(center=(self.screen_width // 2, box_y - 20))
            surface.blit(pressed_surface, pressed_rect)
            
            # Show timeout progress above keys pressed text
            if self.is_timeout_active:
                # Calculate remaining time
                current_time = time.time()
                elapsed = current_time - self.last_key_time
                remaining = max(0, self.player_timeout - elapsed)
                percentage = remaining / self.player_timeout * 100
                
                # Draw timeout bar
                bar_width = 400
                bar_height = 10
                bar_x = (self.screen_width - bar_width) // 2
                bar_y = box_y - 40
                
                # Background
                pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                
                # Fill with appropriate decay color based on timer
                if percentage > 66:
                    bar_color = self.healthy_color
                elif percentage > 33:
                    bar_color = self.warning_color
                else:
                    bar_color = self.decay_color
                    
                fill_width = int(bar_width * percentage / 100)
                pygame.draw.rect(surface, bar_color, (bar_x, bar_y, fill_width, bar_height))
    
    def draw_keyboard(self, surface):
        """
        This function is no longer used - keyboard visualization has been removed
        as per user's request
        """
        pass  # Do nothing - keyboard visualization removed
    
    def update(self):
        """Update game state and handle events"""
        # Calculate delta time
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - self.last_time) / 1000.0  # Convert to seconds
        self.last_time = current_time
        
        # Update decay naturally over time
        self.decay_engine.update(delta_time)
        
        # Update game and apply decay change
        decay_change = self.update_game(delta_time)
        if decay_change != 0:
            self.decay_engine.modify_decay(decay_change)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "main_menu"
                else:
                    # Handle game key presses
                    decay_change = self.handle_key_press(event.key)
                    self.decay_engine.modify_decay(decay_change)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    pos = event.pos
                    
                    # Check if back button was clicked
                    if self.back_button and self.back_button.collidepoint(pos):
                        print("Back button clicked in Game3")
                        return "main_menu"
        
        # If this is the first frame, start the game
        if not self.sequence:
            self.start_new_level()
        
        return True
    
    def draw(self):
        """Draw all game elements"""
        # Fill background with black
        self.screen.fill((0, 0, 0))
        
        # Draw current animation frame - centered on screen for maximum visibility
        frame = self.animation.get_current_frame()
        if frame:
            # Calculate a good size for the frame to be prominent
            # Scale to 85% of the screen width, maintaining aspect ratio
            original_width = frame.get_width()
            original_height = frame.get_height()
            scale_factor = self.screen_width * 0.85 / original_width
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            scaled_frame = pygame.transform.scale(frame, (new_width, new_height))
            # Center the frame on screen
            frame_rect = scaled_frame.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 40))
            self.screen.blit(scaled_frame, frame_rect)
        
        # No keyboard visualization as per user's request
        
        # Draw UI elements
        self.decay_bar.draw(self.screen)
        self.back_button = self.draw_back_button(self.screen)
        self.draw_stats(self.screen)
        self.draw_instruction(self.screen)  # Now moved to bottom of screen
    
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