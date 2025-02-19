import asyncio
import pygame
import src.engine.settings as settings


class Game:
    """main game loop code"""

    def __init__(self):
        self.done: bool = False
        self.window: pygame.Window = settings.window
        self.state = settings.STATES[settings.start_state]
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.fps: int = 60
        self.state.startup()

    def event_loop(self):
        for event in pygame.event.get():
            self.state.process_event(event)

    def flip_state(self):
        self.state.done = False
        self.state = settings.STATES[self.state.next_state]
        self.state.startup()

    def update(self, dt):
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()

        self.state.update(dt)

    async def run(self):
        while not self.done:
            dt = self.clock.tick(self.fps)
            self.event_loop()
            self.update(dt)
            self.state.draw(settings.window)
            pygame.display.update()
            await asyncio.sleep(0)
        pygame.quit()
