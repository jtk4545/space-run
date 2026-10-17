"""Campaign / Endless controllers and progress persistence."""

import json
import os
import random
from constants import PROGRESS_FILE, HIGH_SCORE_FILE, ENDLESS_SPEED_START, ENDLESS_SPEED_MAX, WIDTH
from game.levels import (
    CAMPAIGN_LEVELS, ENDLESS_POOL, ENDLESS_WAVES, LEAD_IN, place, level_beats, R,
)


def load_progress():
    data = {"unlocked": 1, "stars": {}, "endless_high": 0, "muted": False}
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE) as f:
                data.update(json.load(f))
        except (json.JSONDecodeError, OSError):
            pass
    if not data["endless_high"] and os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE) as f:
                data["endless_high"] = json.load(f).get("high_score", 0)
        except (json.JSONDecodeError, OSError):
            pass
    return data


def save_progress(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def record_clear(progress, level_id, stars):
    progress["unlocked"] = max(progress.get("unlocked", 1), min(level_id + 1, len(CAMPAIGN_LEVELS)))
    key = str(level_id)
    if stars > int(progress.setdefault("stars", {}).get(key, 0)):
        progress["stars"][key] = stars
    save_progress(progress)


def stars_for_hits(hits):
    return 3 if hits == 0 else 2 if hits == 1 else 1


class CampaignController:
    def __init__(self, level_index):
        self.level_index = level_index
        self.level = CAMPAIGN_LEVELS[level_index]
        self.end_scroll = 0.0
        self.hits = 0

    @property
    def speed(self):
        return float(self.level["speed"])

    def setup(self, world):
        world.clear()
        end_x, _ = place(world, level_beats(self.level), LEAD_IN)
        self.end_scroll = end_x - WIDTH * 0.5

    def progress(self, world):
        return min(1.0, world.scroll / max(1.0, self.end_scroll))

    def update(self, world):
        return world.scroll >= self.end_scroll


class EndlessController:
    """Sequences beats from the endless pool; each wave tightens rests and raises speed."""

    BEATS_PER_WAVE = 8

    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.wave = 0
        self.beats_in_wave = 0
        self.cursor = 0.0
        self.since_cell = 0

    @property
    def speed(self):
        t = min(1.0, self.wave / (len(ENDLESS_WAVES) + 2))
        return ENDLESS_SPEED_START + (ENDLESS_SPEED_MAX - ENDLESS_SPEED_START) * t

    def setup(self, world):
        world.clear()
        self.wave = 0
        self.beats_in_wave = 0
        self.cursor = LEAD_IN
        self.since_cell = 0
        self._fill(world)

    def _next_beats(self):
        tags, rmin, rmax = ENDLESS_WAVES[min(self.wave, len(ENDLESS_WAVES) - 1)]
        tag = self.rng.choice(tags)
        beat = self.rng.choice(ENDLESS_POOL[tag])()
        out = [beat, R(self.rng.randint(rmin, rmax))]
        self.since_cell += 1
        if tag == "hard" and self.since_cell >= 6:
            from game.levels import cell
            out += [cell(self.rng.choice(["shield", "slow", "overdrive"])), R(rmin)]
            self.since_cell = 0
        self.beats_in_wave += 1
        if self.beats_in_wave >= self.BEATS_PER_WAVE:
            self.beats_in_wave = 0
            self.wave += 1
        return out

    def _fill(self, world):
        while self.cursor - world.scroll < WIDTH * 2.2:
            screen_x = self.cursor - world.scroll
            end_x, _ = place(world, self._next_beats(), screen_x)
            self.cursor = end_x + world.scroll

    def progress(self, world):
        return None

    def update(self, world):
        self._fill(world)
        return False
