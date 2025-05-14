"""
build_executable_mac.py - Mac-specific build script for Digital Decay

This creates a proper macOS app bundle without path errors.
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

def create_mac_spec_file():
    """Create a Mac-specific PyInstaller spec file"""
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

# Define data files - be very explicit about paths
datas = []

# Add decay_grids.json specifically
if os.path.exists('assets/decay_grids.json'):
    datas.append(('assets/decay_grids.json', 'assets'))
elif os.path.exists('decay_grids.json'):
    datas.append(('decay_grids.json', 'assets'))

# Add entire directories
asset_dirs = [
    'assets/blender',
    'assets/fonts', 
    'assets/sounds'
]

for asset_dir in asset_dirs:
    if os.path.exists(asset_dir):
        for root, dirs, files in os.walk(asset_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Calculate relative path from project root
                rel_path = os.path.relpath(root, '.')
                datas.append((file_path, rel_path))

# Add Python modules
for module_dir in ['games', 'utils']:
    if os.path.exists(module_dir):
        for root, dirs, files in os.walk(module_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(root, '.')
                    datas.append((file_path, rel_path))

# Hidden imports
hiddenimports = [
    'pygame',
    'pygame.image',
    'pygame.font',
    'OpenGL',
    'OpenGL.GL',
    'OpenGL.GLU',
    'numpy',
    'colorama',
    'json',
    'games.game1',
    'games.game2', 
    'games.game3',
    'utils.blender_loader',
    'utils.color_utils',
    'utils.decay_bar',
]

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create a regular executable first
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
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Create app bundle
app = BUNDLE(
    exe,
    name='DigitalDecay.app',
    icon=None,
    bundle_identifier='com.digitaldecay.game',
    info_plist={
        'CFBundleName': 'Digital Decay',
        'CFBundleDisplayName': 'Digital Decay',
        'CFBundleIdentifier': 'com.digitaldecay.game',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': 'True',
        'NSRequiresAquaSystemAppearance': 'False',
    }
)
'''
    
    with open('DigitalDecay.spec', 'w') as f:
        f.write(spec_content)
    print("Created Mac-specific PyInstaller spec file")

def fix_app_bundle_assets():
    """Fix asset paths in the app bundle"""
    app_path = 'dist/DigitalDecay.app'
    
    if not os.path.exists(app_path):
        print("App bundle not found!")
        return False
    
    # Path to the MacOS directory inside the app bundle
    macos_dir = os.path.join(app_path, 'Contents', 'MacOS')
    
    # Ensure assets directory exists
    assets_dir = os.path.join(macos_dir, 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    
    # Copy critical files
    critical_files = [
        ('assets/decay_grids.json', os.path.join(assets_dir, 'decay_grids.json')),
        ('decay_grids.json', os.path.join(assets_dir, 'decay_grids.json')),
    ]
    
    for src, dst in critical_files:
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"Copied {src} to app bundle")
    
    # Copy asset directories
    asset_dirs = ['blender', 'fonts', 'sounds', 'images']
    for asset_dir in asset_dirs:
        src_dir = os.path.join('assets', asset_dir)
        if os.path.exists(src_dir):
            dst_dir = os.path.join(assets_dir, asset_dir)
            if os.path.exists(dst_dir):
                shutil.rmtree(dst_dir)
            shutil.copytree(src_dir, dst_dir)
            print(f"Copied {src_dir} to app bundle")
    
    return True

def create_standalone_directory():
    """Create a standalone directory version for USB distribution"""
    print("Creating standalone directory version...")
    
    standalone_dir = 'dist/DigitalDecay_Standalone'
    if os.path.exists(standalone_dir):
        shutil.rmtree(standalone_dir)
    
    # Copy the executable from the app bundle
    app_exe = 'dist/DigitalDecay.app/Contents/MacOS/DigitalDecay'
    if os.path.exists(app_exe):
        os.makedirs(standalone_dir)
        shutil.copy2(app_exe, os.path.join(standalone_dir, 'DigitalDecay'))
        
        # Copy assets
        app_assets = 'dist/DigitalDecay.app/Contents/MacOS/assets'
        if os.path.exists(app_assets):
            shutil.copytree(app_assets, os.path.join(standalone_dir, 'assets'))
        
        # Create run script
        run_script = os.path.join(standalone_dir, 'run.sh')
        with open(run_script, 'w') as f:
            f.write('''#!/bin/bash
cd "$(dirname "$0")"
echo "Starting Digital Decay..."
chmod +x ./DigitalDecay
./DigitalDecay
''')
        os.chmod(run_script, 0o755)
        
        # Create README
        readme_content = '''# Digital Decay - Standalone Version

## Running the Game

1. Double-click `DigitalDecay` or run `./run.sh`
2. If it doesn't work, try running from Terminal:
   ```
   cd path/to/DigitalDecay_Standalone
   chmod +x DigitalDecay
   ./DigitalDecay
   ```

## First Time on macOS

macOS may show a security warning:
1. Right-click on `DigitalDecay`
2. Select "Open"
3. Click "Open" in the security dialog

## Contents

- `DigitalDecay` - The game executable
- `assets/` - Game data (keep this folder with the executable)
- `run.sh` - Helper script to launch the game
'''
        
        with open(os.path.join(standalone_dir, 'README.txt'), 'w') as f:
            f.write(readme_content)
        
        print(f"Created standalone version: {standalone_dir}")
        return True
    
    return False

def build_mac_executable():
    """Main build function for macOS"""
    print("=" * 60)
    print("Building Digital Decay for macOS")
    print("=" * 60)
    
    # Verify we're on macOS
    if platform.system() != "Darwin":
        print("This script is for macOS only!")
        return False
    
    # Check for main.py
    if not os.path.exists('main.py'):
        print("Error: main.py not found!")
        return False
    
    # Install PyInstaller
    if not install_pyinstaller():
        return False
    
    # Clean previous builds
    print("Cleaning previous builds...")
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    if os.path.exists('DigitalDecay.spec'):
        os.remove('DigitalDecay.spec')
    
    # Create spec file
    create_mac_spec_file()
    
    # Run PyInstaller
    print("Running PyInstaller...")
    result = subprocess.run([
        sys.executable, '-m', 'PyInstaller', 
        'DigitalDecay.spec',
        '--clean',
        '--noconfirm'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("PyInstaller failed!")
        print("STDERR:", result.stderr)
        return False
    
    print("Build completed!")
    
    # Fix app bundle assets
    print("Fixing app bundle assets...")
    fix_app_bundle_assets()
    
    # Create standalone version
    create_standalone_directory()
    
    # Create distribution archives
    print("Creating distribution archives...")
    
    # App bundle zip
    if os.path.exists('dist/DigitalDecay.app'):
        os.chdir('dist')
        shutil.make_archive('DigitalDecay-macOS-App', 'zip', '.', 'DigitalDecay.app')
        os.chdir('..')
        print("Created DigitalDecay-macOS-App.zip")
    
    # Standalone zip
    if os.path.exists('dist/DigitalDecay_Standalone'):
        os.chdir('dist')
        shutil.make_archive('DigitalDecay-macOS-Standalone', 'zip', '.', 'DigitalDecay_Standalone')
        os.chdir('..')
        print("Created DigitalDecay-macOS-Standalone.zip")
    
    print("\n" + "=" * 60)
    print("BUILD SUCCESSFUL!")
    print("=" * 60)
    print("Created:")
    print("1. DigitalDecay.app - App bundle (double-click to run)")
    print("2. DigitalDecay_Standalone/ - Directory version (for USB)")
    print("3. ZIP files for distribution")
    print("\nFor USB distribution, use the Standalone version")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = build_mac_executable()
    if not success:
        print("Build failed!")
        sys.exit(1)