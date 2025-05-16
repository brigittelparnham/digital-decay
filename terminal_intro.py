"""
Fixed terminal_intro.py - Terminal intro animation with proper asset loading
"""
import os
import sys
import time
import random
import json
from colorama import init, Fore, Style

# Add the project root to the path so we can import utils
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from utils.asset_utils import get_asset_path

# Initialize colorama
init()

# Load colors from decay_grids.json
def load_decay_colors():
    """Load color scheme from decay_grids.json"""
    try:
        # Load the decay grids JSON using centralized asset function
        json_path = get_asset_path('decay_grids.json')
        
        with open(json_path, 'r') as f:
            decay_grids = json.load(f)
            
        # Use the selected Option 2 colors from the grid
        begin_hex = "#adb47d"  # Muted Green from Stage 1
        middle_hex = "#dce4aa"  # Pale Yellow from Stage 3
        end_hex = "#799f96"    # Teal from Stage 6
        
        return begin_hex, middle_hex, end_hex
    except Exception as e:
        print(f"Error loading decay colors: {e}")
        # Default fallback colors (standard terminal colors)
        return "#a0ff00", "#ffcc00", "#ff4000"

# Convert hex to RGB
def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Get ANSI color code for RGB values
def rgb_to_ansi(r, g, b):
    """Convert RGB values to ANSI color code"""
    return f"\033[38;2;{r};{g};{b}m"

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_at(text, x, y, color=Fore.WHITE):
    """Print text at specific position in the terminal with color"""
    # Move cursor to position
    sys.stdout.write(f"\033[{y};{x}H")
    # Print colored text
    sys.stdout.write(f"{color}{text}{Style.RESET_ALL}")
    sys.stdout.flush()

def get_terminal_size():
    """Get the size of the terminal window"""
    try:
        columns, lines = os.get_terminal_size()
    except:
        columns, lines = 80, 24
    return columns, lines

def glitch_text(text):
    """Create a glitched version of text"""
    glitch_chars = "!@#$%^&*()-_=+[]{}|;:,.<>/?`~"
    result = ""
    for char in text:
        if random.random() < 0.2:  # 20% chance to glitch
            result += random.choice(glitch_chars)
        else:
            result += char
    return result

def play_intro_animation():
    """Play the "Digital Decay" intro animation in the terminal with colors from decay_grids.json"""
    clear_screen()
    width, height = get_terminal_size()
    
    # Load decay colors from JSON
    begin_hex, middle_hex, end_hex = load_decay_colors()
    
    # Convert hex colors to RGB
    begin_rgb = hex_to_rgb(begin_hex)
    middle_rgb = hex_to_rgb(middle_hex)
    end_rgb = hex_to_rgb(end_hex)
    
    # Convert RGB to ANSI color codes
    begin_color = rgb_to_ansi(*begin_rgb)
    middle_color = rgb_to_ansi(*middle_rgb)
    end_color = rgb_to_ansi(*end_rgb)
    
    # Define colors for different decay stages - using our custom colors
    colors = [begin_color, middle_color, end_color]
    
    # Digital Decay ASCII art
    ascii_art = [
        "██████╗ ██╗ ██████╗ ██╗████████╗ █████╗ ██╗         ",
        "██╔══██╗██║██╔════╝ ██║╚══██╔══╝██╔══██╗██║         ",
        "██║  ██║██║██║  ███╗██║   ██║   ███████║██║         ",
        "██║  ██║██║██║   ██║██║   ██║   ██╔══██║██║         ",
        "██████╔╝██║╚██████╔╝██║   ██║   ██║  ██║███████╗    ",
        "╚═════╝ ╚═╝ ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝    ",
        "                                                     ",
        "██████╗ ███████╗ ██████╗ █████╗ ██╗   ██╗           ",
        "██╔══██╗██╔════╝██╔════╝██╔══██╗╚██╗ ██╔╝           ",
        "██║  ██║█████╗  ██║     ███████║ ╚████╔╝            ",
        "██║  ██║██╔══╝  ██║     ██╔══██║  ╚██╔╝             ",
        "██████╔╝███████╗╚██████╗██║  ██║   ██║              ",
        "╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝   ╚═╝              "
    ]
    
    # Calculate starting position to center the art
    start_x = (width - len(ascii_art[0])) // 2
    start_y = (height - len(ascii_art)) // 2
    
    # First pass: Reveal the ASCII art character by character
    for y, line in enumerate(ascii_art):
        for x, char in enumerate(line):
            if char != ' ':
                print_at(char, start_x + x, start_y + y, begin_color)
                time.sleep(0.001)  # Short delay for reveal effect
    
    time.sleep(1)
    
    # Second pass: Add glitch effects
    for _ in range(10):
        # Choose random positions to glitch
        for _ in range(20):
            y = random.randint(0, len(ascii_art) - 1)
            x = random.randint(0, len(ascii_art[0]) - 1)
            if ascii_art[y][x] != ' ':
                print_at(random.choice("!@#$%^&*"), start_x + x, start_y + y, random.choice(colors))
        time.sleep(0.1)
    
    # Third pass: Color decay animation (begin -> middle -> end)
    for i in range(20):
        color_index = min(2, i // 7)
        color = colors[color_index]
        
        for y, line in enumerate(ascii_art):
            for x, char in enumerate(line):
                if char != ' ' and random.random() < 0.3:  # Only update some characters each frame
                    if random.random() < 0.1:  # 10% chance for glitch effect
                        print_at(random.choice("!@#$%^&*"), start_x + x, start_y + y, color)
                    else:
                        print_at(char, start_x + x, start_y + y, color)
        time.sleep(0.1)
    
    # Final message
    loading_msg = "Loading game..."
    loading_x = (width - len(loading_msg)) // 2
    loading_y = start_y + len(ascii_art) + 2
    print_at(loading_msg, loading_x, loading_y, Fore.WHITE)
    
    # Loading animation with the begin_color
    for i in range(10):
        sys.stdout.write(f"\033[{loading_y + 1};{loading_x}H")
        sys.stdout.write(f"{begin_color}[" + "=" * i + " " * (10 - i) + "]" + Style.RESET_ALL)
        sys.stdout.flush()
        time.sleep(0.2)
    
    time.sleep(1)
    clear_screen()

if __name__ == "__main__":
    play_intro_animation()