"""
build_mac_correct_assets.py - Mac build with correct asset structure

Based on actual asset structure:
assets/
├── decay_grids.json
├── images/
├── fonts/
│   └── (ttf file)
└── blender/
    ├── objects/
    └── animation/
"""
import os
import sys
import subprocess
import shutil
import platform

def verify_actual_assets():
    """Verify and display the actual asset structure"""
    print("=" * 50)
    print("VERIFYING ACTUAL ASSET STRUCTURE")
    print("=" * 50)
    
    # Check main assets directory
    if not os.path.exists('assets'):
        print("❌ assets/ directory not found!")
        return False
    
    print("✓ assets/ directory found")
    
    # Check each expected item
    expected_items = {
        'decay_grids.json': 'file',
        'images': 'dir',
        'fonts': 'dir', 
        'blender': 'dir'
    }
    
    found_items = []
    for item, item_type in expected_items.items():
        path = os.path.join('assets', item)
        if os.path.exists(path):
            if item_type == 'dir' and os.path.isdir(path):
                print(f"✓ assets/{item}/ (directory)")
                found_items.append(item)
                
                # List contents
                contents = os.listdir(path)
                print(f"    Contains: {contents}")
                
            elif item_type == 'file' and os.path.isfile(path):
                print(f"✓ assets/{item} (file)")
                found_items.append(item)
        else:
            print(f"❌ assets/{item} not found")
    
    # Check blender subdirectories
    if 'blender' in found_items:
        blender_path = os.path.join('assets', 'blender')
        expected_blender = ['objects', 'animation']
        
        for subdir in expected_blender:
            subdir_path = os.path.join(blender_path, subdir)
            if os.path.exists(subdir_path):
                print(f"✓ assets/blender/{subdir}/")
                contents = os.listdir(subdir_path)
                print(f"    Contains: {contents}")
                
                # Special check for OBJ files
                if subdir == 'objects':
                    obj_files = [f for f in contents if f.endswith('.obj')]
                    print(f"    OBJ files: {obj_files}")
                    row_files = [f for f in obj_files if f.startswith('row')]
                    if row_files:
                        print(f"    Row-specific: {row_files}")
            else:
                print(f"❌ assets/blender/{subdir}/ not found")
    
    # Check fonts
    if 'fonts' in found_items:
        fonts_path = os.path.join('assets', 'fonts')
        font_files = [f for f in os.listdir(fonts_path) if f.endswith('.ttf')]
        print(f"✓ Font files found: {font_files}")
    
    return True

def create_correct_spec_file():
    """Create spec file with the correct asset structure"""
    
    # Verify assets first
    verify_actual_assets()
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

# Define data files based on actual structure
datas = []

# Add the entire assets directory
if os.path.exists('assets'):
    print("Adding assets directory...")
    datas.append(('assets', 'assets'))

# Verify specific critical files
critical_files = [
    ('assets/decay_grids.json', 'assets'),
]

for src, dest in critical_files:
    if os.path.exists(src):
        print(f"Verified critical file: {src}")
    else:
        print(f"WARNING: Missing critical file: {src}")

# Hidden imports (comprehensive list)
hiddenimports = [
    # Pygame modules
    'pygame',
    'pygame.image',
    'pygame.font',
    'pygame.mixer',
    'pygame.transform',
    'pygame.time',
    'pygame.event',
    'pygame.key',
    'pygame.mouse',
    'pygame.display',
    'pygame.surface',
    'pygame.rect',
    'pygame.color',
    
    # OpenGL
    'OpenGL',
    'OpenGL.GL',
    'OpenGL.GLU',
    
    # Core Python
    'numpy',
    'colorama',
    'json',
    'random',
    'math',
    'time',
    'os',
    'sys',
    're',
    
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
    
    # Main game modules
    'main',
    'main_menu',
    'start_screen',
    'end_screen',
    'decay_engine',
    'terminal_intro',
]

# Analysis
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

# Single file executable
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
    console=True,  # Keep console for now to debug
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Mac app bundle
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
        'LSMinimumSystemVersion': '10.12',
    }
)
'''
    
    with open('DigitalDecay.spec', 'w') as f:
        f.write(spec_content)
    print("Created spec file with correct asset structure")

def add_comprehensive_debug():
    """Add debug code to track asset loading in detail"""
    
    # Add debug to main.py
    if not os.path.exists('main.py'):
        print("main.py not found!")
        return
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Check if debug already exists
    if 'ASSET DEBUG START' in content:
        print("Debug code already exists in main.py")
        return
    
    debug_code = '''
# ASSET DEBUG START
print("="*60)
print("DIGITAL DECAY - ASSET DEBUG")
print("="*60)

import sys
import os

print(f"Python: {sys.version}")
print(f"Platform: {sys.platform}")

# Check execution context
if hasattr(sys, '_MEIPASS'):
    print(f"PyInstaller bundle: {sys._MEIPASS}")
    bundle_path = sys._MEIPASS
    
    # Check bundle contents
    print(f"Bundle contents: {os.listdir(bundle_path)}")
    
    # Check assets specifically
    assets_path = os.path.join(bundle_path, 'assets')
    if os.path.exists(assets_path):
        print(f"✓ Assets found at: {assets_path}")
        assets_contents = os.listdir(assets_path)
        print(f"Assets contents: {assets_contents}")
        
        # Check each expected directory
        for item in ['decay_grids.json', 'images', 'fonts', 'blender']:
            item_path = os.path.join(assets_path, item)
            if os.path.exists(item_path):
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    print(f"✓ {item} (file, {size} bytes)")
                else:
                    contents = os.listdir(item_path)
                    print(f"✓ {item}/ directory: {contents}")
                    
                    # Special checks
                    if item == 'blender':
                        for subdir in ['objects', 'animation']:
                            subdir_path = os.path.join(item_path, subdir)
                            if os.path.exists(subdir_path):
                                subdir_contents = os.listdir(subdir_path)
                                print(f"  ✓ blender/{subdir}/: {subdir_contents}")
                                if subdir == 'objects':
                                    obj_files = [f for f in subdir_contents if f.endswith('.obj')]
                                    print(f"    OBJ files: {obj_files}")
                            else:
                                print(f"  ✗ blender/{subdir}/ not found")
                    
                    elif item == 'fonts':
                        ttf_files = [f for f in contents if f.endswith('.ttf')]
                        print(f"  TTF files: {ttf_files}")
            else:
                print(f"✗ {item} not found")
    else:
        print(f"✗ Assets directory not found!")
        print(f"Available in bundle: {os.listdir(bundle_path)}")
else:
    print("Running in development mode")
    if os.path.exists('assets'):
        print("Development assets found")
    else:
        print("No assets directory in development!")

print("="*60)
# ASSET DEBUG END

'''
    
    # Insert at the beginning (after docstring if present)
    lines = content.split('\\n')
    insert_pos = 0
    
    # Skip docstring
    in_docstring = False
    for i, line in enumerate(lines):
        if line.strip().startswith('"""') and not in_docstring:
            in_docstring = True
        elif line.strip().endswith('"""') and in_docstring:
            insert_pos = i + 1
            break
        elif not in_docstring and line.strip() and not line.strip().startswith('#'):
            break
    
    # Insert debug code
    debug_lines = debug_code.strip().split('\\n')
    for i, debug_line in enumerate(debug_lines):
        lines.insert(insert_pos + i, debug_line)
    
    # Write back
    with open('main.py', 'w') as f:
        f.write('\\n'.join(lines))
    
    print("Added comprehensive debug code to main.py")

def create_test_launchers():
    """Create test launchers for the Mac version"""
    
    # Console test launcher
    console_launcher = '''#!/bin/bash
echo "Digital Decay - Console Test"
echo "This shows all debug output and errors"
echo "======================================"
echo

cd "$(dirname "$0")"

# Run with console output
if [ -d "DigitalDecay.app" ]; then
    echo "Running app bundle with console..."
    ./DigitalDecay.app/Contents/MacOS/DigitalDecay
    exit_code=$?
else
    echo "Running standalone executable..."
    ./DigitalDecay
    exit_code=$?
fi

echo
echo "======================================"
echo "Exit code: $exit_code"
echo "Press Enter to close..."
read
'''
    
    with open('dist/test_console.sh', 'w') as f:
        f.write(console_launcher)
    os.chmod('dist/test_console.sh', 0o755)
    
    # Quick test launcher
    quick_launcher = '''#!/bin/bash
cd "$(dirname "$0")"
if [ -d "DigitalDecay.app" ]; then
    ./DigitalDecay.app/Contents/MacOS/DigitalDecay
else
    ./DigitalDecay
fi
'''
    
    with open('dist/quick_test.sh', 'w') as f:
        f.write(quick_launcher)
    os.chmod('dist/quick_test.sh', 0o755)

def create_detailed_readme():
    """Create README with asset-specific troubleshooting"""
    readme = '''# Digital Decay - macOS Distribution

## Quick Start

1. **Double-click**: `DigitalDecay.app`
2. **First time**: Right-click → Open → Confirm security dialog

## Testing & Debugging

- `test_console.sh` - Shows detailed debug output
- `quick_test.sh` - Fast command-line test

## Asset Structure

The game includes these assets:
- `decay_grids.json` - Color schemes (critical)
- `images/` - Graphics and textures  
- `fonts/` - TTF font files
- `blender/objects/` - Your custom 3D models
- `blender/animation/` - Animation frames

## Troubleshooting

### App Quits Immediately
Run `./test_console.sh` to see the error. Common issues:
- Missing assets (will be listed in debug output)
- macOS security blocking the app
- OpenGL compatibility

### Main Menu Shows Default Objects  
Look for this in console output:
```
✓ blender/objects/: ['row1.obj', 'row2.obj', ...]
OBJ files: ['row1.obj', 'row2.obj', ...]
```

If you see empty lists or errors, your OBJ files weren't included.

### Debug Output Explanation

**Good output** (assets found):
```
✓ Assets found at: /var/folders/.../assets
✓ decay_grids.json (file, 2048 bytes)
✓ blender/ directory: ['objects', 'animation']
✓ blender/objects/: ['row1.obj', 'row2.obj', ...]
```

**Problem output** (assets missing):
```
✗ Assets directory not found!
Available in bundle: ['main.py', 'pygame', ...]
```

## Game Controls

- **ENTER**: Start game / Continue
- **ESC**: Back to menu / Quit
- **Mouse**: Click blocks (Game 1)
- **Arrow Keys**: Paddle (Game 2)  
- **WASD**: Simon Says (Game 3)

## Contents

- `DigitalDecay.app` - Main game
- `test_console.sh` - Debug launcher
- `quick_test.sh` - Quick test
- `README.txt` - This file

Run the console test first if you have any issues!
'''
    
    with open('dist/README.txt', 'w') as f:
        f.write(readme)

def build_with_correct_assets():
    """Build with the correct asset structure"""
    print("=" * 60)
    print("Digital Decay - Mac Build (Correct Assets)")
    print("=" * 60)
    
    # Install PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'PyInstaller'])
    
    # Verify we have the right files
    if not os.path.exists('main.py'):
        print("ERROR: main.py not found!")
        return False
    
    # Verify and show asset structure
    print("\\nVerifying asset structure...")
    if not verify_actual_assets():
        print("Asset verification issues - continuing anyway...")
    
    # Add debug code
    print("\\nAdding debug code...")
    add_comprehensive_debug()
    
    # Clean previous builds
    print("\\nCleaning previous builds...")
    for item in ['build', 'dist', 'DigitalDecay.spec']:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)
    
    # Create spec file
    print("\\nCreating build specification...")
    create_correct_spec_file()
    
    # Build
    print("\\nBuilding executable...")
    result = subprocess.run([
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        'DigitalDecay.spec'
    ])
    
    if result.returncode != 0:
        print("BUILD FAILED!")
        return False
    
    # Verify build
    if os.path.exists('dist/DigitalDecay.app'):
        print("✓ App bundle created successfully")
    else:
        print("✗ App bundle not found!")
        return False
    
    # Create launchers and docs
    print("\\nCreating test launchers...")
    create_test_launchers()
    
    print("Creating documentation...")
    create_detailed_readme()
    
    # Create distribution
    print("\\nCreating distribution archive...")
    os.chdir('dist')
    
    # Simple zip with just the essentials
    import zipfile
    with zipfile.ZipFile('DigitalDecay-macOS.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        # App bundle
        for root, dirs, files in os.walk('DigitalDecay.app'):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, '.')
                zipf.write(file_path, arc_path)
        
        # Launchers and docs
        zipf.write('test_console.sh')
        zipf.write('quick_test.sh')
        zipf.write('README.txt')
    
    os.chdir('..')
    
    # Final report
    print("\\n" + "=" * 60)
    print("BUILD COMPLETED!")
    print("=" * 60)
    print("Created:")
    print("  • DigitalDecay.app")
    print("  • test_console.sh (debug launcher)")
    print("  • README.txt")
    print("  • DigitalDecay-macOS.zip")
    print("\\nNext steps:")
    print("1. Double-click DigitalDecay.app")
    print("2. If issues, run: ./dist/test_console.sh")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = build_with_correct_assets()
    if success:
        print("\\n✓ Build successful! Check dist/ folder.")
    else:
        print("\\n✗ Build failed!")
    
    input("\\nPress Enter to exit...")