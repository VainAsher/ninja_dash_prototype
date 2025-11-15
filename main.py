
# main.py - bootstrap for Ninja Dash refactored state-based architecture

import sys
import pygame

from settings import FPS
from core.game import Game


def main() -> None:
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2)

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
