import pygame
import random
import math
from constants import *
from utils import apply_bloom_effect

class Obstacle:
    def __init__(self, x):
        self.height = random.randint(OBSTACLE_MIN_HEIGHT, OBSTACLE_MAX_HEIGHT)
        self.width = random.randint(OBSTACLE_WIDTH_MIN, OBSTACLE_WIDTH_MAX)
        self.x = x
        self.y = HEIGHT - GROUND_HEIGHT - self.height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.passed = False
        self.color = (OBSTACLE_COLOR[0], OBSTACLE_COLOR[1], OBSTACLE_COLOR[2])
        self.glow_factor = 0
        self.glow_dir = 1
        
        # Visual enhancements
        self.pattern_type = random.choice(["stripes", "grid", "dots", "chevron"])
        self.accent_color = (min(255, self.color[0]+50), 
                           min(255, self.color[1]+50), 
                           min(255, self.color[2]+50))
        self.shadow_color = (max(0, self.color[0]-70), 
                           max(0, self.color[1]-70), 
                           max(0, self.color[2]-70))
        self.highlight_pos = random.random()  # Position of highlight
    
    def update(self, speed=None):
        # Use provided speed if available, otherwise use constant
        move_speed = speed if speed is not None else GAME_SPEED
        self.x -= move_speed
        self.rect.x = self.x
        
        # Update glow effect
        self.glow_factor += 0.05 * self.glow_dir
        if self.glow_factor > 1 or self.glow_factor < 0:
            self.glow_dir *= -1
        
        # Update highlight position
        self.highlight_pos += 0.01
        if self.highlight_pos > 1:
            self.highlight_pos = 0
    
    def draw(self, surface):
        # Create obstacle surface with more detailed visuals
        obstacle_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Base gradient fill
        for y in range(self.height):
            ratio = y / self.height
            r = int(self.color[0] * (1-ratio) + self.shadow_color[0] * ratio)
            g = int(self.color[1] * (1-ratio) + self.shadow_color[1] * ratio)
            b = int(self.color[2] * (1-ratio) + self.shadow_color[2] * ratio)
            pygame.draw.line(obstacle_surface, (r, g, b), (0, y), (self.width, y))
        
        # Add pattern based on pattern_type
        if self.pattern_type == "stripes":
            # Diagonal stripes
            stripe_count = self.width // 10
            for i in range(-self.height, self.width, 15):
                stripe_color = (self.shadow_color[0], self.shadow_color[1], self.shadow_color[2], 150)
                pygame.draw.line(obstacle_surface, stripe_color,
                              (i, 0), (i + self.height, self.height), 2)
        
        elif self.pattern_type == "grid":
            # Grid pattern
            for x in range(0, self.width, 10):
                pygame.draw.line(obstacle_surface, (*self.shadow_color, 100), 
                               (x, 0), (x, self.height), 1)
            for y in range(0, self.height, 10):
                pygame.draw.line(obstacle_surface, (*self.shadow_color, 100), 
                               (0, y), (self.width, y), 1)
        
        elif self.pattern_type == "dots":
            # Dot pattern
            for x in range(5, self.width, 10):
                for y in range(5, self.height, 10):
                    pygame.draw.circle(obstacle_surface, (*self.shadow_color, 150), 
                                     (x, y), 2)
        
        elif self.pattern_type == "chevron":
            # Chevron pattern
            for y in range(0, self.height, 10):
                for x in range(0, self.width, 20):
                    points = [
                        (x, y),
                        (x + 5, y - 5),
                        (x + 10, y),
                        (x + 15, y - 5),
                        (x + 20, y)
                    ]
                    pygame.draw.lines(obstacle_surface, (*self.shadow_color, 150), 
                                    False, points, 1)
        
        # Add border with bevel effect
        pygame.draw.rect(obstacle_surface, (180, 50, 50), (0, 0, self.width, self.height), 2)
        pygame.draw.line(obstacle_surface, (220, 70, 70), (0, 0), (self.width, 0), 2)  # Top
        pygame.draw.line(obstacle_surface, (120, 30, 30), (0, self.height-1), (self.width, self.height-1), 2)  # Bottom
        
        # Add shine/highlight effect that moves across the obstacle
        highlight_width = 20
        highlight_x = int((self.width + highlight_width) * self.highlight_pos) - highlight_width
        
        if 0 <= highlight_x < self.width:
            for i in range(highlight_width):
                # Calculate alpha based on distance from center of highlight
                dist = abs(i - highlight_width//2)
                alpha = 100 * (1 - dist/(highlight_width//2))
                pygame.draw.line(obstacle_surface, (*self.accent_color, int(alpha)), 
                               (highlight_x + i, 0), (highlight_x + i, self.height))
        
        # Apply glow effect to the edges if enabled
        if ENABLE_BLOOM:
            glow_val = int(70 * self.glow_factor)
            glow_color = (min(255, self.color[0] + glow_val),
                         min(255, self.color[1] + glow_val),
                         min(255, self.color[2] + glow_val), 100)
            
            # Top glow
            glow_rect = pygame.Surface((self.width, 10), pygame.SRCALPHA)
            for y in range(10):
                alpha = int(100 * (1 - y/10))
                pygame.draw.line(glow_rect, (*glow_color[:3], alpha), 
                               (0, y), (self.width, y))
            obstacle_surface.blit(glow_rect, (0, -5))
        
        # Blit the final obstacle to the screen
        surface.blit(obstacle_surface, (self.x, self.y))

class Spike:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.passed = False  # Add this attribute to track if player passed the spike
        self.color = SPIKE_COLOR
        self.spikiness = random.uniform(1.0, 1.5)  # Reduced spikiness for shorter spikes
        
    def update(self, speed=None):
        # Use provided speed if available, otherwise use constant
        move_speed = speed if speed is not None else GAME_SPEED
        self.x -= move_speed
        self.rect.x = self.x
        
    def draw(self, surface):
        # Enhanced rendering with shorter, more spread out spikes
        shadow_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        shadow_color = (self.color[0]//3, self.color[1]//3, self.color[2]//3, 120)
        
        # Fewer spikes with more space between them
        num_spikes = 2 + int(self.width / 30)  # Fewer spikes based on width
        spike_width = self.width / num_spikes
        spacing_factor = 0.6  # Only use 60% of the width for actual spikes
        
        for i in range(num_spikes):
            # Calculate spike position with spacing
            start_pos = i * spike_width + (spike_width * (1 - spacing_factor) / 2)
            end_pos = (i + spacing_factor) * spike_width
            mid_pos = (start_pos + end_pos) / 2
            
            # Draw shadow with more modest height
            spike_top = self.height * self.spikiness
            pygame.draw.polygon(shadow_surf, shadow_color, [
                (start_pos, self.height),  # Bottom left 
                (end_pos, self.height),    # Bottom right
                (mid_pos, self.height - spike_top * 0.3),  # Top point, more modest height
            ])
        
        # Draw the actual spikes - shorter and more spread out
        for i in range(num_spikes):
            # Calculate spike position with spacing
            start_pos = i * spike_width + (spike_width * (1 - spacing_factor) / 2)
            end_pos = (i + spacing_factor) * spike_width
            mid_pos = (start_pos + end_pos) / 2
            
            # Draw base glow
            glow_width = int(spike_width * spacing_factor * 1.2)
            glow_height = int(self.height * self.spikiness * 1.2)
            glow_surf = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
            
            pygame.draw.polygon(glow_surf, (255, 100, 100, 40), [
                (0, glow_height),
                (glow_width, glow_height),
                (glow_width // 2, 0),
            ])
            
            x_pos = self.x + mid_pos - glow_width // 2
            y_pos = self.y + self.height - glow_height
            surface.blit(glow_surf, (x_pos, y_pos))
            
            # Draw a shorter, sharper spike
            pygame.draw.polygon(surface, self.color, [
                (self.x + start_pos, self.y + self.height),       # Bottom left
                (self.x + end_pos, self.y + self.height),         # Bottom right
                (self.x + mid_pos, self.y + self.height - (self.height * self.spikiness)), # Lower top point
            ])
            
            # Add highlight line for definition
            pygame.draw.line(surface, (255, 150, 150), 
                (self.x + start_pos + 2, self.y + self.height - 1),
                (self.x + mid_pos, self.y + self.height - (self.height * self.spikiness)),
                2)

def create_obstacles(num_obstacles=20):
    obstacles = []
    spikes = []
    x = WIDTH  # Start just off screen
    
    for _ in range(num_obstacles):
        # Add more distance between obstacles
        next_distance = random.randint(MIN_OBSTACLE_DISTANCE + 30, MAX_OBSTACLE_DISTANCE + 50)
        
        # Randomize obstacle type with some spacing
        if random.random() < SPIKE_CHANCE:
            # Create a spike
            spike_width = random.randint(SPIKE_WIDTH, SPIKE_WIDTH * 2)
            spike_height = random.randint(SPIKE_HEIGHT, SPIKE_HEIGHT * 3 // 2)
            
            # Position spikes at ground level
            spike_y = HEIGHT - GROUND_HEIGHT - spike_height
            
            # Add spike with extra spacing
            spikes.append(Spike(x + 20, spike_y, spike_width, spike_height))
            x += spike_width + next_distance + 20  # Extra spacing after spikes
        else:
            # Create regular obstacle - only pass x coordinate as the constructor handles the rest
            obstacle = Obstacle(x)
            obstacles.append(obstacle)
            x += obstacle.width + next_distance
    
    return obstacles, spikes 