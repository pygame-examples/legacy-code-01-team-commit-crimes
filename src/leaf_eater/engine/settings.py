import sys
import os.path

import pygame
from pygame._sdl2.video import Renderer

IS_WEB: bool = sys.platform in ["wasi", "emscriptem"]
FPS: int = 60

LOGICAL_SIZE_RECT = pygame.Rect(0, 0, 640, 640)  # should not be changed
WINDOW_SIZE = pygame.Vector2(640, 640)
WINDOW: pygame.Window
RENDERER: Renderer

EDGE: int = 3
BLOCK_SIZE: int = 8

CONTROLS = {'W': pygame.K_w,
            'S': pygame.K_s,
            'A': pygame.K_a,
            'D': pygame.K_d,
            'Up': pygame.K_UP,
            'Down': pygame.K_DOWN,
            'Left': pygame.K_LEFT,
            'Right': pygame.K_RIGHT,
            'Ok': pygame.K_SPACE,
            'Esc': pygame.K_ESCAPE,
            }

ASSETSPATH = os.path.join(os.path.dirname(os.path.abspath(__name__)), 'assets')
