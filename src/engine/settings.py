import sys
import pygame
from src.screens.gameplay import GamePlay
from src.screens.intro import Intro

isweb: bool = sys.platform in ["wasi", "emscriptem"]
fps: int = 60

screensize: pygame.math.Vector2
screensize = pygame.Vector2(1024, 768)
blocksize: int = 16
edge: int = 6
pe2 = blocksize
ctrlrect = pygame.Rect(pe2, pe2, screensize[0] - 2 * pe2, screensize[1] - 2 * pe2)

VERSION: float = 0.1
COMPATABLE_VERSIONS: list[float] = []

start_state: str = "Intro"

fullscreen: bool = False

window: pygame.surface.Surface
f_fw: pygame.font.Font
STATES: dict[str, Intro | GamePlay]
