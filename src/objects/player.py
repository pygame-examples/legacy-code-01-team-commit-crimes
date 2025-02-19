import pygame
import numpy as np
import src.engine.settings as settings
from src.objects.txt_item import Txt_item


class Player:
    def __init__(self, pos: pygame.Vector2):
        self.pos: pygame.Vector2 = pos
        self.size: float = 10

        g: pygame.Surface = pygame.image.load("graphics/bug_alpha.png").convert_alpha()
        self.inp_graphic = pygame.transform.scale(g, (128, 128))
        self.graphic: pygame.Surface = self.inp_graphic.copy()
        self.mode: str = "waiting"
        self.angle: float = 0
        self.cx, self.cy = self.graphic.get_size()

        self.grid = np.array([[0, 1, 1, 0], [1, 1, 1, 1], [1, 1, 1, 1], [0, 1, 1, 0]])
        self.gx, self.gy = 0, 0

    def new_pos_xy(self, x, y):
        self.pos = pygame.Vector2(x, y)

    def new_size(self, size):
        self.size = size

    def process_event(self, event):
        if self.mode == "waiting":
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mode = "click_start"
                print("click down")
        elif self.mode == "button_down":
            if event.type == pygame.MOUSEBUTTONUP:
                self.mode = "click_end"
                print("click up")

    def update(self, dt):
        if self.mode == "click_start":
            print("in click start")
            self.mode = "button_down"
        elif self.mode == "button_down":
            self.angle += 1
            self.graphic = pygame.transform.rotate(self.inp_graphic, self.angle)
            self.cx, self.cy = self.graphic.get_size()
            self.cx = self.cx / 2
            self.cy = self.cy / 2
        elif self.mode == "click_end":
            self.mode = "waiting"

    def draw(self, window):
        window.blit(
            self.graphic, (self.pos[0] - self.cx, self.pos[1] - self.cy, 128, 128)
        )

        for y in range(self.grid.shape[0]):
            for x in range(self.grid.shape[1]):
                if self.grid[y, x]:
                    r = pygame.Rect(
                        (self.gx + x) * settings.blocksize,
                        (self.gy + y) * settings.blocksize,
                        settings.blocksize,
                        settings.blocksize,
                    )
                    pygame.draw.rect(window, pygame.Color("grey20"), r)
