import pygame

from ..engine import events, settings as s
from ..objects.ui import Text
from . import GamePlay, Scene
from ..farkas_tools.multi_sprite_renderer_hardware import MultiSprite as Msr
from ..farkas_tools.buttons import Button
from ..farkas_tools.UIblock import UIblock




class Intro(Scene):
    """Intro Screen"""

    def __init__(self):
        self.white_font = Msr(folders=(s.ASSETSPATH,), font="MonospaceTypewriter", size=40)
        self.ui_button = UIblock(Msr((s.ASSETSPATH,), names=("ui_button",)), (5, 7), (5, 7), 0, True, scale=(2, 2))

        self.start_btn = Button(Msr((s.ASSETSPATH,), names=("placeholder",)), scale=(1.6, 0.5), pos=(120, 350), popup=(1.1, 1.1))
        self.quit_btn = Button(Msr((s.ASSETSPATH,), names=("placeholder",)), scale=(1.6, 0.5), pos=(120, 430), popup=(1.1, 1.1))
        self.buttons = self.start_btn, self.quit_btn
        Button.bridgelink(self.buttons, horisontal=False)

        #play theme music once
        pygame.mixer.music.load("assets/themeWithFades.wav")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(1)

    def startup(self):
        Button.selectedB = self.start_btn

    def process_event(self, event: pygame.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        Button.select(self.buttons)
        for button in self.buttons:
            button.update("check")

        if self.start_btn.clicked:
            pygame.event.post(pygame.event.Event(events.SET_SCREEN, screen=GamePlay))

        if self.quit_btn.clicked or Button.keys((s.CONTROLS["Esc"],))[0]:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def render(self) -> None:
        self.white_font.write("Infestation", scale=(2, 2), pos=(100, 150))

        box = self.start_btn.rects_only()[0]
        self.ui_button.draw(box)
        self.white_font.write("Play", pos=box.center, relativeOffset=(0, 0))

        box = self.quit_btn.rects_only()[0]
        self.ui_button.draw(box)
        self.white_font.write("Quit", pos=box.center, relativeOffset=(0, 0))
