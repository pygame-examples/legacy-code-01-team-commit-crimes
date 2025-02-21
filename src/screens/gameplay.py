import pygame
import src.engine.settings as settings
from src.objects.txt_item import Txt_item, draw_text
from src.objects.player import Player
from src.engine.make_map import get_blocks


class GamePlay:
    """Main game code"""

    def __init__(self):
        self.quit: bool = False
        self.done: bool = False
        self.next_state: str = "GamePlay"

        startxy = settings.edge * settings.blocksize // 2
        self.player: Player = Player(pygame.Vector2(startxy, startxy))

        self.score: int
        self.score_text: Txt_item = Txt_item("Score:", (100, 30))

        self.background: pygame.Surface = pygame.Surface(settings.screensize)
        self.background.fill(pygame.Color("black"))
        pygame.draw.rect(
            self.background, pygame.Color("red"), settings.ctrlrect, width=1
        )

        bs = settings.blocksize
        edge = settings.edge
        dx = int(settings.screensize[0]) // bs - edge * 2
        dy = int(settings.screensize[1]) // bs - edge * 2
        self.food = get_blocks(dx, dy, edge)

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

    def draw(self, window):
        window.blit(self.background, (0, 0))

        bs = settings.blocksize
        for y in range(self.food.shape[0]):
            for x in range(self.food.shape[1]):
                if self.food[y, x]:
                    r = pygame.Rect(x * bs, y * bs, bs - 1, bs - 1)
                    pygame.draw.rect(self.background, pygame.Color("white"), r)

        self.score_text.render(window)

        self.player.draw(window)
