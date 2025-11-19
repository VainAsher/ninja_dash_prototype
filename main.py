
# main.py - bootstrap for Ninja Dash refactored state-based architecture

import sys
import pygame

# Import environment configuration first
import env_config

from settings import FPS
from core.game import Game


def main() -> None:
    # Print environment info if console is visible
    if env_config.CONSOLE_VISIBLE:
        env_config.print_env_info()

    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2)

    # Set window title with environment suffix
    pygame.display.set_caption(f"Ninja Dash{env_config.WINDOW_TITLE_SUFFIX}")

    clock = pygame.time.Clock()
    game = Game()

    while game.running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            game.handle_event(event)

        game.update(dt)
        game.draw()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
