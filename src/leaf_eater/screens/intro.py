import pygame

from ..engine import events
from ..objects.ui import Text
from . import GamePlay, Screen


class Intro(Screen):
    """Intro Screen"""

    def __init__(self):
        self.game_name = Text("Game", (100, 150), font_size=80)
        self.start_btn = Text("Start", (100, 350), is_selectable=True, font_size=40)

    def startup(self):
        pass

    def process_event(self, event: pygame.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_btn.check_select(event.pos):
                pygame.event.post(pygame.event.Event(events.SET_SCREEN, screen=GamePlay))

    def update(self, dt: float) -> None:
        pass

    def render(self, dest: pygame.Surface) -> None:
        dest.fill("black")

        self.game_name.render(dest)
        self.start_btn.render(dest)
