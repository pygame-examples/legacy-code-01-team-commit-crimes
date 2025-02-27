import pygame

from ..engine import settings
from ..engine.make_map import get_blocks2
from ..objects.player import Player
from ..objects.ui import Text


class GamePlay:
    """Main game code"""

    def __init__(self):
        self.player: Player = Player(pygame.Vector2())
        self.score_text = Text("Score: 0", (100, 30))

    def startup(self):
        pass

    def process_event(self, event: pygame.Event) -> None:
        self.player.process_event(event)

    def update(self, dt: float) -> None:
        self.player.update(dt)
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
