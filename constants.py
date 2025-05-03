import pygame

# Game constants
# Original values for reference
ORIGINAL_WIDTH, ORIGINAL_HEIGHT = 800, 400  

# Get the display info to determine full screen dimensions
pygame.init()
display_info = pygame.display.Info()
WIDTH, HEIGHT = display_info.current_w, display_info.current_h

# Calculate scaling factors to maintain proper element sizing
SCALE_X = WIDTH / ORIGINAL_WIDTH
SCALE_Y = HEIGHT / ORIGINAL_HEIGHT

# Adjusted constants for full screen
GRAVITY = 1 * SCALE_Y
JUMP_STRENGTH = 18 * SCALE_Y
GROUND_HEIGHT = int(50 * SCALE_Y)
PLAYER_SIZE = int(40 * SCALE_X)
OBSTACLE_WIDTH_MIN = int(60 * SCALE_X)
OBSTACLE_WIDTH_MAX = int(120 * SCALE_X)
OBSTACLE_MIN_HEIGHT = int(50 * SCALE_Y)
OBSTACLE_MAX_HEIGHT = int(120 * SCALE_Y)
GAME_SPEED = 5 * SCALE_X
MIN_OBSTACLE_DISTANCE = int(150 * SCALE_X)
MAX_OBSTACLE_DISTANCE = int(300 * SCALE_X)
SPIKE_WIDTH = int(30 * SCALE_X)
SPIKE_HEIGHT = int(30 * SCALE_Y)
SPIKE_CHANCE = 0.3  # 30% chance for a spike instead of a platform

# Enhanced colors and visuals
BG_COLOR = (10, 10, 35)  # Darker blue background
PLAYER_COLOR = (0, 240, 255)  # Brighter player color
OBSTACLE_COLOR = (255, 70, 70)  # Lighter red for obstacles
GROUND_COLOR = (40, 210, 40)  # Green ground
PARTICLE_COLORS = [(255, 255, 150), (255, 200, 100), (255, 150, 100), (255, 220, 220)]  # Lighter, less saturated colors
SPIKE_COLOR = (255, 30, 30)  # Red for spikes

# Visual effects constants
ENABLE_BLOOM = True
ENABLE_PARALLAX = True
PARTICLE_FREQUENCY = 0.005  # Lower value means fewer particles

# High score file
HIGH_SCORE_FILE = "high_score.json"

# Set up the display - fullscreen mode
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Geometry Dash - Enhanced Edition")
clock = pygame.time.Clock()

# Add fullscreen toggle flag
is_fullscreen = True 