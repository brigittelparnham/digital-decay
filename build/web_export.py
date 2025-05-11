"""
web_export.py - Script to prepare the game for web deployment
"""
import os
import shutil
import zipfile
import json

def create_web_version():
    """Create a web-deployable version of the game"""
    print("Creating web version of Digital Decay...")
    
    # Create web directory
    web_dir = "web_build"
    os.makedirs(web_dir, exist_ok=True)
    
    # Copy core game files
    print("Copying game files...")
    core_files = [
        "main.py",
        "terminal_intro.py",
        "main_menu.py",
        "decay_engine.py",
        "start_screen.py",  # Will be created
        "end_screen.py",    # Will be created
    ]
    
    for file in core_files:
        if os.path.exists(file):
            shutil.copy(file, os.path.join(web_dir, file))
    
    # Create directories
    os.makedirs(os.path.join(web_dir, "games"), exist_ok=True)
    os.makedirs(os.path.join(web_dir, "utils"), exist_ok=True)
    os.makedirs(os.path.join(web_dir, "assets"), exist_ok=True)
    
    # Copy game modules
    game_files = ["__init__.py", "game1.py", "game2.py", "game3.py"]
    for file in game_files:
        src = os.path.join("games", file)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(web_dir, "games", file))
    
    # Copy utility modules
    util_files = ["__init__.py", "blender_loader.py", "color_utils.py", "decay_bar.py"]
    for file in util_files:
        src = os.path.join("utils", file)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(web_dir, "utils", file))
    
    # Copy assets
    if os.path.exists("assets"):
        shutil.copytree("assets", os.path.join(web_dir, "assets"), dirs_exist_ok=True)
    
    # Create HTML wrapper
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
            color: #0f0;
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
            color: #0f0;
        }
        #loadingBar {
            width: 300px;
            height: 20px;
            border: 2px solid #0f0;
            border-radius: 5px;
        }
        #loadingProgress {
            width: 0%;
            height: 100%;
            background-color: #0f0;
            transition: width 0.3s;
        }
    </style>
</head>
<body>
    <div id="loadingScreen">
        <div id="loadingText">Loading Digital Decay...</div>
        <div id="loadingBar">
            <div id="loadingProgress"></div>
        </div>
    </div>
    <canvas id="gameCanvas" width="1024" height="768"></canvas>
    
    <script src="https://cdn.jsdelivr.net/pyodide/v0.23.4/full/pyodide.js"></script>
    <script>
        async function main() {
            const loadingProgress = document.getElementById('loadingProgress');
            const loadingText = document.getElementById('loadingText');
            
            // Update loading bar
            function updateLoading(progress, text) {
                loadingProgress.style.width = `${progress}%`;
                if (text) loadingText.innerText = text;
            }
            
            updateLoading(10, "Initializing Python...");
            
            // Initialize Pyodide
            const pyodide = await loadPyodide();
            updateLoading(30, "Loading Python dependencies...");
            
            // Install required packages
            await pyodide.loadPackagesFromImports(`
                import numpy
            `);
            updateLoading(50, "Loading game files...");
            
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
            const response = await fetch('game_files.zip');
            const blob = await response.blob();
            const file = new File([blob], "game_files.zip");
            
            // Mount the zip file
            pyodide.FS.writeFile("game_files.zip", await file.arrayBuffer());
            
            await pyodide.runPythonAsync(`
                import zipfile
                import os
                
                # Extract game files
                with zipfile.ZipFile('game_files.zip', 'r') as zip_ref:
                    zip_ref.extractall('/game')
                    
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
            
            updateLoading(80, "Starting game...");
            
            // Run main game script
            await pyodide.runPythonAsync(`
                import sys
                sys.path.insert(0, '/game')
                
                # Override pygame with web version
                import sys
                import pyodide
                
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
                
                # Run the start screen (simplified version for web)
                from start_screen import start_screen
                start_screen()
            `);
            
            // Hide loading screen
            document.getElementById('loadingScreen').style.display = 'none';
        }
        
        main();
    </script>
</body>
</html>
"""
    
    with open(os.path.join(web_dir, "index.html"), "w") as f:
        f.write(html_content)
    
    # Create a zip file with all game files
    print("Creating game archive...")
    with zipfile.ZipFile(os.path.join(web_dir, "game_files.zip"), "w") as zipf:
        for root, dirs, files in os.walk(web_dir):
            for file in files:
                if file != "game_files.zip" and file != "index.html":
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, web_dir)
                    zipf.write(file_path, arc_path)
    
    # Create web manifest
    manifest = {
        "name": "Digital Decay",
        "short_name": "Decay",
        "description": "A game exploring digital decay concepts",
        "start_url": "./index.html",
        "display": "fullscreen",
        "background_color": "#000000",
        "theme_color": "#00ff00",
        "icons": [
            {
                "src": "assets/icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "assets/icon-512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    
    with open(os.path.join(web_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Web version created in {web_dir} directory")
    print("To deploy to a web server, upload all files in this directory")

if __name__ == "__main__":
    create_web_version()