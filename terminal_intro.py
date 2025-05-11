"""
terminal_intro.py - Terminal "Digital Decay" intro animation
"""
import os
import time
import sys
import random
from colorama import init, Fore, Style

# Initialize colorama
init()

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_at(text, x, y, color=Fore.WHITE):
    """Print text at specific position in the terminal"""
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
    """Play the "Digital Decay" intro animation in the terminal"""
    clear_screen()
    width, height = get_terminal_size()
    
    # Define colors for different decay stages
    colors = [Fore.GREEN, Fore.YELLOW, Fore.RED]
    
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
                print_at(char, start_x + x, start_y + y, Fore.GREEN)
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
    
    # Third pass: Color decay animation (green -> yellow -> red)
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
    
    # Loading animation
    for i in range(10):
        sys.stdout.write(f"\033[{loading_y + 1};{loading_x}H")
        sys.stdout.write(Fore.GREEN + "[" + "=" * i + " " * (10 - i) + "]" + Style.RESET_ALL)
        sys.stdout.flush()
        time.sleep(0.2)
    
    time.sleep(1)
    clear_screen()

if __name__ == "__main__":
    play_intro_animation()