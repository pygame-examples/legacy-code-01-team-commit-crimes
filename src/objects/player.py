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
        self.score: int = 0

        NDArrayInt = npt.NDArray[np.int_]
        self.grid: NDArrayInt = np.array(
            [
                [0, 1, 1, 1, 0],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0],
            ]
        )
        sb = settings.blocksize
        sgs = self.grid.shape
        self.gx: int = int(self.pos[0] / sb - (sgs[0] - 1) / 2)
        self.gy: int = int(self.pos[1] / sb - (sgs[1] - 1) / 2)
        self.mouse_pos: pygame.Vector2 = pygame.Vector2(1, 1)
        self.eat = pygame.mixer.Sound("audio/Footstep__009.ogg")
        self.eat.set_volume(1)

    def process_event(self, event):
        if self.mode == "waiting":
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pos = pygame.Vector2(event.pos)
                self.mode = "button_down"
        elif self.mode == "button_down":
            if event.type == pygame.MOUSEBUTTONUP:
                self.mode = "waiting"
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = pygame.Vector2(event.pos)

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

            # rotate graphic, calculate new center location
            self.graphic = pygame.transform.rotate(self.inp_graphic, self.angle)
            self.cpos = pygame.Vector2(self.graphic.size) / 2

            # to avoid oscillation when mouse distance to player is small
            if self.pos.distance_to(self.mouse_pos) < 2.0:  # may need adjustment
                dxy = pygame.Vector2(0, 0)
            else:
                dxy = (dt / 16) * (self.mouse_pos - self.pos).normalize()

            # Constrain player position
            # -------------------------------------------------------------
            sb = settings.blocksize
            ss = settings.screensize
            sgs = self.grid.shape

            # Limit player position to screen edges - currently not needed
            trygx = max(int((dxy[0] + self.pos[0]) / sb - (sgs[0] - 1) / 2), 0)
            trygx = min(trygx, int(ss[0]) // sb - sgs[0])
            trygy = max(int((dxy[1] + self.pos[1]) / sb - (sgs[1] - 1) / 2), 0)
            trygy = min(trygy, int(ss[1]) // sb - sgs[1])

            # calculate collision with food
            food = settings.STATES["GamePlay"].food
            grid_portion = food[
                trygy : trygy + self.grid.shape[1],
                trygx : trygx + self.grid.shape[0],
            ]
            collision = np.any(grid_portion * self.grid)

            # calculate positions based on collisions
            if collision:
                self.pos = (
                    pygame.Vector2(self.gx + sgs[0] / 2, self.gy + sgs[1] / 2) * sb
                )
            else:
                self.pos += dxy
                self.gx = trygx
                self.gy = trygy

            # color food close to mouth
            if self.mouse_pos == self.pos:
                mouth = self.mouse_pos
            else:
                mouth = self.pos + 3 * sb * (self.mouse_pos - self.pos).normalize()

            # Limit to screen
            mx = min(food.shape[1] - 1, int(mouth[0] / sb))
            my = min(food.shape[0] - 1, int(mouth[1] / sb))

            # bite food
            food[my, mx] = int(food[my, mx] > 0) * (1 + food[my, mx])

            # eat food on threshold of 100 bites
            if food[my, mx] > 100:
                food[my, mx] = 0
                self.score += 1
                self.eat.play()

    def draw(self, window):
        drawxy = self.pos - self.cpos
        window.blit(self.graphic, (*drawxy, *self.graphic.size))

        # to debug player position
        # sb = settings.blocksize
        # for y in range(self.grid.shape[0]):
        #     for x in range(self.grid.shape[1]):
        #         if self.grid[y, x]:
        #             r = pygame.Rect(
        #                 (self.gx + x) * sb,
        #                 (self.gy + y) * sb,
        #                 sb,
        #                 sb,
        #             )
        #             pygame.draw.rect(window, pygame.Color("grey50"), r)
        # pygame.draw.circle(window, pygame.Color("red"), self.pos, 2)
        # if self.mode == "button_down":
        #     if self.mouse_pos != self.pos:
        #         mouth = self.pos + 3 * sb * (self.mouse_pos - self.pos).normalize()
        #         mx = int(mouth[0] / sb)
        #         my = int(mouth[1] / sb)
        #         mr = pygame.Rect(sb * mx, sb * my, sb, sb)
        #         pygame.draw.rect(window, pygame.Color("orange"), mr)
        #         pygame.draw.circle(window, pygame.Color("green"), mouth, 2)
