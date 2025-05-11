"""
build_web.py - Directly builds the web version of Digital Decay

Usage:
    python build_web.py

Place this file in your project root (not in the build directory).
"""
import os
import shutil
import zipfile
import json
import glob
import time
import sys
from js import document

def create_web_version():
    """Create a web-deployable version of the game"""
    print("Creating web version of Digital Decay...")
    
    # Get the project root directory
    project_root = os.path.abspath(os.path.dirname(__file__))
    print(f"Project root: {project_root}")
    
    # Create web directory
    web_dir = os.path.join(project_root, "web_build")
    if os.path.exists(web_dir):
        print(f"Removing existing web_build directory...")
        shutil.rmtree(web_dir)
    os.makedirs(web_dir, exist_ok=True)
    print(f"Created directory: {web_dir}")
    
    # Core Python files to copy
    core_files = [
        "main.py",
        "terminal_intro.py",
        "main_menu.py",
        "decay_engine.py",
        "start_screen.py",
        "end_screen.py",
    ]
    
    # Copy core game files
    print("Copying core game files...")
    for file in core_files:
        source_file = os.path.join(project_root, file)
        if os.path.exists(source_file):
            shutil.copy(source_file, os.path.join(web_dir, file))
            print(f"Copied {file}")
        else:
            print(f"Warning: {file} not found")
    
    # Create directory structure
    directories = [
        "games",
        "utils",
        "assets",
        "assets/blender",
        "assets/blender/objects",
        "assets/blender/animation",
        "assets/fonts"
    ]
    
    for directory in directories:
        os.makedirs(os.path.join(web_dir, directory), exist_ok=True)
        print(f"Created directory: {web_dir}/{directory}")
    
    # Helper function to copy directory contents
    def copy_directory(src_dir, dest_dir):
        """
        Copy all files from src_dir to dest_dir, preserving directory structure
        
        Args:
            src_dir (str): Source directory
            dest_dir (str): Destination directory
            
        Returns:
            int: Number of files copied
        """
        copied = 0
        if not os.path.exists(src_dir):
            print(f"Warning: Source directory not found: {src_dir}")
            return copied
            
        for root, dirs, files in os.walk(src_dir):
            # Create destination subdirectory
            rel_path = os.path.relpath(root, src_dir)
            dest_path = os.path.join(dest_dir, rel_path)
            os.makedirs(dest_path, exist_ok=True)
            
            # Copy files
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dest_path, file)
                try:
                    shutil.copy2(src_file, dst_file)
                    copied += 1
                except Exception as e:
                    print(f"Error copying {src_file}: {e}")
        
        return copied
    
    # Copy game modules
    games_src = os.path.join(project_root, "games")
    games_dest = os.path.join(web_dir, "games")
    games_copied = copy_directory(games_src, games_dest)
    print(f"Copied {games_copied} files from games directory")
    
    # Copy utility modules
    utils_src = os.path.join(project_root, "utils")
    utils_dest = os.path.join(web_dir, "utils")
    utils_copied = copy_directory(utils_src, utils_dest)
    print(f"Copied {utils_copied} files from utils directory")
    
    # Copy assets
    assets_src = os.path.join(project_root, "assets")
    assets_dest = os.path.join(web_dir, "assets")
    assets_copied = copy_directory(assets_src, assets_dest)
    print(f"Copied {assets_copied} files from assets directory")
    
    # Make sure decay_grids.json exists (critical for the game)
    decay_grids_path = os.path.join(web_dir, "assets", "decay_grids.json")
    decay_grids_src = os.path.join(project_root, "assets", "decay_grids.json")
    
    if not os.path.exists(decay_grids_src):
        print("Warning: decay_grids.json not found. Creating a simple version.")
        simple_decay_grids = {
            "description": "Six color stages for each cell in the 7x13 decay grid",
            "stages": []
        }
        
        # Create 6 stages with placeholder colors
        for stage in range(6):
            stage_data = {
                "stage": stage + 1,
                "description": f"Decay stage {stage + 1}",
                "grid": []
            }
            
            # Create a 7x13 grid
            for row in range(7):
                grid_row = []
                for col in range(13):
                    # Generate colors based on stage
                    if stage == 0:
                        color = "#adb47d"  # Healthy
                    elif stage == 1:
                        color = "#bbb580"  # Early decay
                    elif stage == 2:
                        color = "#e4dab1"  # Mid decay
                    elif stage == 3:
                        color = "#ded4b1"  # Advanced decay
                    elif stage == 4:
                        color = "#c2c9b5"  # Heavy decay
                    else:
                        color = "#799f96"  # Complete decay
                    grid_row.append(color)
                stage_data["grid"].append(grid_row)
            
            simple_decay_grids["stages"].append(stage_data)
        
        # Write the simple decay grids file
        with open(decay_grids_path, "w") as f:
            json.dump(simple_decay_grids, f, indent=2)
    else:
        # Copy the original decay_grids.json
        shutil.copy2(decay_grids_src, decay_grids_path)
        print(f"Copied {decay_grids_src} to {decay_grids_path}")
    
    # Create HTML wrapper with better loading indicators
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Decay</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #000;
            color: #adb47d;
            font-family: monospace;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }
        #gameCanvas {
            display: block;
            margin: 0 auto;
            width: 1024px;
            height: 768px;
            max-width: 100%;
            max-height: 100vh;
            image-rendering: pixelated;
        }
        #loadingScreen {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background-color: #000;
            z-index: 100;
        }
        #loadingText {
            font-size: 24px;
            margin-bottom: 20px;
            color: #adb47d;
        }
        #loadingBar {
            width: 300px;
            height: 20px;
            border: 2px solid #adb47d;
            border-radius: 5px;
        }
        #loadingProgress {
            width: 0%;
            height: 100%;
            background-color: #adb47d;
            transition: width 0.3s;
        }
        #loadingStatus {
            margin-top: 10px;
            font-size: 14px;
            color: #adb47d;
            text-align: center;
            max-width: 80%;
        }
        #errorScreen {
            display: none;
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 200;
            padding: 20px;
            box-sizing: border-box;
        }
        #errorTitle {
            color: #ff5555;
            font-size: 28px;
            margin-bottom: 20px;
        }
        #errorMessage {
            color: #ffaaaa;
            font-size: 16px;
            max-width: 600px;
            text-align: center;
            margin-bottom: 20px;
        }
        #browserSupport {
            background-color: #111;
            border: 1px solid #333;
            padding: 15px;
            border-radius: 5px;
            max-width: 500px;
            margin-top: 30px;
        }
        .glitchText {
            animation: glitch 2s infinite;
        }
        @keyframes glitch {
            0% { opacity: 1; transform: translateX(0); }
            1% { opacity: 0.8; transform: translateX(2px); }
            2% { transform: translateX(-2px); }
            3% { transform: translateX(0); }
            10% { opacity: 1; }
            90% { opacity: 1; }
            91% { opacity: 0.8; transform: translateX(-2px); }
            92% { transform: translateX(2px); }
            93% { transform: translateX(0); }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div id="loadingScreen">
        <div id="loadingText" class="glitchText">Loading Digital Decay...</div>
        <div id="loadingBar">
            <div id="loadingProgress"></div>
        </div>
        <div id="loadingStatus">Preparing environment...</div>
        <div id="browserSupport">
            For best experience, use Chrome or Firefox on a desktop computer.
        </div>
    </div>
    
    <div id="errorScreen">
        <div id="errorTitle">Error Loading Game</div>
        <div id="errorMessage">There was a problem loading the game components.</div>
        <button onclick="location.reload()">Try Again</button>
        <div id="browserSupport">
            This game requires a modern browser with WebAssembly support.<br>
            Please try using the latest version of Chrome or Firefox on a desktop computer.
        </div>
    </div>
    
    <canvas id="gameCanvas" width="1024" height="768"></canvas>
    
    <script src="https://cdn.jsdelivr.net/pyodide/v0.23.4/full/pyodide.js"></script>
    <script>
        const loadingProgress = document.getElementById('loadingProgress');
        const loadingText = document.getElementById('loadingText');
        const loadingStatus = document.getElementById('loadingStatus');
        const errorScreen = document.getElementById('errorScreen');
        const errorMessage = document.getElementById('errorMessage');
        
        // Update loading bar
        function updateLoading(progress, text, status) {
            loadingProgress.style.width = `${progress}%`;
            if (text) loadingText.innerText = text;
            if (status) loadingStatus.innerText = status;
        }
        
        // Show error
        function showError(message) {
            errorMessage.innerText = message;
            errorScreen.style.display = 'flex';
            document.getElementById('loadingScreen').style.display = 'none';
        }
        
        async function main() {
            try {
                updateLoading(10, "Initializing Python...", "This may take a minute on slow connections");
                
                // Initialize Pyodide
                const pyodide = await loadPyodide();
                updateLoading(30, "Loading Python dependencies...", "Downloading required packages");
                
                // Install required packages
                try {
                    await pyodide.loadPackagesFromImports(`
                        import numpy
                    `);
                } catch (e) {
                    console.error("Error loading packages:", e);
                    updateLoading(30, "Error loading packages", "Retrying with minimal setup");
                }
                
                updateLoading(50, "Loading game files...", "Downloading game assets");
                
                // Mount game files
                await pyodide.runPythonAsync(`
                    import sys
                    import os
                    import pyodide
                    
                    # Mount game directory
                    game_dir = '/game'
                    os.makedirs(game_dir, exist_ok=True)
                    sys.path.append(game_dir)
                `);
                
                // Fetch and load game files
                try {
                    const response = await fetch('game_files.zip');
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    const blob = await response.blob();
                    const file = new File([blob], "game_files.zip");
                    
                    // Mount the zip file
                    pyodide.FS.writeFile("game_files.zip", new Uint8Array(await file.arrayBuffer()));
                    
                    updateLoading(70, "Extracting game files...", "Setting up game environment");
                    
                    await pyodide.runPythonAsync(`
                        import zipfile
                        import os
                        
                        # Extract game files
                        try:
                            with zipfile.ZipFile('game_files.zip', 'r') as zip_ref:
                                zip_ref.extractall('/game')
                            print("Game files extracted successfully")
                        except Exception as e:
                            print(f"Error extracting game files: {e}")
                            
                        # List extracted files for debugging
                        print("Files in /game:")
                        for root, dirs, files in os.walk('/game'):
                            print(f"Directory: {root}")
                            for file in files:
                                print(f"  {file}")
                                
                        # Setup pygame web adapter
                        import sys
                        class PygameWebAdapter:
                            def __init__(self):
                                self.canvas = None
                                self.events = []
                                
                            def init(self):
                                return 1
                                
                            def display_init(self):
                                return 1
                                
                            def get_canvas(self):
                                return self.canvas
                                
                            def set_canvas(self, canvas):
                                self.canvas = canvas
                                
                            def add_event(self, event):
                                self.events.append(event)
                                
                            def poll_events(self):
                                events = self.events
                                self.events = []
                                return events
                                
                        sys.modules['pygame_web'] = PygameWebAdapter()
                    `);
                } catch (e) {
                    console.error("Error loading game files:", e);
                    showError("Could not load game files. Please check your internet connection and try again.");
                    return;
                }
                
                updateLoading(90, "Starting game...", "Initializing game engine");
                
                // Run main game script - simplified version for web
                try {
                    await pyodide.runPythonAsync(`
                        import sys
                        sys.path.insert(0, '/game')
                        
                        # Override pygame with web version
                        import sys
                        
                        class WebPygame:
                            def __init__(self):
                                self.canvas = document.getElementById('gameCanvas')
                                self.context = self.canvas.getContext('2d')
                                
                            def init(self):
                                return 1
                                
                            def quit(self):
                                return
                                
                            def display(self):
                                class DisplayModule:
                                    def __init__(self, pygame):
                                        self.pygame = pygame
                                        
                                    def set_mode(self, size):
                                        return self.pygame.canvas
                                        
                                    def flip(self):
                                        return
                                        
                                    def set_caption(self, caption):
                                        document.title = caption
                                        
                                return DisplayModule(self)
                        
                        # Initialize our web game
                        web_game = WebPygame()
                        sys.modules['pygame'] = web_game
                        
                        print("Game engine initialized, starting game...")
                        
                        # Run the start screen (simplified version for web)
                        try:
                            from start_screen import run_start_screen
                            run_start_screen()
                        except Exception as e:
                            print(f"Error starting game: {e}")
                            raise
                    `);
                    
                    updateLoading(100, "Game Ready!", "Click to play");
                    
                    // Hide loading screen after brief delay
                    setTimeout(() => {
                        document.getElementById('loadingScreen').style.display = 'none';
                    }, 1000);
                    
                } catch (e) {
                    console.error("Error starting game:", e);
                    showError(`Error starting game: ${e.message}`);
                }
            } catch (e) {
                console.error("Fatal error:", e);
                showError(`Could not initialize Python environment: ${e.message}`);
            }
        }
        
        // Start the game loading process
        window.onload = main;
    </script>
</body>
</html>
"""
    
    with open(os.path.join(web_dir, "index.html"), "w") as f:
        f.write(html_content)
    
    # Create a zip file with all game files
    print("Creating game archive...")
    
    # Add timestamp to avoid caching issues
    timestamp = int(time.time())
    
    with zipfile.ZipFile(os.path.join(web_dir, "game_files.zip"), "w") as zipf:
        # Add all files in the web_dir except the zip file itself and index.html
        for root, dirs, files in os.walk(web_dir):
            for file in files:
                if file != "game_files.zip" and file != "index.html":
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, web_dir)
                    zipf.write(file_path, arc_path)
                    print(f"Added to archive: {arc_path}")
    
    # Create web manifest
    manifest = {
        "name": "Digital Decay",
        "short_name": "Decay",
        "description": "A game exploring digital decay concepts",
        "start_url": "./index.html",
        "display": "fullscreen",
        "background_color": "#000000",
        "theme_color": "#adb47d",
        "icons": [
            {
                "src": "icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "icon-512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    
    with open(os.path.join(web_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    
    # Create simple icons for PWA
    try:
        import pygame
        pygame.init()
        
        # Create a simple icon with the game name
        for size in [192, 512]:
            icon = pygame.Surface((size, size), pygame.SRCALPHA)
            icon.fill((0, 0, 0, 255))  # Black background
            
            # Draw text
            font_size = size // 8
            try:
                # Try to find the font in the project root
                font_path = os.path.join(project_root, "assets", "fonts", "JetBrainsMono-Regular.ttf")
                if not os.path.exists(font_path):
                    # Try alternative paths
                    alt_paths = [
                        os.path.join(project_root, "assets", "fonts", "JetBrains_Mono", "JetBrainsMono-Regular.ttf"),
                        os.path.join(project_root, "assets", "fonts", "JetBrains_Mono", "static", "JetBrainsMono-Regular.ttf")
                    ]
                    for path in alt_paths:
                        if os.path.exists(path):
                            font_path = path
                            break
                
                if os.path.exists(font_path):
                    font = pygame.font.Font(font_path, font_size)
                else:
                    font = pygame.font.Font(None, font_size)
                    
            except:
                font = pygame.font.Font(None, font_size)
                
            # Title
            title_text = font.render("DIGITAL", True, (173, 180, 125))  # Using decay color
            decay_text = font.render("DECAY", True, (121, 159, 150))  # Using decay color
            
            # Position text
            title_rect = title_text.get_rect(center=(size//2, size//2 - font_size))
            decay_rect = decay_text.get_rect(center=(size//2, size//2 + font_size))
            
            # Draw to icon
            icon.blit(title_text, title_rect)
            icon.blit(decay_text, decay_rect)
            
            # Draw a border
            pygame.draw.rect(icon, (173, 180, 125), (0, 0, size, size), 6)
            
            # Save the icon
            pygame.image.save(icon, os.path.join(web_dir, f"icon-{size}.png"))
            print(f"Created icon: icon-{size}.png")
            
    except ImportError:
        print("Warning: pygame not available for icon creation. Icons will be missing.")
    except Exception as e:
        print(f"Error creating icons: {e}")
    
    print(f"\nWeb version created successfully in {web_dir} directory")
    print("To deploy to a web server, upload all files in this directory")
    print("For GitHub Pages, push this directory to your repository and enable GitHub Pages")
    
    # Create a zip file of the web build for easy uploading
    try:
        web_zip_path = os.path.join(project_root, "web_build.zip")
        print(f"Creating zip file of web build at: {web_zip_path}")
        
        with zipfile.ZipFile(web_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(web_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(web_dir))
                    zipf.write(file_path, arcname)
                    
        print(f"Created zip file at: {web_zip_path}")
    except Exception as e:
        print(f"Error creating web zip file: {e}")
    
    return True

if __name__ == "__main__":
    create_web_version()