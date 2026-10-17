"""Main menu, campaign select, how-to-play — drawn over a live scene."""

import math
import pygame
from constants import WIDTH, HEIGHT, GROUND_Y, ACCENT, TEXT, TEXT_DIM, GOLD, WARN
from game import art
from game.particles import ParticleSystem
from game.ship import Player
from game.levels import CAMPAIGN_LEVELS
from game.modes import load_progress, save_progress
from utils import text, panel, star_icon

ACTION_QUIT = "quit"
ACTION_ENDLESS = "endless"
ACTION_CAMPAIGN = "campaign"


class Scene:
    """Slow-scrolling backdrop with the ship idling."""

    def __init__(self):
        self.backdrop = art.Backdrop()
        self.particles = ParticleSystem()
        self.ship = Player(self.particles)
        self.scroll = 0.0
        self.t = 0.0

    def draw(self, surface, dt):
        self.t += dt
        self.scroll += 90 * dt
        self.backdrop.draw(surface, self.scroll)
        self.ship.update(dt, (), (), False, False)
        self.particles.update(dt, 90 * dt)
        self.ship.draw(surface)
        self.particles.draw(surface)


def _nav(e, idx, n, audio, horizontal=False):
    prev_keys = (pygame.K_LEFT, pygame.K_a) if horizontal else (pygame.K_UP, pygame.K_w)
    next_keys = (pygame.K_RIGHT, pygame.K_d) if horizontal else (pygame.K_DOWN, pygame.K_s)
    if e.key in prev_keys:
        audio.play("ui")
        return (idx - 1) % n
    if e.key in next_keys:
        audio.play("ui")
        return (idx + 1) % n
    return idx


def _common(e, display):
    if e.type == pygame.VIDEORESIZE:
        display.handle_resize()
    if e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
        display.toggle_fullscreen()


def _option_list(c, options, idx, x, y, w=320):
    for i, label in enumerate(options):
        r = pygame.Rect(x, y + i * 54, w, 44)
        sel = i == idx
        if sel:
            bar = pygame.Surface(r.size, pygame.SRCALPHA)
            pygame.draw.rect(bar, (60, 140, 200, 60), bar.get_rect(), border_radius=8)
            c.blit(bar, r.topleft)
            pygame.draw.rect(c, ACCENT, (r.x, r.y + 8, 3, r.h - 16), border_radius=2)
        text(c, label, 24, TEXT if sel else TEXT_DIM, (r.x + 20, r.centery), anchor="midleft", bold=sel)


def run_main_menu(display, audio):
    scene = Scene()
    progress = load_progress()
    audio.set_muted(progress.get("muted", False))
    idx = 0

    while True:
        dt = display.tick()
        options = ["Campaign", "Endless", "How to Play", f"Sound: {'Off' if audio.muted else 'On'}", "Quit"]
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return ACTION_QUIT, None
            _common(e, display)
            if e.type != pygame.KEYDOWN:
                continue
            idx = _nav(e, idx, len(options), audio)
            if e.key == pygame.K_ESCAPE:
                return ACTION_QUIT, None
            if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                audio.play("select")
                if idx == 0:
                    level = run_level_select(display, audio, scene)
                    progress = load_progress()
                    if level is not None:
                        return ACTION_CAMPAIGN, level
                elif idx == 1:
                    return ACTION_ENDLESS, None
                elif idx == 2:
                    run_howto(display, audio, scene)
                elif idx == 3:
                    audio.set_muted(not audio.muted)
                    progress["muted"] = audio.muted
                    save_progress(progress)
                else:
                    return ACTION_QUIT, None

        c = display.canvas
        scene.draw(c, dt)
        shade = pygame.Surface((560, HEIGHT), pygame.SRCALPHA)
        for x in range(560):
            pygame.draw.line(shade, (4, 6, 12, int(200 * (1 - x / 560) ** 1.4)), (x, 0), (x, HEIGHT))
        c.blit(shade, (0, 0))

        text(c, "SPACE RUN", 76, TEXT, (80, 110), bold=True, spacing=6)
        pygame.draw.rect(c, ACCENT, (84, 206, 60, 3))
        text(c, "Lunar freight runner", 20, TEXT_DIM, (84, 222))
        _option_list(c, options, idx, 70, 300)

        unlocked = progress.get("unlocked", 1)
        stars = sum(int(v) for v in progress.get("stars", {}).values())
        info = f"Campaign {min(unlocked, len(CAMPAIGN_LEVELS))}/{len(CAMPAIGN_LEVELS)}  ·  {stars}/{3 * len(CAMPAIGN_LEVELS)} stars"
        if progress.get("endless_high"):
            info += f"  ·  Endless best {progress['endless_high']}"
        text(c, info, 15, TEXT_DIM, (84, HEIGHT - 70))
        text(c, "Arrows select   Enter confirm   F11 fullscreen", 14, (100, 110, 128), (84, HEIGHT - 44), shadow=False)
        display.present()


def run_level_select(display, audio, scene):
    progress = load_progress()
    unlocked = progress.get("unlocked", 1)
    stars = progress.get("stars", {})
    cols, n = 5, len(CAMPAIGN_LEVELS)
    idx = min(unlocked, n) - 1

    while True:
        dt = display.tick()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return None
            _common(e, display)
            if e.type != pygame.KEYDOWN:
                continue
            if e.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                audio.play("ui")
                return None
            if e.key in (pygame.K_LEFT, pygame.K_a):
                idx = (idx - 1) % n
                audio.play("ui")
            elif e.key in (pygame.K_RIGHT, pygame.K_d):
                idx = (idx + 1) % n
                audio.play("ui")
            elif e.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                idx = (idx + cols) % n
                audio.play("ui")
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                if idx + 1 <= unlocked:
                    audio.play("select")
                    return idx
                audio.play("hit")

        c = display.canvas
        scene.draw(c, dt)
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((4, 6, 12, 150))
        c.blit(veil, (0, 0))
        text(c, "CAMPAIGN", 44, TEXT, (WIDTH // 2, 56), anchor="midtop", bold=True, spacing=5)
        text(c, "Ten sectors. Each one teaches one new skill.", 18, TEXT_DIM, (WIDTH // 2, 112), anchor="midtop")

        cw, ch, gap = 208, 150, 18
        x0 = (WIDTH - (cols * cw + (cols - 1) * gap)) // 2
        for i, lvl in enumerate(CAMPAIGN_LEVELS):
            r = pygame.Rect(x0 + (i % cols) * (cw + gap), 170 + (i // cols) * (ch + gap), cw, ch)
            locked = lvl["id"] > unlocked
            sel = i == idx
            border = ACCENT if sel else (60, 72, 92)
            panel(c, r, alpha=215 if sel else 175, border=border, radius=12)
            if sel:
                pygame.draw.rect(c, ACCENT, r, 2, border_radius=12)
            text(c, f"{lvl['id']:02d}", 34, (TEXT if not locked else (80, 90, 106)), (r.x + 18, r.y + 14), bold=True)
            if locked:
                lx, ly = r.right - 38, r.y + 22
                pygame.draw.rect(c, (80, 90, 106), (lx, ly + 10, 20, 15), border_radius=3)
                pygame.draw.arc(c, (80, 90, 106), (lx + 3, ly, 14, 20), 0, math.pi, 3)
                text(c, "Locked", 16, (90, 100, 116), (r.x + 18, r.y + 70))
            else:
                text(c, lvl["name"], 19, TEXT, (r.x + 18, r.y + 66), bold=True)
                got = int(stars.get(str(lvl["id"]), 0))
                for s in range(3):
                    star_icon(c, (r.x + 28 + s * 26, r.bottom - 28), 10, s < got, GOLD)

        lvl = CAMPAIGN_LEVELS[idx]
        locked = lvl["id"] > unlocked
        msg = "Clear the previous sector to unlock." if locked else lvl["subtitle"]
        text(c, msg, 20, WARN if locked else TEXT, (WIDTH // 2, HEIGHT - 120), anchor="midtop")
        text(c, "Arrows choose   Enter launch   Esc back", 14, (100, 110, 128), (WIDTH // 2, HEIGHT - 50), anchor="midtop", shadow=False)
        display.present()


def run_howto(display, audio, scene):
    rows = [
        ("crate", "Cargo crate", "Land on the lit top. The striped sides will hurt."),
        ("spikes", "Spike strip", "Clear the whole strip. Wider strips need a double jump."),
        ("catwalk", "Catwalk", "A raised deck you can land on, over spikes."),
        ("mine", "Hover mine", "Stay low and pass under it. Tap a short hop to clear spikes below one."),
        ("vent", "Plasma vent", "An orange glow means it's about to erupt. Jump the column."),
    ]
    cells = [("shield", "Shield", "Absorbs one hit."),
             ("overdrive", "Overdrive", "Time runs faster. Score counts double."),
             ("slow", "Slow Time", "Everything slows down, including you.")]

    while True:
        dt = display.tick()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            _common(e, display)
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE, pygame.K_BACKSPACE):
                audio.play("ui")
                return

        c = display.canvas
        scene.draw(c, dt)
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((4, 6, 12, 170))
        c.blit(veil, (0, 0))
        text(c, "HOW TO PLAY", 40, TEXT, (WIDTH // 2, 36), anchor="midtop", bold=True, spacing=5)
        text(c, "SPACE / W / Up: jump      Press again in the air: second thruster      Release early: shorter hop",
             15, TEXT_DIM, (WIDTH // 2, 96), anchor="midtop")

        y = 140
        for kind, name, desc in rows:
            box = pygame.Rect(150, y, 90, 58)
            if kind == "crate":
                c.blit(art.crate(56, 48), (box.centerx - 28, box.bottom - 48))
            elif kind == "spikes":
                c.blit(art.spikes(72, 30), (box.centerx - 36, box.bottom - 30))
            elif kind == "catwalk":
                c.blit(art.catwalk_deck(80), (box.centerx - 40, box.y + 22))
            elif kind == "mine":
                img = art.mine(15)
                c.blit(img, img.get_rect(center=box.center))
            else:
                col = art.plasma_column(28, 50)
                c.blit(col, (box.centerx - 14, box.bottom - 54))
                c.blit(art.vent_base(40), (box.centerx - 20, box.bottom - 8))
            text(c, name, 20, TEXT, (270, y + 6), bold=True)
            text(c, desc, 17, TEXT_DIM, (270, y + 32))
            y += 72

        y += 6
        text(c, "POWER CELLS", 13, ACCENT, (150, y), bold=True, spacing=3)
        x = 150
        for kind, name, desc in cells:
            img = art.cell(kind)
            c.blit(img, (x, y + 28))
            text(c, name, 18, TEXT, (x + 44, y + 26), bold=True)
            text(c, desc, 14, TEXT_DIM, (x + 44, y + 50))
            x += 340
        text(c, "Esc pause  ·  Every level has been verified clearable", 14, (100, 110, 128), (WIDTH // 2, HEIGHT - 40), anchor="midtop", shadow=False)
        display.present()
