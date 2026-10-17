#!/usr/bin/env python3
"""Prove every campaign level (and sampled endless runs) can be cleared without a hit.

The bot uses the game's own physics and world code, but with handicaps so a
passing level is comfortably humanly clearable, not frame-perfect:
  * hazards are grown by MARGIN px on every side
  * landing surfaces are trimmed by SOLID_TRIM px at each end
  * inputs only on every GRID-th frame, with a few fixed hold lengths
"""

import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from constants import SIM_DT, PLAYER_X  # noqa: E402
from game.world import World  # noqa: E402
from game.physics import Body, step, EV_HIT  # noqa: E402
from game.modes import CampaignController, EndlessController  # noqa: E402
from game.levels import CAMPAIGN_LEVELS  # noqa: E402

MARGIN = 4
SOLID_TRIM = 6
GRID = 3
HOLDS = (3, 8, 40)
BEAM = 1500


def snapshots(controller, max_frames=None):
    world = World()
    controller.setup(world)
    snaps = []
    while True:
        world.update(SIM_DT, controller.speed)
        done = controller.update(world)
        solids, hazards = world.collision_near()
        solids = [(x0 + SOLID_TRIM, t, x1 - SOLID_TRIM) for x0, t, x1 in solids]
        hazards = [(x0 - MARGIN, y0 - MARGIN, x1 + MARGIN, y1 + MARGIN) for x0, y0, x1, y1 in hazards]
        snaps.append((solids, hazards, world.scroll))
        if done or (max_frames and len(snaps) >= max_frames):
            return snaps


def entities_at(controller, frame):
    """Re-simulate to `frame` and list the entities near the player."""
    world = World()
    controller.setup(world)
    for _ in range(frame + 1):
        world.update(SIM_DT, controller.speed)
        controller.update(world)
    near = [e for e in world.entities if PLAYER_X - 150 < e.x < PLAYER_X + 250]
    return ", ".join(
        f"{type(e).__name__}(x={e.x - PLAYER_X:+.0f}{', h=%d' % e.h if hasattr(e, 'h') else ''}"
        f"{', height=%d' % e.height if hasattr(e, 'height') else ''}, w={e.w:.0f})"
        for e in near
    )


def _key(b, hold):
    return (round(b.y / 3), round(b.vy / 60), b.grounded, b.can_double, b.buffer > 0, hold)


def solve(snaps, beam=BEAM):
    """Returns (ok, fail_frame, peak_states). beam=None searches exhaustively."""
    frontier = {0: (Body(), 0)}
    peak = 1
    for f, (solids, hazards, _scroll) in enumerate(snaps):
        nxt = {}
        for body, hold in frontier.values():
            if hold > 0:
                options = ((False, True, hold - 1),)
            elif f % GRID == 0:
                options = ((False, False, 0),) + tuple((True, True, d - 1) for d in HOLDS)
            else:
                options = ((False, False, 0),)
            for pressed, held, nh in options:
                nb = body.copy()
                if step(nb, SIM_DT, solids, hazards, pressed, held) & EV_HIT:
                    continue
                k = _key(nb, nh)
                if k not in nxt:
                    nxt[k] = (nb, nh)
        if not nxt:
            return False, f, peak
        peak = max(peak, len(nxt))
        if beam and len(nxt) > beam:
            keys = sorted(nxt)
            stride = len(keys) / beam
            nxt = {keys[int(i * stride)]: nxt[keys[int(i * stride)]] for i in range(beam)}
        frontier = nxt
    return True, None, peak


def check(snaps):
    ok, fail, peak = solve(snaps)
    if not ok:
        ok, fail, peak = solve(snaps, beam=None)
    return ok, fail, peak


def validate_campaign(only=None):
    ok_all = True
    for idx, level in enumerate(CAMPAIGN_LEVELS):
        if only and level["id"] not in only:
            continue
        t0 = time.time()
        snaps = snapshots(CampaignController(idx))
        ok, fail, peak = check(snaps)
        secs = len(snaps) * SIM_DT
        if ok:
            print(f"  PASS  L{level['id']:>2} {level['name']:<15} {secs:5.1f}s  ({time.time() - t0:.1f}s)", flush=True)
        else:
            ok_all = False
            near = entities_at(CampaignController(idx), fail)
            print(f"  FAIL  L{level['id']:>2} {level['name']:<15} at t={fail * SIM_DT:.1f}s near: {near}", flush=True)
    return ok_all


def validate_endless(seeds, seconds):
    ok_all = True
    for seed in seeds:
        t0 = time.time()
        ctl = EndlessController(seed)
        snaps = snapshots(ctl, max_frames=int(seconds / SIM_DT))
        ok, fail, peak = check(snaps)
        if ok:
            print(f"  PASS  endless seed {seed:<3} {seconds}s, reached wave {ctl.wave + 1}  ({time.time() - t0:.1f}s)", flush=True)
        else:
            ok_all = False
            near = entities_at(EndlessController(seed), fail)
            print(f"  FAIL  endless seed {seed} at t={fail * SIM_DT:.1f}s near: {near}", flush=True)
    return ok_all


if __name__ == "__main__":
    only = {int(a) for a in sys.argv[1:] if a.isdigit()}
    print("Campaign:")
    c = validate_campaign(only or None)
    e = True
    if not only:
        print("Endless:")
        e = validate_endless(seeds=range(1, 6), seconds=90)
    sys.exit(0 if (c and e) else 1)
