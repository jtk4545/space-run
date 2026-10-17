"""Window management and letterboxed scaling to logical resolution."""

import pygame
from constants import WIDTH, HEIGHT, FPS


class Display:
    def __init__(self):
        self.fullscreen = False
        self.window = None
        self.canvas = pygame.Surface((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self._scale = 1.0
        self._offset = (0, 0)
        self.set_windowed()

    def set_windowed(self):
        self.fullscreen = False
        # Fit comfortably on most screens
        flags = pygame.RESIZABLE
        self.window = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        pygame.display.set_caption("Space Run")
        self._recompute_scale()

    def set_fullscreen(self):
        self.fullscreen = True
        info = pygame.display.Info()
        self.window = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
        self._recompute_scale()

    def toggle_fullscreen(self):
        if self.fullscreen:
            self.set_windowed()
        else:
            self.set_fullscreen()

    def _recompute_scale(self):
        ww, wh = self.window.get_size()
        self._scale = min(ww / WIDTH, wh / HEIGHT)
        sw, sh = int(WIDTH * self._scale), int(HEIGHT * self._scale)
        self._offset = ((ww - sw) // 2, (wh - sh) // 2)

    def handle_resize(self):
        if not self.fullscreen:
            self._recompute_scale()

    def tick(self):
        return self.clock.tick(FPS) / 1000.0

    def present(self):
        self.window.fill((0, 0, 0))
        ww, wh = self.window.get_size()
        sw, sh = max(1, int(WIDTH * self._scale)), max(1, int(HEIGHT * self._scale))
        scaled = pygame.transform.smoothscale(self.canvas, (sw, sh))
        self.window.blit(scaled, self._offset)
        pygame.display.flip()

    def window_to_canvas(self, pos):
        x, y = pos
        ox, oy = self._offset
        if self._scale <= 0:
            return (0, 0)
        return ((x - ox) / self._scale, (y - oy) / self._scale)
