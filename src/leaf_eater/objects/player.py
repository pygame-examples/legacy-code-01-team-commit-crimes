import math

import pygame
from pygame import sprite

from ..engine import settings
from ..farkas_tools.buttons import Button
from ..farkas_tools.multi_sprite_renderer_hardware import MultiSprite as Msr
from ..utils import create_fading_circle


class Player:
    def __init__(self, pos: pygame.Vector2, game) -> None:
        self.pos: pygame.Vector2 = pos
        self.game = game  # Gameplay scene

        image: pygame.Surface = pygame.image.load("assets/bug_alpha.png")
        self.base_image = pygame.transform.scale(
            pygame.transform.rotate(image, -90), (64, 64)
        )
        self.base_image.blit(
            create_fading_circle(32, intensity=1.4),
            special_flags=pygame.BLEND_RGBA_MULT,
        )
        self.image_msr = Msr(images=(self.base_image,))

        self.projectiles = sprite.Group()
        self.shoot_timer = 1
        self.shootSound = pygame.mixer.Sound("assets/shoot.wav")
        self.shootSound.set_volume(0.25)

        self.angle: float = 0
        self.score: int = 0
        self.speed = 200
        self.health = 100

        grid = [  # hitbox shape
            [0, 1, 1, 0],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [0, 1, 1, 0],
        ]
        self._mask = pygame.Mask(self.base_image.get_size())
        x, y = 0, 0
        for row in grid:
            for _ in range(self.base_image.get_height() // len(grid)):
                for cell in row:
                    for _ in range(self.base_image.get_width() // len(row)):
                        if cell:
                            self._mask.set_at((x, y))
                        x += 1
                y += 1
                x = 0

        self.sfx_eat = pygame.mixer.Sound("audio/Footstep__009.ogg")
        self.sfx_eat.set_volume(1)

    @property
    def mask(self) -> pygame.mask.Mask:
        return self._mask

    @property
    def collide_rect(self) -> pygame.FRect:
        return self.base_image.get_frect(center=self.pos)

    def process_event(self, event: pygame.Event) -> None: ...

    def update(self, dt):
        mouse_pos = Button.mousepos[1]
        m_left, _, _ = Button.mouse[1]

        # mouse control
        # disabled mouse control, seemed awkward to have to shoot where you're flying towards
        #    - if touchscreen is wanted I'm thinking auto shoot.
        # vec_towards_mouse = mouse_pos - self.pos
        # vec_towards_mouse_normalized = vec_towards_mouse and vec_towards_mouse.normalize()
        # if vec_towards_mouse.length() > 5.0 and m_left:
        #     self.angle = vec_towards_mouse.angle_to(pygame.Vector2(1, 0))
        #     self.pos += vec_towards_mouse_normalized * self.speed * dt

        ##        else:  # keyboard control
        vec = pygame.Vector2(0, 0)

        rad = math.atan2(mouse_pos[1] - self.pos.y, mouse_pos[0] - self.pos.x)
        self.angle = -math.degrees(rad)
        vec.x = math.cos(rad)
        vec.y = math.sin(rad)

        self.pos += vec * self.speed * dt

        hit = self.game.handle_player_collisions()
        self.health -= bool(hit) * dt * 1

        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            self.shoot_timer += 0.1

            self.projectiles.add(
                Projectile(
                    self.game,
                    self.pos,
                    damage=20,
                    speed=800,
                    punchthrough=50,
                    lifetime=1.5,
                )
            )

            # play shooting sound
            self.shootSound.play()

    def draw(self) -> None:
        self.image_msr.draw(
            0, scale=(1, 1), pos=self.pos, relativeOffset=(0, 0), rotation=self.angle
        )


class Projectile(sprite.Sprite):
    image_msr = Msr()

    def __init__(self, game, pos, damage, speed, punchthrough, lifetime):
        super().__init__()
        self.game = game
        self.pos = pos.copy()
        self.damage = damage
        self.speed = speed
        self.punchthrough = punchthrough
        self.lifetime = lifetime

        self.scale = 2

        self.direction = (
            direction.normalize()
            if (direction := (-self.pos + Button.mousepos[1]))
            else pygame.Vector2(1, 0)
        )
        self.rotation = self.direction.angle_to(pygame.Vector2(1, 0))
        self.rects = Projectile.image_msr.rects(
            0,
            scale=(self.scale, self.scale),
            pos=self.pos,
            relativeOffset=(0, 0),
            rotation=self.rotation,
        )

    def update(self, mode):
        # this is why we cant have nice things
        match mode:
            case "draw":
                self.draw()
            case _:
                self.loop(mode)

    def loop(self, dt):
        self.pos += self.direction * self.speed * dt

        self.rects = Projectile.image_msr.rects(
            0,
            scale=(self.scale, self.scale),
            pos=self.pos,
            relativeOffset=(0, 0),
            rotation=self.rotation,
        )

        self.hit()

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()

    def hit(self):
        # damages Cell grid
        for grid_pos in self.game.get_colliding_cells(self.rects[0]):
            if grid_pos not in self.game.map:
                continue

            if self.game.rect_collides_at_grid_pos(self.rects[0], grid_pos):
                self.game.change_map_cell(*grid_pos, -self.damage)
                self.punchthrough -= 1

        if self.punchthrough <= 0:
            self.kill()

    def draw(self):
        rendered = Projectile.image_msr.draw_only(0, self.rects)
        if not rendered:
            self.kill()
