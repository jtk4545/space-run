#!/usr/bin/env python3
"""Space Run entry point."""

import os
import platform
import pygame
from main import main

if __name__ == "__main__":
    if platform.system() == "Darwin":
        os.environ["SDL_VIDEO_MAC_FULLSCREEN_SPACES"] = "0"
        os.environ.setdefault("SDL_VIDEO_WINDOW_POS", "100,80")

    pygame.init()
    pygame.event.get()
    main()
