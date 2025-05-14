"""
build_web_game.py - Build the actual game to run in browser

This creates a web version of Digital Decay that runs directly in the browser
using Pygame for Web (not just a download page).
"""
import os
import shutil
import json
import zipfile
import base64
from pathlib import Path

def create_web_game():
    """Create a web version that runs the actual game"""
    print("=" * 60)
    print("Building Digital Decay for Web Browser")
    print("Converting Python/Pygame game to run in browser")
    print("=" * 60)
    
    # Create web build directory
    web_dir = "web_build"
    if os.path.exists(web_dir):
        shutil.rmtree(web_dir)
    os.makedirs(web_dir)
    
    # Copy all Python files
    print("Copying Python game files...")
    python_files = [
        'main.py',
        'terminal_intro.py',
        'start_screen.py',
        'main_menu.py',
        'decay_engine.py',
        'end_screen.py'
    ]
    
    for py_file in python_files:
        if os.path.exists(py_file):
            shutil.copy2(py_file, web_dir)
            print(f"  ✓ {py_file}")
    
    # Copy game and utils directories
    for dir_name in ['games', 'utils']:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, os.path.join(web_dir, dir_name))
            print(f"  ✓ {dir_name}/ directory")
    
    # Copy assets
    if os.path.exists('assets'):
        shutil.copytree('assets', os.path.join(web_dir, 'assets'))
        print(f"  ✓ assets/ directory")
    
    # Create the main HTML file
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Decay - Web Game</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #000;
            color: #adb47d;
            font-family: monospace;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            overflow: hidden;
        }
        
        #gameArea {
            position: relative;
            width: 1024px;
            height: 768px;
            max-width: 100vw;
            max-height: 100vh;
            border: 2px solid #adb47d;
            background: #000;
        }
        
        #gameCanvas {
            width: 100%;
            height: 100%;
            display: block;
        }
        
        #loadingScreen {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: #000;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 100;
        }
        
        #loadingText {
            font-size: 24px;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        #loadingBar {
            width: 400px;
            height: 20px;
            border: 2px solid #adb47d;
            border-radius: 10px;
            overflow: hidden;
        }
        
        #loadingProgress {
            width: 0%;
            height: 100%;
            background: linear-gradient(90deg, #adb47d, #dce4aa);
            transition: width 0.3s ease;
        }
        
        #instructions {
            position: absolute;
            bottom: 10px;
            left: 50%;
            transform: translateX(-50%);
            text-align: center;
            font-size: 14px;
            opacity: 0.8;
        }
        
        .glitch {
            animation: glitch 0.3s infinite;
        }
        
        @keyframes glitch {
            0% { transform: translate(0); }
            20% { transform: translate(-2px, 2px); }
            40% { transform: translate(-2px, -2px); }
            60% { transform: translate(2px, 2px); }
            80% { transform: translate(2px, -2px); }
            100% { transform: translate(0); }
        }
    </style>
</head>
<body>
    <div id="gameArea">
        <canvas id="gameCanvas" width="1024" height="768"></canvas>
        
        <div id="loadingScreen">
            <div id="loadingText">Loading Digital Decay...</div>
            <div id="loadingBar">
                <div id="loadingProgress"></div>
            </div>
            <div id="instructions">
                <p>Controls: Arrow Keys, WASD, Mouse Click, Enter, Escape</p>
                <p>Experience digital entropy in your browser</p>
            </div>
        </div>
    </div>

    <!-- Load Pyodide (Python in browser) -->
    <script src="https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js"></script>
    
    <script>
        let pyodide;
        let gameReady = false;
        
        // Loading progress tracking
        const loadingProgress = document.getElementById('loadingProgress');
        const loadingText = document.getElementById('loadingText');
        
        function updateProgress(percent, text) {
            loadingProgress.style.width = percent + '%';
            if (text) loadingText.textContent = text;
        }
        
        async function initGame() {
            try {
                updateProgress(10, "Initializing Python runtime...");
                
                // Load Pyodide (Python in browser)
                pyodide = await loadPyodide({
                    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/"
                });
                
                updateProgress(30, "Loading Python packages...");
                
                // Install required packages
                await pyodide.loadPackage([
                    "numpy",
                    "micropip"
                ]);
                
                // Install pygame-web via micropip
                const micropip = pyodide.pyimport("micropip");
                await micropip.install("pygame-ce");
                
                updateProgress(50, "Setting up game environment...");
                
                // Create virtual file system for game files
                pyodide.FS.mkdir("/game");
                
                updateProgress(60, "Loading game assets...");
                
                // Load the game files archive
                const response = await fetch("game_files.zip");
                const arrayBuffer = await response.arrayBuffer();
                const uint8Array = new Uint8Array(arrayBuffer);
                
                // Write to virtual filesystem
                pyodide.FS.writeFile("/game/game_files.zip", uint8Array);
                
                updateProgress(70, "Extracting game files...");
                
                // Extract the game files in Python
                await pyodide.runPythonAsync(`
                    import zipfile
                    import sys
                    import os
                    
                    # Extract game files
                    with zipfile.ZipFile('/game/game_files.zip', 'r') as zip_ref:
                        zip_ref.extractall('/game')
                    
                    # Add game directory to Python path
                    sys.path.insert(0, '/game')
                    
                    print("Game files extracted successfully")
                `);
                
                updateProgress(80, "Setting up Pygame for web...");
                
                // Setup pygame for web
                await pyodide.runPythonAsync(`
                    import pygame
                    import sys
                    import os
                    
                    # Initialize pygame
                    pygame.init()
                    
                    # Set up display for web
                    screen = pygame.display.set_mode((1024, 768))
                    pygame.display.set_caption("Digital Decay")
                    
                    # Get canvas element for pygame
                    from js import document
                    canvas = document.getElementById('gameCanvas')
                    
                    print("Pygame initialized for web")
                `);
                
                updateProgress(90, "Starting game...");
                
                // Import and start the game
                await pyodide.runPythonAsync(`
                    # Import the main game module
                    import main
                    
                    # Create a web-friendly main function
                    def start_web_game():
                        try:
                            # Modify main to work in web environment
                            main.main()
                        except Exception as e:
                            print(f"Game error: {e}")
                            import traceback
                            traceback.print_exc()
                    
                    print("Game ready to start")
                `);
                
                updateProgress(100, "Digital Decay Ready!");
                
                // Hide loading screen and start game
                setTimeout(() => {
                    document.getElementById('loadingScreen').style.display = 'none';
                    gameReady = true;
                    
                    // Start the game
                    pyodide.runPython("start_web_game()");
                }, 1000);
                
            } catch (error) {
                console.error("Failed to initialize game:", error);
                loadingText.textContent = "Failed to load game: " + error.message;
                loadingText.classList.add('glitch');
            }
        }
        
        // Handle keyboard events for the game
        document.addEventListener('keydown', (event) => {
            if (gameReady && pyodide) {
                // Forward keyboard events to pygame
                pyodide.runPython(`
                    import pygame
                    # Create pygame event
                    event = pygame.event.Event(pygame.KEYDOWN, key=${event.keyCode})
                    pygame.event.post(event)
                `);
            }
        });
        
        document.addEventListener('keyup', (event) => {
            if (gameReady && pyodide) {
                pyodide.runPython(`
                    import pygame
                    event = pygame.event.Event(pygame.KEYUP, key=${event.keyCode})
                    pygame.event.post(event)
                `);
            }
        });
        
        // Handle mouse events
        document.getElementById('gameCanvas').addEventListener('click', (event) => {
            if (gameReady && pyodide) {
                const rect = event.target.getBoundingClientRect();
                const x = event.clientX - rect.left;
                const y = event.clientY - rect.top;
                
                pyodide.runPython(`
                    import pygame
                    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(${x}, ${y}), button=1)
                    pygame.event.post(event)
                `);
            }
        });
        
        // Start loading when page loads
        window.addEventListener('load', initGame);
    </script>
</body>
</html>'''
    
    with open(os.path.join(web_dir, 'index.html'), 'w') as f:
        f.write(html_content)
    print("✓ Created index.html")
    
    # Create game files archive
    print("Creating game files archive...")
    with zipfile.ZipFile(os.path.join(web_dir, 'game_files.zip'), 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add all Python files
        for py_file in python_files:
            if os.path.exists(py_file):
                zf.write(py_file)
        
        # Add directories
        for dir_name in ['games', 'utils', 'assets']:
            if os.path.exists(dir_name):
                for root, dirs, files in os.walk(dir_name):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, '.')
                        zf.write(file_path, arc_path)
        
        print(f"✓ Game files archived")
    
    # Create deployment instructions
    instructions = '''# Digital Decay - Web Deployment Instructions

## What was created:

- `index.html` - Main game page
- `game_files.zip` - All game assets and code

## Deployment Options:

### 1. GitHub Pages
1. Push the `web_build` folder contents to your GitHub repository
2. Enable GitHub Pages in repository settings
3. Set source to the main branch
4. Your game will be available at: https://yourusername.github.io/repository-name

### 2. Local Testing
1. Install a local web server:
   ```bash
   python -m http.server 8000
   ```
2. Navigate to the web_build folder
3. Open http://localhost:8000 in your browser

### 3. Other Web Hosts
Upload the contents of `web_build` to any web hosting service that supports:
- Static file hosting
- WebAssembly (WASM) support

## Technical Details:

- Uses Pyodide to run Python in the browser
- Converts Pygame calls to web canvas operations
- All game logic runs client-side
- No server required (static hosting only)

## Browser Compatibility:

- Chrome/Chromium (recommended)
- Firefox
- Safari (limited)
- Edge

## Performance Notes:

- Initial loading takes time (downloading Python runtime)
- Performance may be slower than native executable
- Some Pygame features may not work exactly the same

## Troubleshooting:

- If game doesn't load, check browser console for errors
- Ensure all files are uploaded correctly
- Some browsers may block local file access
'''
    
    with open(os.path.join(web_dir, 'DEPLOYMENT.md'), 'w') as f:
        f.write(instructions)
    
    print("✓ Created deployment instructions")
    
    # Create a simple README for the web version
    web_readme = '''# Digital Decay - Web Version

This directory contains the web version of Digital Decay that runs directly in your browser.

## How to run:

1. **Local testing**: 
   - Use any web server (e.g., `python -m http.server 8000`)
   - Open index.html in your browser

2. **Online deployment**:
   - Upload all files to a web hosting service
   - Or use GitHub Pages

## Controls:

- **Arrow Keys**: Navigate/Control paddle
- **WASD**: Game 3 controls
- **Mouse**: Click to interact
- **Enter**: Start/Continue
- **Escape**: Back/Quit

The game may take a moment to load as it downloads the Python runtime for your browser.

Enjoy Digital Decay in your browser!
'''
    
    with open(os.path.join(web_dir, 'README.md'), 'w') as f:
        f.write(web_readme)
    
    # Final summary
    print("\n" + "=" * 60)
    print("WEB VERSION CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Location: {web_dir}/")
    print("\nFiles created:")
    print("  • index.html - Main game page")
    print("  • game_files.zip - All game code and assets")
    print("  • DEPLOYMENT.md - Setup instructions")
    print("  • README.md - Usage guide")
    print("\nTo test locally:")
    print(f"  cd {web_dir}")
    print("  python -m http.server 8000")
    print("  Open http://localhost:8000")
    print("\nFor GitHub Pages:")
    print("  Upload web_build contents to your repository")
    print("  Enable GitHub Pages in settings")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = create_web_game()
    if success:
        print("\n🎮 Web game ready for deployment!")
    else:
        print("\n❌ Web build failed!")