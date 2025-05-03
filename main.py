import pygame
import random
import math
import os
import platform
from constants import *
from player import Player
from obstacles import Obstacle, Spike, create_obstacles
from visuals import EnhancedParticle, draw_parallax_background, draw_ground, PowerUp
from utils import load_high_score, save_high_score, ScreenShake, draw_neon_text
from collections import deque

os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'  # Position window at top-left of screen for better maximize behavior

class Notification:
    def __init__(self, text, color, duration=120, size="medium"):
        self.text = text
        self.base_color = color
        self.duration = duration
        self.remaining = duration
        self.y_offset = 0
        
        # Choose font size based on importance
        if size == "large":
            self.font = pygame.font.SysFont('Arial', int(36 * SCALE_Y), bold=True)
        elif size == "medium":
            self.font = pygame.font.SysFont('Arial', int(28 * SCALE_Y), bold=True)
        else:
            self.font = pygame.font.SysFont('Arial', int(24 * SCALE_Y))
        
        self.render = self.font.render(self.text, True, self.base_color)
        self.width = self.render.get_width()
    
    def update(self):
        self.remaining -= 1
        
        # Move notification upward as it ages
        if self.remaining > self.duration - 30:
            self.y_offset -= 1
        
        return self.remaining > 0
    
    def draw(self, surface, x, y):
        # Calculate alpha based on remaining lifetime
        alpha = int(255 * min(1.0, self.remaining / self.duration))
        
        # Create a surface with transparency
        text_surf = pygame.Surface((self.width + 20, self.render.get_height() + 10), pygame.SRCALPHA)
        
        # Draw background
        bg_color = (*self.base_color[:3], 40)  # Semi-transparent background
        pygame.draw.rect(text_surf, bg_color, 
                       (0, 0, self.width + 20, self.render.get_height() + 10),
                       border_radius=5)
        
        # Adjust text color for fading
        temp_surf = self.render.copy()
        temp_surf.set_alpha(alpha)
        
        # Center text in the background
        text_surf.blit(temp_surf, (10, 5))
        
        # Draw with the calculated offset
        surface.blit(text_surf, (x - self.width//2, y + self.y_offset))

def main():
    # Initialize pygame with proper flags
    pygame.init()
    
    # Debug logging
    import sys
    debug_log = open('debug_log.txt', 'w')
    def log(msg):
        debug_log.write(f"{msg}\n")
        debug_log.flush()
    
    log("Game started")
    
    # Special handling for macOS
    if platform.system() == 'Darwin':  # Darwin is the core of macOS
        log("Running on macOS")
        # Configure pygame to work better with macOS
        os.environ['SDL_VIDEO_MAC_FULLSCREEN_SPACES'] = '0'
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'  # Position window at top-left of screen
    
    # Make sure key events get through
    pygame.key.set_repeat(500, 30)
    
    # Set initial fullscreen state - default to False
    FULLSCREEN = False  # Set to True if you want fullscreen by default
    
    # Set up display with a fixed size (no RESIZABLE flag)
    pygame.display.set_caption("Space Run")
    
    # Create the window - either fullscreen or fixed size
    if FULLSCREEN:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    # Force processing of events to help with input focus
    for _ in range(3):  # Process multiple times to ensure we catch everything
        pygame.event.pump()
        pygame.event.get()
    
    # Ensure window has focus
    pygame.display.flip()
    pygame.event.clear()  # Clear any pending events
    
    # Create game objects
    player = Player()
    obstacles, spikes = create_obstacles()
    
    # Game variables
    score = 0
    lives = 3  # Added lives system
    high_score = load_high_score()
    game_over = False
    bg_offset = 0
    pulse_value = 0
    pulse_dir = 1
    particles = []
    screen_shake = ScreenShake()
    power_ups = []  # List for power-ups
    invincibility_timer = 0  # For temporary invincibility after hit
    notifications = deque(maxlen=5)  # Limit to 5 notifications at once
    active_powerups = []  # Track active power-ups with their timers
    
    # Create fonts
    score_font = pygame.font.SysFont('Arial', 36, bold=True)
    game_over_font = pygame.font.SysFont('Arial', 72, bold=True)
    info_font = pygame.font.SysFont('Arial', 24)
    
    # Load heart image for lives display
    heart_img = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.polygon(heart_img, (255, 50, 50), [(10, 5), (5, 0), (0, 5), (0, 12), (10, 19), (20, 12), (20, 5), (15, 0)])
    
    # Near the top of the main function, add a variable to track normal game speed
    normal_game_speed = GAME_SPEED
    current_game_speed = normal_game_speed
    
    # Title screen loop
    def show_title_screen():
        nonlocal bg_offset, pulse_value, pulse_dir
        
        title_font = pygame.font.SysFont('Arial', 56, bold=True)
        subtitle_font = pygame.font.SysFont('Arial', 28)
        info_font = pygame.font.SysFont('Arial', 20)
        
        # Create mini power-up examples
        mini_powerups = []
        powerup_types = ["extra_life", "shield", "score_boost", "slow_time"]
        powerup_descriptions = [
            "Extra Life: +1 life",
            "Shield: Temporary invincibility",
            "Score Boost: Bonus points",
            "Slow Time: Slows game speed"
        ]
        
        # Create mini versions of each powerup
        for i, p_type in enumerate(powerup_types):
            mini_pu = PowerUp(WIDTH//2 - 200, HEIGHT//2 + 80 + i*30, p_type)
            mini_pu.size = 20  # Smaller size for display
            mini_powerups.append((mini_pu, powerup_descriptions[i]))
        
        # Show explanation toggle
        show_explanations = False
        
        while True:
            # Process all events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return True  # Continue to game
                    if event.key == pygame.K_h:
                        show_explanations = not show_explanations
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return False
                    if event.key == pygame.K_F11:
                        toggle_fullscreen()
                elif event.type == pygame.ACTIVEEVENT:
                    if event.gain:  # Window gained focus
                        pygame.event.clear()  # Clear any pending events
                        pygame.key.set_repeat(500, 30)  # Reset key repeat
            
            # Draw title screen background
            draw_parallax_background(bg_offset)
            bg_offset += 1  # Slow background scroll
            draw_ground()
            
            # Pulsing effect for text
            pulse_value += 0.03 * pulse_dir
            if pulse_value > 1 or pulse_value < 0:
                pulse_dir *= -1
            
            # Always draw the title, regardless of mode
            title_pos = (WIDTH//2, HEIGHT//5)  # Move title higher up
            draw_neon_text(screen, "SPACE RUN", title_font, 
                          (50, 255, 255),  # Brighter cyan color
                          (title_pos[0] - title_font.size("SPACE RUN")[0]//2, title_pos[1]),
                          (40, 180, 255), 8)
            
            if show_explanations:
                # Draw powerup explanations panel
                panel_rect = pygame.Rect(WIDTH//4, HEIGHT//3, WIDTH//2, HEIGHT//2)
                panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
                panel_surface.fill((0, 0, 30, 200))  # Semi-transparent dark blue
                screen.blit(panel_surface, panel_rect)
                
                # Draw help title
                help_text = info_font.render("POWER-UPS GUIDE", True, (255, 255, 255))
                screen.blit(help_text, (WIDTH//2 - help_text.get_width()//2, panel_rect.y + 20))
                
                # Draw each powerup with description
                for i, (mini_pu, desc) in enumerate(mini_powerups):
                    mini_pu.y = panel_rect.y + 60 + i*40  # Position within panel
                    mini_pu.x = panel_rect.x + 30  # Align to left of panel
                    mini_pu.draw(screen)
                    
                    # Draw description
                    desc_text = info_font.render(desc, True, (255, 255, 255))
                    screen.blit(desc_text, (mini_pu.x + 30, mini_pu.y))
                
                # Back instruction
                back_text = info_font.render("Press H to return", True, (200, 200, 200))
                screen.blit(back_text, (WIDTH//2 - back_text.get_width()//2, panel_rect.y + panel_rect.height - 30))
            else:
                # Draw subtitle with pulse
                subtitle_alpha = 100 + int(155 * pulse_value)
                subtitle_text = subtitle_font.render("Press SPACE to play", True, (255, 255, 255))
                subtitle_text.set_alpha(subtitle_alpha)
                screen.blit(subtitle_text, 
                          (WIDTH//2 - subtitle_text.get_width()//2, HEIGHT//2))
                
                # Draw high score
                high_score_text = subtitle_font.render(f"High Score: {high_score}", True, (255, 230, 0))
                screen.blit(high_score_text, 
                          (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 + 50))
                
                # Add QUIT option with highlight
                quit_text = subtitle_font.render("Press Q to QUIT", True, (255, 100, 100))
                # Add subtle glow effect that pulses
                glow_intensity = 0.5 + 0.5 * pulse_value
                quit_x = WIDTH//2 - quit_text.get_width()//2
                quit_y = HEIGHT//2 + 100
                
                # Draw subtle glow behind text
                glow_surf = pygame.Surface((quit_text.get_width() + 20, quit_text.get_height() + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (255, 50, 50, int(50 * glow_intensity)), 
                               (0, 0, quit_text.get_width() + 20, quit_text.get_height() + 10),
                               border_radius=10)
                screen.blit(glow_surf, (quit_x - 10, quit_y - 5))
                
                # Draw the text
                screen.blit(quit_text, (quit_x, quit_y))
                
                # Help instruction
                help_text = info_font.render("Press H for power-up guide", True, (200, 200, 200))
                screen.blit(help_text, (WIDTH//2 - help_text.get_width()//2, HEIGHT - 100))
            
            pygame.display.flip()
            clock.tick(60)
    
    # Game over screen
    def show_game_over_screen():
        nonlocal game_over, score, high_score, bg_offset, pulse_value, pulse_dir
        
        # Check for new high score
        new_high_score = False
        if score > high_score:
            high_score = score
            save_high_score(high_score)
            new_high_score = True
        
        # Create particles for game over effect
        for _ in range(50):
            particles.append(EnhancedParticle(
                WIDTH//2 + random.randint(-100, 100),
                HEIGHT//2 + random.randint(-50, 50),
                "explode"
            ))
        
        # Start screen shake
        screen_shake.start(10, 20)
        
        while game_over:
            # Process all events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return True  # Restart game
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return False
                    if event.key == pygame.K_F11:  # Toggle fullscreen
                        toggle_fullscreen()
                elif event.type == pygame.ACTIVEEVENT:
                    if event.gain:  # Window gained focus
                        pygame.event.clear()  # Clear any pending events
                        pygame.key.set_repeat(500, 30)  # Reset key repeat
            
            # Get screen shake offset
            shake_offset = screen_shake.update()
            
            # Draw game over screen
            draw_parallax_background(bg_offset)
            bg_offset += 0.5  # Slower background scroll when game over
            draw_ground()
            
            # Draw existing obstacles and spikes
            for obstacle in obstacles:
                obstacle.draw(screen)
            for spike in spikes:
                spike.draw(screen)
            
            # Update pulse effect
            pulse_value += 0.05 * pulse_dir
            if pulse_value > 1 or pulse_value < 0:
                pulse_dir *= -1
            
            # Draw game over text with glow
            game_over_text = "GAME OVER"
            text_y = HEIGHT//3
            draw_neon_text(screen, game_over_text, game_over_font, 
                         (255, 50, 50), 
                         (WIDTH//2 - game_over_font.size(game_over_text)[0]//2 + shake_offset[0], 
                          text_y + shake_offset[1]),
                         (255, 100, 100), 15)
            
            # Draw score
            score_text = f"Score: {score}"
            score_y = text_y + 100
            draw_neon_text(screen, score_text, score_font, 
                         (255, 255, 255), 
                         (WIDTH//2 - score_font.size(score_text)[0]//2 + shake_offset[0], 
                          score_y + shake_offset[1]))
            
            # Draw high score message
            if new_high_score:
                # Pulsing effect for high score text
                glow_intensity = 0.5 + 0.5 * pulse_value
                
                high_score_text = "NEW HIGH SCORE!"
                draw_neon_text(screen, high_score_text, score_font, 
                             (255, 255, 0), 
                             (WIDTH//2 - score_font.size(high_score_text)[0]//2, score_y + 50),
                             (255, 200, 0), int(15 * glow_intensity))
            else:
                high_score_text = f"High Score: {high_score}"
                draw_neon_text(screen, high_score_text, info_font, 
                             (200, 200, 0), 
                             (WIDTH//2 - info_font.size(high_score_text)[0]//2, score_y + 50))
            
            # Draw restart instruction
            restart_text = "Press R to restart, Q to quit"
            restart_alpha = 100 + int(155 * pulse_value)
            restart_render = info_font.render(restart_text, True, (200, 200, 200))
            restart_render.set_alpha(restart_alpha)
            screen.blit(restart_render, 
                      (WIDTH//2 - restart_render.get_width()//2, HEIGHT - 150))
            
            # Update and draw particles
            for particle in list(particles):
                particle.update()
                if particle.lifetime <= 0:
                    particles.remove(particle)
                else:
                    particle.draw(screen)
            
            pygame.display.flip()
            clock.tick(60)
        
        return True  # Default to continue
    
    # Main game loop with restart capability
    running = True
    clock = pygame.time.Clock()
    
    while running:
        # Show title screen
        if not show_title_screen():
            break
        
        # Reset game state for new game
        player = Player()
        obstacles, spikes = create_obstacles()
        power_ups = []  # Reset power-ups
        score = 0
        lives = 3  # Reset lives
        game_over = False
        invincibility_timer = 0
        particles.clear()
        
        # Main gameplay loop
        while not game_over:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        player.jump()
                    if event.key == pygame.K_F11:  # Toggle fullscreen
                        toggle_fullscreen()
                elif event.type == pygame.ACTIVEEVENT:
                    if event.gain:  # Window gained focus
                        pygame.event.clear()  # Clear any pending events
                        pygame.key.set_repeat(500, 30)  # Reset key repeat
            
            # Get keyboard state
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
                player.jump()
            
            # Update game objects
            bg_offset += current_game_speed//2  # Background parallax effect
            
            # Update invincibility timer
            if invincibility_timer > 0:
                invincibility_timer -= 1
            
            # Remove obstacles/spikes that have moved off-screen
            obstacles = [o for o in obstacles if o.x > -o.width]
            spikes = [s for s in spikes if s.x > -s.width]
            power_ups = [p for p in power_ups if p.x > -p.size]
            
            # Create new obstacles/spikes as needed
            if len(obstacles) + len(spikes) < 5:
                # Find the rightmost x position
                rightmost_x = WIDTH
                if obstacles:
                    rightmost_x = max(rightmost_x, max(o.x for o in obstacles))
                if spikes:
                    rightmost_x = max(rightmost_x, max(s.x for s in spikes))
                
                # Place new obstacle/spike
                new_x = max(WIDTH, rightmost_x + random.randint(MIN_OBSTACLE_DISTANCE, MAX_OBSTACLE_DISTANCE))
                
                # Randomly choose between obstacle and spike
                if random.random() < SPIKE_CHANCE:
                    # Create spike with proper parameters
                    spike_width = random.randint(SPIKE_WIDTH, SPIKE_WIDTH * 2)
                    spike_height = random.randint(SPIKE_HEIGHT, SPIKE_HEIGHT * 3 // 2)
                    spike_y = HEIGHT - GROUND_HEIGHT - spike_height
                    spikes.append(Spike(new_x, spike_y, spike_width, spike_height))
                else:
                    obstacles.append(Obstacle(new_x))
            
            # Spawn power-ups occasionally
            if random.random() < 0.005 and len(power_ups) < 2:  # 0.5% chance each frame
                # Choose a clear spot for the power-up
                power_up_x = WIDTH + random.randint(50, 200)
                power_up_y = random.randint(HEIGHT // 4, HEIGHT - GROUND_HEIGHT - 50)
                
                # Choose a random power-up type
                power_up_type = random.choice(["extra_life", "shield", "score_boost", "slow_time"])
                power_ups.append(PowerUp(power_up_x, power_up_y, power_up_type))
            
            # Update obstacles
            for obstacle in obstacles:
                obstacle.update(current_game_speed)
                
                # Add score when passing
                if not obstacle.passed and obstacle.x + obstacle.width < player.x:
                    obstacle.passed = True
                    score += 1
            
            # Update spikes
            for spike in spikes:
                spike.update(current_game_speed)
                
                # Add score when passing
                if not spike.passed and spike.x + spike.width < player.x:
                    spike.passed = True
                    score += 1
            
            # Update power-ups
            for power_up in list(power_ups):
                power_up.update(current_game_speed)
                
                # Check for power-up collection
                if player.rect.colliderect(power_up.rect):
                    power_ups.remove(power_up)
                    
                    # Apply power-up effect
                    if power_up.type == "extra_life":
                        old_lives = lives
                        lives = min(lives + 1, 5)  # Maximum 5 lives
                        
                        # Only show notification if player actually gained a life
                        if lives > old_lives:
                            notifications.append(Notification("Extra Life!", (255, 50, 50), size="medium"))
                        
                        # Add special effect for life gain
                        for _ in range(20):
                            particles.append(EnhancedParticle(
                                player.rect.centerx, player.rect.centery, "trail"))
                    
                    elif power_up.type == "shield":
                        invincibility_timer = 300  # 5 seconds at 60 FPS
                        notifications.append(Notification("Shield Activated!", (50, 100, 255), size="medium"))
                        
                        # Add to active power-ups
                        active_powerups.append({
                            "type": "shield",
                            "timer": invincibility_timer,
                            "icon": "🛡️",
                            "color": (50, 100, 255)
                        })
                        
                        # Add shield effect particles
                        for _ in range(30):
                            particles.append(EnhancedParticle(
                                player.rect.centerx, player.rect.centery, "shield"))
                    
                    elif power_up.type == "score_boost":
                        score += 10
                        notifications.append(Notification("+10 Points!", (255, 215, 0), size="medium"))
                        
                        # Add score boost effect
                        for _ in range(15):
                            particles.append(EnhancedParticle(
                                player.rect.centerx, player.rect.centery, "score"))
                    
                    elif power_up.type == "slow_time":
                        # Apply slow time effect - now 50% of normal speed instead of 30%
                        notifications.append(Notification("Time Slowed!", (180, 180, 255), size="medium"))
                        
                        # Slow game speed to 50% of normal
                        current_game_speed = normal_game_speed * 0.5
                        
                        # Add to active power-ups list
                        active_powerups.append({
                            "type": "slow_time",
                            "timer": 300,  # 5 seconds
                            "icon": "⏱️",
                            "color": (180, 180, 255),
                            "original_speed": normal_game_speed
                        })
                        
                        # Add time slowing effect particles
                        for _ in range(20):
                            particles.append(EnhancedParticle(
                                player.rect.centerx, player.rect.centery, "shield"))
            
            # Check for collisions
            collision = player.update(obstacles, spikes)
            if collision and invincibility_timer <= 0:
                lives -= 1
                if lives <= 0:
                    game_over = True
                    screen_shake.start(10, 20)
                else:
                    # Player still has lives, show notification with remaining lives
                    life_text = f"{lives} {'Lives' if lives > 1 else 'Life'} Remaining"
                    notifications.append(Notification(life_text, (255, 50, 50), size="large"))
                    
                    # Create an impactful visual effect
                    for _ in range(15):
                        particles.append(EnhancedParticle(
                            player.rect.centerx, 
                            player.rect.centery, 
                            "explode"
                        ))
                        
                    # Player still has lives
                    invincibility_timer = 120  # 2 seconds of invincibility
                    screen_shake.start(5, 10)  # Smaller screen shake for hit
            
            # Generate occasional background particles (reduced frequency)
            if random.random() < 0.005:  # Reduced from 0.01
                particles.append(EnhancedParticle(
                    random.randint(0, WIDTH),
                    random.randint(0, HEIGHT - GROUND_HEIGHT),
                    "trail"
                ))
            
            # Update background particles
            for particle in list(particles):
                particle.update()
                if particle.lifetime <= 0:
                    particles.remove(particle)
            
            # Drawing
            shake_offset = screen_shake.update()
            
            # Apply screen shake
            draw_offset_x, draw_offset_y = shake_offset
            
            # Draw background
            draw_parallax_background(bg_offset)
            
            # Draw ground
            draw_ground()
            
            # Draw power-ups
            for power_up in power_ups:
                power_up.draw(screen)
            
            # Draw obstacles and spikes
            for obstacle in obstacles:
                obstacle.draw(screen)
            
            for spike in spikes:
                spike.draw(screen)
            
            # Draw player - make player blink if invincible
            if invincibility_timer <= 0 or pygame.time.get_ticks() % 10 < 7:
                player.draw(screen)
            
            # Draw background particles
            for particle in particles:
                particle.draw(screen)
            
            # Draw score with glow effect (reduced glow)
            score_text = f"Score: {score}"
            draw_neon_text(screen, score_text, score_font, 
                         (255, 255, 255), 
                         (20 + draw_offset_x, 20 + draw_offset_y),
                         (150, 150, 150), 3)  # Reduced glow radius from 5 to 3
            
            # Draw lives
            for i in range(lives):
                screen.blit(heart_img, (20 + i * 25 + draw_offset_x, 70 + draw_offset_y))
            
            # Draw high score (with reduced glow)
            high_score_text = f"High Score: {high_score}"
            high_score_color = (255, 255, 0) if score >= high_score else (200, 200, 0)
            draw_neon_text(screen, high_score_text, info_font, 
                         high_score_color, 
                         (20 + draw_offset_x, 100 + draw_offset_y))
            
            # Update and remove expired notifications
            for notification in list(notifications):
                if not notification.update():
                    notifications.remove(notification)
            
            # Draw notifications
            notification_y = HEIGHT // 4
            for notification in notifications:
                notification.draw(screen, WIDTH // 2, notification_y)
                notification_y += 50 * SCALE_Y
            
            # Update and display active power-ups - made much more obvious
            powerup_x = WIDTH - 220 * SCALE_X  # Moved more to the left for more space
            powerup_y = 20 * SCALE_Y
            
            for powerup in list(active_powerups):
                powerup["timer"] -= 1
                
                # Remove expired power-ups
                if powerup["timer"] <= 0:
                    active_powerups.remove(powerup)
                    if powerup["type"] == "shield":
                        invincibility_timer = 0
                    elif powerup["type"] == "slow_time":
                        current_game_speed = normal_game_speed
                    continue
                
                # Draw power-up indicator with timer - ENHANCED
                remaining_seconds = math.ceil(powerup["timer"] / 60)
                icon_text = f"{powerup['icon']} {remaining_seconds}s"
                icon_font = pygame.font.SysFont('Arial', int(32 * SCALE_Y))  # Larger font
                icon_surf = icon_font.render(icon_text, True, powerup["color"])
                
                # Create larger, more noticeable background
                bg_rect = pygame.Rect(powerup_x - 15, powerup_y - 10, 
                                    icon_surf.get_width() + 30, icon_surf.get_height() + 20)
                
                # More dramatic pulse effect for time running out
                alpha = 150
                if powerup["timer"] < 120:  # Last 2 seconds
                    pulse_rate = max(5, powerup["timer"] // 10)  # Faster pulse as time runs out
                    if pygame.time.get_ticks() % pulse_rate < pulse_rate // 2:
                        alpha = 230
                
                # Draw background with more opacity
                bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
                bg_surf.fill((*powerup["color"][:3], alpha // 2))  # More visible background
                
                # Add border for emphasis
                pygame.draw.rect(bg_surf, powerup["color"], 
                               (0, 0, bg_rect.width, bg_rect.height), 
                               3)  # Thicker border
                
                screen.blit(bg_surf, bg_rect)
                
                # Draw more prominent progress bar
                progress_height = 8 * SCALE_Y  # Taller progress bar
                progress_width = int((powerup["timer"] / 300) * bg_rect.width)
                progress_rect = pygame.Rect(bg_rect.x, bg_rect.y + bg_rect.height - progress_height, 
                                          progress_width, progress_height)
                
                # Create gradient effect for progress bar
                for i in range(progress_width):
                    gradient_color = (
                        powerup["color"][0],
                        powerup["color"][1],
                        powerup["color"][2],
                        int(255 * (i / progress_width))  # Gradient alpha
                    )
                    pygame.draw.line(screen, gradient_color, 
                                   (progress_rect.x + i, progress_rect.y),
                                   (progress_rect.x + i, progress_rect.y + progress_rect.height))
                
                # Draw icon and text centered
                screen.blit(icon_surf, (powerup_x, powerup_y + 5))  # Small vertical adjustment
                
                # If very low time, add additional indicator
                if powerup["timer"] < 60:  # Last second
                    warning_text = "!"
                    warning_font = pygame.font.SysFont('Arial', int(40 * SCALE_Y), bold=True)
                    warning_surf = warning_font.render(warning_text, True, (255, 50, 50))
                    screen.blit(warning_surf, (bg_rect.x + bg_rect.width + 5, bg_rect.y))
                
                powerup_y += bg_rect.height + 15  # More spacing between power-ups
            
            pygame.display.flip()
            clock.tick(60)
        
        # Show game over screen and check if we should restart
        if not show_game_over_screen():
            running = False

if __name__ == "__main__":
    main() 