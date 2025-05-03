"""
Direct keyboard input helper for macOS PyGame apps
"""
import os
import sys
import time
import threading
from queue import Queue

# For direct key input on macOS
try:
    from pynput import keyboard
    HAVE_PYNPUT = True
except ImportError:
    HAVE_PYNPUT = False
    print("pynput not available - keyboard helper disabled")

# Create a global key state dictionary that will be checked by the game
GAME_KEYS = {
    'space': False,
    'up': False,
    'down': False,
    'left': False,
    'right': False,
    'escape': False,
    'return': False,
    'r': False,
}

# Create a queue for key events
key_queue = Queue()

def on_press(key):
    try:
        if key == keyboard.Key.space:
            GAME_KEYS['space'] = True
        elif key == keyboard.Key.up:
            GAME_KEYS['up'] = True
        elif key == keyboard.Key.down:
            GAME_KEYS['down'] = True
        elif key == keyboard.Key.left:
            GAME_KEYS['left'] = True
        elif key == keyboard.Key.right:
            GAME_KEYS['right'] = True
        elif key == keyboard.Key.esc:
            GAME_KEYS['escape'] = True
        elif key == keyboard.Key.enter:
            GAME_KEYS['return'] = True
        elif hasattr(key, 'char') and key.char == 'r':
            GAME_KEYS['r'] = True
        key_queue.put(('press', key))
    except:
        pass

def on_release(key):
    try:
        if key == keyboard.Key.space:
            GAME_KEYS['space'] = False
        elif key == keyboard.Key.up:
            GAME_KEYS['up'] = False
        elif key == keyboard.Key.down:
            GAME_KEYS['down'] = False
        elif key == keyboard.Key.left:
            GAME_KEYS['left'] = False
        elif key == keyboard.Key.right:
            GAME_KEYS['right'] = False
        elif key == keyboard.Key.esc:
            GAME_KEYS['escape'] = False
        elif key == keyboard.Key.enter:
            GAME_KEYS['return'] = False
        elif hasattr(key, 'char') and key.char == 'r':
            GAME_KEYS['r'] = False
        key_queue.put(('release', key))
    except:
        pass

def start_listening():
    """Start the keyboard listener in a background thread"""
    if not HAVE_PYNPUT:
        return False
        
    # Create and start the listener
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release,
        suppress=False  # Don't suppress system-wide keyboard events
    )
    listener.daemon = True
    listener.start()
    return True

# Automatically start listening when imported
if HAVE_PYNPUT:
    start_listening() 