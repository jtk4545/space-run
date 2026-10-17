"""Deterministic player physics shared by the game and the level validator."""

from constants import (
    GROUND_Y, PLAYER_X, PLAYER_W, PLAYER_H, HURT_INSET_X, HURT_INSET_Y,
    GRAVITY, JUMP_VELOCITY, DOUBLE_JUMP_VELOCITY, MAX_FALL_SPEED,
    COYOTE_TIME, JUMP_BUFFER, VARIABLE_JUMP_CUT, LEDGE_TOLERANCE,
)

EV_JUMP = 1
EV_DOUBLE = 2
EV_LAND = 4
EV_HIT = 8

HURT_X0 = PLAYER_X + HURT_INSET_X
HURT_X1 = PLAYER_X + PLAYER_W - HURT_INSET_X


class Body:
    __slots__ = ("y", "vy", "grounded", "can_double", "coyote", "buffer", "held")

    def __init__(self):
        self.y = GROUND_Y - PLAYER_H
        self.vy = 0.0
        self.grounded = True
        self.can_double = True
        self.coyote = COYOTE_TIME
        self.buffer = 0.0
        self.held = False

    def copy(self):
        b = Body.__new__(Body)
        b.y = self.y
        b.vy = self.vy
        b.grounded = self.grounded
        b.can_double = self.can_double
        b.coyote = self.coyote
        b.buffer = self.buffer
        b.held = self.held
        return b

    def hurtbox(self):
        return (HURT_X0, self.y + HURT_INSET_Y, HURT_X1, self.y + PLAYER_H - HURT_INSET_Y)


def step(b, dt, solids, hazards, pressed, held):
    """Advance one tick.

    solids:  iterable of (x0, top, x1) landable surfaces
    hazards: iterable of (x0, y0, x1, y1) damaging boxes
    Returns an event bitmask.
    """
    ev = 0
    if pressed:
        b.buffer = JUMP_BUFFER
    if b.held and not held and b.vy < 0:
        b.vy *= VARIABLE_JUMP_CUT
    b.held = held

    if b.grounded:
        b.coyote = COYOTE_TIME
        b.can_double = True
    else:
        b.coyote = max(0.0, b.coyote - dt)

    if b.buffer > 0:
        if b.coyote > 0:
            b.vy = -JUMP_VELOCITY
            b.coyote = 0.0
            b.buffer = 0.0
            b.grounded = False
            ev |= EV_JUMP
        elif b.can_double:
            b.vy = -DOUBLE_JUMP_VELOCITY
            b.can_double = False
            b.buffer = 0.0
            ev |= EV_DOUBLE
        else:
            b.buffer = max(0.0, b.buffer - dt)

    was_grounded = b.grounded
    prev_feet = b.y + PLAYER_H
    b.vy = min(MAX_FALL_SPEED, b.vy + GRAVITY * dt)
    b.y += b.vy * dt
    feet = b.y + PLAYER_H
    b.grounded = False

    if feet >= GROUND_Y:
        b.y = GROUND_Y - PLAYER_H
        b.vy = 0.0
        b.grounded = True
    elif b.vy >= 0:
        for x0, top, x1 in solids:
            if HURT_X1 > x0 and HURT_X0 < x1 and feet >= top and prev_feet <= top + LEDGE_TOLERANCE:
                b.y = top - PLAYER_H
                b.vy = 0.0
                b.grounded = True
                break

    if b.grounded and not was_grounded:
        ev |= EV_LAND

    hx0, hy0, hx1, hy1 = b.hurtbox()
    for x0, y0, x1, y1 in hazards:
        if hx1 > x0 and hx0 < x1 and hy1 > y0 and hy0 < y1:
            ev |= EV_HIT
            break
    return ev
