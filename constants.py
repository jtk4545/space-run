"""Pure game constants — no display side effects on import."""

# Logical design resolution (scaled to window at runtime)
WIDTH, HEIGHT = 1280, 720
FPS = 60
SIM_DT = 1 / 60

GROUND_HEIGHT = 110
GROUND_Y = HEIGHT - GROUND_HEIGHT

# Player body (side-view hovercraft) and forgiving hurtbox
PLAYER_X = 260
PLAYER_W, PLAYER_H = 56, 26
HURT_INSET_X, HURT_INSET_Y = 8, 4

# Physics (px, px/s, px/s^2)
GRAVITY = 2200.0
JUMP_VELOCITY = 720.0
DOUBLE_JUMP_VELOCITY = 680.0
MAX_FALL_SPEED = 1400.0
COYOTE_TIME = 0.10
JUMP_BUFFER = 0.12
VARIABLE_JUMP_CUT = 0.45
LEDGE_TOLERANCE = 10

# Derived reach — level design rules are written against these
SINGLE_JUMP_RISE = JUMP_VELOCITY ** 2 / (2 * GRAVITY)            # ~118 px
DOUBLE_JUMP_RISE = SINGLE_JUMP_RISE + DOUBLE_JUMP_VELOCITY ** 2 / (2 * GRAVITY)  # ~223 px

# Endless pacing
ENDLESS_SPEED_START = 360.0
ENDLESS_SPEED_MAX = 500.0

# Power-ups
SHIELD_DURATION = 8.0
OVERDRIVE_DURATION = 5.0
OVERDRIVE_TIME_SCALE = 1.25
SLOW_DURATION = 4.0
SLOW_TIME_SCALE = 0.6

HIT_IFRAMES = 1.5
HIT_STOP = 0.07

# Palette — muted lunar industrial, warm only for danger
SKY_TOP = (4, 6, 12)
SKY_HORIZON = (16, 26, 44)
MOUNTAIN_FAR = (20, 27, 40)
MOUNTAIN_NEAR = (28, 35, 50)
GROUND_TOP = (70, 76, 88)
GROUND_BOTTOM = (26, 29, 36)
STEEL = (52, 60, 74)
STEEL_LIGHT = (128, 144, 164)
STEEL_DARK = (26, 31, 40)
HAZARD_YELLOW = (230, 180, 40)
DANGER = (255, 96, 60)
PLASMA = (255, 150, 70)
ACCENT = (96, 200, 255)
TEXT = (226, 232, 240)
TEXT_DIM = (140, 152, 170)
GOLD = (255, 205, 90)
WARN = (255, 100, 90)
SHIELD_COLOR = (90, 170, 255)
OVERDRIVE_COLOR = (255, 175, 70)
SLOW_COLOR = (170, 150, 255)

# Persistence
PROGRESS_FILE = "progress.json"
HIGH_SCORE_FILE = "high_score.json"

STARTING_LIVES = 3
