"""Player: physics body plus hovercraft presentation."""

import math
import random
import pygame
from constants import PLAYER_X, PLAYER_W, PLAYER_H, GROUND_Y, ACCENT
from game.physics import Body, step, EV_JUMP, EV_DOUBLE, EV_LAND, EV_HIT
from game import art


class Player:
    def __init__(self, particles):
        self.body = Body()
        self.particles = particles
        self.tilt = 0.0
        self.jet = 0.0
        self.hurt_flash = 0.0
        self.t = 0.0
        self.exhaust_timer = 0.0

    @property
    def rect(self):
        return pygame.Rect(PLAYER_X, round(self.body.y), PLAYER_W, PLAYER_H)

    def update(self, dt, solids, hazards, pressed, held):
        ev = step(self.body, dt, solids, hazards, pressed, held)
        self.t += dt
        b = self.body
        cx, bottom = PLAYER_X + PLAYER_W / 2, b.y + PLAYER_H

        if ev & (EV_JUMP | EV_DOUBLE):
            self.jet = 1.0
            n = 10 if ev & EV_DOUBLE else 6
            for side in (PLAYER_X + 16, PLAYER_X + 40):
                self.particles.emit(side, bottom, "jet", n // 2, direction=math.pi / 2)
            if ev & EV_JUMP and b.y + PLAYER_H > GROUND_Y - 40:
                self.particles.emit(cx, GROUND_Y, "dust", 6, direction=-math.pi / 2)
        if ev & EV_LAND:
            self.particles.emit(cx - 10, bottom, "dust", 4, direction=math.pi * 1.1)
            self.particles.emit(cx + 10, bottom, "dust", 4, direction=-math.pi * 0.1)
        if ev & EV_HIT:
            self.particles.emit(cx, b.y + PLAYER_H / 2, "spark", 18)

        self.jet = max(0.0, self.jet - dt * 3.5)
        self.hurt_flash = max(0.0, self.hurt_flash - dt)
        target = max(-14.0, min(14.0, -b.vy * 0.018))
        self.tilt += (target - self.tilt) * min(1.0, dt * 14)

        self.exhaust_timer -= dt
        if self.exhaust_timer <= 0:
            self.exhaust_timer = 0.03
            self.particles.emit(PLAYER_X - 1, b.y + 15 + random.uniform(-2, 2), "exhaust", 1, direction=math.pi)
        return ev

    def draw(self, surface, blink=False, shield=False):
        b = self.body
        cx, cy = PLAYER_X + PLAYER_W / 2, b.y + PLAYER_H / 2
        height_above = GROUND_Y - (b.y + PLAYER_H)
        if height_above < 140:
            k = 1 - height_above / 140
            shadow = pygame.Surface((70, 12), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, int(110 * k)), shadow.get_rect())
            surface.blit(shadow, (cx - 35, GROUND_Y - 6))
            art.draw_glow(surface, (int(cx), GROUND_Y - 2), int(26 + 10 * k), (90, 170, 255), int(55 * k))

        if blink and int(self.t * 14) % 2 == 0:
            return

        if self.jet > 0:
            for jx in (PLAYER_X + 16, PLAYER_X + 40):
                L = int(8 + 22 * self.jet)
                flame = pygame.Surface((10, L), pygame.SRCALPHA)
                for i in range(L):
                    a = int(220 * (1 - i / L) * self.jet)
                    w = max(1, int(5 * (1 - i / L)))
                    pygame.draw.line(flame, (170, 220, 255, a), (5 - w, i), (5 + w, i))
                surface.blit(flame, (jx - 5, b.y + PLAYER_H - 2))

        flicker = 0.75 + 0.25 * math.sin(self.t * 50)
        art.draw_glow(surface, (PLAYER_X + 1, int(b.y + 15)), 12, (120, 190, 255), int(140 * flicker))

        img = art.ship("hurt" if self.hurt_flash > 0 else "normal")
        bob = math.sin(self.t * 5) * 1.2 if b.grounded else 0
        rotated = pygame.transform.rotozoom(img, self.tilt, 1.0)
        surface.blit(rotated, rotated.get_rect(center=(cx, cy + bob)))

        if shield:
            r = 40
            ring = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pulse = 0.6 + 0.4 * math.sin(self.t * 6)
            pygame.draw.ellipse(ring, (90, 170, 255, int(50 * pulse)), ring.get_rect().inflate(-4, -26))
            pygame.draw.ellipse(ring, (140, 200, 255, int(170 * pulse)), ring.get_rect().inflate(-4, -26), 2)
            surface.blit(ring, ring.get_rect(center=(cx, cy)))
