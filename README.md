# Space Run

A side-scrolling lunar freight runner. Pilot a hovercraft through cargo yards, spike strips, catwalks, and plasma vents across a **10-sector Campaign**, or survive as long as you can in **Endless**.

Requires Python 3 and pygame.

## Play

```bash
./start.sh
```

That creates a virtualenv if needed, installs dependencies, and launches the game. Or:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Modes

| Mode | What it is |
|---|---|
| **Campaign** | Ten authored sectors. Each teaches one skill, then mixes them. Unlock the next sector by clearing the current one. Earn 1–3 stars from how cleanly you finish. |
| **Endless** | Designed hazard chunks in waves. Speed and density climb over time. Power cells appear after hard stretches. |
| **How to Play** | Controls and a primer for every hazard and power cell. |

Progress (unlocks, stars, Endless best, mute) is saved locally in `progress.json`.

## Controls

| Input | Action |
|---|---|
| SPACE / W / Up | Jump |
| Jump again in the air | Second thruster (double jump) |
| Release jump early | Shorter hop |
| ESC / P | Pause |
| F11 | Toggle fullscreen |
| Arrows + Enter | Menus |

## Hazards

| Hazard | How to read it |
|---|---|
| **Cargo crate** | Lit top is safe to land on. Striped sides hurt. |
| **Spike strip** | Clear the whole strip. Wider beds need the double jump. |
| **Catwalk** | Raised steel deck — land on it to cross spikes below. |
| **Hover mine** | Stay low and pass under. Guarding spikes: tap a short hop, don't full-jump. |
| **Plasma vent** | Orange glow means it's about to erupt. Jump the column when it fires. |

## Power cells

| Cell | Effect |
|---|---|
| **Shield** | Absorbs one hit |
| **Overdrive** | Everything runs faster; score counts double |
| **Slow Time** | Everything slows down, including you — jump distances stay fair |

## Campaign sectors

1. **Liftoff** — Tap to hop. Clear the cargo.
2. **Spike Strip** — Spikes punish early landings.
3. **Double Burn** — Fire the second thruster mid-air.
4. **Catwalks** — Raised decks over the spikes.
5. **Minefield** — Stay low under mines; tap-hop guarded spikes.
6. **Vent Line** — Orange glow means a vent is about to erupt.
7. **Freight Yard** — Climb the stacks.
8. **Night Shift** — Everything you've learned, faster.
9. **Gauntlet** — Back-to-back combinations.
10. **Final Approach** — Reach the launch site.

## Level design & validation

Levels are built from physics-aware beats in [`game/levels.py`](game/levels.py). Obstacle heights are tied to real jump reach (single jump ~118 px, double ~223 px), so nothing is placed out of reach by accident.

Every campaign level (and sampled Endless runs) is checked by a bot that uses the **same physics** as the game, with handicaps so a pass means "comfortably clearable", not frame-perfect:

```bash
python tools/validate_levels.py          # all campaign levels + Endless samples
python tools/validate_levels.py 3 4      # specific sectors
```

Run the validator after editing levels.

## Project layout

```
run.py / main.py     Entry + mode orchestrator
constants.py         Physics, palette, tuning (1280×720 logical)
game/physics.py      Deterministic player step (shared with the validator)
game/world.py        Entities and collision boxes
game/levels.py       Beats, campaign scripts, Endless pool
game/art.py          Procedural art at exact gameplay sizes
game/ship.py         Hovercraft presentation
game/core.py         Gameplay loop, HUD, pause / clear screens
ui/menu.py           Main menu, campaign select, how to play
tools/               Level validator
```

## License

See [LICENSE](LICENSE).
