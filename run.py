#!/usr/bin/env python3
"""
Space Run Game
Entry point script
"""

# Import the main game function
import pygame
import os
import platform
import sys
from main import main

if __name__ == "__main__":
    # Special handling for macOS
    if platform.system() == 'Darwin':  # Darwin is the core of macOS
        # Configure pygame to work better with macOS
        os.environ['SDL_VIDEO_MAC_FULLSCREEN_SPACES'] = '0'
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'  # Position window at top-left of screen
        
        # Try to import and initialize key helper
        try:
            import key_helper
            if key_helper.HAVE_PYNPUT:
                print("Using direct keyboard input for macOS")
            else:
                print("pynput not available - using standard keyboard input")
        except ImportError:
            print("key_helper not available - using standard keyboard input")
    
    # Initialize pygame
    pygame.init()
    
    # Process any pending events before starting the game
    # This can help with keyboard focus issues
    pygame.event.get()
    pygame.event.clear()  # Clear any pending events
    
    # Start the game
    main()