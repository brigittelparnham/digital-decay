"""
main.py - Entry point for the Digital Decay game with Start/End screens and preloading
"""
import os
import sys
import pygame
import time
import random
from terminal_intro import play_intro_animation
from start_screen import run_start_screen
from end_screen import run_end_screen
from main_menu import MainMenu
from decay_engine import DecayEngine
from games.game1 import Game1
from games.game2 import Game2
from games.game3 import Game3

# Import OpenGL functions
from OpenGL.GL import *
from OpenGL.GLU import *

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Global preloaded assets
preloaded_objects = {}

def create_asset_directories():
    """Create necessary directories for assets if they don't exist"""
    directories = [
        "assets",
        "assets/blender",
        "assets/blender/animation",
        "assets/blender/objects",  # Directory for custom objects
        "assets/fonts",
        "assets/sounds"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def preload_assets():
    """Preload assets to avoid delays during transitions"""
    global preloaded_objects
    print("Preloading assets...")
    
    # Create temporary OpenGL context for preloading
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
    
    # Setup OpenGL for preloading
    glViewport(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (SCREEN_WIDTH / SCREEN_HEIGHT), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Preload Blender objects from the objects directory
    from utils.blender_loader import BlenderModel
    
    obj_dir = os.path.join("assets", "blender", "objects")
    if os.path.exists(obj_dir):
        for filename in os.listdir(obj_dir):
            if filename.endswith('.obj'):
                try:
                    filepath = os.path.join(obj_dir, filename)
                    print(f"Preloading {filepath}...")
                    model = BlenderModel(filepath)
                    # Store the preloaded model
                    preloaded_objects[filename] = model
                except Exception as e:
                    print(f"Error preloading {filename}: {e}")
    
    # Clean up OpenGL context after preloading
    pygame.display.quit()
    pygame.display.init()
    
    print(f"Preloaded {len(preloaded_objects)} assets")

def check_decay_for_end_screen(decay_engine, current_state, game_over):
    """
    Check if decay has reached zero and we need to show the end screen
    
    Args:
        decay_engine: The decay engine to check
        current_state: Current game state
        game_over: Whether the game is already over
        
    Returns:
        str or None: "end_screen" if should transition, None otherwise
    """
    # Force exact comparison with 0.0 to ensure we catch it
    if decay_engine.decay_percentage <= 0.0 and not game_over and current_state != "end_screen":
        print(f"DECAY DETECTED AT EXACTLY 0% - Showing end screen (from {current_state})")
        return "end_screen"
    return None

# Final fix for main.py - handling "end_screen" state transition correctly
def main():
    """Main function to run the game"""
    # Create asset directories
    create_asset_directories()
    
    # Play terminal intro animation
    play_intro_animation()
    
    # Initialize pygame
    pygame.init()
    clock = pygame.time.Clock()
    
    # Preload assets before starting the game
    preload_assets()
    
    # Create decay engine
    decay_engine = DecayEngine(decay_time=120)  # 120 seconds for full decay
    
    # Show start screen
    if not run_start_screen():
        pygame.quit()
        sys.exit()
    
    # Simple fade out of start screen
    surface = pygame.display.get_surface()
    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill((0, 0, 0))
    
    for alpha in range(0, 256, 15):
        surface.fill((0, 0, 0))
        fade_surface.set_alpha(alpha)
        surface.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)
    
    # Switch to MainMenu (OpenGL mode)
    pygame.display.quit()  
    pygame.display.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
    
    # Create main menu with preloaded objects
    menu = MainMenu(decay_engine, preloaded_objects)
    
    # Pre-populate objects far off-screen to the right
    for _ in range(5):
        new_obj = menu.spawn_new_object()
        new_obj.position[0] = 20.0  # Much further off-screen to the right
    
    # Game state
    current_state = "main_menu"
    next_state = None
    running = True
    restart_flag = False
    
    # Current active game
    current_game = None
    
    # Add a flag to prevent loops between screens
    end_screen_shown = False
    
    # Main game loop
    while running:
        # Handle zero decay detection and the restart flag first
        
        # Check for restart flag - this is our way to handle the End -> Start -> Main flow
        if restart_flag:
            print("Detected restart flag - resetting and going to main menu")
            restart_flag = False
            current_state = "main_menu"

            MainMenu.reset_state()
            
            # Make sure display is properly set up for main menu
            pygame.display.quit()
            pygame.display.init()
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
            
            # Create a new main menu with fresh decay engine
            decay_engine = DecayEngine(decay_time=120)
            menu = MainMenu(decay_engine, preloaded_objects)
            end_screen_shown = False
            
            # Skip the rest of the loop
            continue
            
        # Check for zero decay
        if decay_engine.decay_percentage <= 0.0 and not end_screen_shown:
            print(f"DECAY DETECTED AT EXACTLY 0% - Showing end screen (from {current_state})")
            end_screen_shown = True
            
            # If next_state is set to "end_screen", clear it to avoid confusion
            if next_state == "end_screen":
                next_state = None
            
            # Clean up current display
            pygame.display.quit()
            pygame.display.init()
            
            # Switch to regular display mode for end screen
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            
            # Run end screen
            print("Running end screen")
            if run_end_screen():  # Returns True when user presses Enter or after 30 seconds
                print("End screen complete - going to start screen")
                
                # Clean up resources
                pygame.display.quit()
                pygame.display.init()
                
                # Switch to regular display mode for start screen
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                
                # Run start screen with a completely fresh decay engine
                print("Running start screen")
                if run_start_screen():
                    # Reset main menu state when starting a fresh game
                    MainMenu.reset_state()
                    # User pressed Enter on start screen - set flag to restart the game
                    restart_flag = True
                    print("Start screen complete - setting restart flag")
                else:
                    # User pressed ESC on start screen - quit
                    running = False
            else:
                # User pressed ESC on end screen - quit
                running = False
            
            # Skip the rest of the loop
            continue
        
        # Process state transitions for normal game states (not end/start)
        if next_state:
            print(f"Transitioning from {current_state} to {next_state}")
            
            # Special handling for end_screen transition
            if next_state == "end_screen":
                # This will be handled by the decay detection above
                # Just set end_screen_shown flag and continue
                print("Transition to end_screen - letting decay detection handle it")
                end_screen_shown = True
                next_state = None
                continue
                
            # Clean up previous state
            if current_state == "main_menu":
                # Clean up menu resources if needed
                pass
            elif current_state in ["game1", "game2", "game3"]:
                # Clean up current game resources
                current_game = None
            
            # Initialize new state
            if next_state == "main_menu":
                # Prepare to go back to main menu
                pygame.display.quit()
                pygame.display.init()
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
                menu = MainMenu(decay_engine, preloaded_objects)
                
            elif next_state == "game1":
                # Switch to Game1
                pygame.display.quit()
                pygame.display.init()
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                current_game = Game1(decay_engine, SCREEN_WIDTH, SCREEN_HEIGHT)
            elif next_state == "game2":
                # Switch to Game2
                pygame.display.quit()
                pygame.display.init()
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                current_game = Game2(decay_engine, SCREEN_WIDTH, SCREEN_HEIGHT)
            elif next_state == "game3":
                # Switch to Game3
                pygame.display.quit()
                pygame.display.init()
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                current_game = Game3(decay_engine, SCREEN_WIDTH, SCREEN_HEIGHT)
            else:
                print(f"Unknown next state: {next_state} - ignoring")
                next_state = None
                continue
            
            # Complete the transition
            current_state = next_state
            next_state = None
        
        # Handle current state
        if current_state == "main_menu":
            result = menu.run()
            
            # Handle the result from main menu
            if result is None:
                running = False
            elif result == "end_screen":
                # Special handling for end_screen - let decay detection handle it
                decay_engine.decay_percentage = 0.0
                end_screen_shown = False  # This will trigger the zero decay detection
            elif isinstance(result, str):
                next_state = result
                
        elif current_state in ["game1", "game2", "game3"]:
            if current_game:
                result = current_game.run()
                
                # Handle the result from games
                if result is None:
                    running = False
                elif result == "end_screen":
                    # Special handling for end_screen - let decay detection handle it
                    decay_engine.decay_percentage = 0.0
                    end_screen_shown = False  # This will trigger the zero decay detection
                elif isinstance(result, str):
                    next_state = result
            else:
                # If game object is missing, go back to menu
                next_state = "main_menu"
                
        else:
            print(f"Unknown state: {current_state}")
            running = False
            
        # Keep the frame rate consistent
        clock.tick(FPS)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()