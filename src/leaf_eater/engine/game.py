import asyncio
from typing import Any
import platform

import pygame
from pygame._sdl2.video import Window, Renderer, Texture
from ..farkas_tools.multi_sprite_renderer_hardware import MultiSprite as Msr
from ..farkas_tools.buttons import Button

from ..scene import GamePlay, Scene, Intro, GameOver
from . import events, settings as s


class Game:
    """main game loop code"""

    def __init__(self, *, fullscreen: bool = False):
        pygame.init()
        self.fullscreen = fullscreen
        self.window: Window = Window(
            title="Leaf Eater",
            size=s.WINDOW_SIZE,
            fullscreen=self.fullscreen,
            fullscreen_desktop=self.fullscreen,
            resizable=True,
        )
        self.window.minimum_size = s.WINDOW_SIZE//2
        s.WINDOW = self.window

        self.renderer = Renderer(self.window, target_texture=False)
        s.RENDERER = self.renderer

        self.screen = Texture(self.renderer, s.LOGICAL_SIZE_RECT.size, target=True)  # game screen
        Msr.setScreen(self.renderer)

        Button.controls = s.CONTROLS

        # circular imports get around
        GamePlay.redirects["intro"] = Intro
        GamePlay.redirects["over"] = GameOver
        GameOver.redirects["intro"] = Intro

        self.clock: pygame.Clock = pygame.Clock()

        self.is_running: bool = True
        self.state: Scene = Intro()
        # self.state: Screen = GamePlay()
        self.state.startup()

    def events(self):
        for event in pygame.event.get():
            self.state.process_event(event)

            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.WINDOWRESIZED and not self.fullscreen:
                s.WINDOW_SIZE.xy = self.window.size
            elif event.type == events.SET_SCREEN:
                self.state = event.screen()
                self.state.startup()

        #                (previous frame, current frame)
        self.keyboard = (self.keyboard[1], pygame.key.get_pressed())
        self.mouse = [self.mouse[1], pygame.mouse.get_pressed()]

        rect = s.LOGICAL_SIZE_RECT.fit(pygame.Rect(0, 0, *self.window.size))

        self.mousepos[0].update(self.mousepos[1])
        self.mousepos[1].update(pygame.mouse.get_pos())
        self.mousepos[1].x -= rect.x
        self.mousepos[1].y -= rect.y
        if not (self.mouse[1][0] or self.mouse[1][2] or self.mouse[1][1]):
            self.mousepos[1].x = pygame.math.clamp(self.mousepos[1].x, 0, rect.w)
            self.mousepos[1].y = pygame.math.clamp(self.mousepos[1].y, 0, rect.h)
        self.mousepos[1].x *= s.LOGICAL_SIZE_RECT.w / rect.w
        self.mousepos[1].y *= s.LOGICAL_SIZE_RECT.h / rect.h
        self.mousepos[1].x = round(self.mousepos[1].x)
        self.mousepos[1].y = round(self.mousepos[1].y)

        Button.mouse = self.mouse
        Button.mousepos = self.mousepos
        Button.keyboard = self.keyboard

    def resize_or_fullscreen(self, scale: tuple[int, int] | None = None):
        """
        None scale toggles between fullscreen and last non fulscreen size
        int, int sets window size
        """

        if hasattr(platform, 'window'):
            return

        pygame.mouse.set_pos(0, 0)

        if scale is None:
            self.fullscreen = not self.fullscreen

            if self.fullscreen:
                self.window.set_fullscreen(True)
            else:
                self.window.set_windowed()
                s.WINDOW_SIZE.xy = self.window.size
        else:
            rect = pygame.Rect(*self.window.position, *self.window.size)

            self.window.set_windowed()
            self.fullscreen = False
            s.WINDOW_SIZE.xy = scale[0], scale[1]
            self.window.size = scale

            self.window.position = rect.centerx - self.window.size[0] / 2, rect.centery - self.window.size[1] / 2

        rect = s.LOGICAL_SIZE_RECT.fit(pygame.Rect(0, 0, *self.window.size))
        pygame.mouse.set_pos(self.mousepos[1].x / s.LOGICAL_SIZE_RECT.w * rect.w + rect.x, self.mousepos[1].y / s.LOGICAL_SIZE_RECT.h * rect.h + rect.y)

    async def run(self) -> None:
        self.mousepos = (pygame.Vector2(0, 0), pygame.Vector2(0, 0))
        self.keyboard = (pygame.key.get_pressed(), pygame.key.get_pressed())
        self.mouse = [pygame.mouse.get_pressed(), pygame.mouse.get_pressed()]
        self.events()

        while self.is_running:
            dt = self.clock.tick(s.FPS) * 1e-3

            self.renderer.draw_color = (0, 10, 0, 0)  # background color
            self.renderer.target = self.screen  # drawing on screen
            Msr.screenrect = s.LOGICAL_SIZE_RECT
            self.renderer.clear()  # fills background

            self.events()

            # toggle full screen with F
            if Button.keys((pygame.K_f,))[0]:
                self.resize_or_fullscreen(s.LOGICAL_SIZE_RECT.size if self.fullscreen else None)

            self.state.update(dt)
            self.state.render()

            self.renderer.target = None  # drawing on window
            Msr.screenrect = self.renderer.get_viewport()
            self.renderer.draw_color = (0, 0, 0, 0)  # border color
            self.renderer.clear()

            self.screen.draw(dstrect=s.LOGICAL_SIZE_RECT.fit(pygame.Rect(0, 0, *self.window.size)))  # draws screen onto window
            self.renderer.present()

            await asyncio.sleep(0)

        pygame.quit()
