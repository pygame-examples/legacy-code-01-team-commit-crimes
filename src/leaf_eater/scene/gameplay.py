import heapq
import math
from collections import defaultdict
from typing import Protocol, runtime_checkable

import pygame
from ..farkas_tools.multi_sprite_renderer_hardware import MultiSprite as Msr
from ..farkas_tools.buttons import Button


from ..engine import events, settings as s
from ..engine.make_map import get_blocks2
from ..objects.player import Player
from ..objects.ui import Text
from . import Scene

Rect = pygame.Rect | pygame.FRect


class Cell:
    def __init__(self, x, y, value):
        self.position = pygame.Vector2(x * s.BLOCK_SIZE, y * s.BLOCK_SIZE)
        self.mask = pygame.Mask((s.BLOCK_SIZE, s.BLOCK_SIZE), fill=True)
        self.rect = pygame.Rect(self.position, (s.BLOCK_SIZE, s.BLOCK_SIZE))
        self.value = value


class GamePlay(Scene):
    """Main game code"""
    redirects: dict[str, type(Scene)] = {}  # "circular imports"

    def __init__(self):
        self.player: Player = Player(pygame.Vector2(10, 10))
        self.white_font = Msr(folders=(s.ASSETSPATH,), font="MonospaceTypewriter", size=20)

        bs = s.BLOCK_SIZE
        edge = s.EDGE
        dx = s.LOGICAL_SIZE_RECT.w // bs - edge * 2
        dy = s.LOGICAL_SIZE_RECT.h // bs - edge * 2
        maparray = get_blocks2(int(dx), int(dy), edge)
        self.map: dict[tuple[int, int], Cell] = dict()
        for y, row in enumerate(maparray):
            for x, value in enumerate(row):
                if value == 0:
                    continue
                self.map[x, y] = Cell(x, y, value)

    def startup(self):
        pass

    def process_event(self, event: pygame.Event) -> None:
        self.player.process_event(event)

    def update(self, dt: float) -> None:

        self.player.update(dt)
        self.handle_player_collisions()

        if Button.keys((s.CONTROLS["Esc"],))[0]:
            pygame.event.post(pygame.event.Event(events.SET_SCREEN, screen=self.redirects["intro"]))

    def render(self) -> None:

        bs = s.BLOCK_SIZE
        for xy, cell in self.map.items():
            x, y = xy
            c = pygame.Color.from_hsva(cell.value + 60, 100, 100, 0)
            r = pygame.Rect(x * bs, y * bs, bs, bs)
            s.RENDERER.draw_color = c
            s.RENDERER.fill_rect(r)

        self.player.render()

        self.white_font.write(f"Score: {self.player.score}", pos=(100, 30))

    def get_colliding_cells(self, rect: Rect):
        cell_size = s.BLOCK_SIZE
        min_x = int(rect.x // cell_size)
        min_y = int(rect.y // cell_size)
        max_x = int(rect.right // cell_size)
        max_y = int(rect.bottom // cell_size)

        for grid_y in range(min_y, max_y + 1):
            for grid_x in range(min_x, max_x + 1):
                yield grid_x, grid_y

    def rect_collides_at_grid_pos(self, rect: Rect, grid_pos: tuple[int, int]) -> bool:
        if grid_pos not in self.map:
            return False
        return rect.colliderect(self.map[grid_pos].rect)

    def mask_collides_at_grid_pos(self, rect: Rect, mask: pygame.Mask, grid_pos: tuple[int, int]) -> bool:
        if grid_pos not in self.map:
            return False
        return bool(self.map[grid_pos].mask.overlap(mask, rect.topleft - self.map[grid_pos].position))

    def rect_collides_any(self, rect: Rect) -> bool:
        for grid_pos in self.get_colliding_cells(rect):
            if grid_pos not in self.map:
                continue
            if self.rect_collides_at_grid_pos(rect, grid_pos):
                break
        else:
            return False
        return True

    def mask_collides_any(self, rect: Rect, mask: pygame.Mask) -> bool:
        for grid_pos in self.get_colliding_cells(rect):
            if grid_pos not in self.map:
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

        displacements: list[tuple[int, int, int]] = [(0, 0, 0)]  # dist_squared, displacement_x, displacement_y
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
