"""Procedural art drawn at exact gameplay sizes, cached per size."""

import math
import random
import pygame
from functools import lru_cache
from constants import (
    WIDTH, HEIGHT, GROUND_Y, GROUND_HEIGHT, PLAYER_W, PLAYER_H,
    SKY_TOP, SKY_HORIZON, MOUNTAIN_FAR, MOUNTAIN_NEAR, GROUND_TOP, GROUND_BOTTOM,
    STEEL, STEEL_LIGHT, STEEL_DARK, HAZARD_YELLOW, DANGER, PLASMA, ACCENT,
    SHIELD_COLOR, OVERDRIVE_COLOR, SLOW_COLOR,
)

SS = 3  # supersample factor for anti-aliased shapes


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgradient(w, h, top, bottom):
    s = pygame.Surface((w, h))
    for y in range(h):
        pygame.draw.line(s, _lerp(top, bottom, y / max(1, h - 1)), (0, y), (w, y))
    return s


def _aa(surface_big, w, h):
    return pygame.transform.smoothscale(surface_big, (w, h))


# ---------------------------------------------------------------- background

class Backdrop:
    """Sky, planet, mountain parallax, regolith ground."""

    def __init__(self, seed=7):
        rnd = random.Random(seed)
        self.sky = vgradient(WIDTH, GROUND_Y, SKY_TOP, SKY_HORIZON)
        self._draw_stars(self.sky, rnd)
        self.planet = self._make_planet(150)
        self.far = self._make_ridge(rnd, MOUNTAIN_FAR, base=GROUND_Y - 50, amp=150, rough=0.42, rim=(40, 52, 72))
        self.near = self._make_ridge(rnd, MOUNTAIN_NEAR, base=GROUND_Y - 4, amp=80, rough=0.45, rim=(62, 72, 92))
        self.ground = self._make_ground(rnd)

    def _draw_stars(self, surf, rnd):
        for _ in range(220):
            x = rnd.randrange(WIDTH)
            y = rnd.randrange(GROUND_Y - 60)
            b = rnd.choice([90, 120, 150, 190, 230])
            surf.set_at((x, y), (b, b, min(255, b + 15)))
            if b > 200 and rnd.random() < 0.4:
                pygame.draw.circle(surf, (b, b, 255), (x, y), 1)

    def _make_planet(self, r):
        size = r * 2 + 80
        out = pygame.Surface((size, size), pygame.SRCALPHA)
        c = size // 2
        for i in range(40, 0, -2):
            pygame.draw.circle(out, (90, 150, 210, int(3 + (40 - i) * 0.25)), (c, c), r + i)

        body = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        bands = [(70, 112, 150), (84, 128, 166), (64, 104, 142), (96, 140, 176), (74, 118, 156), (60, 98, 136)]
        for y in range(r * 2):
            t = (y / (r * 2)) * 9 + math.sin(y * 0.05) * 0.4
            i = int(t)
            col = _lerp(bands[i % len(bands)], bands[(i + 1) % len(bands)], t - i)
            pygame.draw.line(body, col, (0, y), (r * 2, y))
        storm = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(storm, (130, 168, 196, 80), (r * 0.9, r * 1.15, r * 0.46, r * 0.16))
        body.blit(storm, (0, 0))
        small = pygame.transform.smoothscale(body, (r // 2, r // 2))
        body = pygame.transform.smoothscale(small, (r * 2, r * 2))
        shadow = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        for i in range(24):
            a = int(10 + i * 9)
            pygame.draw.circle(shadow, (4, 6, 14, min(235, a)), (int(r * 1.55 + i * 2), int(r * 1.35 + i * 1.5)), int(r * 1.25 - i * 2))
        body.blit(shadow, (0, 0))
        mask = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255), (r, r), r)
        body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        out.blit(body, (c - r, c - r))
        return out

    def _ridge_heights(self, rnd, n, amp, rough):
        pts = [0.0] * (n + 1)
        pts[0] = pts[n] = rnd.uniform(0.3, 0.6) * amp
        step = n
        scale = amp
        while step > 1:
            half = step // 2
            for i in range(half, n, step):
                pts[i] = (pts[i - half] + pts[i + half]) / 2 + rnd.uniform(-scale, scale) * 0.5
            step = half
            scale *= rough
        return [max(8.0, min(amp * 1.4, p)) for p in pts]

    def _make_ridge(self, rnd, color, base, amp, rough, rim):
        n = 128
        hs = self._ridge_heights(rnd, n, amp, rough)
        surf = pygame.Surface((WIDTH, GROUND_Y), pygame.SRCALPHA)
        pts = [(i * WIDTH / n, base - hs[i]) for i in range(n + 1)]
        pygame.draw.polygon(surf, color, pts + [(WIDTH, GROUND_Y), (0, GROUND_Y)])
        pygame.draw.lines(surf, rim, False, pts, 2)
        return surf

    def _make_ground(self, rnd):
        g = vgradient(WIDTH, GROUND_HEIGHT, GROUND_TOP, GROUND_BOTTOM).convert()
        for _ in range(26):
            cx, cy = rnd.randrange(WIDTH), rnd.randrange(14, GROUND_HEIGHT - 6)
            rw = rnd.randint(18, 60)
            rh = max(4, rw // 4)
            for dx in (0, -WIDTH, WIDTH):
                pygame.draw.ellipse(g, (40, 44, 54), (cx - rw // 2 + dx, cy - rh // 2, rw, rh))
                pygame.draw.arc(g, (88, 94, 106), (cx - rw // 2 + dx, cy - rh // 2, rw, rh), 3.4, 6.0, 1)
        for _ in range(500):
            x, y = rnd.randrange(WIDTH), rnd.randrange(6, GROUND_HEIGHT)
            v = rnd.randint(-14, 14)
            base = _lerp(GROUND_TOP, GROUND_BOTTOM, y / GROUND_HEIGHT)
            g.set_at((x, y), tuple(max(0, min(255, c + v)) for c in base))
        pygame.draw.line(g, (132, 140, 154), (0, 0), (WIDTH, 0), 2)
        pygame.draw.line(g, (50, 55, 66), (0, 3), (WIDTH, 3), 1)
        return g

    def draw(self, surface, scroll):
        surface.blit(self.sky, (0, 0))
        surface.blit(self.planet, (WIDTH - 420 - (scroll * 0.01) % 40, 10))
        for layer, factor in ((self.far, 0.06), (self.near, 0.18)):
            off = -(scroll * factor) % WIDTH
            surface.blit(layer, (off - WIDTH, 0))
            surface.blit(layer, (off, 0))
        off = -scroll % WIDTH
        surface.blit(self.ground, (off - WIDTH, GROUND_Y))
        surface.blit(self.ground, (off, GROUND_Y))


# ---------------------------------------------------------------- structures

@lru_cache(maxsize=256)
def crate(w, h):
    """Steel cargo block. Lit top edge = safe to land; striped base = solid wall."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.blit(vgradient(w, h, (62, 70, 86), (38, 44, 56)), (0, 0))
    seam = (30, 35, 45)
    cols = max(1, w // 42)
    for i in range(1, cols + 1):
        x = int(i * w / (cols + 1))
        pygame.draw.line(s, seam, (x, 6), (x, h - 12), 2)
        pygame.draw.line(s, (78, 88, 106), (x + 2, 6), (x + 2, h - 12), 1)
    if h > 70:
        pygame.draw.line(s, seam, (4, h // 2), (w - 4, h // 2), 2)
    band = min(12, max(6, h // 6))
    stripe = pygame.Surface((w, band), pygame.SRCALPHA)
    stripe.fill((24, 24, 24))
    for x in range(-band, w + band, 14):
        pygame.draw.polygon(stripe, HAZARD_YELLOW, [(x, band), (x + 7, band), (x + 7 + band, 0), (x + band, 0)])
    s.blit(stripe, (0, h - band))
    pygame.draw.rect(s, (138, 154, 176), (0, 0, w, 4))
    pygame.draw.line(s, (200, 214, 230), (0, 0), (w - 1, 0), 1)
    pygame.draw.rect(s, (22, 26, 34), (w - 5, 4, 5, h - 4))
    pygame.draw.rect(s, (18, 21, 28), s.get_rect(), 1)
    for rx in (6, w - 9):
        for ry in (10, h - band - 6):
            if 4 < ry < h - band:
                pygame.draw.circle(s, (100, 112, 130), (rx, ry), 2)
    return s


@lru_cache(maxsize=128)
def spikes(w, h):
    big = pygame.Surface((w * SS, h * SS), pygame.SRCALPHA)
    plate = 5 * SS
    pygame.draw.rect(big, (34, 38, 48), (0, h * SS - plate, w * SS, plate))
    n = max(2, w // 16)
    sw = w * SS / n
    for i in range(n):
        x0 = i * sw + SS
        x1 = (i + 1) * sw - SS
        mid = (x0 + x1) / 2
        top = 2 * SS
        base = h * SS - plate
        pygame.draw.polygon(big, (150, 160, 174), [(x0, base), (mid, top), (mid, base)])
        pygame.draw.polygon(big, (92, 100, 114), [(mid, top), (x1, base), (mid, base)])
        tip_h = (base - top) * 0.28
        pygame.draw.polygon(big, DANGER, [(mid - (mid - x0) * 0.28, top + tip_h), (mid, top), (mid + (x1 - mid) * 0.28, top + tip_h)])
    return _aa(big, w, h)


@lru_cache(maxsize=128)
def catwalk_deck(w):
    h = 18
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, (96, 110, 128), (0, 0, w, 7))
    pygame.draw.line(s, (196, 210, 226), (0, 0), (w - 1, 0), 1)
    pygame.draw.rect(s, (40, 46, 58), (0, 7, w, 3))
    for x in range(0, w - 10, 16):
        pygame.draw.line(s, (70, 80, 96), (x, 10), (x + 8, h - 1), 2)
        pygame.draw.line(s, (70, 80, 96), (x + 16, 10), (x + 8, h - 1), 2)
    pygame.draw.line(s, (60, 68, 82), (0, h - 1), (w, h - 1), 2)
    for x in (4, w - 8):
        pygame.draw.rect(s, (255, 190, 80), (x, 2, 4, 3))
    return s


@lru_cache(maxsize=16)
def vent_base(w):
    s = pygame.Surface((w, 12), pygame.SRCALPHA)
    pygame.draw.rect(s, (36, 40, 50), (0, 0, w, 12), border_radius=2)
    pygame.draw.rect(s, (90, 98, 112), (0, 0, w, 12), 1, border_radius=2)
    for x in range(6, w - 4, 7):
        pygame.draw.line(s, (16, 18, 24), (x, 3), (x, 9), 3)
    return s


@lru_cache(maxsize=32)
def plasma_column(w, h):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        t = y / max(1, h - 1)
        fade = t ** 0.7
        for x in range(w):
            d = abs(x - w / 2) / (w / 2)
            core = max(0.0, 1 - d * d)
            a = int(255 * min(1.0, core * 1.3) * (0.3 + 0.7 * fade))
            col = _lerp((255, 120, 50), (255, 240, 200), core ** 2)
            s.set_at((x, y), (*col, min(255, a)))
    return s


@lru_cache(maxsize=4)
def mine(r):
    size = r * 2 + 12
    big = pygame.Surface((size * SS, size * SS), pygame.SRCALPHA)
    c = size * SS // 2
    rr = r * SS
    for i in range(8):
        a = i * math.tau / 8
        tip = (c + math.cos(a) * (rr + 5 * SS), c + math.sin(a) * (rr + 5 * SS))
        l = (c + math.cos(a - 0.22) * rr * 0.9, c + math.sin(a - 0.22) * rr * 0.9)
        rgt = (c + math.cos(a + 0.22) * rr * 0.9, c + math.sin(a + 0.22) * rr * 0.9)
        pygame.draw.polygon(big, (120, 128, 140), [l, tip, rgt])
    pygame.draw.circle(big, (46, 50, 60), (c, c), rr)
    pygame.draw.circle(big, (80, 86, 98), (c - rr // 3, c - rr // 3), rr // 2)
    pygame.draw.circle(big, (46, 50, 60), (c - rr // 6, c - rr // 6), rr // 2)
    pygame.draw.circle(big, (20, 22, 28), (c, c), rr, 2 * SS)
    return _aa(big, size, size)


@lru_cache(maxsize=8)
def cell(kind, r=15):
    color = {"shield": SHIELD_COLOR, "overdrive": OVERDRIVE_COLOR, "slow": SLOW_COLOR}[kind]
    size = r * 2 + 4
    big = pygame.Surface((size * SS, size * SS), pygame.SRCALPHA)
    c = size * SS // 2
    rr = r * SS
    hexpts = [(c + math.cos(math.pi / 6 + i * math.pi / 3) * rr, c + math.sin(math.pi / 6 + i * math.pi / 3) * rr) for i in range(6)]
    pygame.draw.polygon(big, (20, 26, 38), hexpts)
    pygame.draw.polygon(big, color, hexpts, 2 * SS)
    g = rr * 0.5
    white = (240, 246, 255)
    if kind == "shield":
        pygame.draw.polygon(big, white, [(c - g, c - g * 0.8), (c + g, c - g * 0.8), (c + g, c), (c, c + g * 1.1), (c - g, c)])
        pygame.draw.polygon(big, color, [(c - g * 0.55, c - g * 0.45), (c + g * 0.55, c - g * 0.45), (c + g * 0.55, c - g * 0.05), (c, c + g * 0.6), (c - g * 0.55, c - g * 0.05)])
    elif kind == "overdrive":
        for off in (-g * 0.55, g * 0.35):
            pygame.draw.polygon(big, white, [(c + off - g * 0.35, c - g), (c + off + g * 0.45, c), (c + off - g * 0.35, c + g), (c + off - g * 0.05, c)])
    else:
        pygame.draw.polygon(big, white, [(c - g * 0.8, c - g), (c + g * 0.8, c - g), (c, c)])
        pygame.draw.polygon(big, white, [(c - g * 0.8, c + g), (c + g * 0.8, c + g), (c, c)])
    return _aa(big, size, size)


# ---------------------------------------------------------------- ship

@lru_cache(maxsize=4)
def ship(tint="normal"):
    w, h = PLAYER_W, PLAYER_H
    S = 4
    big = pygame.Surface((w * S, h * S), pygame.SRCALPHA)

    def P(pts):
        return [(x * S, y * S) for x, y in pts]

    hull_top = (206, 214, 226) if tint == "normal" else (255, 170, 160)
    hull_low = (104, 114, 132) if tint == "normal" else (170, 90, 90)
    outline = (30, 36, 48)
    hull = [(1, 15), (8, 9), (22, 6), (40, 7), (52, 11), (55, 14), (50, 18), (36, 21), (10, 21), (3, 19)]
    pygame.draw.polygon(big, hull_top, P(hull))
    pygame.draw.polygon(big, hull_low, P([(2, 15), (55, 14), (50, 18), (36, 21), (10, 21), (3, 19)]))
    pygame.draw.polygon(big, (60, 70, 86), P([(10, 21), (36, 21), (33, 24), (13, 24)]))
    pygame.draw.polygon(big, (24, 30, 42), P([(26, 7), (35, 2), (45, 7), (42, 10), (28, 10)]))
    pygame.draw.polygon(big, (90, 190, 240), P([(28, 7), (35, 3.5), (43, 7.4), (40, 9), (29, 9)]))
    pygame.draw.polygon(big, (210, 245, 255), P([(31, 6), (35, 4.4), (37, 5.2), (33, 6.8)]))
    pygame.draw.line(big, ACCENT, (8 * S, 13 * S), (48 * S, 12 * S), 2 * S)
    pygame.draw.rect(big, (40, 46, 58), (0, 11 * S, 5 * S, 8 * S))
    pygame.draw.rect(big, (70, 78, 92), (0, 12 * S, 2 * S, 6 * S))
    pygame.draw.polygon(big, outline, P(hull), S)
    return _aa(big, w, h)


@lru_cache(maxsize=256)
def _glow(radius, color, alpha):
    """Additive radial glow; RGB is pre-scaled because BLEND_ADD ignores alpha."""
    g = pygame.Surface((radius * 2, radius * 2))
    g.fill((0, 0, 0))
    steps = max(4, radius // 3)
    for i in range(steps, 0, -1):
        k = (1 - i / steps) ** 1.6 * (alpha / 255) * 0.9 + 0.02 * (alpha / 255)
        pygame.draw.circle(g, tuple(min(255, int(ch * k)) for ch in color), (radius, radius), int(radius * i / steps))
    return g


def draw_glow(surface, center, radius, color, alpha):
    radius = max(2, int(radius))
    alpha = max(0, min(255, int(alpha) // 8 * 8))
    surface.blit(_glow(radius, tuple(color), alpha), (center[0] - radius, center[1] - radius), special_flags=pygame.BLEND_RGB_ADD)
