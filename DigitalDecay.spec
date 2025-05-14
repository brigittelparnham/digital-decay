# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

# Define what data files to include
datas = [
        ('assets', 'assets'),
        ('assets/blender', 'assets/blender'),
        ('assets/blender/objects', 'assets/blender/objects'),
        ('assets/blender/animation', 'assets/blender/animation'),
        ('assets/blender/animation/rerender', 'assets/blender/animation/rerender'),
        ('assets/fonts', 'assets/fonts'),
        ('assets/sounds', 'assets/sounds'),
        ('assets/decay_grids.json', 'assets/decay_grids.json'),
        ('requirements.txt', 'assets/requirements.txt')
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
    hooksconfig={},
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
        info_plist={
            'CFBundleName': 'Digital Decay',
            'CFBundleDisplayName': 'Digital Decay',
            'CFBundleIdentifier': 'com.digitaldecay.game',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
        }
    )
