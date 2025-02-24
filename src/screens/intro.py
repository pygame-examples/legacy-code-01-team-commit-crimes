import pygame

from src.objects.txt_item import Txt_item


class Intro:
    """Intro Screen"""

    def __init__(self):
        self.quit: bool = False
        self.done: bool = False
        self.next_state: str = "GamePlay"

        self.game_name: Txt_item = Txt_item("Game", ((100, 150)), fontsize=80)
        self.start_btn: Txt_item = Txt_item("Start", ((100, 350)), True, "start", fontsize=40)

    def startup(self):
        pass

    def process_event(self, event):
        if event.type == pygame.QUIT:
            self.done = True
            self.quit = True
            return
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_btn.check_select(event.pos):
                self.done = True

    def update(self, dt):
        pass

    def draw(self, window):
        window.fill(pygame.Color("black"))
        self.game_name.render(window)
        self.start_btn.render(window)
