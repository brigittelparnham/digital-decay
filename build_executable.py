"""
build_mac_fixed.py - Mac executable builder with proper OBJ file handling

This version specifically handles the main menu object loading issue.
"""
import os
import sys
import subprocess
import shutil

def check_obj_files():
    """Check and list available OBJ files"""
    obj_dir = 'assets/blender/objects'
    if not os.path.exists(obj_dir):
        print(f"Creating {obj_dir} directory...")
        os.makedirs(obj_dir, exist_ok=True)
        return []
    
    obj_files = [f for f in os.listdir(obj_dir) if f.endswith('.obj')]
    print(f"Found {len(obj_files)} OBJ files in {obj_dir}:")
    for obj_file in obj_files:
        print(f"  - {obj_file}")
    
    # Check for row-specific objects
    row_objects = [f for f in obj_files if f.startswith('row') and f.endswith('.obj')]
    if row_objects:
        print(f"Row-specific objects found: {row_objects}")
    else:
        print("No row-specific objects (row1.obj, row2.obj, etc.) found")
        print("Game will use default shapes")
    
    return obj_files

def create_detailed_spec():
    """Create a spec file with explicit OBJ file handling"""
    
    # Check OBJ files before building
    obj_files = check_obj_files()
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

# Collect all data files explicitly
datas = []

# Critical files first
critical_files = [
    ('assets/decay_grids.json', 'assets'),
]

for src, dest in critical_files:
    if os.path.exists(src):
        datas.append((src, dest))
        print(f"Added critical file: {src}")

# Add ALL files in assets directory recursively
if os.path.exists('assets'):
    for root, dirs, files in os.walk('assets'):
        for file in files:
            src_path = os.path.join(root, file)
            # Calculate the destination directory
            rel_root = os.path.relpath(root, '.')
            datas.append((src_path, rel_root))
            print(f"Added asset: {src_path} -> {rel_root}")

# Specifically ensure blender objects are included
obj_dir = 'assets/blender/objects'
if os.path.exists(obj_dir):
    obj_files = [f for f in os.listdir(obj_dir) if f.endswith('.obj')]
    print(f"\\nExplicitly adding {len(obj_files)} OBJ files:")
    for obj_file in obj_files:
        src_path = os.path.join(obj_dir, obj_file)
        datas.append((src_path, 'assets/blender/objects'))
        print(f"  OBJ: {src_path}")

# Add Python modules
for module_dir in ['games', 'utils']:
    if os.path.exists(module_dir):
        datas.append((module_dir, module_dir))
        print(f"Added module directory: {module_dir}")

print(f"\\nTotal data files to include: {len(datas)}")

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'pygame',
        'pygame.image',
        'pygame.font',
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
        'main_menu',
        'start_screen',
        'end_screen',
        'decay_engine',
        'terminal_intro',
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

# Create single executable with console for debugging
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DigitalDecay',
    debug=True,  # Enable debug mode to see what files are included
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console to see any loading errors
    disable_windowed_traceback=False,
    icon=None,
)
'''
    
    with open('DigitalDecay.spec', 'w') as f:
        f.write(spec_content)
    print("\\nCreated detailed spec file with explicit OBJ handling")

def add_resource_path_fix():
    """Add a resource path fix to main.py"""
    
    # Read main.py
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Check if resource path fix is already present
    if 'def resource_path' in content:
        print("Resource path fix already present in main.py")
        return
    
    # Add resource path function at the top of main.py
    resource_fix = '''
import sys
import os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        print(f"Running from PyInstaller bundle: {base_path}")
        
        # List contents to debug
        if 'assets' in relative_path:
            assets_path = os.path.join(base_path, 'assets')
            if os.path.exists(assets_path):
                print(f"Assets directory found at: {assets_path}")
                if 'blender/objects' in relative_path:
                    obj_path = os.path.join(assets_path, 'blender', 'objects')
                    if os.path.exists(obj_path):
                        obj_files = os.listdir(obj_path)
                        print(f"OBJ files in bundle: {obj_files}")
                    else:
                        print(f"OBJ directory not found at: {obj_path}")
            else:
                print(f"Assets directory not found at: {assets_path}")
    except Exception as e:
        # Running in development
        base_path = os.path.abspath(".")
        print(f"Running in development mode from: {base_path}")
    
    full_path = os.path.join(base_path, relative_path)
    print(f"Resource path: {relative_path} -> {full_path}")
    return full_path

# Patch the os.path.join calls for assets
original_join = os.path.join
def patched_join(*args):
    if len(args) >= 2 and args[0] == 'assets':
        # Use resource_path for asset files
        result = resource_path(original_join(*args))
        print(f"Patched asset path: {args} -> {result}")
        return result
    return original_join(*args)

# Apply the patch
os.path.join = patched_join

'''
    
    # Insert the fix at the beginning (after the docstring if present)
    lines = content.split('\\n')
    insert_pos = 0
    
    # Skip docstring
    if lines[0].startswith('"""'):
        for i, line in enumerate(lines):
            if line.strip().endswith('"""') and i > 0:
                insert_pos = i + 1
                break
    
    # Insert the resource path fix
    lines.insert(insert_pos, resource_fix)
    
    # Write back to main.py
    with open('main.py', 'w') as f:
        f.write('\\n'.join(lines))
    
    print("Added resource path fix to main.py")

def build_with_debug():
    """Build with debug information to track asset loading"""
    print("=" * 60)
    print("Building Digital Decay with OBJ File Debug Info")
    print("=" * 60)
    
    # Verify main files
    if not os.path.exists('main.py'):
        print("Error: main.py not found!")
        return False
    
    # Install PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'PyInstaller'])
    
    # Check current OBJ files
    print("\\nChecking asset structure...")
    check_obj_files()
    
    # Add resource path debugging
    print("\\nAdding resource path debugging...")
    add_resource_path_fix()
    
    # Clean up previous builds
    print("\\nCleaning previous builds...")
    for item in ['build', 'dist', 'DigitalDecay.spec']:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)
    
    # Create detailed spec
    print("\\nCreating build specification...")
    create_detailed_spec()
    
    # Build with verbose output
    print("\\nBuilding executable (this will show detailed info)...")
    result = subprocess.run([
        sys.executable, '-m', 'PyInstaller',
        '--log-level', 'DEBUG',  # Show detailed PyInstaller logs
        '--clean',
        '--noconfirm',
        'DigitalDecay.spec'
    ])
    
    if result.returncode != 0:
        print("\\nBuild failed! Check the output above for errors.")
        return False
    
    # Verify the build
    exe_path = 'dist/DigitalDecay'
    if os.path.exists(exe_path):
        print(f"\\nBuild successful! Executable at: {exe_path}")
        
        # Make executable
        os.chmod(exe_path, 0o755)
        
        # Create test script
        test_script = '''#!/bin/bash
echo "Testing Digital Decay with debug output..."
echo "This will show resource loading information."
echo "Look for messages about OBJ files loading."
echo ""
./DigitalDecay
'''
        
        with open('dist/test_debug.sh', 'w') as f:
            f.write(test_script)
        os.chmod('dist/test_debug.sh', 0o755)
        
        print("\\nTo test with debug info: ./dist/test_debug.sh")
        print("This will show resource loading messages in the console.")
        
        # Create standard README
        readme = '''# Digital Decay - Debug Build

This build includes debug information to help diagnose asset loading issues.

## Running

1. For normal use: `./DigitalDecay`
2. For debug info: `./test_debug.sh` 

The debug version will print information about:
- Where assets are being loaded from
- Which OBJ files are found in the bundle
- Resource path resolution

Look for messages about OBJ file loading in the console output.

## Main Menu Objects

If you still see default shapes instead of your custom objects:
1. Check the console output for OBJ loading messages
2. Verify your OBJ files are named correctly (row1.obj, row2.obj, etc.)
3. Make sure they're in assets/blender/objects/ before building

## File Structure

Your built executable contains:
- All Python code
- assets/decay_grids.json (for colors)
- assets/blender/objects/*.obj (your 3D models)
- All other assets
'''
        
        with open('dist/README.txt', 'w') as f:
            f.write(readme)
        
        return True
    else:
        print("\\nError: Executable not found after build!")
        return False

if __name__ == "__main__":
    success = build_with_debug()
    
    if success:
        print("\\n" + "=" * 60)
        print("BUILD COMPLETE WITH DEBUG")
        print("=" * 60)
        print("Next steps:")
        print("1. Run: ./dist/test_debug.sh")
        print("2. Look for OBJ loading messages in console")
        print("3. If objects still don't load, check the debug output")
        print("=" * 60)
    else:
        print("\\nBuild failed! Please fix the errors above.")