import heapq
import math
from collections import defaultdict
from typing import Protocol, runtime_checkable
import random

import pygame
from ..farkas_tools.multi_sprite_renderer_hardware import MultiSprite as Msr
from ..farkas_tools.buttons import Button


from ..engine import events, settings as s
from ..engine.make_map import get_blocks2
from ..objects.player import Player, Projectile
from ..objects.ui import Text
from . import Scene

Rect = pygame.Rect | pygame.FRect


class Cell:
    def __init__(self, x, y, value):
        self.pos = pygame.Vector2(x * s.BLOCK_SIZE, y * s.BLOCK_SIZE)
        self.mask = pygame.Mask((s.BLOCK_SIZE, s.BLOCK_SIZE), fill=True)
        self.rect = pygame.Rect(self.pos, (s.BLOCK_SIZE, s.BLOCK_SIZE))
        self.value = value

    def draw(self):
        c = pygame.Color.from_hsva(pygame.math.clamp(self.value, 0, 299) + 60, 100, 100, 0)
        s.RENDERER.draw_color = c
        s.RENDERER.fill_rect(self.rect)


class GamePlay(Scene):
    """Main game code"""
    redirects: dict[str, type(Scene)] = {}  # "circular imports"

    def __init__(self):
        self.dt = 0
        self.player: Player = Player(pygame.Vector2(10, 10), self)
        Projectile.image_msr(folders=(s.ASSETSPATH,), names=("projectile",))
        self.white_font = Msr(folders=(s.ASSETSPATH,), font="MonospaceTypewriter", size=20)

        self.grow_timer = 1
        self.grow_seeds = [(-1, -1) for _ in range(4)]

        bs = s.BLOCK_SIZE
        edge = s.EDGE
        dx = s.LOGICAL_SIZE_RECT.w // bs - edge * 2
        dy = s.LOGICAL_SIZE_RECT.h // bs - edge * 2
        maparray = get_blocks2(int(dx), int(dy), edge)
        self.map: dict[tuple[int, int], Cell] = dict()
        self.map_size = pygame.Vector2(maparray.shape)
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
        self.dt = dt

        self.grow_map()

        self.player.update(dt)

        self.player.projectiles.update(dt)

        if Button.keys((s.CONTROLS["Esc"],))[0]:
            pygame.event.post(pygame.event.Event(events.SET_SCREEN, screen=self.redirects["intro"]))

        if self.player.health <= 0:
            pygame.event.post(pygame.event.Event(events.SET_SCREEN, screen=self.redirects["over"]))

    def render(self) -> None:
        for cell in self.map.values():
            cell.draw()

        self.player.draw()
        self.player.projectiles.update("draw")

        self.white_font.write(f"Health: {round(self.player.health)}", pos=(100, 10))
        self.white_font.write(f"Score: {self.player.score}", pos=(100, 30))

    def add_cell_to_map(self, x, y, value):
        if 0 <= x < self.map_size.x and 0 <= y < self.map_size.y:
            cell = self.map.setdefault((x, y), Cell(x, y, value))
            if cell.value < value:
                cell.value = value

    def remove_cell_from_map(self, x, y):
        cell = self.map.pop((x, y), None)
        if cell:
            self.player.score += cell.value

    def change_map_cell(self, x, y, value):
        cell = self.map.setdefault((x, y), None)
        if cell:
            if cell.value <= -value:
                self.remove_cell_from_map(x, y)
            else:
                cell.value += value
                if value < 0:
                    self.player.score -= value

    def grow_map(self):

        def grow():
            if self.map:
                seed = random.randrange(len(self.grow_seeds))
                if tuple(self.grow_seeds[seed]) in self.map:
                    origin = self.grow_seeds[seed]
                else:
                    origin = random.choice(tuple(self.map.values())).pos // s.BLOCK_SIZE

                direction = random.choice(((0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)))
                value = 0
                pos = self.grow_seeds[seed]
                while tuple(origin) in self.map:
                    cell = self.map[tuple(origin)]
                    value = max(cell.value + random.randrange(-4, 4), 10)
                    pos = cell.pos
                    origin += direction
                self.grow_seeds[seed] = pos // s.BLOCK_SIZE
                self.add_cell_to_map(*origin, value)

        self.grow_timer -= self.dt
        if self.grow_timer <= 0 and self.map:
            while self.grow_timer <= 0:
                self.grow_timer += (len(self.map)/150000)
                grow()

    @staticmethod
    def get_colliding_cells(rect: Rect):
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
        return bool(self.map[grid_pos].mask.overlap(mask, rect.topleft - self.map[grid_pos].pos))

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

        return dx or dy
