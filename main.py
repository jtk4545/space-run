"""Space Run — thin orchestrator for menus and game modes."""

import pygame
from game.display import Display
from game.audio import Audio
from game.core import GameCore, RESULT_QUIT, RESULT_RESTART, RESULT_NEXT
from ui.menu import run_main_menu, ACTION_QUIT, ACTION_ENDLESS, ACTION_CAMPAIGN


def run_session(display, audio, mode, level_index=0):
    while True:
        result = GameCore(display, audio, mode=mode, level_index=level_index).run()
        if result == RESULT_RESTART:
            continue
        if result == RESULT_NEXT:
            level_index += 1
            continue
        return result


def main():
    pygame.init()
    display = Display()
    audio = Audio()

    while True:
        action, payload = run_main_menu(display, audio)
        if action == ACTION_QUIT:
            break
        mode = "campaign" if action == ACTION_CAMPAIGN else "endless"
        if run_session(display, audio, mode, payload or 0) == RESULT_QUIT:
            break

    pygame.quit()


if __name__ == "__main__":
    main()
