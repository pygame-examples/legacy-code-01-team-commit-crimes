import heapq
import math
from collections import defaultdict
from typing import Protocol, runtime_checkable

import pygame

from ..engine import settings
from ..engine.make_map import get_blocks2
from ..objects.player import Player
from ..objects.ui import Text
from . import Screen

Rect = pygame.Rect | pygame.FRect


@runtime_checkable
class RectCollider(Protocol):
    @property
    def rect(self) -> pygame.Rect: ...


@runtime_checkable
class MaskCollider(Protocol):
    @property
    def position(self) -> pygame.Vector2: ...

    @property
    def mask(self) -> pygame.Mask: ...


Collider = RectCollider | MaskCollider


class GamePlay(Screen):
    """Main game code"""

    def __init__(self):
        self.player: Player = Player(pygame.Vector2())
        self.score_text = Text("Score: 0", (100, 30))
        self.background = pygame.Surface((settings.WINDOW_SIZE))

        bs = settings.BLOCK_SIZE
        edge = settings.EDGE
        dx = settings.LOGICAL_SIZE.x // bs - edge * 2
        dy = settings.LOGICAL_SIZE.y // bs - edge * 2
        self.food = get_blocks2(int(dx), int(dy), edge)

        self.colliders: dict[tuple[int, int], list[Collider]] = defaultdict(list)
        for y, row in enumerate(self.food):
            for x, cell in enumerate(row):
                if cell == 0:
                    continue

                # sorry...
                uh_oh = type(
                    "Ummm, my apologies",
                    (),
                    {
                        "__init__": lambda self, x, y: [
                            setattr(
                                self,
                                "position",
                                pygame.Vector2(x * settings.BLOCK_SIZE, y * settings.BLOCK_SIZE),
                            ),
                            setattr(
                                self,
                                "mask",
                                pygame.Mask((settings.BLOCK_SIZE, settings.BLOCK_SIZE), fill=True),
                            ),
                            None,
                        ][-1],
                    },
                )(x, y)
                self.colliders[x, y].append(uh_oh)

    def startup(self):
        pass

    def process_event(self, event: pygame.Event) -> None:
        self.player.process_event(event)

    def update(self, dt: float) -> None:
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        m_left, _, _ = pygame.mouse.get_pressed()

        vec_towards_mouse = mouse_pos - self.player.pos
        vec_towards_mouse_normalized = vec_towards_mouse and vec_towards_mouse.normalize()

        if vec_towards_mouse.length() > 5.0 and m_left:  # I love hardcoded random values
            self.player.angle = vec_towards_mouse.angle_to(pygame.Vector2(1, 0))
            self.player.pos += vec_towards_mouse_normalized * 100 * dt  # oh hey, look, another one

        self.player.update(dt)
        self.handle_player_collisions()

        self.score_text.text = f"Score: {self.player.score}"

    def render(self, dest: pygame.Surface) -> None:
        dest.blit(self.background, (0, 0))

        bs = settings.BLOCK_SIZE
        for y in range(self.food.shape[0]):
            for x in range(self.food.shape[1]):
                if self.food[y, x]:
                    c = pygame.Color.from_hsva(self.food[y, x] + 60, 100, 100, 0)
                    r = pygame.Rect(x * bs, y * bs, bs, bs)
                    pygame.draw.rect(dest, c, r)

        self.score_text.render(dest)
        self.player.render(dest)

    def get_colliding_cells(self, rect: Rect):
        cell_size = settings.BLOCK_SIZE
        min_x = int(rect.x // cell_size)
        min_y = int(rect.y // cell_size)
        max_x = int(rect.right // cell_size)
        max_y = int(rect.bottom // cell_size)

        for grid_y in range(min_y, max_y + 1):
            for grid_x in range(min_x, max_x + 1):
                yield grid_x, grid_y

    def rect_collides_at_grid_pos(self, rect: Rect, grid_pos: tuple[int, int]) -> bool:
        if grid_pos not in self.colliders:
            return False
        return any(
            rect.colliderect(collider.rect)
            for collider in self.colliders[grid_pos]
            if isinstance(collider, RectCollider)
        )

    def mask_collides_at_grid_pos(self, rect: Rect, mask: pygame.Mask, grid_pos: tuple[int, int]) -> bool:
        if grid_pos not in self.colliders:
            return False

        return any(
            collider.mask.overlap(mask, rect.topleft - collider.position)
            for collider in self.colliders[grid_pos]
            if isinstance(collider, MaskCollider)
        )

    def rect_collides_any(self, rect: Rect) -> bool:
        for grid_pos in self.get_colliding_cells(rect):
            if grid_pos not in self.colliders:
                continue
            if self.rect_collides_at_grid_pos(rect, grid_pos):
                break
        else:
            return False
        return True

    def mask_collides_any(self, rect: Rect, mask: pygame.Mask) -> bool:
        for grid_pos in self.get_colliding_cells(rect):
            if grid_pos not in self.colliders:
                continue
            if self.mask_collides_at_grid_pos(rect, mask, grid_pos):
                break
        else:
            return False
        return True

    def handle_player_collisions(self):
        rect = self.player.collide_rect
        mask = self.player.mask

        # if not self.rect_collides_any(rect):
        #     return

        displacements: list[tuple[int, int, int]] = [
            (0, 0, 0)
        ]  # dist_squared, displacement_x, displacement_y
        seen_displacements = {(0, 0)}

        while True:
            _, dis_x, dis_y = heapq.heappop(displacements)
            dis_xy = (dis_x, dis_y)
            displaced_rect = rect.move(dis_xy)

            if not self.mask_collides_any(displaced_rect, mask):
                best_displacement = dis_xy
                break
            else:
                for dx, dy in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
                    new_dis_xy = new_dis_x, new_dis_y = dis_x + dx, dis_y + dy
                    if new_dis_xy in seen_displacements:
                        continue

                    dist_squared = new_dis_x**2 + new_dis_y**2

                    seen_displacements.add(new_dis_xy)
                    heapq.heappush(displacements, (dist_squared, new_dis_x, new_dis_y))

        dx, dy = best_displacement

        if dx > 0:
            dx += math.floor(rect.x) - rect.x
        elif dx < 0:
            dx += math.ceil(rect.x) - rect.x

        if dy > 0:
            dy += math.floor(rect.y) - rect.y
        elif dy < 0:
            dy += math.ceil(rect.y) - rect.y

        self.player.pos.x += dx
        self.player.pos.y += dy

        # if dx != 0:
        #     self.player.velocity.x = 0
        #     # self.player.state = enums.EntityState.IDLE
        # if dy != 0:
        #     if self.player.velocity.y * dy < 0:
        #         self.player.velocity.y = 0
