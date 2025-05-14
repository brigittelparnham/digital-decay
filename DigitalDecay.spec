# -*- mode: python ; coding: utf-8 -*-

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
