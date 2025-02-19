import sys
import asyncio
import pygame

# /// script
# dependencies = [
#  "pygame-ce",
#  "numpy",
# ]
# ///

import src.engine.settings as settings
from src.engine.game import Game
from src.screens.intro import Intro
from src.screens.gameplay import GamePlay

if __name__ == "__main__":
    if len(sys.argv) > 1 and not settings.isweb:
        settings.fullscreen = sys.argv[1] == "full"

    pygame.init()
    if settings.fullscreen:
        settings.window = pygame.display.set_mode(
            settings.screensize, flags=pygame.FULLSCREEN | pygame.SCALED
        )
    else:
        settings.window = pygame.display.set_mode(settings.screensize)

    pygame.display.set_caption("Pass-the-code: commit-crimes")

    settings.f_fw = pygame.font.Font("graphics/MonospaceTypewriter.ttf", 12)

    settings.STATES = {
        "Intro": Intro(),
        "GamePlay": GamePlay(),
        "Winner": None,
    }

    game = Game()
    asyncio.run(game.run())
