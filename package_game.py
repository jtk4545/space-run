#!/usr/bin/env python3
import PyInstaller.__main__
import os
import shutil

# Clean previous builds
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')

# Run PyInstaller with basic settings
PyInstaller.__main__.run([
    'run.py',
    '--name=Space Run',
    '--onefile',
    '--windowed',
    '--add-data=high_score.json:.',
    '--add-data=constants.py:geodash',
    '--add-data=main.py:geodash',
    '--add-data=obstacles.py:geodash',
    '--add-data=player.py:geodash',
    '--add-data=utils.py:geodash',
    '--add-data=visuals.py:geodash',
    '--hidden-import=pygame',
    '--clean',
    '--noconfirm',
    '--osx-bundle-identifier=com.yourname.spacerun',
])

print("Build complete. The app is in the 'dist' folder.") 