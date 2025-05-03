import pygame
import random
import math
from constants import *
from utils import create_gradient_rect, apply_bloom_effect

# Initialize stars for the parallax background
stars = []
for _ in range(200):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT - GROUND_HEIGHT)
    size = random.uniform(0.5, 2.5)
    stars.append((x, y, size))

# Enhanced particle system
class EnhancedParticle:
    def __init__(self, x, y, particle_type="normal"):
        self.x = x
        self.y = y
        self.type = particle_type
        
        # Base properties - make particles smaller
        self.size = random.uniform(1, 4)  # Reduced from 2-6
        self.color = random.choice(PARTICLE_COLORS)
        self.alpha = 200  # Reduced from 255
        
        # Set behavior based on type - make lifetimes shorter
        if particle_type == "normal":
            self.vx = random.uniform(-1.5, 1.5)  # Reduced velocity
            self.vy = random.uniform(-3, -0.5)
            self.lifetime = random.randint(15, 30)  # Shorter lifetime
            self.gravity = 0.1
            self.decay_rate = 6  # Faster decay
            
        elif particle_type == "explode":
            self.vx = random.uniform(-4, 4)  # Reduced velocity
            self.vy = random.uniform(-4, 4)
            self.lifetime = random.randint(20, 40)  # Shorter lifetime
            self.gravity = 0.05
            self.size = random.uniform(2, 5)  # Smaller size
            self.decay_rate = 6  # Faster decay
            
        elif particle_type == "trail":
            self.vx = random.uniform(-0.5, 0.5)  # Reduced velocity
            self.vy = random.uniform(-0.3, 0.3)
            self.lifetime = random.randint(8, 15)  # Much shorter lifetime
            self.gravity = 0
            self.size = random.uniform(1, 2)  # Smaller size
            self.decay_rate = 15  # Much faster decay
            
        elif particle_type == "land":
            self.vx = random.uniform(-3, 3)
            self.vy = random.uniform(-2, 0)
            self.lifetime = random.randint(15, 30)
            self.gravity = 0.15
            self.decay_rate = 8
            
        # New particle types for power-ups
        elif particle_type == "shield":
            self.vx = random.uniform(-2, 2)
            self.vy = random.uniform(-2, 2)
            self.lifetime = random.randint(20, 40)
            self.gravity = 0
            self.size = random.uniform(2, 4)
            self.decay_rate = 6
            self.color = (50, 150, 255)  # Blue shield particles
            
        elif particle_type == "score":
            self.vx = random.uniform(-3, 3)
            self.vy = random.uniform(-4, -1)
            self.lifetime = random.randint(20, 35)
            self.gravity = 0.05
            self.size = random.uniform(2, 4)
            self.decay_rate = 7
            self.color = (255, 215, 0)  # Gold particles for score
        
        # Special properties
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)
        self.shape = random.choice(["circle", "square", "star"]) if random.random() > 0.7 else "circle"
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= 1
        self.alpha = max(0, self.alpha - self.decay_rate)
        self.size = max(0, self.size - 0.05)
        self.rotation += self.rotation_speed
    
    def draw(self, surface):
        # Make particles less bright and more transparent
        if self.alpha < 70:  # Don't even draw nearly-invisible particles
            return
            
        # Create particle surface
        particle_surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        
        if self.shape == "circle":
            pygame.draw.circle(particle_surf, (*self.color, self.alpha), 
                             (int(self.size), int(self.size)), int(self.size))
                             
        elif self.shape == "square":
            rect = pygame.Rect(0, 0, int(self.size * 2), int(self.size * 2))
            pygame.draw.rect(particle_surf, (*self.color, self.alpha), rect)
            
        elif self.shape == "star":
            # Simple star shape
            points = []
            for i in range(5):
                # Outer points
                angle = math.pi * 2 * i / 5 - math.pi / 2
                points.append((
                    self.size + math.cos(angle) * self.size,
                    self.size + math.sin(angle) * self.size
                ))
                # Inner points
                angle += math.pi / 5
                points.append((
                    self.size + math.cos(angle) * (self.size / 2),
                    self.size + math.sin(angle) * (self.size / 2)
                ))
            pygame.draw.polygon(particle_surf, (*self.color, self.alpha), points)
        
        # Apply rotation if needed
        if self.rotation != 0 and self.shape != "circle":
            particle_surf = pygame.transform.rotate(particle_surf, self.rotation)
        
        # Add glow for certain particles
        if ENABLE_BLOOM and (self.type == "explode" or random.random() > 0.7):
            glow_size = int(self.size * 3)
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color, min(100, self.alpha // 2)), 
                             (glow_size, glow_size), glow_size)
            
            # Position for glow (centered)
            glow_pos = (int(self.x - glow_size), int(self.y - glow_size))
            surface.blit(glow_surf, glow_pos, special_flags=pygame.BLEND_ADD)
        
        # Position for particle (centered)
        pos = (int(self.x - particle_surf.get_width() // 2), 
               int(self.y - particle_surf.get_height() // 2))
        surface.blit(particle_surf, pos)

# Create starry background with parallax layers
def create_starry_background(width, height, stars=200):
    """Create a dynamic multi-layered starry background"""
    main_bg = pygame.Surface((width, height))
    bg_layers = []  # For parallax effect
    
    # Fill background with dark gradient
    for y in range(height):
        # Calculate color
        ratio = y / height
        r = int(10 * (1 - ratio) + 5 * ratio)
        g = int(10 * (1 - ratio) + 5 * ratio)
        b = int(35 * (1 - ratio) + 20 * ratio)
        pygame.draw.line(main_bg, (r, g, b), (0, y), (width, y))
    
    # Add stars to main background
    for _ in range(stars):
        x = random.randint(0, width)
        y = random.randint(0, height - GROUND_HEIGHT)
        size = random.random() * 2 + 0.5
        brightness = random.randint(180, 255)
        
        # Add glow for some stars
        if random.random() > 0.8:
            glow_size = size * random.uniform(2, 4)
            glow_color = (brightness // 8, brightness // 8, brightness // 6, 100)
            pygame.draw.circle(main_bg, glow_color, (x, y), glow_size)
        
        # Add the star
        pygame.draw.circle(main_bg, (brightness, brightness, brightness), (x, y), size)
    
    # Add nebulas with more vibrant colors
    for _ in range(5):
        center_x = random.randint(0, width)
        center_y = random.randint(0, height - GROUND_HEIGHT)
        
        # Choose a color scheme for this nebula
        schemes = [
            # Purple/blue
            [(80, 50, 150, 10), (60, 30, 130, 10), (40, 20, 110, 10)],
            # Red/orange
            [(150, 50, 50, 10), (130, 40, 30, 10), (100, 30, 30, 10)],
            # Blue/cyan
            [(30, 80, 150, 10), (20, 60, 130, 10), (10, 50, 110, 10)],
            # Green/cyan
            [(30, 150, 80, 10), (20, 130, 60, 10), (10, 110, 50, 10)]
        ]
        
        nebula_colors = random.choice(schemes)
        
        # Create the nebula with multiple overlapping translucent areas
        for i in range(25):
            radius = random.randint(30, 80)
            offset_x = random.randint(-60, 60)
            offset_y = random.randint(-60, 60)
            color = random.choice(nebula_colors)
            
            s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (radius, radius), radius)
            main_bg.blit(s, (center_x + offset_x - radius, center_y + offset_y - radius))
    
    # Add distant stars layer (moves slower in parallax)
    if ENABLE_PARALLAX:
        distant_stars = pygame.Surface((width * 2, height), pygame.SRCALPHA)
        for _ in range(100):
            x = random.randint(0, width * 2)
            y = random.randint(0, height - GROUND_HEIGHT)
            size = random.random() * 1.5
            brightness = random.randint(150, 220)
            pygame.draw.circle(distant_stars, (brightness, brightness, brightness), (x, y), size)
        bg_layers.append(distant_stars)
    
        # Add closer stars layer (moves faster in parallax)
        close_stars = pygame.Surface((width * 2, height), pygame.SRCALPHA)
        for _ in range(50):
            x = random.randint(0, width * 2)
            y = random.randint(0, height - GROUND_HEIGHT)
            size = random.random() * 2.0
            brightness = random.randint(200, 255)
            pygame.draw.circle(close_stars, (brightness, brightness, brightness), (x, y), size)
        bg_layers.append(close_stars)
    
    return main_bg, bg_layers

# Create enhanced ground texture
def create_enhanced_ground():
    ground = pygame.Surface((WIDTH, GROUND_HEIGHT))
    
    # Base gradient
    for y in range(GROUND_HEIGHT):
        ratio = y / GROUND_HEIGHT
        r = int(40 * (1-ratio) + 30 * ratio)
        g = int(210 * (1-ratio) + 120 * ratio)
        b = int(40 * (1-ratio) + 30 * ratio)
        pygame.draw.line(ground, (r, g, b), (0, y), (WIDTH, y))
    
    # Add texture lines
    for i in range(0, WIDTH, 20):
        darkness = random.randint(0, 30)
        pygame.draw.line(ground, (30-darkness, 180-darkness, 30-darkness), 
                       (i, 0), (i, GROUND_HEIGHT), random.randint(1, 3))
    
    # Add highlight at top
    pygame.draw.line(ground, (100, 255, 100, 180), (0, 0), (WIDTH, 0), 2)
    
    # Add some random grassy tufts
    for i in range(0, WIDTH, random.randint(30, 80)):
        height = random.randint(5, 15)
        width = random.randint(3, 8)
        pygame.draw.polygon(ground, (30, 180, 30), 
                          [(i, 0), (i+width//2, -height), (i+width, 0)])
    
    return ground

# Create enhanced player image
def create_player_image():
    img = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
    
    # Draw base with gradient
    for y in range(PLAYER_SIZE):
        ratio = y / PLAYER_SIZE
        r = int(0)
        g = int(180 + 60 * (1-ratio))
        b = int(200 + 55 * (1-ratio))
        pygame.draw.line(img, (r, g, b), (0, y), (PLAYER_SIZE, y))
    
    # Add highlights
    pygame.draw.rect(img, (200, 255, 255), (5, 5, PLAYER_SIZE - 10, 10))
    pygame.draw.rect(img, (0, 100, 200), (0, 0, PLAYER_SIZE, PLAYER_SIZE), 2)
    
    # Add diagonal corner highlights
    pygame.draw.line(img, (150, 255, 255), (0, 0), (10, 10), 2)
    pygame.draw.line(img, (150, 255, 255), (PLAYER_SIZE, 0), (PLAYER_SIZE-10, 10), 2)
    
    # Add inner detail (geometric pattern)
    pygame.draw.line(img, (0, 220, 255), (PLAYER_SIZE//4, PLAYER_SIZE//4), 
                   (PLAYER_SIZE*3//4, PLAYER_SIZE//4), 2)
    pygame.draw.line(img, (0, 220, 255), (PLAYER_SIZE//2, PLAYER_SIZE//4), 
                   (PLAYER_SIZE//2, PLAYER_SIZE*3//4), 2)
    
    # Add border
    pygame.draw.rect(img, (0, 100, 200), (0, 0, PLAYER_SIZE, PLAYER_SIZE), 2)
    
    # Add glow surface for the player
    glow_surface = pygame.Surface((PLAYER_SIZE*2, PLAYER_SIZE*2), pygame.SRCALPHA)
    pygame.draw.rect(glow_surface, (0, 240, 255, 50), 
                   (PLAYER_SIZE//2, PLAYER_SIZE//2, PLAYER_SIZE, PLAYER_SIZE))
    
    for i in range(5):
        size_factor = 1 + (i * 0.1)
        glow_size = int(PLAYER_SIZE * size_factor)
        rect = pygame.Rect(
            (PLAYER_SIZE*2 - glow_size)//2,
            (PLAYER_SIZE*2 - glow_size)//2,
            glow_size, glow_size
        )
        alpha = 40 - (i * 8)
        if alpha > 0:
            pygame.draw.rect(glow_surface, (0, 240, 255, alpha), rect, 2)
    
    return img, glow_surface

# Initialize background, ground, and player images
background, bg_layers = create_starry_background(WIDTH, HEIGHT)
ground_surface = create_enhanced_ground()
player_img, player_glow = create_player_image()

# Draw functions
def draw_parallax_background(offset):
    # Draw starry background
    screen.fill(BG_COLOR)
    
    # Draw stars with parallax effect
    for i, star in enumerate(stars):
        # Calculate parallax offset based on layer
        layer_offset = (offset * (i % 3 + 1) / 5) % WIDTH
        
        # Draw stars with different brightness based on layer
        alpha = 100 + 50 * (i % 3)
        pygame.draw.circle(
            screen, 
            (255, 255, 255, alpha), 
            ((star[0] - layer_offset) % WIDTH, star[1]), 
            star[2]
        )
    
    # Draw a subtle gradient overlay for depth
    gradient = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for y in range(HEIGHT):
        alpha = int(y / HEIGHT * 50)  # Gradually increase transparency
        pygame.draw.line(gradient, (0, 0, 30, alpha), (0, y), (WIDTH, y))
    screen.blit(gradient, (0, 0))

def draw_ground():
    # Draw the ground
    ground_surface = pygame.Surface((WIDTH, GROUND_HEIGHT))
    ground_surface.fill(GROUND_COLOR)
    
    # Add grid lines
    for x in range(0, WIDTH, 40):
        pygame.draw.line(ground_surface, (30, 180, 30), (x, 0), (x, GROUND_HEIGHT), 2)
    for y in range(0, GROUND_HEIGHT, 20):
        pygame.draw.line(ground_surface, (30, 180, 30), (0, y), (WIDTH, y), 2)
    
    screen.blit(ground_surface, (0, HEIGHT - GROUND_HEIGHT))

# Add PowerUp class
class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type
        self.size = 30
        self.rect = pygame.Rect(x, y, self.size, self.size)
        
        # Different colors for different power-ups
        self.colors = {
            "extra_life": (255, 50, 50),    # Red for extra life
            "shield": (50, 100, 255),       # Blue for shield
            "score_boost": (255, 215, 0),   # Gold for score boost
            "slow_time": (180, 180, 255)    # Light blue for slow time
        }
        
        self.color = self.colors.get(power_type, (255, 255, 255))
        self.pulse_dir = 1
        self.pulse = 0
        self.rotation = 0
        
    def update(self, speed=None):
        # Use provided speed if available, otherwise use constant
        move_speed = speed if speed is not None else GAME_SPEED
        self.x -= move_speed
        self.rect.x = self.x
        
        # Update visual effects
        self.pulse += 0.05 * self.pulse_dir
        if self.pulse > 1 or self.pulse < 0:
            self.pulse_dir *= -1
            
        self.rotation = (self.rotation + 3) % 360
        
    def draw(self, surface):
        # Create power-up surface
        power_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Draw different shapes for different power-ups
        if self.type == "extra_life":
            # Heart shape
            pygame.draw.polygon(power_surf, self.color, 
                              [(self.size//2, self.size//4), 
                              (self.size//4, self.size//2), 
                              (self.size//2, self.size*3//4), 
                              (self.size*3//4, self.size//2)])
                              
        elif self.type == "shield":
            # Shield shape
            pygame.draw.circle(power_surf, self.color, 
                             (self.size//2, self.size//2), self.size//2 - 4)
            pygame.draw.circle(power_surf, (0, 0, 0, 0), 
                             (self.size//2, self.size//2), self.size//3)
                             
        elif self.type == "score_boost":
            # Star shape for score boost
            points = []
            for i in range(5):
                angle = math.pi * 2 * i / 5 - math.pi / 2
                points.append((
                    self.size//2 + math.cos(angle) * (self.size//2 - 4),
                    self.size//2 + math.sin(angle) * (self.size//2 - 4)
                ))
                angle += math.pi / 5
                points.append((
                    self.size//2 + math.cos(angle) * (self.size//3 - 2),
                    self.size//2 + math.sin(angle) * (self.size//3 - 2)
                ))
            pygame.draw.polygon(power_surf, self.color, points)
            
        elif self.type == "slow_time":
            # Clock shape for slow time
            pygame.draw.circle(power_surf, self.color, 
                             (self.size//2, self.size//2), self.size//2 - 4)
            pygame.draw.line(power_surf, (255, 255, 255), 
                           (self.size//2, self.size//2), 
                           (self.size//2, self.size//4), 2)
            pygame.draw.line(power_surf, (255, 255, 255), 
                           (self.size//2, self.size//2), 
                           (self.size*3//4, self.size//2), 2)
        
        # Add glow effect
        glow_size = int(self.size * (1.0 + 0.3 * self.pulse))
        glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        
        # Draw glow
        alpha = int(100 * (0.5 + 0.5 * self.pulse))
        glow_color = (*self.color, alpha)
        pygame.draw.circle(glow_surf, glow_color, 
                         (glow_size//2, glow_size//2), glow_size//2)
        
        # Draw glow with offset for the pulsing effect
        glow_offset = (self.size - glow_size) // 2
        surface.blit(glow_surf, (self.x + glow_offset, self.y + glow_offset))
        
        # Apply rotation and draw the power-up
        rotated = pygame.transform.rotate(power_surf, self.rotation)
        rotated_rect = rotated.get_rect(center=(self.x + self.size//2, self.y + self.size//2))
        surface.blit(rotated, rotated_rect) 