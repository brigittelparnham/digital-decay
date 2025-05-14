#!/usr/bin/env python3
"""
App wrapper for Digital Decay
Handles proper initialization and error catching on macOS
"""
import sys
import os
import traceback

def setup_paths():
    """Setup proper paths for PyInstaller bundle"""
    if hasattr(sys, '_MEIPASS'):
        # Running from PyInstaller bundle
        base_path = sys._MEIPASS
        # Add the bundle path to sys.path
        if base_path not in sys.path:
            sys.path.insert(0, base_path)
        
        # Set working directory to bundle location
        os.chdir(base_path)
        print(f"Running from bundle: {base_path}")
    else:
        # Development mode
        base_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(base_path)
        print(f"Running in development: {base_path}")
    
    return base_path

def main():
    """Main wrapper function"""
    try:
        # Setup paths
        base_path = setup_paths()
        print("Digital Decay starting...")
        
        # Import and run the actual game
        import main as game_main
        game_main.main()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Failed to import game modules")
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)
        
    except Exception as e:
        print(f"Game error: {e}")
        print("An error occurred while running the game")
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
