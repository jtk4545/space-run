"""Level design: physics-aware beats, campaign scripts, endless beat pool.

Reach limits (see constants): single jump rises ~118 px, double ~223 px.
Design rules used below, all verified by tools/validate_levels.py:
  crate h <= 80 and catwalk <= 96 are single-jump; walls 120-150 and catwalks
  140-160 need the double jump; low mines (height ~60) are run-under; a mine at
  height ~125 over a short spike strip asks for a tap-hop, not a full jump.
"""

from constants import WIDTH
from game.world import Crate, Spikes, Catwalk, Vent, Mine, Cell


class Beat:
    def __init__(self, width, items, tag="intro"):
        self.width = width
        self.items = items
        self.tag = tag


def R(px):
    return Beat(px, [])


def crate(h, w=64):
    return Beat(w, [(Crate, 0, dict(w=w, h=h))])


def wall(h=140, w=48):
    return Beat(w, [(Crate, 0, dict(w=w, h=h))], "medium")


def spikes(w):
    return Beat(w, [(Spikes, 0, dict(w=w))])


def stair(heights, w=100):
    items = [(Crate, i * w, dict(w=w, h=h)) for i, h in enumerate(heights)]
    return Beat(w * len(heights), items, "medium")


def crate_spikes(h, w, bed):
    """Land on a crate, launch from its top over a spike bed."""
    return Beat(w + bed, [(Crate, 0, dict(w=w, h=h)), (Spikes, w, dict(w=bed))], "medium")


def bridge(height, deck, bed, lead=50):
    """Catwalk over a spike bed. Bed extends `lead` px before and after the deck."""
    return Beat(bed, [
        (Spikes, 0, dict(w=bed)),
        (Catwalk, lead, dict(w=deck, height=height)),
    ], "medium" if height <= 100 else "hard")


def catwalk(height, w):
    return Beat(w, [(Catwalk, 0, dict(w=w, height=height))])


def crate_to_catwalk(h, w, height, deck, gap=40):
    return Beat(w + gap + deck, [
        (Crate, 0, dict(w=w, h=h)),
        (Spikes, w, dict(w=gap + deck)),
        (Catwalk, w + gap, dict(w=deck, height=height)),
    ], "hard")


def mine_low(height=60):
    return Beat(Mine.R * 2, [(Mine, 0, dict(height=height))], "medium")


def mine_hop(bed=48):
    """Spike strip with a mine overhead: tap a short hop, don't full-jump."""
    return Beat(bed, [
        (Spikes, 0, dict(w=bed)),
        (Mine, bed / 2 - Mine.R, dict(height=125, bob=3)),
    ], "hard")


def mine_over_crate(h=64, w=180):
    """Long crate with a mine floating above its far half."""
    return Beat(w, [
        (Crate, 0, dict(w=w, h=h)),
        (Mine, w - 70, dict(height=h + 62, bob=3)),
    ], "hard")


def vent(period=2.2, active=0.8, phase=0.0):
    return Beat(Vent.WIDTH, [(Vent, 0, dict(period=period, active=active, phase=phase))], "medium")


def cell(kind, height=34):
    return Beat(40, [(Cell, 0, dict(height=height, kind=kind))])


def seq(beats, rest):
    out = []
    for b in beats:
        out.append(b)
        out.append(R(rest))
    return out


# ------------------------------------------------------------------ campaign

def _liftoff():
    L = [R(500)]
    for h in (40, 48, 56, 64, 64, 72):
        L += [crate(h), R(560)]
    L += [crate(56, 130), R(520), crate(48), R(230), crate(48), R(560)]
    L += [crate(64, 160), R(500)]
    for h in (56, 72, 80):
        L += [crate(h), R(440)]
    L += [stair((40, 80), 110), R(560)]
    L += [crate(72), R(320), crate(56), R(320), crate(72), R(600)]
    L += [cell("shield"), R(420)]
    for h in (64, 80, 64, 80):
        L += [crate(h, 72), R(380)]
    L += [stair((48, 88), 120), R(500), crate(80, 170), R(900)]
    return L


def _spikefield():
    L = [R(500)]
    for w in (48, 64, 80):
        L += [spikes(w), R(560)]
    L += [crate(56), R(500), spikes(64), R(500)]
    for w in (64, 96, 64, 112):
        L += [spikes(w), R(460)]
    L += [crate_spikes(56, 90, 80), R(520)]
    L += [spikes(48), R(220), spikes(48), R(540)]
    L += [crate(64), R(260), spikes(80), R(520)]
    L += [cell("slow"), R(400)]
    L += [crate_spikes(72, 100, 110), R(500)]
    for w in (96, 120, 96):
        L += [spikes(w), R(420)]
    L += [spikes(64), R(240), crate(64), R(240), spikes(64), R(560)]
    L += [crate_spikes(64, 120, 120), R(900)]
    return L


def _double_burn():
    L = [R(500)]
    for h in (120, 130, 140):
        L += [wall(h), R(620)]
    L += [spikes(170), R(600), spikes(210), R(620)]
    L += [crate(64), R(520), wall(140), R(600)]
    L += [crate_spikes(64, 90, 160), R(580)]
    L += [wall(150, 60), R(580), spikes(220), R(600)]
    L += [stair((56, 120), 110), R(580)]
    L += [cell("shield"), R(400)]
    L += [wall(140), R(340), crate(64), R(560)]
    L += [spikes(180), R(300), crate(72), R(560)]
    L += [wall(150), R(560)]
    L += [stair((48, 96, 144), 100), R(600)]
    L += [crate_spikes(80, 100, 200), R(900)]
    return L


def _catwalks():
    L = [R(500), catwalk(70, 240), R(560)]
    for h in (80, 90, 96):
        L += [bridge(h, 180, 280), R(560)]
    L += [stair((48, 96), 100), R(240), catwalk(96, 200), R(560)]
    L += [Beat(560, [
        (Spikes, 0, dict(w=560)),
        (Catwalk, 50, dict(w=170, height=80)),
        (Catwalk, 330, dict(w=170, height=100)),
    ], "medium"), R(600)]
    L += [cell("slow"), R(400)]
    L += [bridge(150, 200, 300), R(600)]
    L += [crate_to_catwalk(80, 100, 150, 180), R(600)]
    L += [bridge(96, 160, 260), R(320), wall(130), R(600)]
    L += [Beat(640, [
        (Spikes, 0, dict(w=640)),
        (Catwalk, 50, dict(w=150, height=90)),
        (Catwalk, 260, dict(w=150, height=150)),
        (Catwalk, 470, dict(w=130, height=96)),
    ], "hard"), R(900)]
    return L


def _minefield():
    L = [R(500)]
    for _ in range(3):
        L += [mine_low(60), R(560)]
    L += [crate(56), R(360), mine_low(60), R(560)]
    for _ in range(3):
        L += [mine_hop(48), R(560)]
    L += [mine_low(60), R(260), spikes(64), R(560)]
    L += [cell("shield"), R(400)]
    L += [mine_over_crate(64, 180), R(560)]
    L += [spikes(64), R(300), mine_low(60), R(300), crate(64), R(560)]
    L += [mine_hop(48), R(320), mine_hop(48), R(560)]
    L += [mine_over_crate(72, 200), R(400), mine_low(60), R(560)]
    L += [wall(130), R(400), mine_hop(48), R(900)]
    return L


def _vents():
    L = [R(500)]
    for ph in (0.0, 0.5, 0.25):
        L += [vent(2.2, 0.9, ph), R(560)]
    L += [vent(1.6, 0.8, 0.0), R(260), vent(1.6, 0.8, 0.5), R(560)]
    L += [crate(64), R(320), vent(2.0, 0.9, 0.3), R(560)]
    L += [spikes(80), R(320), vent(1.8, 0.9, 0.6), R(560)]
    L += [cell("slow"), R(400)]
    L += [vent(1.4, 0.7, 0.0), R(220), crate(64), R(220), vent(1.4, 0.7, 0.4), R(560)]
    L += [bridge(90, 180, 280), R(320), vent(2.0, 1.0, 0.1), R(560)]
    L += [mine_low(60), R(300), vent(1.8, 0.9, 0.7), R(560)]
    L += [wall(130), R(360), vent(1.6, 0.8, 0.2), R(360), spikes(96), R(900)]
    return L


def _freight_yard():
    L = [R(500)]
    L += [stair((48, 96, 144), 100), R(560)]
    L += [crate(80, 220), R(300), wall(140), R(560)]
    L += [crate_spikes(96, 100, 160), R(540)]
    L += [stair((64, 128), 110), R(260), spikes(120), R(540)]
    L += [cell("overdrive", 90), R(420)]
    L += [crate_to_catwalk(80, 100, 150, 180), R(540)]
    L += [Beat(420, [
        (Crate, 0, dict(w=90, h=64)),
        (Crate, 160, dict(w=90, h=110)),
        (Crate, 320, dict(w=100, h=64)),
    ], "hard"), R(560)]
    L += [mine_over_crate(80, 200), R(400), vent(1.8, 0.9, 0.2), R(540)]
    L += [stair((56, 112), 100), R(200), bridge(96, 160, 240), R(560)]
    L += [cell("shield"), R(400)]
    L += [wall(150), R(320), crate(72, 160), R(300), wall(140), R(900)]
    return L


def _night_shift():
    L = [R(500)]
    L += seq([crate(72), spikes(96), mine_low(60), vent(1.8, 0.8, 0.2), wall(140)], 400)
    L += [crate_spikes(72, 100, 140), R(420)]
    L += [mine_hop(48), R(300), crate(64), R(300), spikes(96), R(460)]
    L += [cell("slow"), R(380)]
    L += [bridge(96, 160, 260), R(300), bridge(150, 180, 280), R(460)]
    L += seq([vent(1.5, 0.7, 0.0), vent(1.5, 0.7, 0.5), mine_low(60), wall(130)], 340)
    L += [stair((64, 128), 100), R(260), spikes(120), R(460)]
    L += [mine_over_crate(64, 200), R(360), crate_spikes(80, 90, 160), R(460)]
    L += [cell("shield"), R(380)]
    L += seq([spikes(64), mine_hop(48), crate(80), vent(1.6, 0.8, 0.3), wall(150)], 360)
    L += [R(500)]
    return L


def _gauntlet():
    L = [R(500)]
    combos = [
        [crate(72), R(260), spikes(96), R(260), wall(140)],
        [mine_low(60), R(240), vent(1.6, 0.8, 0.4), R(240), crate(64)],
        [bridge(96, 160, 260), R(240), mine_hop(48)],
        [stair((64, 128), 100), R(220), spikes(140)],
        [crate_to_catwalk(80, 100, 150, 180), R(260), vent(1.8, 0.9, 0.1)],
        [mine_over_crate(72, 200), R(260), spikes(96), R(260), crate(80)],
    ]
    for i, c in enumerate(combos):
        L += c + [R(460)]
        if i == 2:
            L += [cell("overdrive", 90), R(400)]
        if i == 4:
            L += [cell("shield"), R(400)]
    for c in combos[::-1][:3]:
        L += c + [R(420)]
    L += [R(500)]
    return L


def _final_approach():
    L = [R(500)]
    L += seq([crate(80), spikes(120), wall(150), mine_low(60), vent(1.5, 0.75, 0.2)], 360)
    L += [crate_spikes(80, 100, 180), R(400)]
    L += [cell("slow"), R(360)]
    L += [Beat(640, [
        (Spikes, 0, dict(w=640)),
        (Catwalk, 50, dict(w=150, height=90)),
        (Catwalk, 260, dict(w=150, height=150)),
        (Catwalk, 470, dict(w=130, height=96)),
    ], "hard"), R(420)]
    L += seq([mine_hop(48), mine_hop(48), stair((56, 112), 100), vent(1.4, 0.7, 0.0)], 320)
    L += [mine_over_crate(80, 200), R(320), wall(140), R(420)]
    L += [cell("shield"), R(360)]
    L += [crate_to_catwalk(80, 100, 150, 180), R(300), spikes(140), R(400)]
    L += seq([vent(1.4, 0.7, 0.3), crate(72), mine_low(60), spikes(96), wall(150)], 300)
    L += [stair((48, 96, 144), 100), R(260), spikes(160), R(400)]
    L += seq([mine_hop(48), crate(80, 180), vent(1.6, 0.8, 0.6), wall(150)], 320)
    L += [R(600)]
    return L


CAMPAIGN_LEVELS = [
    dict(id=1, name="Liftoff", subtitle="Tap to hop. Clear the cargo.", speed=340, build=_liftoff),
    dict(id=2, name="Spike Strip", subtitle="Spikes punish early landings.", speed=350, build=_spikefield),
    dict(id=3, name="Double Burn", subtitle="Tap again mid-air to fire the second thruster.", speed=360, build=_double_burn),
    dict(id=4, name="Catwalks", subtitle="Raised decks carry you over the spikes.", speed=360, build=_catwalks),
    dict(id=5, name="Minefield", subtitle="Stay low under mines. Tap-hop the guarded spikes.", speed=360, build=_minefield),
    dict(id=6, name="Vent Line", subtitle="Orange glow means a vent is about to erupt.", speed=370, build=_vents),
    dict(id=7, name="Freight Yard", subtitle="Climb the stacks.", speed=370, build=_freight_yard),
    dict(id=8, name="Night Shift", subtitle="Everything you've learned, faster.", speed=385, build=_night_shift),
    dict(id=9, name="Gauntlet", subtitle="Back-to-back combinations.", speed=395, build=_gauntlet),
    dict(id=10, name="Final Approach", subtitle="Reach the launch site.", speed=405, build=_final_approach),
]

LEAD_IN = WIDTH + 80


def place(world, beats, start_x):
    """Spawn beats starting at start_x (screen space). Returns (end_x, beat_starts)."""
    x = start_x
    starts = []
    for b in beats:
        starts.append(x)
        for cls, rel, kw in b.items:
            world.add(cls(x + rel, **kw))
        x += b.width
    return x, starts


def level_beats(level):
    return level["build"]()


def level_length(level):
    return LEAD_IN + sum(b.width for b in level_beats(level))


# ------------------------------------------------------------------ endless

ENDLESS_POOL = {
    "intro": [
        lambda: crate(56), lambda: crate(72), lambda: spikes(64), lambda: spikes(96),
        lambda: crate(64, 140), lambda: catwalk(80, 200), lambda: stair((48, 88), 100),
    ],
    "medium": [
        lambda: wall(130), lambda: wall(140), lambda: spikes(170), lambda: mine_low(60),
        lambda: crate_spikes(64, 90, 120), lambda: bridge(90, 180, 280),
        lambda: vent(1.8, 0.8, 0.0), lambda: vent(2.0, 0.9, 0.5),
        lambda: stair((56, 112), 100),
    ],
    "hard": [
        lambda: mine_hop(48), lambda: mine_over_crate(72, 200), lambda: bridge(150, 200, 300),
        lambda: crate_to_catwalk(80, 100, 150, 180), lambda: wall(150, 60),
        lambda: stair((48, 96, 144), 100), lambda: crate_spikes(80, 100, 180),
    ],
}

# (tags, rest_min, rest_max) per wave
ENDLESS_WAVES = [
    (("intro",), 480, 580),
    (("intro", "medium"), 440, 540),
    (("medium",), 400, 500),
    (("medium", "hard"), 360, 460),
    (("medium", "hard"), 330, 420),
    (("hard",), 320, 400),
]
