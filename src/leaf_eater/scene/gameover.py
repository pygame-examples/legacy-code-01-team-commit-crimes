import pygame

from ..engine import events
from ..engine import settings as s
from ..farkas_tools.buttons import Button
from ..farkas_tools.multi_sprite_renderer_hardware import MultiSprite as Msr
from ..farkas_tools.UIblock import UIblock
from . import Scene


class GameOver(Scene):
    """Game Over Screen"""

    redirects: dict[str, type[Scene]] = {}  # "circular imports"

    def __init__(self):
        self.white_font = Msr(
            folders=(s.ASSETSPATH,), font="MonospaceTypewriter", size=40
        )
        self.ui_button = UIblock(
            Msr((s.ASSETSPATH,), names=("ui_button",)),
            (5, 7),
            (5, 7),
            0,
            True,
            scale=(2, 2),
        )

        self.back_btn = Button(
            Msr((s.ASSETSPATH,), names=("placeholder",)),
            scale=(1.6, 0.5),
            pos=(120, 350),
            popup=(1.1, 1.1),
        )
        self.buttons = (self.back_btn,)
        Button.bridgelink(self.buttons, horisontal=False)

        # Play gameover sound
        pygame.mixer.music.stop()

        gameOverSound = pygame.mixer.Sound("assets/gameover.wav")
        gameOverSound.play()

    def startup(self):
        Button.selectedB = self.back_btn

    def process_event(self, event: pygame.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        Button.select(self.buttons)
        for button in self.buttons:
            button.update("check")

        if self.back_btn.clicked:
            pygame.event.post(
                pygame.event.Event(events.SET_SCREEN, screen=self.redirects["intro"])
            )

    def render(self) -> None:
        self.white_font.write("Game Over", scale=(2, 2), pos=(100, 150))

        box = self.back_btn.rects_only()[0]
        self.ui_button.draw(box)
        self.white_font.write("Back", pos=box.center, relativeOffset=(0, 0))
