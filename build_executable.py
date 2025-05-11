"""
build_executable.py - Directly builds the Digital Decay executable using PyInstaller

Usage:
    python build_executable.py

Place this file in your project root (not in the build directory).
"""
import os
import sys
import subprocess
import shutil

def build_executable():
    print("Building Digital Decay executable...")
    
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PyInstaller'])
    
    # Get the project root directory
    project_root = os.path.abspath(os.path.dirname(__file__))
    print(f"Project root: {project_root}")
    
    # Create a simple spec file
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Get the list of Python files
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('games', 'games'),
        ('utils', 'utils'),
    ],
    hiddenimports=[
        'pygame',
        'OpenGL.GL',
        'OpenGL.GLU',
        'numpy',
        'colorama',
        'games.game1',
        'games.game2',
        'games.game3',
        'utils.blender_loader',
        'utils.color_utils',
        'utils.decay_bar',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DigitalDecay',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=True,  # Use True for macOS
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DigitalDecay',
)
"""
    
    # Create a temporary spec file
    spec_path = os.path.join(project_root, "DigitalDecay.spec")
    with open(spec_path, "w") as f:
        f.write(spec_content)
    
    print("Created spec file.")
    
    # Run PyInstaller with just the spec file (no additional options)
    print("Running PyInstaller (this may take a while)...")
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'PyInstaller', 'DigitalDecay.spec'],
            cwd=project_root,
            text=True,
            capture_output=True
        )
        
        # Print the output for debugging
        print("\nPyInstaller Output:")
        print(result.stdout)
        
        if result.returncode != 0:
            print("\nPyInstaller Error:")
            print(result.stderr)
            print("\nBuild failed. See error messages above.")
            return False
    except Exception as e:
        print(f"Error running PyInstaller: {e}")
        return False
    
    print("PyInstaller process completed.")
    
    # Create a README file for the executable
    readme_content = """
Digital Decay Game
=================

To run the game:
1. Double-click on 'DigitalDecay.exe' (Windows) or 'DigitalDecay' (Mac/Linux)

Controls:
- Press ENTER to start the game
- Use LEFT/RIGHT arrow keys for paddle movement in Game 2
- For Game 3 (Keyboard Simon Says), use the W, A, S, D keys when prompted
- Press ESC to return to main menu
- Click directly on objects to interact with them

About Digital Decay:
This game explores the concept of entropy and decay in digital systems. Your goal is to reverse
the decay process through various mini-games and interactions. The decay bar at the bottom of
the screen indicates the overall system health - keep it from reaching zero!

Games:
1. Grid Rejuvenation - Click on blocks to restore them
2. Bounce - Use the paddle to bounce falling blocks
3. Keyboard Simon Says - Follow the prompts to press keys

Enjoy!
"""
    
    readme_path = os.path.join(project_root, "dist/DigitalDecay/README.txt")
    os.makedirs(os.path.dirname(readme_path), exist_ok=True)
    
    try:
        with open(readme_path, "w") as f:
            f.write(readme_content)
        print("Created README file.")
    except Exception as e:
        print(f"Error creating README: {e}")
    
    # Create helper scripts
    if os.name == 'nt':  # Windows
        # Create a run.bat file
        bat_content = """@echo off
echo Starting Digital Decay...
start DigitalDecay.exe
"""
        bat_path = os.path.join(project_root, "dist/DigitalDecay/run.bat")
        with open(bat_path, "w") as f:
            f.write(bat_content)
        print("Created run.bat file for Windows.")
    else:  # macOS/Linux
        # Create a run.sh file
        sh_content = """#!/bin/bash
echo "Starting Digital Decay..."
chmod +x ./DigitalDecay
./DigitalDecay
"""
        sh_path = os.path.join(project_root, "dist/DigitalDecay/run.sh")
        with open(sh_path, "w") as f:
            f.write(sh_content)
        # Make it executable
        try:
            os.chmod(sh_path, 0o755)
            print("Created and made executable run.sh file for macOS/Linux.")
        except Exception as e:
            print(f"Error making run.sh executable: {e}")
    
    # Create a zip file for easy distribution
    try:
        # Get the executable directory
        exe_dir = os.path.join(project_root, "dist", "DigitalDecay")
        zip_path = os.path.join(project_root, "dist", "DigitalDecay.zip")
        
        # Create the zip file
        if os.name == 'nt':  # Windows
            import zipfile
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(exe_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(exe_dir))
                        zipf.write(file_path, arcname)
        else:  # macOS/Linux
            # Use the zip command which is typically available
            subprocess.run(['zip', '-r', zip_path, 'DigitalDecay'], cwd=os.path.join(project_root, "dist"))
            
        print(f"Created zip file at: {zip_path}")
    except Exception as e:
        print(f"Error creating zip file: {e}")
    
    print("\nBuild completed successfully!")
    print(f"Executable is located in: {os.path.join(project_root, 'dist', 'DigitalDecay')}")
    print(f"Zip file is located at: {os.path.join(project_root, 'dist', 'DigitalDecay.zip')}")
    
    return True

if __name__ == "__main__":
    build_executable()