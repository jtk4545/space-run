"""
Setup script for Space Run - Minimal Version
"""
from setuptools import setup
import os
import sys

# Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define paths relative to current directory
run_script = 'launcher.py'  # Use our minimal launcher
high_score_path = os.path.join(current_dir, 'high_score.json')

# Python modules in the root directory
python_modules = [
    'constants.py', 'main.py', 'obstacles.py', 
    'player.py', 'utils.py', 'visuals.py'
]

DATA_FILES = [
    ('', ['high_score.json']),
    ('', python_modules)
]

OPTIONS = {
    'argv_emulation': True,
    'packages': ['pygame'],
    # Absolute minimal configuration
    'plist': {
        'CFBundleName': 'Space Run',
        'NSHighResolutionCapable': True,
    }
}

setup(
    name="Space Run",
    version="1.0",
    app=[run_script],
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
) 