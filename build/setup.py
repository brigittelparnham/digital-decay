"""
setup.py - Script to create standalone executables using PyInstaller
"""
import os
import sys
import shutil
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop

class PostInstallCommand(install):
    """Post-installation command to create the executable."""
    def run(self):
        install.run(self)
        self.create_executable()
    
    def create_executable(self):
        """Create the executable using PyInstaller."""
        # Make sure PyInstaller is installed
        try:
            import PyInstaller
        except ImportError:
            self.announce("Installing PyInstaller...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PyInstaller'])
        
        self.announce("Creating executable with PyInstaller...")
        
        # Create necessary directories
        os.makedirs("dist/DigitalDecay", exist_ok=True)
        
        # Create the .spec file content
        spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('*.py', '.'),
        ('games/*.py', 'games'),
        ('utils/*.py', 'utils'),
    ],
    hiddenimports=[
        'pygame',
        'OpenGL.GL',
        'OpenGL.GLU',
        'numpy',
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
    argv_emulation=False,
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
        
        # Write the spec file
        with open("DigitalDecay.spec", "w") as f:
            f.write(spec_content)
        
        # Run PyInstaller with the spec file
        subprocess.check_call([
            sys.executable,
            '-m',
            'PyInstaller',
            'DigitalDecay.spec',
            '--onedir',
            '--name=DigitalDecay'
        ])
        
        # Create a README file for the executable
        readme_content = """
Digital Decay Game
=================

To run the game:
1. Double-click on 'DigitalDecay.exe' (Windows) or 'DigitalDecay' (Mac/Linux)

Controls:
- Press ENTER to start the game
- Use arrow keys for paddle movement in Game 2
- Press ESC to return to main menu
- Click directly on objects to interact with them

About Digital Decay:
This game explores the concept of entropy and decay in digital systems. Your goal is to reverse
the decay process through various mini-games and interactions. The decay bar at the bottom of
the screen indicates the overall system health - keep it from reaching zero!

Enjoy!
"""
        
        with open("dist/DigitalDecay/README.txt", "w") as f:
            f.write(readme_content)
        
        # Create a run.bat for Windows users
        bat_content = """@echo off
echo Starting Digital Decay...
start DigitalDecay.exe
"""
        with open("dist/DigitalDecay/run.bat", "w") as f:
            f.write(bat_content)
        
        # Create a run.sh for Linux/Mac users
        sh_content = """#!/bin/bash
echo "Starting Digital Decay..."
chmod +x ./DigitalDecay
./DigitalDecay
"""
        with open("dist/DigitalDecay/run.sh", "w") as f:
            f.write(sh_content)
        
        # Make the shell script executable
        os.chmod("dist/DigitalDecay/run.sh", 0o755)
        
        self.announce("Executable created in dist/DigitalDecay/")
        self.announce("Copy the entire DigitalDecay folder to a USB drive to share the game")

# Setup configuration
setup(
    name="digital_decay",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        'pygame>=2.0.0',
        'PyOpenGL>=3.1.0',
        'numpy>=1.19.0',
        'colorama>=0.4.4',
    ],
    cmdclass={
        'install': PostInstallCommand,
    },
    author="Digital Decay Creator",
    description="A game exploring digital decay concepts with three mini-games",
    keywords="game, pygame, digital decay",
    python_requires='>=3.6',
)