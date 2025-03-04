import sys
import os.path

import pygame
from pygame._sdl2.video import Renderer

IS_WEB: bool = sys.platform in ["wasi", "emscriptem"]
FPS: int = 60

LOGICAL_SIZE_RECT = pygame.Rect(0, 0, 640, 640)
WINDOW_SIZE = pygame.Vector2(640, 640)
WINDOW: pygame.Window
RENDERER: Renderer

EDGE: int = 3
BLOCK_SIZE: int = 8

CONTROLS = {'Up': pygame.K_w,
            'Down': pygame.K_s,
            'Left': pygame.K_a,
            'Right': pygame.K_d,
            'Ok': pygame.K_SPACE,
            'Esc': pygame.K_ESCAPE,
            }

ASSETSPATH = os.path.join(os.path.dirname(os.path.abspath(__name__)), 'assets')
