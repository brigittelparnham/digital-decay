"""
game3.py - Simon Says game with Blender animation frames
"""
import pygame
import random
import os
import time
from utils.decay_bar import DecayBar
from utils.blender_loader import AnimationLoader
from utils.color_utils import load_jetbrains_mono_font

class BlenderAnimation:
    """Manages a sequence of Blender animation frames"""
    
    def __init__(self, frames_dir=None, num_frames=120):
        """
        Initialize the animation
        
        Args:
            frames_dir (str): Directory containing animation frames
            num_frames (int): Number of frames to generate if directory doesn't exist
        """
        self.loader = AnimationLoader(frames_dir)
        
        # If no frames were loaded, create default frames
        if len(self.loader.frames) == 0:
            self.create_default_frames(num_frames)
        
        self.num_frames = len(self.loader.frames)
        self.current_frame = 0
    
    def create_default_frames(self, num_frames):
        """
        Create default animation frames when no image files are available
        
        Args:
            num_frames (int): Number of frames to generate
        """
        self.loader.frames = []
        
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
            self.loader.frames.append(surface)
    
    def get_frame(self, frame_index):
        """
        Get a specific frame
        
        Args:
            frame_index (int): Index of the frame to get
            
        Returns:
            pygame.Surface: The frame surface
        """
        return self.loader.get_frame(frame_index)
    
    def get_current_frame(self):
        """
        Get the current frame
        
        Returns:
            pygame.Surface: The current frame surface
        """
        return self.loader.get_frame(self.current_frame)
    
    def advance(self, amount=1):
        """
        Advance the animation by a given number of frames
        
        Args:
            amount (int): Number of frames to advance (can be negative to rewind)
        """
        self.current_frame = (self.current_frame + amount) % self.num_frames
    
    def set_frame(self, frame_index):
        """
        Set the current frame
        
        Args:
            frame_index (int): Index of the frame to set as current
        """
        self.current_frame = max(0, min(self.num_frames - 1, frame_index))
    
    def get_progress(self):
        """
        Get the current progress through the animation
        
        Returns:
            float: Progress from 0.0 to 1.0
        """
        return self.current_frame / (self.num_frames - 1) if self.num_frames > 1 else 0

class SimonButton:
    """Represents a colored button in the Simon Says game"""
    
    def __init__(self, rect, color, sound_id):
        """
        Initialize a Simon button
        
        Args:
            rect (pygame.Rect): Rectangle defining position and size
            color (tuple): RGB color tuple for the button
            sound_id (int): ID of the sound to play when button is pressed
        """
        self.rect = rect
        self.color = color
        self.sound_id = sound_id
        self.is_lit = False
        self.lit_time = 0
        self.lit_duration = 0.5  # Seconds to stay lit
    
    def light_up(self):
        """Light up the button"""
        self.is_lit = True
        self.lit_time = time.time()
        # TODO: Play sound based on sound_id
    
    def update(self):
        """Update button state"""
        if self.is_lit and time.time() - self.lit_time > self.lit_duration:
            self.is_lit = False
    
    def draw(self, surface, decay_engine):
        """
        Draw the button
        
        Args:
            surface (pygame.Surface): Surface to draw on
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
        
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)  # Border

class Game3:
    """Simon Says game with Blender animation frames"""
    
    def __init__(self, decay_engine, screen_width, screen_height):
        """
        Initialize the game with loading animations
        """
        self.decay_engine = decay_engine
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Simon Says Animation")
        self.clock = pygame.time.Clock()
        
        # Show loading message
        loading_font = load_jetbrains_mono_font(24)
        loading_text = loading_font.render("Loading Animation Frames...", True, (0, 255, 0))
        loading_rect = loading_text.get_rect(center=(screen_width // 2, screen_height // 2))
        
        # Draw loading screen
        self.screen.fill((0, 0, 0))
        self.screen.blit(loading_text, loading_rect)
        pygame.display.flip()
        
        # Create Blender animation
        frames_dir = os.path.join("assets", "blender", "animation")
        self.animation = BlenderAnimation(frames_dir)
        
        # Create a loading bar showing animation progress
        bar_width = 400
        bar_height = 20
        bar_x = (self.screen_width - bar_width) // 2
        bar_y = self.screen_height // 2 + 40
        
        # Load all animation frames with progress bar
        num_frames = self.animation.num_frames
        for i in range(num_frames):
            if i % 5 == 0 or i == num_frames - 1:  # Update every 5 frames or on last frame
                progress = (i / num_frames) * 100
                bar_fill_width = int(bar_width * (i / num_frames))
                
                self.screen.fill((0, 0, 0))
                self.screen.blit(loading_text, loading_rect)
                pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(self.screen, (0, 255, 0), (bar_x, bar_y, bar_fill_width, bar_height))
                
                # Show preview of current frame
                if self.animation.get_frame(i):
                    preview = self.animation.get_frame(i)
                    # Scale down for preview
                    preview = pygame.transform.scale(preview, (200, 150))
                    preview_rect = preview.get_rect(center=(screen_width // 2, screen_height - 100))
                    self.screen.blit(preview, preview_rect)
                
                pygame.display.flip()
        
        # Load UI and game elements
        self.screen.fill((0, 0, 0))
        loading_text = loading_font.render("Creating Game Elements...", True, (0, 255, 0))
        self.screen.blit(loading_text, loading_rect)
        pygame.display.flip()
        
        # Create decay bar - full width at bottom
        self.decay_bar = DecayBar(pygame.Rect(0, screen_height - 40, screen_width, 30), decay_engine, full_width=True)
        
        # Font for text
        self.font = load_jetbrains_mono_font(24)
        
        # Create Simon buttons
        button_size = 100
        margin = 20
        self.buttons = [
            SimonButton(pygame.Rect(screen_width - button_size*2 - margin, 
                                    screen_height - button_size*2 - margin - 40, 
                                    button_size, button_size), 
                        (255, 0, 0), 0),  # Red - top left
            SimonButton(pygame.Rect(screen_width - button_size - margin, 
                                    screen_height - button_size*2 - margin - 40, 
                                    button_size, button_size), 
                        (0, 255, 0), 1),  # Green - top right
            SimonButton(pygame.Rect(screen_width - button_size*2 - margin, 
                                    screen_height - button_size - margin - 40, 
                                    button_size, button_size), 
                        (0, 0, 255), 2),  # Blue - bottom left
            SimonButton(pygame.Rect(screen_width - button_size - margin, 
                                    screen_height - button_size - margin - 40, 
                                    button_size, button_size), 
                        (255, 255, 0), 3)  # Yellow - bottom right
        ]
        
        # Game state initialization
        self.sequence = []
        self.player_sequence = []
        self.displaying_sequence = False
        self.sequence_index = 0
        self.next_button_time = 0
        self.sequence_delay = 0.8  # Seconds between buttons in sequence
        self.waiting_for_player = False
        self.game_over = False
        self.level = 1
        self.score = 0
        
        # Animation control parameters
        self.animation_direction = 1  # 1 for forward, -1 for backward
        self.animation_speed = 1  # Frames per second
        self.animation_timer = 0
        
        # For calculating delta time
        self.last_time = pygame.time.get_ticks()
        
        # Back button
        self.back_button = None
        
        # Show ready message
        self.screen.fill((0, 0, 0))
        ready_text = loading_font.render("Game Ready!", True, (0, 255, 0))
        ready_rect = ready_text.get_rect(center=(screen_width // 2, screen_height // 2))
        self.screen.blit(ready_text, ready_rect)
        pygame.display.flip()
        pygame.time.delay(300)  # Brief pause
    
    def start_new_level(self):
        """Start a new level by adding to the sequence"""
        self.sequence.append(random.randint(0, len(self.buttons) - 1))
        self.player_sequence = []
        self.displaying_sequence = True
        self.sequence_index = 0
        self.next_button_time = time.time() + 1.0  # Wait a second before starting
        self.waiting_for_player = False
    
    def update_simon_game(self, delta_time):
        """
        Update the Simon Says game state
        
        Args:
            delta_time (float): Time in seconds since last update
            
        Returns:
            float: Amount to modify the global decay percentage
        """
        decay_change = 0.0
        
        # Update all buttons
        for button in self.buttons:
            button.update()
        
        # If displaying sequence to player
        if self.displaying_sequence:
            current_time = time.time()
            
            if current_time >= self.next_button_time:
                if self.sequence_index < len(self.sequence):
                    # Light up the next button in the sequence
                    button_idx = self.sequence[self.sequence_index]
                    self.buttons[button_idx].light_up()
                    self.sequence_index += 1
                    self.next_button_time = current_time + self.sequence_delay
                else:
                    # Finished displaying sequence
                    self.displaying_sequence = False
                    self.waiting_for_player = True
        
        # If game over, no further updates
        if self.game_over:
            return decay_change
        
        return decay_change
    
    def handle_button_press(self, button_idx):
        """
        Handle a player pressing a button
        
        Args:
            button_idx (int): Index of the button pressed
            
        Returns:
            float: Amount to modify the global decay percentage
        """
        if not self.waiting_for_player or self.displaying_sequence:
            return 0.0
        
        # Light up the pressed button
        self.buttons[button_idx].light_up()
        
        # Add to player sequence
        self.player_sequence.append(button_idx)
        
        # Check if correct
        sequence_idx = len(self.player_sequence) - 1
        if button_idx != self.sequence[sequence_idx]:
            # Wrong button - animation rewinds and decay increases
            self.game_over = True
            self.animation_direction = -1
            return -5.0  # Increase decay by 5%
        
        # Correct button - advance animation and decrease decay
        self.animation_direction = 1
        self.animation.advance(1)
        
        # If completed the sequence
        if len(self.player_sequence) == len(self.sequence):
            self.score += len(self.sequence) * 10
            self.level += 1
            self.waiting_for_player = False
            self.start_new_level()
            return 5.0  # Decrease decay by 5%
        
        return 1.0  # Decrease decay by 1% for each correct press
    
    def update_animation(self, delta_time):
        """
        Update the Blender animation
        
        Args:
            delta_time (float): Time in seconds since last update
        """
        self.animation_timer += delta_time
        frames_to_advance = int(self.animation_timer * self.animation_speed)
        
        if frames_to_advance > 0:
            self.animation_timer = 0
            self.animation.advance(frames_to_advance * self.animation_direction)
    
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
        """
        Draw game statistics
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        stats_text = f"Level: {self.level} | Score: {self.score} | Animation Frame: {self.animation.current_frame + 1}/{self.animation.num_frames}"
        text = self.font.render(stats_text, True, (255, 255, 255))
        surface.blit(text, (20, self.screen_height - 30))
    
    def update(self):
        """Update game state and handle events"""
        # Calculate delta time
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - self.last_time) / 1000.0  # Convert to seconds
        self.last_time = current_time
        
        # Update decay naturally over time
        self.decay_engine.update(delta_time)
        
        # Update animation
        self.update_animation(delta_time)
        
        # Update Simon game and apply decay change
        decay_change = self.update_simon_game(delta_time)
        if decay_change != 0:
            self.decay_engine.modify_decay(decay_change)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "main_menu"
                elif event.key == pygame.K_SPACE and self.game_over:
                    # Restart game
                    self.__init__(self.decay_engine, self.screen_width, self.screen_height)
                    self.start_new_level()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    pos = event.pos
                    
                    # Check if back button was clicked
                    if self.back_button and self.back_button.collidepoint(pos):
                        print("Back button clicked in Game3")
                        return "main_menu"
                    
                    # Check if any Simon button was clicked
                    for i, button in enumerate(self.buttons):
                        if button.rect.collidepoint(pos):
                            decay_change = self.handle_button_press(i)
                            self.decay_engine.modify_decay(decay_change)
        
        # If this is the first frame, start the game
        if not self.sequence:
            self.start_new_level()
        
        return True
    
    def draw(self):
        """Draw all game elements"""
        # Fill background with black
        self.screen.fill((0, 0, 0))
        
        # Draw current animation frame - FIXED: Position higher to avoid decay bar
        frame = self.animation.get_current_frame()
        frame_rect = frame.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 80))  # Adjusted from -50 to -80
        self.screen.blit(frame, frame_rect)
        
        # Draw Simon buttons 
        for button in self.buttons:
            button.draw(self.screen, self.decay_engine)
        
        # Draw UI elements
        self.decay_bar.draw(self.screen)
        self.back_button = self.draw_back_button(self.screen)
        self.draw_stats(self.screen)
        
        # Draw game state messages
        if self.displaying_sequence:
            message = "Watch the sequence..."
        elif self.waiting_for_player:
            message = "Your turn! Repeat the sequence."
        elif self.game_over:
            message = "Game Over! Press SPACE to restart."
        else:
            message = "Simon Says: Animation Controller"
        
        text = self.font.render(message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen_width // 2, 60))
        self.screen.blit(text, text_rect)
    
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