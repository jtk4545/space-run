# Space Run

A side-scrolling lunar freight runner with a 10-sector **Campaign** and an **Endless** mode.

## Run

```bash
./start.sh
```

## Controls

| Input | Action |
|---|---|
| SPACE / W / Up | Jump; press again in the air for the second thruster |
| Release jump early | Shorter hop |
| ESC | Pause |
| F11 | Toggle fullscreen |
| Arrows + Enter | Menus |

## Level design

Levels are built from physics-aware beats in `game/levels.py` (crates, walls, spike strips,
catwalks, hover mines, plasma vents). Every campaign level and sampled endless runs are
checked by a bot that plays them with the real physics, handicapped so a pass means
"comfortably clearable", not frame-perfect:

```bash
python tools/validate_levels.py        # all levels + endless samples
python tools/validate_levels.py 3 4    # specific sectors
```

Run it after editing any level.

## Layout

```
run.py / main.py     entry + orchestrator
constants.py         physics, palette, tuning (1280x720 logical)
game/physics.py      deterministic player step (shared with the validator)
game/world.py        entities and their collision boxes
game/levels.py       beats, campaign scripts, endless pool
game/art.py          procedural art drawn at exact gameplay sizes
game/core.py         gameplay loop, HUD, pause/clear screens
ui/menu.py           main menu, campaign select, how to play
tools/               level validator
```
