import pygame

from ..engine import settings
from ..farkas_tools.multi_sprite_renderer_hardware import MultiSprite as Msr


class Player:
    def __init__(self, pos: pygame.Vector2) -> None:
        self.pos: pygame.Vector2 = pos

        image: pygame.Surface = pygame.image.load("assets/bug_alpha.png").convert_alpha()
        self.base_image = pygame.transform.scale(pygame.transform.rotate(image, -90), (64, 64))
        self.image_msr = Msr(images=(self.base_image,))

        self.angle: float = 0
        self.score: int = 0
        self.speed = 150

        grid = [
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
        pass

    def render(self) -> None:
        self.image_msr.draw(0, scale=(1, 1), pos=self.pos, relativeOffset=(0, 0), rotation=self.angle)
