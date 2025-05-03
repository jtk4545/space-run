#!/bin/bash

# Space Run Game Launcher for macOS
echo "Starting Space Run..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if we're running from inside an app bundle
if [[ "$SCRIPT_DIR" == *"/Contents/MacOS" ]]; then
    # We're inside an app bundle
    RESOURCES_DIR="$SCRIPT_DIR/../Resources"
    echo "Running from app bundle: $SCRIPT_DIR"
else
    # We're running the script directly
    RESOURCES_DIR="$SCRIPT_DIR"
    echo "Running directly from: $SCRIPT_DIR"
fi

# Set critical environment variables
export SDL_VIDEO_MAC_FULLSCREEN_SPACES=0
export SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1
export PYTHONPATH="${RESOURCES_DIR}:${PYTHONPATH}"

# Move to the resources directory
cd "$RESOURCES_DIR"
echo "Using resources in: $RESOURCES_DIR"

# Launch the game with Python directly
echo "Starting Python game..."
/usr/bin/env python3 "$RESOURCES_DIR/main.py"

echo "Game exited."