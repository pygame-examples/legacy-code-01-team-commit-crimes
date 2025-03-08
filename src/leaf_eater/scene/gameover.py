import pygame

from ..engine import events, settings as s
from . import Scene
from ..farkas_tools.multi_sprite_renderer_hardware import MultiSprite as Msr
from ..farkas_tools.buttons import Button


class GameOver(Scene):
    """Game Over Screen"""
    redirects: dict[str, type(Scene)] = {}  # "circular imports"

    def __init__(self):
        self.white_font = Msr(folders=(s.ASSETSPATH,), font="MonospaceTypewriter", size=40)

        self.back_btn = Button(Msr((s.ASSETSPATH,), names=("placeholder",)), scale=(1.6, 0.5), pos=(120, 350), popup=(1.1, 1.1))
        self.buttons = self.back_btn,
        Button.bridgelink(self.buttons, horisontal=False)

    def startup(self):
        Button.selectedB = self.back_btn

    def process_event(self, event: pygame.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        Button.select(self.buttons)
        for button in self.buttons:
            button.update("check")

        if self.back_btn.clicked:
            pygame.event.post(pygame.event.Event(events.SET_SCREEN, screen=self.redirects["intro"]))

    def render(self) -> None:
        self.white_font.write("Game Over", scale=(2, 2), pos=(100, 150))

        box = self.back_btn.update("draw")[0]
        self.white_font.write("Back", pos=box.center, relativeOffset=(0, 0))

