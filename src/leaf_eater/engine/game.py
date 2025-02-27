import asyncio

import pygame

from . import settings


class Game:
    """main game loop code"""

    def __init__(self, *, fullscreen: bool = False):
        self.window: pygame.Window = pygame.Window(
            title="Leaf Eater", size=settings.WINDOW_SIZE, fullscreen=fullscreen
        )
        self.clock: pygame.Clock = pygame.Clock()

        self.is_running: bool = True
        self.state = None

    async def run(self):
        while self.is_running:
            dt = self.clock.tick(settings.FPS) * 1e-3

            for event in pygame.event.get():
                self.state.process_event(event)

                if event.type == pygame.QUIT:
                    self.is_running = False

            self.state.update(dt)
            self.state.draw(self.window.get_surface())

            pygame.display.flip()
            await asyncio.sleep(0)

        pygame.quit()
