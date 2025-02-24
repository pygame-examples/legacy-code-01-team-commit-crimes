import pygame

import src.engine.settings as settings
from src.engine.make_map import get_blocks2
from src.objects.player import Player
from src.objects.txt_item import Txt_item


class GamePlay:
    """Main game code"""

    def __init__(self):
        self.quit: bool = False
        self.done: bool = False
        self.next_state: str = "GamePlay"

        startxy = settings.edge * settings.blocksize // 2
        self.player: Player = Player(pygame.Vector2(startxy, startxy))

        self.score_text: Txt_item = Txt_item("Score: 0", (100, 30))

        self.background: pygame.Surface = pygame.Surface(settings.screensize)
        self.background.fill(pygame.Color("black"))
        pygame.draw.rect(self.background, pygame.Color("red"), settings.ctrlrect, width=1)

        bs = settings.blocksize
        edge = settings.edge
        dx = int(settings.screensize[0]) // bs - edge * 2
        dy = int(settings.screensize[1]) // bs - edge * 2
        self.food = get_blocks2(dx, dy, edge)

    def startup(self):
        pass

    def process_event(self, event):
        if event.type == pygame.QUIT:
            self.done = True
            self.quit = True
            return
        self.player.process_event(event)

    def update(self, dt):
        self.player.update(dt)
        self.score_text.change_text(f"Score:{self.player.score}")

    def draw(self, window):
        window.blit(self.background, (0, 0))

        bs = settings.blocksize
        for y in range(self.food.shape[0]):
            for x in range(self.food.shape[1]):
                if self.food[y, x]:
                    c = pygame.Color.from_hsva(self.food[y, x] + 60, 100, 100, 0)
                    r = pygame.Rect(x * bs, y * bs, bs, bs)
                    pygame.draw.rect(window, c, r)

        self.score_text.render(window)

        self.player.draw(window)
