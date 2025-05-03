import pygame
import json
import os
import random
import math
from constants import *

# High score functions
def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
        except (json.JSONDecodeError, FileNotFoundError):
            return 0
    return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, 'w') as f:
        json.dump({'high_score': score}, f)

# Screen shake effect
class ScreenShake:
    def __init__(self):
        self.duration = 0
        self.intensity = 0
        
    def start(self, intensity=5, duration=5):
        self.duration = duration
        self.intensity = intensity
        
    def update(self):
        if self.duration > 0:
            self.duration -= 1
            offset_x = random.randint(-self.intensity, self.intensity)
            offset_y = random.randint(-self.intensity, self.intensity)
            return offset_x, offset_y
        return 0, 0

# Utility functions for creating gradients and visual effects
def create_gradient_rect(width, height, color1, color2, direction=1):
    """Create a vertical or horizontal gradient"""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    if direction:  # vertical
        for y in range(height):
            # Calculate gradient color at this position
            ratio = y / height
            r = color1[0] * (1 - ratio) + color2[0] * ratio
            g = color1[1] * (1 - ratio) + color2[1] * ratio
            b = color1[2] * (1 - ratio) + color2[2] * ratio
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
    else:  # horizontal
        for x in range(width):
            ratio = x / width
            r = color1[0] * (1 - ratio) + color2[0] * ratio
            g = color1[1] * (1 - ratio) + color2[1] * ratio
            b = color1[2] * (1 - ratio) + color2[2] * ratio
            pygame.draw.line(surface, (r, g, b), (x, 0), (x, height))
    return surface

def apply_bloom_effect(surface, radius=10, color=(255, 255, 255), alpha_factor=0.5):
    """Apply a bloom/glow effect to a surface"""
    # Create a larger surface to accommodate the bloom
    width, height = surface.get_width() + radius * 2, surface.get_height() + radius * 2
    bloom = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Scale the surface for the bloom effect
    scaled = pygame.transform.scale(surface, (surface.get_width() + radius, surface.get_height() + radius))
    
    # Set alpha/opacity based on the alpha_factor
    scaled.set_alpha(int(255 * alpha_factor))
    
    # Apply the color tint to the glow
    for x in range(width):
        for y in range(height):
            if x < scaled.get_width() and y < scaled.get_height():
                pixel = scaled.get_at((x, y))
                if pixel[3] > 0:  # If pixel is not fully transparent
                    # Create a colored glow based on the pixel's alpha
                    alpha = pixel[3] / 255.0 * alpha_factor
                    bloom_color = (
                        min(255, int(color[0] * alpha)),
                        min(255, int(color[1] * alpha)),
                        min(255, int(color[2] * alpha)),
                        min(255, int(alpha * 255))
                    )
                    bloom.set_at((x + (radius//2), y + (radius//2)), bloom_color)
    
    return bloom

def draw_neon_text(surface, text, font, color, position, glow_color=(100, 100, 100), glow_radius=3):
    # Create main text surface with the specified color
    text_surface = font.render(text, True, color)
    
    # Add black outline for better contrast against any background
    outline_surface = font.render(text, True, (0, 0, 0))
    
    # Draw text shadow/outline first (offset by 2 pixels)
    surface.blit(outline_surface, (position[0] + 2, position[1] + 2))
    
    # Apply bloom/glow effect if enabled and radius > 0
    if ENABLE_BLOOM and glow_radius > 0:
        # Increase alpha/opacity of glow for better visibility
        bloom_surface = apply_bloom_effect(text_surface, glow_radius, glow_color, alpha_factor=0.8)
        surface.blit(bloom_surface, position)
    
    # Draw main text on top
    surface.blit(text_surface, position)
    
    return text_surface.get_size() 