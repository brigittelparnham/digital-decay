"""
build_executable_fixed.py - Working executable builder for Digital Decay

Usage:
    python build_executable_fixed.py

This will create a standalone executable that properly includes all assets
"""
import os
import sys
import subprocess
import shutil
import platform

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
        return True
    except ImportError:
        print("Installing PyInstaller...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'PyInstaller'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Failed to install PyInstaller: {result.stderr}")
            return False
        return True

def find_all_assets():
    """Find all asset files that need to be included"""
    assets = []
    
    # Define directories to search
    asset_dirs = [
        'assets',
        'assets/blender',
        'assets/blender/objects',
        'assets/blender/animation',
        'assets/blender/animation/rerender',  # Include the dissolve frames
        'assets/fonts',
        'assets/fonts/JetBrains_Mono',
        'assets/fonts/JetBrains_Mono/static',
        'assets/sounds'
    ]
    
    # Add all directories and their contents
    for dir_path in asset_dirs:
        if os.path.exists(dir_path):
            # Add the entire directory
            assets.append(f"('{dir_path}', '{dir_path}')")
            print(f"Found asset directory: {dir_path}")
    
    # Add specific important files
    important_files = [
        'decay_grids.json',
        'requirements.txt'
    ]
    
    # Check if these files exist in assets folder
    for file in important_files:
        file_path = os.path.join('assets', file)
        if os.path.exists(file_path):
            assets.append(f"('{file_path}', '{file_path}')")
        elif os.path.exists(file):
            assets.append(f"('{file}', 'assets/{file}')")
    
    return assets

def create_spec_file():
    """Create a proper PyInstaller spec file with all assets"""
    
    # Find all assets
    assets = find_all_assets()
    assets_str = ',\n        '.join(assets)
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

# Define what data files to include
datas = [
        {assets_str}
]

# Add hidden imports for all game modules
hiddenimports = [
    'pygame',
    'pygame.image',
    'pygame.font',
    'pygame.mixer',
    'OpenGL',
    'OpenGL.GL',
    'OpenGL.GLU',
    'OpenGL.GLUT',
    'numpy',
    'colorama',
    'json',
    'random',
    'math',
    'time',
    
    # Game modules
    'games',
    'games.game1',
    'games.game2', 
    'games.game3',
    
    # Utility modules
    'utils',
    'utils.blender_loader',
    'utils.color_utils',
    'utils.decay_bar',
    
    # Other modules that might be dynamically imported
    'PIL',
    'PIL.Image',
]

# Add any .py files in the project root
for file in os.listdir('.'):
    if file.endswith('.py') and file != 'build_executable_fixed.py':
        module_name = file[:-3]
        if module_name not in ['setup', 'test']:
            hiddenimports.append(module_name)

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',  # Exclude GUI frameworks we don't use
        'matplotlib',
        'scipy',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DigitalDecay',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console for debugging - change to False for release
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# For macOS, create an app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='DigitalDecay.app',
        icon=None,
        bundle_identifier='com.digitaldecay.game',
        info_plist={{
            'CFBundleName': 'Digital Decay',
            'CFBundleDisplayName': 'Digital Decay',
            'CFBundleIdentifier': 'com.digitaldecay.game',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
        }}
    )
'''
    
    with open('DigitalDecay.spec', 'w') as f:
        f.write(spec_content)
    print("Created PyInstaller spec file: DigitalDecay.spec")

def verify_assets():
    """Verify that critical assets exist before building"""
    critical_files = [
        'assets/decay_grids.json',
        'main.py',
        'terminal_intro.py',
        'start_screen.py',
        'main_menu.py',
        'decay_engine.py',
        'end_screen.py'
    ]
    
    missing_files = []
    for file in critical_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("WARNING: Missing critical files:")
        for file in missing_files:
            print(f"  - {file}")
        
        # Try to find decay_grids.json in alternate locations
        if 'assets/decay_grids.json' in missing_files:
            if os.path.exists('decay_grids.json'):
                print("Found decay_grids.json in root, copying to assets/")
                os.makedirs('assets', exist_ok=True)
                shutil.copy2('decay_grids.json', 'assets/decay_grids.json')
                missing_files.remove('assets/decay_grids.json')
        
        if missing_files:
            print("\nSome files are still missing. The build may not work correctly.")
            return False
    
    print("All critical files found.")
    return True

def create_launcher_scripts(dist_dir):
    """Create platform-specific launcher scripts"""
    system = platform.system()
    
    # Windows batch file
    if system == "Windows":
        bat_content = '''@echo off
cd /d "%~dp0"
echo Starting Digital Decay...
echo.

REM Check if the executable exists
if not exist "DigitalDecay.exe" (
    echo ERROR: DigitalDecay.exe not found!
    echo Make sure all files are extracted properly.
    pause
    exit /b 1
)

REM Run the game
DigitalDecay.exe

REM Check exit code
if errorlevel 1 (
    echo.
    echo Game exited with error code %errorlevel%
    echo Press any key to close this window.
    pause >nul
)
'''
        with open(os.path.join(dist_dir, 'run.bat'), 'w') as f:
            f.write(bat_content)
        print("Created run.bat for Windows")
    
    # Unix shell script (macOS/Linux)
    sh_content = '''#!/bin/bash
cd "$(dirname "$0")"
echo "Starting Digital Decay..."
echo

# Check if executable exists
if [ ! -f "./DigitalDecay" ]; then
    echo "ERROR: DigitalDecay executable not found!"
    echo "Make sure all files are extracted properly."
    echo "Press enter to continue..."
    read
    exit 1
fi

# Make sure it's executable
chmod +x ./DigitalDecay

# Run the game
./DigitalDecay
exit_code=$?

# Check exit code
if [ $exit_code -ne 0 ]; then
    echo
    echo "Game exited with error code $exit_code"
    echo "Press enter to continue..."
    read
fi
'''
    
    sh_path = os.path.join(dist_dir, 'run.sh')
    with open(sh_path, 'w') as f:
        f.write(sh_content)
    
    # Make executable on Unix systems
    if system in ["Linux", "Darwin"]:
        os.chmod(sh_path, 0o755)
        print("Created and made executable run.sh for Unix systems")

def post_build_fixes(dist_dir):
    """Apply post-build fixes to ensure all assets are properly copied"""
    
    # Ensure assets directory exists in the distribution
    dist_assets = os.path.join(dist_dir, 'assets')
    if not os.path.exists(dist_assets):
        os.makedirs(dist_assets)
    
    # Copy critical files that might have been missed
    critical_assets = [
        ('decay_grids.json', 'assets/decay_grids.json'),
        ('assets/decay_grids.json', 'assets/decay_grids.json'),
    ]
    
    for src, dst in critical_assets:
        if os.path.exists(src):
            dst_path = os.path.join(dist_dir, dst)
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src, dst_path)
            print(f"Copied {src} to {dst_path}")
    
    # Copy assets directories
    asset_dirs = [
        'assets/blender',
        'assets/fonts', 
        'assets/sounds'
    ]
    
    for asset_dir in asset_dirs:
        if os.path.exists(asset_dir):
            dst_dir = os.path.join(dist_dir, asset_dir)
            if os.path.exists(dst_dir):
                shutil.rmtree(dst_dir)
            shutil.copytree(asset_dir, dst_dir)
            print(f"Copied {asset_dir} directory")

def create_readme():
    """Create a comprehensive README for the executable"""
    readme_content = '''# Digital Decay - Standalone Game

## Quick Start

1. **Windows**: Double-click `DigitalDecay.exe` or run `run.bat`
2. **macOS**: Double-click `DigitalDecay` or run `./run.sh`
3. **Linux**: Double-click `DigitalDecay` or run `./run.sh`

## First Time Setup (macOS)

macOS may show a security warning for unsigned applications:
1. Right-click on `DigitalDecay` 
2. Select "Open"
3. Click "Open" in the security dialog

## First Time Setup (Linux)

Make sure the executable has permission to run:
```bash
chmod +x ./DigitalDecay
```

## Controls

- **ENTER**: Start game / Continue / Confirm
- **ESC**: Exit to main menu / Quit game
- **Arrow Keys**: Move paddle (Game 2) / Navigate menus
- **WASD**: Game controls (Game 3 - Keyboard Simon Says)
- **Mouse**: Click to interact (Game 1 - Grid Rejuvenation)
- **SPACE**: Complete sequence (Game 3)

## Game Modes

### 1. Grid Rejuvenation
Click on the colored grid blocks to restore them from their decayed state.
Watch the colors change as you rejuvenate the system!

### 2. Bounce
Use the left/right arrow keys to control your paddle and bounce the falling
blocks to prevent system decay.

### 3. Keyboard Simon Says
Follow the sequence prompts carefully. Only press keys when you see 
"Computer says" - pressing at the wrong time accelerates system decay!

## Troubleshooting

### Game Won't Start
- Make sure all files from the zip are extracted together
- Try running from command line to see any error messages
- Ensure your system supports OpenGL 2.1 or higher

### Missing Graphics/Assets
- Verify the `assets` folder is present alongside the executable
- Try re-extracting the entire zip file
- Check that `assets/decay_grids.json` exists

### Performance Issues
- Close other applications to free up memory
- Try running in compatibility mode (Windows)
- Update your graphics drivers

### Terminal Colors Not Showing (colorama issue)
This is expected on some systems. The game will still run correctly,
just without colored terminal output.

## Technical Information

- Built with Python and PyGame
- Uses OpenGL for 3D graphics
- Requires OpenGL 2.1+ support
- Self-contained - no Python installation needed

## File Structure

Keep these files together:
```
DigitalDecay/
├── DigitalDecay.exe (or DigitalDecay on Mac/Linux)
├── assets/
│   ├── decay_grids.json (critical!)
│   ├── blender/ (3D objects and animations)
│   ├── fonts/ (game fonts)
│   └── ...
├── run.bat (Windows launcher)
├── run.sh (Unix launcher)
└── README.txt (this file)
```

## About the Game

Digital Decay explores themes of entropy and digital deterioration. 
Your goal is to maintain system integrity through various mini-games
as you watch the overall system health decay over time.

The game features:
- Dynamic color palettes that change with system health
- 3D objects with decay-based coloring
- Multiple game modes with different mechanics
- Real-time system decay tracking

Enjoy the game, and remember: entropy always wins in the end!

---
Version 1.0 - Built {date}
'''
    
    import datetime
    return readme_content.format(date=datetime.datetime.now().strftime("%Y-%m-%d"))

def build_executable():
    """Main build function"""
    print("=" * 60)
    print("Building Digital Decay Standalone Executable")
    print("=" * 60)
    
    # Verify we're in the right directory
    if not os.path.exists('main.py'):
        print("ERROR: main.py not found!")
        print("Make sure you're running this script from the project root directory.")
        return False
    
    # Verify critical assets exist
    print("Verifying assets...")
    if not verify_assets():
        print("WARNING: Some assets are missing. Build will continue but may not work correctly.")
    
    # Install PyInstaller
    if not install_pyinstaller():
        return False
    
    # Clean previous builds
    print("Cleaning previous builds...")
    for dir_name in ['build', 'dist', '__pycache__']:
        if os.path.exists(dir_name):
            print(f"  Removing {dir_name}/")
            shutil.rmtree(dir_name)
    
    # Remove old spec file
    if os.path.exists('DigitalDecay.spec'):
        os.remove('DigitalDecay.spec')
    
    # Create spec file
    print("Creating PyInstaller specification...")
    create_spec_file()
    
    # Run PyInstaller
    print("Running PyInstaller...")
    print("This may take several minutes, especially on first run...")
    print("PyInstaller is analyzing dependencies and bundling assets...")
    
    result = subprocess.run([
        sys.executable, '-m', 'PyInstaller', 
        'DigitalDecay.spec',
        '--clean',
        '--noconfirm'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("PyInstaller FAILED!")
        print("\n--- STDOUT ---")
        print(result.stdout)
        print("\n--- STDERR ---") 
        print(result.stderr)
        print("\nTry fixing the errors above and run again.")
        return False
    
    print("PyInstaller completed successfully!")
    
    # Find the distribution directory
    if platform.system() == "Darwin" and os.path.exists('dist/DigitalDecay.app'):
        # macOS app bundle
        dist_dir = 'dist/DigitalDecay.app/Contents/MacOS'
        app_dir = 'dist/DigitalDecay.app'
        print(f"macOS app bundle created at: {app_dir}")
    else:
        # Regular executable
        dist_dir = 'dist'
        if not os.path.exists(dist_dir):
            print(f"ERROR: Distribution directory not found at {dist_dir}")
            return False
    
    # Apply post-build fixes
    print("Applying post-build fixes...")
    if platform.system() != "Darwin":
        post_build_fixes(dist_dir)
    
    # Create README
    print("Creating README...")
    readme_content = create_readme()
    readme_path = os.path.join(dist_dir, 'README.txt')
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    # Create launcher scripts (not for app bundles)
    if platform.system() != "Darwin" or not os.path.exists('dist/DigitalDecay.app'):
        print("Creating launcher scripts...")
        create_launcher_scripts(dist_dir)
    
    # Create distribution archive
    print("Creating distribution archive...")
    system_name = platform.system()
    if system_name == "Darwin":
        if os.path.exists('dist/DigitalDecay.app'):
            # Create DMG or zip for app bundle
            zip_name = "DigitalDecay-macOS"
            shutil.make_archive(f'dist/{zip_name}', 'zip', 'dist', 'DigitalDecay.app')
        else:
            zip_name = "DigitalDecay-macOS"
            shutil.make_archive(f'dist/{zip_name}', 'zip', 'dist')
    else:
        zip_name = f"DigitalDecay-{system_name}"
        if os.path.exists(os.path.join(dist_dir, 'DigitalDecay.exe')):
            # Windows - create archive with all files in dist
            shutil.make_archive(f'dist/{zip_name}', 'zip', 'dist')
        else:
            # Linux - create archive with executable and assets
            shutil.make_archive(f'dist/{zip_name}', 'zip', 'dist')
    
    print(f"Created {zip_name}.zip")
    
    # Final verification
    print("\nVerifying build...")
    if platform.system() == "Windows":
        exe_path = os.path.join(dist_dir, 'DigitalDecay.exe')
    else:
        exe_path = os.path.join(dist_dir, 'DigitalDecay')
        if platform.system() == "Darwin" and os.path.exists('dist/DigitalDecay.app'):
            exe_path = 'dist/DigitalDecay.app/Contents/MacOS/DigitalDecay'
    
    if os.path.exists(exe_path):
        print(f"✓ Executable created: {exe_path}")
    else:
        print(f"✗ Executable not found at: {exe_path}")
        return False
    
    # Check for critical assets
    asset_checks = [
        ('assets/decay_grids.json', 'Critical color data'),
        ('assets', 'Assets directory')
    ]
    
    for asset_path, description in asset_checks:
        if platform.system() == "Darwin" and os.path.exists('dist/DigitalDecay.app'):
            full_path = f'dist/DigitalDecay.app/Contents/MacOS/{asset_path}'
        else:
            full_path = os.path.join(dist_dir, asset_path)
            
        if os.path.exists(full_path):
            print(f"✓ {description}: {asset_path}")
        else:
            print(f"✗ {description} missing: {asset_path}")
    
    # Success message
    print("\n" + "=" * 60)
    print("BUILD COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    if platform.system() == "Darwin" and os.path.exists('dist/DigitalDecay.app'):
        print(f"macOS app bundle: dist/DigitalDecay.app")
        print("Double-click the app to run, or right-click -> Open for first run")
    else:
        print(f"Executable directory: {dist_dir}")
        print("Run the game by double-clicking the executable")
    
    print(f"Distribution archive: dist/{zip_name}.zip")
    print("\nYou can now:")
    print("1. Copy the executable/app to a USB drive")
    print("2. Upload the zip file to GitHub releases")
    print("3. Test the game on another computer")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = build_executable()
    if not success:
        print("\nBuild failed. Check the errors above and try again.")
        input("Press Enter to exit...")
        sys.exit(1)
    else:
        print("\nBuild completed successfully!")
        input("Press Enter to exit...")