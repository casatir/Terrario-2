import sys

import pygame

from .map import Map
from .saving import get_saves, save, load
from .tests import test_saving


class Game:
    def __init__(self):
        """Initialise la fenêtre Pygame et les différentes instances nécessaires au jeu."""

        pygame.init()
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])

        flags = pygame.FULLSCREEN | pygame.DOUBLEBUF
        self.screen = pygame.display.set_mode(flags=flags)
        self.clock = pygame.time.Clock()

        self.save_name = "World"
        if self.save_name in get_saves():
            self.map = load(self.save_name)
        else:
            self.map = Map()

        self.run()

    def run(self):
        """Commence la boucle d'execution."""

        show_stats = False
        max_fps = 30

        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                    show_stats = not show_stats

                if event.type == pygame.KEYDOWN and event.key == pygame.K_F2:
                    max_fps = 120 if max_fps == 60 else 60 if max_fps == 30 else 30

                if event.type == pygame.QUIT:
                    save(self.save_name, self.map)
                    pygame.quit()
                    sys.exit()

            self.map.update()

            if show_stats:
                font = pygame.font.Font("prstart.ttf", 32)

                fps = font.render(f"FPS: {round(self.clock.get_fps())}", True, pygame.Color(255, 255, 255))
                pygame.display.get_surface().blit(fps, (2, 0))

                y = font.render(f"Position: {int(self.map.player.position.x)}, {int(self.map.player.position.y)}",
                                True, pygame.Color(255, 255, 255))
                pygame.display.get_surface().blit(y, (2, 32))

            pygame.display.update()
            self.clock.tick(max_fps)
