import pygame
import random
from constants import *
from visuals import EnhancedParticle
from utils import apply_bloom_effect

class Player:
    def __init__(self):
        self.x = int(WIDTH * 0.2)  # Position at 20% of screen width instead of fixed 100px
        self.y = HEIGHT - GROUND_HEIGHT - PLAYER_SIZE
        self.velocity = 0
        self.jumping = False
        self.can_double_jump = False
        self.rect = pygame.Rect(self.x, self.y, PLAYER_SIZE, PLAYER_SIZE)
        self.on_obstacle = False
        self.rotation = 0
        self.particles = []
        self.trail = []  # For motion trail
        self.dash_effect_timer = 0
        self.particle_spawn_timer = 0
        
        # Visual enhancements
        self.glow_factor = 0.5
        self.glow_dir = 1
        self.color_shift = 0
    
    def jump(self):
        if not self.jumping or self.on_obstacle:
            self.velocity = -JUMP_STRENGTH
            self.jumping = True
            self.can_double_jump = True
            self.on_obstacle = False
            self.dash_effect_timer = 10  # Trigger dash effect
            
            # Create fewer jump particles
            for _ in range(3):  # Reduced from 8
                self.particles.append(EnhancedParticle(self.x + PLAYER_SIZE//2, 
                                                    self.y + PLAYER_SIZE, 
                                                    "explode"))
        elif self.can_double_jump:
            self.velocity = -JUMP_STRENGTH
            self.can_double_jump = False
            self.dash_effect_timer = 15
            
            # Create fewer double jump particles
            for _ in range(4):  # Reduced from 12
                self.particles.append(EnhancedParticle(self.x + PLAYER_SIZE//2, 
                                                    self.y + PLAYER_SIZE//2, 
                                                    "explode"))
    
    def update(self, obstacles, spikes):
        # Apply gravity
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Update glow effect
        self.glow_factor += 0.03 * self.glow_dir
        if self.glow_factor > 1 or self.glow_factor < 0.3:
            self.glow_dir *= -1
            
        # Slow color shift for player
        self.color_shift = (self.color_shift + 0.01) % 1.0
        
        # Create trail particles occasionally
        self.particle_spawn_timer -= 1
        if self.particle_spawn_timer <= 0 and abs(self.velocity) > 5:
            self.particle_spawn_timer = 12  # Increased from 6 to 12 (less frequent)
            # Create just a single particle for movement
            self.particles.append(EnhancedParticle(
                self.x + random.randint(0, PLAYER_SIZE),
                self.y + random.randint(0, PLAYER_SIZE),
                "trail"
            ))
        
        # Check ground collision
        if self.y > HEIGHT - GROUND_HEIGHT - PLAYER_SIZE:
            self.y = HEIGHT - GROUND_HEIGHT - PLAYER_SIZE
            self.velocity = 0
            self.jumping = False
            self.on_obstacle = False
            
            # Create landing particles
            for _ in range(2):  # Reduced from typical values
                self.particles.append(EnhancedParticle(self.x + PLAYER_SIZE//2, 
                                                    self.y + PLAYER_SIZE, 
                                                    "land"))
        
        # Update rectangle position
        self.rect = pygame.Rect(self.x, self.y, PLAYER_SIZE, PLAYER_SIZE)
        
        # Add trail effect
        if len(self.trail) < 2 and pygame.time.get_ticks() % 10 == 0:  # Changed from 3 and 6 to 2 and 10
            self.trail.append((self.x, self.y, 20))  # x, y, alpha (lowered alpha too)
        
        # Update trail
        self.trail = [(x, y, a-5) for x, y, a in self.trail if a > 0]
        
        # Update rotation based on velocity
        if self.jumping:
            rotation_speed = 6 if abs(self.velocity) > 10 else 4
            self.rotation += rotation_speed
        
        if self.rotation >= 360:
            self.rotation = 0
            
        # Update dash effect timer
        if self.dash_effect_timer > 0:
            self.dash_effect_timer -= 1
        
        # Update particles
        for particle in list(self.particles):
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)
        
        # Check for landing on spikes
        for spike in spikes:
            if self.rect.colliderect(spike.rect):
                # Create collision particles - explosion effect
                for _ in range(30):
                    self.particles.append(EnhancedParticle(self.rect.centerx, 
                                                        self.rect.centery, 
                                                        "explode"))
                return True  # Collision with spike (game over)
        
        # Check for landing on top of obstacles
        self.on_obstacle = False
        for obstacle in obstacles:
            # Check if player is falling down
            if self.velocity > 0:
                # Check if player's bottom is at or slightly below obstacle's top
                # AND was previously above the obstacle top
                if (self.rect.bottom >= obstacle.rect.top and 
                    self.rect.bottom - self.velocity <= obstacle.rect.top + 5 and
                    self.rect.right > obstacle.rect.left and 
                    self.rect.left < obstacle.rect.right):
                    # Land on the obstacle
                    self.y = obstacle.rect.top - PLAYER_SIZE
                    self.velocity = 0
                    self.jumping = False
                    self.on_obstacle = True
                    # Update rectangle after position change
                    self.rect = pygame.Rect(self.x, self.y, PLAYER_SIZE, PLAYER_SIZE)
                    
                    # Create landing particles
                    for _ in range(12):
                        self.particles.append(EnhancedParticle(self.x + PLAYER_SIZE//2, 
                                                            self.y + PLAYER_SIZE, 
                                                            "land"))
                    break
            
            # Check for side collisions with obstacles (only if not landing on top)
            if (not self.on_obstacle and 
                self.rect.colliderect(obstacle.rect) and 
                not (self.rect.bottom > obstacle.rect.top and 
                     self.rect.bottom < obstacle.rect.top + 10)):
                # Create collision particles - explosion effect
                for _ in range(30):
                    self.particles.append(EnhancedParticle(
                        (self.rect.left + obstacle.rect.right) // 2,
                        (self.rect.top + self.rect.bottom) // 2,
                        "explode"))
                return True  # Collision detected (game over)
                
        return False  # No side collision
    
    def draw(self, surface):
        # Draw trail
        for i, (x, y, alpha) in enumerate(self.trail):
            size_factor = 0.7 + (i * 0.05)
            trail_size = int(PLAYER_SIZE * size_factor)
            trail_rect = pygame.Rect(x - (trail_size - PLAYER_SIZE)//2, 
                                    y - (trail_size - PLAYER_SIZE)//2,
                                    trail_size, trail_size)
            
            # Enhanced trail with color variation
            trail_color = (
                min(255, PLAYER_COLOR[0] + i * 20),
                min(255, PLAYER_COLOR[1] - i * 10),
                min(255, PLAYER_COLOR[2])
            )
            
            s = pygame.Surface((trail_size, trail_size), pygame.SRCALPHA)
            s.fill((*trail_color, alpha))
            rotated = pygame.transform.rotate(s, self.rotation)
            surface.blit(rotated, rotated.get_rect(center=trail_rect.center))
        
        # Get player image from visuals module
        from visuals import player_img, player_glow
        
        # Draw glow effect if enabled
        if ENABLE_BLOOM:
            # Adjust glow size based on pulsing factor but make it smaller
            glow_size = (
                int(player_glow.get_width() * (0.7 + 0.15 * self.glow_factor)),  # Reduced from 0.8+0.2
                int(player_glow.get_height() * (0.7 + 0.15 * self.glow_factor))
            )
            
            glow = pygame.transform.scale(player_glow, glow_size)
            # Apply rotation to glow
            rotated_glow = pygame.transform.rotate(glow, self.rotation)
            
            # Position glow (centered on player)
            glow_rect = rotated_glow.get_rect(center=self.rect.center)
            surface.blit(rotated_glow, glow_rect)
            
            # Add extra glow for dash effect
            if self.dash_effect_timer > 0:
                dash_factor = self.dash_effect_timer / 15
                dash_glow = pygame.transform.scale(
                    player_glow, 
                    (int(player_glow.get_width() * (1.1 + 0.2 * dash_factor)),  # Reduced from 1.2+0.3
                     int(player_glow.get_height() * (1.1 + 0.2 * dash_factor)))
                )
                dash_glow = pygame.transform.rotate(dash_glow, self.rotation)
                dash_glow.set_alpha(int(120 * dash_factor))  # Reduced from 150
                dash_rect = dash_glow.get_rect(center=self.rect.center)
                surface.blit(dash_glow, dash_rect)
        
        # Draw player
        rotated_player = pygame.transform.rotate(player_img, self.rotation)
        player_rect = rotated_player.get_rect(center=self.rect.center)
        surface.blit(rotated_player, player_rect)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(surface)
            
        # Add a "speed line" effect when moving fast
        if abs(self.velocity) > 5 and pygame.time.get_ticks() % 3 == 0:
            for i in range(3):  # Multiple speed lines
                line_y = self.y + random.randint(0, PLAYER_SIZE)
                line_length = random.randint(PLAYER_SIZE, PLAYER_SIZE*2)
                line_thickness = random.randint(1, 3)
                
                speed_line = pygame.Surface((line_length, line_thickness), pygame.SRCALPHA)
                speed_line.fill((255, 255, 255, 100))
                surface.blit(speed_line, (self.x - line_length, line_y)) 