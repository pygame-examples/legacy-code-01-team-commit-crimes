import pygame
import numpy as np
import numpy.typing as npt
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
        self.cpos: pygame.Vector2 = pygame.Vector2(self.graphic.size) / 2

        NDArrayInt = npt.NDArray[np.int_]
        self.grid: NDArrayInt = np.array(
            [[0, 1, 1, 0], [1, 1, 1, 1], [1, 1, 1, 1], [0, 1, 1, 0]]
        )
        self.gx: int = 0
        self.gy: int = 0
        self.move_delta: tuple[int, int] = (0, 0)
        self.mouse_pos: pygame.Vector2 = pygame.Vector2(0, 1)

    def new_pos_xy(self, x, y):
        self.pos = pygame.Vector2(x, y)

    def new_size(self, size):
        self.size = size

    def process_event(self, event):
        if self.mode == "waiting":
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pos = event.pos
                self.mode = "click_start"
                print("click down")
        elif self.mode == "button_down":
            if event.type == pygame.MOUSEBUTTONUP:
                self.mode = "click_end"
                print("click up")
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

        # temporary code to test stuff
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.move_delta = (0, -1)
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.move_delta = (0, 1)
            elif event.key in [pygame.K_LEFT, pygame.K_a]:
                self.move_delta = (-1, 0)
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                self.move_delta = (1, 0)

    def update(self, dt):
        if self.mode == "click_start":
            print("in click start")
            self.mode = "button_down"
        elif self.mode == "button_down":
            # x,y reversed to accommodate angle_to function
            v2m = pygame.Vector2(self.mouse_pos[1], self.mouse_pos[0]) - pygame.Vector2(
                self.pos[1], self.pos[0]
            )
            self.angle = 360.0 - v2m.angle_to(pygame.Vector2(-1, 0))
            self.graphic = pygame.transform.rotate(self.inp_graphic, self.angle)
            self.cpos = pygame.Vector2(self.graphic.size) / 2

            vmove_delta = (self.mouse_pos - self.pos).normalize()
            self.pos += vmove_delta

        elif self.mode == "click_end":
            self.mode = "waiting"

        # Prevent exit screen
        trygx = max(self.gx + self.move_delta[0], 0)
        trygx = min(
            trygx,
            int(settings.screensize[0]) // settings.blocksize - self.grid.shape[0],
        )
        trygy = max(self.gy + self.move_delta[1], 0)
        trygy = min(
            trygy,
            int(settings.screensize[1]) // settings.blocksize - self.grid.shape[1],
        )

        # prevent collision with grid
        food = settings.STATES["GamePlay"].food

        grid_portion = food[
            trygy : trygy + self.grid.shape[1],
            trygx : trygx + self.grid.shape[0],
        ]
        collision = np.any(grid_portion * self.grid)

        if not collision:
            self.gx = trygx
            self.gy = trygy

        self.move_delta = (0, 0)

    def draw(self, window):
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

        drawxy = self.pos - self.cpos
        window.blit(self.graphic, (*drawxy, *self.graphic.size))
