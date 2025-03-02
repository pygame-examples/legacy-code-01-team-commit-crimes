import asyncio
from typing import Any

import pygame
import pygame._sdl2 as pg_sdl2

from ..screens import GamePlay, Screen
from . import events, settings


class Game:
    """main game loop code"""

    def __init__(self, *, fullscreen: bool = False):
        pygame.init()
        self.window: pygame.Window = pygame.Window(
            title="Leaf Eater",
            size=settings.WINDOW_SIZE,
            fullscreen=fullscreen,
            # TODO: if you set this to True, make sure to constrain the mouse position
            # to the renderer's viewport
            resizable=False,
        )
        self.window.minimum_size = settings.LOGICAL_SIZE

        self.renderer = pg_sdl2.Renderer(self.window)
        self.renderer.logical_size = tuple(map(int, settings.LOGICAL_SIZE))
        self.renderer.draw_color = "#3F9B0B"

        original_pygame_mouse_get_pos = pygame.mouse.get_pos

        def pygame_mouse_get_pos(*args: Any, **kwargs: Any) -> Any:
            m_x, m_y = original_pygame_mouse_get_pos(*args, **kwargs)
            r_s_x, r_s_y = self.renderer.scale
            return m_x / r_s_x, m_y / r_s_y

        pygame.mouse.get_pos = pygame_mouse_get_pos

        self.window.get_surface()

        self.clock: pygame.Clock = pygame.Clock()

        self.is_running: bool = True
        # self.state: Screen = Intro()
        self.state: Screen = GamePlay()

    async def run(self) -> None:
        while self.is_running:
            dt = self.clock.tick(settings.FPS) * 1e-3

            for event in pygame.event.get():
                self.state.process_event(event)

                if event.type == pygame.QUIT:
                    self.is_running = False
                elif event.type == events.SET_SCREEN:
                    self.state = event.screen()
                    self.state.startup()

            self.state.update(dt)

            screen = pygame.Surface(settings.LOGICAL_SIZE)
            self.state.render(screen)

            self.renderer.clear()
            texture = pg_sdl2.Texture.from_surface(self.renderer, screen)
            texture.draw()
            self.renderer.present()

            await asyncio.sleep(0)

        pygame.quit()
