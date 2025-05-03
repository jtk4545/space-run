#!/usr/bin/env python3
"""
Minimal Space Run Launcher
"""
import os
import sys
import pygame

# Set SDL environment variables
os.environ['SDL_VIDEO_MAC_FULLSCREEN_SPACES'] = '0'
os.environ['SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS'] = '1'

# Initialize pygame
pygame.init()

# Import main function
from main import main

if __name__ == "__main__":
    main() 