"""Shared UI helpers: fonts, text, panels, screen shake."""

import random
import pygame
from functools import lru_cache

_FONT_CANDIDATES = {
    "regular": ["avenirnext", "helveticaneue", "helvetica", "segoeui", "arial"],
    "bold": ["avenirnextdemibold", "avenirnext", "helveticaneue", "helvetica", "segoeui", "arial"],
}


@lru_cache(maxsize=32)
def font(size, bold=False):
    for name in _FONT_CANDIDATES["bold" if bold else "regular"]:
        path = pygame.font.match_font(name, bold=bold)
        if path:
            f = pygame.font.Font(path, size)
            if bold and "demibold" not in name.lower() and "bold" not in path.lower():
                f.set_bold(True)
            return f
    return pygame.font.SysFont(None, size, bold=bold)


def text(surface, msg, size, color, pos, anchor="topleft", bold=False, shadow=True, spacing=0, alpha=255):
    f = font(size, bold)
    if spacing:
        glyphs = [f.render(ch, True, color) for ch in msg]
        w = sum(g.get_width() for g in glyphs) + spacing * (len(glyphs) - 1)
        img = pygame.Surface((max(1, w), f.get_height()), pygame.SRCALPHA)
        x = 0
        for g in glyphs:
            img.blit(g, (x, 0))
            x += g.get_width() + spacing
    else:
        img = f.render(msg, True, color)
    rect = img.get_rect(**{anchor: pos})
    if alpha < 255:
        img.set_alpha(alpha)
    if shadow:
        sh = img.copy()
        sh.fill((0, 0, 0, 160), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(sh, rect.move(0, 2))
    surface.blit(img, rect)
    return rect


def panel(surface, rect, alpha=200, border=(80, 96, 120), radius=10):
    rect = pygame.Rect(rect)
    p = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(p, (10, 14, 22, alpha), p.get_rect(), border_radius=radius)
    pygame.draw.rect(p, (*border, 200), p.get_rect(), 1, border_radius=radius)
    surface.blit(p, rect.topleft)
    return rect


def dim(surface, alpha=150):
    d = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    d.fill((4, 6, 12, alpha))
    surface.blit(d, (0, 0))


def star_icon(surface, center, r, filled, color):
    import math
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((center[0] + math.cos(a) * rr, center[1] + math.sin(a) * rr))
    if filled:
        pygame.draw.polygon(surface, color, pts)
    else:
        pygame.draw.polygon(surface, (70, 80, 96), pts, 2)


class ScreenShake:
    def __init__(self):
        self.time = 0.0
        self.intensity = 0.0
        self.offset = (0, 0)

    def start(self, intensity=5, duration=0.2):
        self.time = max(self.time, duration)
        self.intensity = max(self.intensity if self.time > 0 else 0, intensity)

    def update(self, dt):
        if self.time > 0:
            self.time -= dt
            i = max(1, int(self.intensity * min(1.0, self.time * 6)))
            self.offset = (random.randint(-i, i), random.randint(-i, i))
        else:
            self.intensity = 0
            self.offset = (0, 0)
        return self.offset
