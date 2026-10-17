"""Shared gameplay loop for Campaign and Endless."""

import math
import pygame
from constants import (
    WIDTH, HEIGHT, PLAYER_X, PLAYER_W, STARTING_LIVES,
    SHIELD_DURATION, OVERDRIVE_DURATION, OVERDRIVE_TIME_SCALE, SLOW_DURATION, SLOW_TIME_SCALE,
    HIT_IFRAMES, HIT_STOP, ACCENT, TEXT, TEXT_DIM, GOLD, WARN,
    SHIELD_COLOR, OVERDRIVE_COLOR, SLOW_COLOR,
)
from game import art
from game.physics import EV_HIT
from game.ship import Player
from game.world import World
from game.particles import ParticleSystem
from game.levels import CAMPAIGN_LEVELS
from game.modes import (
    CampaignController, EndlessController, load_progress, save_progress, record_clear, stars_for_hits,
)
from utils import ScreenShake, text, panel, dim, star_icon

RESULT_QUIT = "quit"
RESULT_MENU = "menu"
RESULT_RESTART = "restart"
RESULT_NEXT = "next"

JUMP_KEYS = (pygame.K_SPACE, pygame.K_UP, pygame.K_w)
BUFF_INFO = {
    "shield": ("SHIELD", SHIELD_COLOR, SHIELD_DURATION),
    "overdrive": ("OVERDRIVE  x2", OVERDRIVE_COLOR, OVERDRIVE_DURATION),
    "slow": ("SLOW TIME", SLOW_COLOR, SLOW_DURATION),
}


_ICONS = {}


def _life_icon(alive):
    if alive not in _ICONS:
        img = pygame.transform.smoothscale(art.ship(), (30, 14))
        if not alive:
            img = img.copy()
            img.fill((60, 68, 82, 120), special_flags=pygame.BLEND_RGBA_MULT)
        _ICONS[alive] = img
    return _ICONS[alive]


class Toast:
    def __init__(self, msg, color, life=1.4):
        self.msg, self.color, self.life, self.max_life = msg, color, life, life

    def update(self, dt):
        self.life -= dt
        return self.life > 0


class GameCore:
    def __init__(self, display, audio, mode="endless", level_index=0):
        self.display = display
        self.audio = audio
        self.mode = mode
        self.level_index = level_index
        self.canvas = display.canvas
        self.particles = ParticleSystem()
        self.world = World()
        self.player = Player(self.particles)
        self.shake = ScreenShake()
        self.toasts = []
        self.progress_data = load_progress()

        self.score = 0
        self.lives = STARTING_LIVES
        self.hits = 0
        self.iframes = 0.0
        self.hit_stop = 0.0
        self.buffs = {}
        self.paused = False
        self.game_over = False
        self.cleared = False
        self.outro = 0.0
        self.intro = 1.6
        self.flash = 0.0

        self.controller = CampaignController(level_index) if mode == "campaign" else EndlessController()
        self.controller.setup(self.world)

    # ------------------------------------------------------------ gameplay

    @property
    def time_scale(self):
        s = 1.0
        if "slow" in self.buffs:
            s *= SLOW_TIME_SCALE
        if "overdrive" in self.buffs:
            s *= OVERDRIVE_TIME_SCALE
        return s

    def _toast(self, msg, color):
        self.toasts = [t for t in self.toasts if t.msg != msg][-2:] + [Toast(msg, color)]

    def _take_hit(self):
        if "shield" in self.buffs:
            del self.buffs["shield"]
            self.iframes = HIT_IFRAMES * 0.6
            self.shake.start(5, 0.15)
            self.audio.play("hit")
            self._toast("Shield absorbed the hit", SHIELD_COLOR)
            return
        self.lives -= 1
        self.hits += 1
        self.iframes = HIT_IFRAMES
        self.hit_stop = HIT_STOP
        self.flash = 0.25
        self.player.hurt_flash = 0.35
        self.shake.start(9, 0.3)
        self.audio.play("hit")
        cx, cy = self.player.rect.center
        self.particles.emit(cx, cy, "debris", 10)
        if self.lives <= 0:
            self.game_over = True
            self.particles.emit(cx, cy, "spark", 40)

    def _collect(self):
        r = self.player.rect.inflate(-16, -8)
        keep = []
        for c in self.world.cells:
            x0, y0, x1, y1 = c.box()
            if r.right > x0 and r.left < x1 and r.bottom > y0 and r.top < y1:
                label, color, dur = BUFF_INFO[c.kind]
                self.buffs[c.kind] = dur
                self.particles.emit(x0 + 18, y0 + 18, "pickup", 16, color=color)
                self.audio.play("collect")
                self._toast(label.split()[0].title() if c.kind != "slow" else "Slow Time", color)
            else:
                keep.append(c)
        self.world.cells = keep

    def _step(self, dt, pressed, held):
        if self.hit_stop > 0:
            self.hit_stop -= dt
            return
        sim = dt * self.time_scale
        for k in list(self.buffs):
            self.buffs[k] -= dt
            if self.buffs[k] <= 0:
                del self.buffs[k]
        self.iframes = max(0.0, self.iframes - sim)

        before = self.world.scroll
        self.world.update(sim, self.controller.speed)
        solids, hazards = self.world.collision_near()
        ev = self.player.update(sim, solids, hazards, pressed, held)
        if ev & 1:
            self.audio.play("jump")
        if ev & 2:
            self.audio.play("double")
        if ev & EV_HIT and self.iframes <= 0 and not self.game_over:
            self._take_hit()
        self._collect()
        passed = self.world.count_passed()
        if passed:
            self.score += passed * (2 if "overdrive" in self.buffs else 1)
        self.particles.update(sim, self.world.scroll - before)

        if self.controller.update(self.world) and not self.cleared:
            self.cleared = True
            self.outro = 1.8
            self.audio.play("clear")

    # ------------------------------------------------------------ drawing

    def _draw_world(self):
        c = self.canvas
        self.world.draw(c)
        if not self.game_over:
            self.player.draw(c, blink=self.iframes > 0, shield="shield" in self.buffs)
        self.particles.draw(c)
        if "slow" in self.buffs:
            tint = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            tint.fill((90, 70, 200, 26))
            c.blit(tint, (0, 0))
        if self.flash > 0:
            f = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            f.fill((255, 60, 40, int(90 * self.flash / 0.25)))
            c.blit(f, (0, 0))

    def _draw_hud(self):
        c = self.canvas
        text(c, "SCORE", 13, TEXT_DIM, (28, 20), bold=True, spacing=2)
        text(c, str(self.score), 34, TEXT, (26, 36), bold=True)
        for i in range(STARTING_LIVES):
            icon = _life_icon(i < self.lives)
            c.blit(icon, (28 + i * 36, 82))

        if self.mode == "campaign":
            lvl = self.controller.level
            text(c, f"SECTOR {lvl['id']:02d}  ·  {lvl['name'].upper()}", 13, TEXT_DIM, (WIDTH // 2, 20), anchor="midtop", bold=True, spacing=2)
            bar = pygame.Rect(WIDTH // 2 - 220, 44, 440, 6)
            pygame.draw.rect(c, (40, 48, 62), bar, border_radius=3)
            p = self.controller.progress(self.world)
            pygame.draw.rect(c, ACCENT, (bar.x, bar.y, int(bar.w * p), bar.h), border_radius=3)
            pygame.draw.circle(c, (230, 245, 255), (bar.x + int(bar.w * p), bar.centery), 6)
        else:
            best = max(self.progress_data.get("endless_high", 0), self.score)
            text(c, f"WAVE {self.controller.wave + 1}", 13, ACCENT, (WIDTH // 2, 20), anchor="midtop", bold=True, spacing=2)
            text(c, f"BEST {best}", 13, TEXT_DIM, (WIDTH // 2, 40), anchor="midtop", bold=True, spacing=2)

        y = 22
        for kind, remaining in self.buffs.items():
            label, color, dur = BUFF_INFO[kind]
            r = pygame.Rect(WIDTH - 236, y, 210, 30)
            panel(c, r, alpha=170, border=color, radius=8)
            text(c, label, 13, color, (r.x + 12, r.y + 8), bold=True, spacing=1)
            pygame.draw.rect(c, color, (r.x + 8, r.bottom - 6, int((r.w - 16) * remaining / dur), 2))
            y += 38

        ty = 140
        for t in self.toasts:
            k = min(1.0, t.life / 0.3, (t.max_life - t.life) / 0.12 + 0.01)
            text(c, t.msg, 22, t.color, (WIDTH // 2, ty), anchor="midtop", bold=True, alpha=int(255 * max(0, min(1, k))))
            ty += 32

        if self.intro > 0 and self.mode == "campaign":
            lvl = self.controller.level
            k = min(1.0, self.intro / 0.4)
            band = pygame.Surface((WIDTH, 150), pygame.SRCALPHA)
            band.fill((4, 6, 12, int(170 * k)))
            c.blit(band, (0, HEIGHT // 2 - 125))
            a = int(255 * k)
            text(c, f"SECTOR {lvl['id']:02d}", 15, ACCENT, (WIDTH // 2, HEIGHT // 2 - 108), anchor="midtop", bold=True, spacing=4, alpha=a)
            text(c, lvl["name"], 52, TEXT, (WIDTH // 2, HEIGHT // 2 - 86), anchor="midtop", bold=True, alpha=a)
            text(c, lvl["subtitle"], 20, TEXT_DIM, (WIDTH // 2, HEIGHT // 2 - 20), anchor="midtop", alpha=a)
        elif self.intro > 0:
            text(c, "ENDLESS", 15, ACCENT, (WIDTH // 2, HEIGHT // 2 - 60), anchor="midtop", bold=True, spacing=4, alpha=int(255 * min(1, self.intro / 0.4)))

        if self.cleared:
            text(c, "SECTOR CLEAR", 44, GOLD, (WIDTH // 2, HEIGHT // 3), anchor="midtop", bold=True, spacing=3)

    def _present(self):
        ox, oy = self.shake.offset
        if ox or oy:
            frame = self.canvas.copy()
            self.canvas.fill((0, 0, 0))
            self.canvas.blit(frame, (ox, oy))
        self.display.present()

    # ------------------------------------------------------------ menus in-run

    def _menu(self, title, subtitle, options, extra=None):
        idx = 0
        backdrop = self.canvas.copy()
        while True:
            self.display.tick()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return RESULT_QUIT
                if e.type == pygame.VIDEORESIZE:
                    self.display.handle_resize()
                if e.type == pygame.KEYDOWN:
                    if e.key in (pygame.K_UP, pygame.K_w):
                        idx = (idx - 1) % len(options)
                        self.audio.play("ui")
                    elif e.key in (pygame.K_DOWN, pygame.K_s):
                        idx = (idx + 1) % len(options)
                        self.audio.play("ui")
                    elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.audio.play("select")
                        return options[idx][1]
                    elif e.key == pygame.K_r:
                        return RESULT_RESTART
                    elif e.key == pygame.K_ESCAPE:
                        return options[0][1] if title == "Paused" else RESULT_MENU
                    elif e.key == pygame.K_F11:
                        self.display.toggle_fullscreen()

            c = self.canvas
            c.blit(backdrop, (0, 0))
            dim(c, 160)
            h = 210 + 52 * len(options) + (40 if extra else 0)
            box = panel(c, (WIDTH // 2 - 230, HEIGHT // 2 - h // 2, 460, h), alpha=225)
            text(c, title.upper(), 34, TEXT, (box.centerx, box.y + 34), anchor="midtop", bold=True, spacing=3)
            if subtitle:
                text(c, subtitle, 18, TEXT_DIM, (box.centerx, box.y + 84), anchor="midtop")
            y = box.y + 124
            if extra:
                extra(c, box.centerx, y)
                y += 48
            for i, (label, _) in enumerate(options):
                r = pygame.Rect(box.x + 40, y + i * 52, box.w - 80, 42)
                if i == idx:
                    pygame.draw.rect(c, (40, 70, 100), r, border_radius=8)
                    pygame.draw.rect(c, ACCENT, r, 1, border_radius=8)
                text(c, label, 22, TEXT if i == idx else TEXT_DIM, r.center, anchor="center", bold=i == idx, shadow=False)
            self.display.present()

    # ------------------------------------------------------------ main loop

    def run(self):
        while True:
            dt = min(1 / 30, self.display.tick())
            pressed = False
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return RESULT_QUIT
                if e.type == pygame.VIDEORESIZE:
                    self.display.handle_resize()
                if e.type == pygame.KEYDOWN:
                    if e.key in JUMP_KEYS:
                        pressed = True
                    elif e.key in (pygame.K_ESCAPE, pygame.K_p):
                        self.paused = True
                    elif e.key == pygame.K_F11:
                        self.display.toggle_fullscreen()
            keys = pygame.key.get_pressed()
            held = any(keys[k] for k in JUMP_KEYS)

            if self.paused:
                self._draw_world()
                self._draw_hud()
                r = self._menu("Paused", "", [("Resume", None), ("Restart", RESULT_RESTART), ("Main Menu", RESULT_MENU)])
                self.paused = False
                if r:
                    return r
                continue

            self.flash = max(0.0, self.flash - dt)
            self.shake.update(dt)
            self.toasts = [t for t in self.toasts if t.update(dt)]

            if self.intro > 0:
                self.intro -= dt
                self.player.update(0.0, (), (), False, False)
            elif self.game_over:
                self.outro += dt
                self.particles.update(dt)
                if self.outro > 1.0:
                    return self._game_over()
            elif self.cleared:
                self.outro -= dt
                self._step(dt, False, False)
                if self.outro <= 0:
                    return self._level_clear()
            else:
                self._step(dt, pressed, held)

            self._draw_world()
            self._draw_hud()
            self._present()

    def _game_over(self):
        sub = f"Score {self.score}"
        if self.mode == "endless":
            best = self.progress_data.get("endless_high", 0)
            if self.score > best:
                self.progress_data["endless_high"] = self.score
                save_progress(self.progress_data)
                sub = f"New best: {self.score}"
            else:
                sub = f"Score {self.score}   ·   Best {best}"
        else:
            p = int(self.controller.progress(self.world) * 100)
            sub = f"Reached {p}% of {self.controller.level['name']}"
        return self._menu("Ship Lost", sub, [("Retry", RESULT_RESTART), ("Main Menu", RESULT_MENU)])

    def _level_clear(self):
        stars = stars_for_hits(self.hits)
        record_clear(self.progress_data, self.controller.level["id"], stars)
        opts = [("Replay", RESULT_RESTART), ("Main Menu", RESULT_MENU)]
        if self.level_index < len(CAMPAIGN_LEVELS) - 1:
            opts.insert(0, ("Next Sector", RESULT_NEXT))
        hits = "Flawless" if self.hits == 0 else f"{self.hits} hit{'s' if self.hits > 1 else ''} taken"

        def draw_stars(c, cx, y):
            for i in range(3):
                star_icon(c, (cx - 44 + i * 44, y + 14), 16, i < stars, GOLD)

        return self._menu("Sector Clear", f"{hits}  ·  Score {self.score}", opts, extra=draw_stars)
