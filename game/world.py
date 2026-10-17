"""Scrolling world entities. Collision boxes sit slightly inside their visuals."""

import math
import random
import pygame
from constants import GROUND_Y, WIDTH, PLAYER_X, PLAYER_W, ACCENT
from game import art

NEAR_MIN = PLAYER_X - 80
NEAR_MAX = PLAYER_X + PLAYER_W + 80


class Entity:
    scoreable = True

    def __init__(self, x, w):
        self.x = float(x)
        self.w = float(w)
        self.passed = False

    def solids(self):
        return ()

    def hazards(self):
        return ()

    def update(self, dt):
        pass


class Crate(Entity):
    def __init__(self, x, w, h):
        super().__init__(x, w)
        self.h = h

    @property
    def top(self):
        return GROUND_Y - self.h

    def solids(self):
        return ((self.x, self.top, self.x + self.w),)

    def hazards(self):
        return ((self.x + 2, self.top + 12, self.x + self.w - 2, GROUND_Y),)

    def draw(self, s):
        s.blit(art.crate(int(self.w), int(self.h)), (round(self.x), round(self.top)))


class Spikes(Entity):
    def __init__(self, x, w, h=30):
        super().__init__(x, w)
        self.h = h

    def hazards(self):
        return ((self.x + 4, GROUND_Y - self.h + 8, self.x + self.w - 4, GROUND_Y),)

    def draw(self, s):
        s.blit(art.spikes(int(self.w), int(self.h)), (round(self.x), GROUND_Y - self.h))


class Catwalk(Entity):
    """Elevated one-way deck on struts. Struts are scenery."""

    def __init__(self, x, w, height):
        super().__init__(x, w)
        self.height = height

    @property
    def top(self):
        return GROUND_Y - self.height

    def solids(self):
        return ((self.x, self.top, self.x + self.w),)

    def draw_back(self, s):
        top = round(self.top)
        for lx in (self.x + 10, self.x + self.w - 16):
            pygame.draw.rect(s, (30, 35, 46), (round(lx), top + 12, 6, GROUND_Y - top - 12))
        if self.w > 70:
            a = (round(self.x + 13), top + 18)
            b = (round(self.x + self.w - 13), GROUND_Y - 6)
            pygame.draw.line(s, (36, 42, 54), a, b, 3)
            pygame.draw.line(s, (36, 42, 54), (a[0], b[1]), (b[0], a[1]), 3)

    def draw(self, s):
        s.blit(art.catwalk_deck(int(self.w)), (round(self.x), round(self.top)))


class Vent(Entity):
    """Plasma vent: idle -> charging (telegraph) -> erupting. Always jumpable."""

    WIDTH = 40
    COLUMN = 84
    CHARGE = 0.45

    def __init__(self, x, period=2.0, active=0.8, phase=0.0):
        super().__init__(x, self.WIDTH)
        self.period = period
        self.active_time = active
        self.t = phase * period

    def _phase(self):
        return self.t % self.period

    @property
    def erupting(self):
        return self._phase() < self.active_time

    @property
    def charging(self):
        return self._phase() >= self.period - self.CHARGE

    def update(self, dt):
        self.t += dt

    def hazards(self):
        if self.erupting:
            return ((self.x + 9, GROUND_Y - self.COLUMN + 10, self.x + self.w - 9, GROUND_Y),)
        return ()

    def draw(self, s):
        x = round(self.x)
        if self.erupting:
            col = art.plasma_column(self.WIDTH - 8, self.COLUMN)
            flick = 215 + int(40 * math.sin(self.t * 40))
            col.set_alpha(flick)
            s.blit(col, (x + 4, GROUND_Y - self.COLUMN))
            art.draw_glow(s, (x + self.WIDTH // 2, GROUND_Y - self.COLUMN // 2), 52, (255, 110, 40), 90)
            art.draw_glow(s, (x + self.WIDTH // 2, GROUND_Y - 6), 40, (255, 150, 70), 140)
        elif self.charging:
            k = (self._phase() - (self.period - self.CHARGE)) / self.CHARGE
            art.draw_glow(s, (x + self.WIDTH // 2, GROUND_Y - 4), int(18 + 20 * k), (255, 140, 60), int(40 + 120 * k))
        s.blit(art.vent_base(self.WIDTH), (x, GROUND_Y - 8))


class Mine(Entity):
    """Hovering proximity mine. Bobs a few px; hitbox smaller than art."""

    R = 15

    def __init__(self, x, height, bob=5.0, phase=0.0):
        super().__init__(x, self.R * 2)
        self.height = height
        self.bob = bob
        self.t = phase

    @property
    def cy(self):
        return GROUND_Y - self.height + math.sin(self.t * 2.4) * self.bob

    def update(self, dt):
        self.t += dt

    def hazards(self):
        cx, cy, r = self.x + self.R, self.cy, self.R - 3
        return ((cx - r, cy - r, cx + r, cy + r),)

    def draw(self, s):
        img = art.mine(self.R)
        cy = self.cy
        s.blit(img, (round(self.x + self.R - img.get_width() / 2), round(cy - img.get_height() / 2)))
        if int(self.t * 3) % 2 == 0:
            pygame.draw.circle(s, (255, 70, 60), (round(self.x + self.R), round(cy)), 3)
            art.draw_glow(s, (round(self.x + self.R), round(cy)), 14, (255, 60, 40), 90)


class Cell(Entity):
    scoreable = False

    def __init__(self, x, height, kind):
        super().__init__(x, 34)
        self.height = height
        self.kind = kind
        self.t = random.random() * 6

    @property
    def cy(self):
        return GROUND_Y - self.height + math.sin(self.t * 2.0) * 4

    def update(self, dt):
        self.t += dt

    def box(self):
        cx, cy = self.x + 17, self.cy
        return (cx - 18, cy - 18, cx + 18, cy + 18)

    def draw(self, s):
        img = art.cell(self.kind)
        cx, cy = self.x + 17, self.cy
        color = {"shield": (90, 170, 255), "overdrive": (255, 175, 70), "slow": (170, 150, 255)}[self.kind]
        art.draw_glow(s, (round(cx), round(cy)), 30, color, 50)
        s.blit(img, (round(cx - img.get_width() / 2), round(cy - img.get_height() / 2)))


class World:
    def __init__(self):
        self.entities = []
        self.cells = []
        self.scroll = 0.0
        self.backdrop = None

    def clear(self):
        self.entities.clear()
        self.cells.clear()
        self.scroll = 0.0

    def add(self, entity):
        (self.cells if isinstance(entity, Cell) else self.entities).append(entity)

    def update(self, dt, speed):
        dx = speed * dt
        self.scroll += dx
        alive = []
        for e in self.entities:
            e.x -= dx
            e.update(dt)
            if e.x + e.w > -60:
                alive.append(e)
        self.entities = alive
        cells = []
        for c in self.cells:
            c.x -= dx
            c.update(dt)
            if c.x + c.w > -60:
                cells.append(c)
        self.cells = cells

    def collision_near(self):
        solids, hazards = [], []
        for e in self.entities:
            if e.x > NEAR_MAX or e.x + e.w < NEAR_MIN:
                continue
            solids.extend(e.solids())
            hazards.extend(e.hazards())
        return solids, hazards

    def count_passed(self):
        n = 0
        for e in self.entities:
            if e.scoreable and not e.passed and e.x + e.w < PLAYER_X:
                e.passed = True
                n += 1
        return n

    def draw(self, s):
        if self.backdrop is None:
            self.backdrop = art.Backdrop()
        self.backdrop.draw(s, self.scroll)
        visible = [e for e in self.entities if -80 < e.x < WIDTH + 40]
        for e in visible:
            if isinstance(e, Catwalk):
                e.draw_back(s)
        for e in visible:
            e.draw(s)
        for c in self.cells:
            if -80 < c.x < WIDTH + 40:
                c.draw(s)
