import pygame
import numpy as np
import numpy.typing as npt
import src.engine.settings as settings


class Player:
    def __init__(self, pos: pygame.Vector2):
        self.pos: pygame.Vector2 = pos

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
        self.mouse_pos: pygame.Vector2 = pygame.Vector2(0, 1)

    def new_pos_xy(self, x, y):
        self.pos = pygame.Vector2(x, y)

    def process_event(self, event):
        if self.mode == "waiting":
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pos = event.pos
                self.mode = "button_down"
        elif self.mode == "button_down":
            if event.type == pygame.MOUSEBUTTONUP:
                self.mode = "waiting"
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

    def update(self, dt):
        if self.mode == "button_down":
            if not settings.ctrlrect.collidepoint(self.mouse_pos):
                self.mode = "waiting"
                return

            # x,y reversed to accommodate angle_to function
            v2m = pygame.Vector2(self.mouse_pos[1], self.mouse_pos[0]) - pygame.Vector2(
                self.pos[1], self.pos[0]
            )
            self.angle = 360.0 - v2m.angle_to(pygame.Vector2(-1, 0))
            self.graphic = pygame.transform.rotate(self.inp_graphic, self.angle)
            self.cpos = pygame.Vector2(self.graphic.size) / 2

            if self.mouse_pos != self.pos:
                if self.pos.distance_to(self.mouse_pos) < 2.0:  # may need adjstment
                    dxy = pygame.Vector2(0, 0)
                else:
                    dxy = (self.mouse_pos - self.pos).normalize()
            else:
                dxy = pygame.Vector2(0, 0)
                return

            # Constrain player position
            # -------------------------------------------------------------
            sb = settings.blocksize
            ss = settings.screensize
            sgs = self.grid.shape

            # Limit player position to screen edges
            trygx = max(int((dxy[0] + self.pos[0]) / sb - sgs[0] / 2 + 0.5), 0)
            trygx = min(trygx, int(ss[0]) // sb - sgs[0])
            trygy = max(int((dxy[1] + self.pos[1]) / sb - sgs[1] / 2 + 0.5), 0)
            trygy = min(trygy, int(ss[1]) // sb - sgs[1])

            # prevent collision with food
            food = settings.STATES["GamePlay"].food
            grid_portion = food[
                trygy : trygy + self.grid.shape[1],
                trygx : trygx + self.grid.shape[0],
            ]
            collision = np.any(grid_portion * self.grid)

            if collision:
                self.pos -= (sb // 2) * dxy
            else:
                self.pos += dxy
                self.gx = trygx
                self.gy = trygy

            # mark food close to mouth
            # ?????

    def draw(self, window):
        drawxy = self.pos - self.cpos
        window.blit(self.graphic, (*drawxy, *self.graphic.size))

        # to debug player position
        for y in range(self.grid.shape[0]):
            for x in range(self.grid.shape[1]):
                if self.grid[y, x]:
                    r = pygame.Rect(
                        (self.gx + x) * settings.blocksize,
                        (self.gy + y) * settings.blocksize,
                        settings.blocksize - 1,
                        settings.blocksize - 1,
                    )
                    pygame.draw.rect(window, pygame.Color("grey50"), r)
        pygame.draw.circle(window, pygame.Color("red"), self.pos, 2)
