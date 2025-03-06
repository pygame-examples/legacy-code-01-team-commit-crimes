import asyncio
from typing import Any

import pygame
from pygame._sdl2.video import Window, Renderer, Texture
from ..farkas_tools.multi_sprite_renderer_hardware import MultiSprite as Msr
from ..farkas_tools.buttons import Button

from ..scene import GamePlay, Scene, Intro
from . import events, settings as s


class Game:
    """main game loop code"""

    def __init__(self, *, fullscreen: bool = False):
        pygame.init()
        self.window: Window = Window(
            title="Leaf Eater",
            size=s.WINDOW_SIZE,
            fullscreen=fullscreen,
            resizable=True,
        )
        self.window.minimum_size = s.WINDOW_SIZE//2
        s.WINDOW = self.window

        self.renderer = Renderer(self.window, target_texture=False)
        s.RENDERER = self.renderer

        self.screen = Texture(self.renderer, s.LOGICAL_SIZE_RECT.size, target=True)
        Msr.setScreen(self.renderer)

        Button.controls = s.CONTROLS

        GamePlay.redirects["intro"] = Intro

        self.clock: pygame.Clock = pygame.Clock()

        self.is_running: bool = True
        self.state: Scene = Intro()
        self.state.startup()
        #self.state: Screen = GamePlay()

    def events(self):
        for event in pygame.event.get():
            self.state.process_event(event)

            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == events.SET_SCREEN:
                self.state = event.screen()
                self.state.startup()

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

    async def run(self) -> None:
        self.mousepos = (pygame.Vector2(0, 0), pygame.Vector2(0, 0))
        self.keyboard = (pygame.key.get_pressed(), pygame.key.get_pressed())
        self.mouse = [pygame.mouse.get_pressed(), pygame.mouse.get_pressed()]
        self.events()

        while self.is_running:
            dt = self.clock.tick(s.FPS) * 1e-3

            self.renderer.draw_color = (0, 10, 0, 0)
            self.renderer.target = self.screen
            Msr.screenrect = s.LOGICAL_SIZE_RECT
            self.renderer.clear()

            self.events()
            self.state.update(dt)
            self.state.render()

            self.renderer.target = None
            Msr.screenrect = self.renderer.get_viewport()
            self.renderer.draw_color = (0, 0, 0, 0)
            self.renderer.clear()

            self.screen.draw(dstrect=s.LOGICAL_SIZE_RECT.fit(pygame.Rect(0, 0, *self.window.size)))
            self.renderer.present()

            await asyncio.sleep(0)

        pygame.quit()
