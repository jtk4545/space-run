#!/usr/bin/env python3
"""
Wrapper script to fix input issues with packaged PyGame apps on macOS
"""
import os
import sys
import time
import pygame

# Set SDL environment variables that help with input on macOS
os.environ['SDL_VIDEO_MAC_FULLSCREEN_SPACES'] = '0'
os.environ['SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS'] = '1'
os.environ['SDL_HINT_MOUSE_FOCUS_CLICKTHROUGH'] = '1'

# Initialize pygame early
pygame.init()

# Add a small delay to allow system to stabilize
time.sleep(0.5)

# Clear any pending events
pygame.event.clear()

# Import and run your actual game
from main import main

if __name__ == "__main__":
    # Process any pending events before starting the game
    pygame.event.get()
    
    # On macOS, sometimes focusing the window helps
    pygame.display.set_mode((100, 100))  # Temporary window
    time.sleep(0.2)  # Give the window time to appear and get focus
    
    # Start the actual game
    main() 