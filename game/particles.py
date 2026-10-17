"""Small particle system: thruster exhaust, landing dust, impact sparks."""

import math
import random
import pygame

KINDS = {
    #          color            speed      life        grav  size
    "exhaust": ((120, 190, 255), (40, 120), (0.12, 0.25), 0, (1.5, 3.0)),
    "jet":     ((150, 210, 255), (60, 160), (0.15, 0.30), 0, (2.0, 3.5)),
    "dust":    ((140, 140, 148), (40, 140), (0.30, 0.55), 300, (1.5, 3.5)),
    "spark":   ((255, 170, 80), (120, 340), (0.25, 0.50), 500, (1.5, 3.0)),
    "debris":  ((180, 186, 196), (80, 260), (0.50, 0.90), 700, (2.0, 4.0)),
    "pickup":  ((200, 230, 255), (60, 200), (0.30, 0.55), 0, (1.5, 3.0)),
}


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "grav", "size", "color")

    def __init__(self, x, y, kind, direction=None, color=None):
        col, (smin, smax), (lmin, lmax), grav, (zmin, zmax) = KINDS[kind]
        a = direction if direction is not None else random.uniform(0, math.tau)
        a += random.uniform(-0.5, 0.5) if direction is not None else 0
        s = random.uniform(smin, smax)
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(a) * s, math.sin(a) * s
        self.life = self.max_life = random.uniform(lmin, lmax)
        self.grav = grav
        self.size = random.uniform(zmin, zmax)
        self.color = color or col


class ParticleSystem:
    def __init__(self):
        self.items = []

    def emit(self, x, y, kind, count=1, direction=None, color=None):
        for _ in range(count):
            self.items.append(Particle(x, y, kind, direction, color))

    def update(self, dt, scroll_dx=0.0):
        alive = []
        for p in self.items:
            p.life -= dt
            if p.life <= 0:
                continue
            p.vy += p.grav * dt
            p.x += p.vx * dt - scroll_dx
            p.y += p.vy * dt
            alive.append(p)
        self.items = alive

    def draw(self, surface):
        for p in self.items:
            k = p.life / p.max_life
            r = max(1, int(p.size * (0.5 + 0.5 * k)))
            a = int(220 * k)
            dot = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(dot, (*p.color, a), (r, r), r)
            surface.blit(dot, (int(p.x - r), int(p.y - r)))

    def clear(self):
        self.items.clear()
