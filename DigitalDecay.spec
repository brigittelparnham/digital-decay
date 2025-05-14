# -*- mode: python ; coding: utf-8 -*-

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
