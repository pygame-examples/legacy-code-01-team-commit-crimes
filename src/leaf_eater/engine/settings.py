import sys

import pygame

IS_WEB: bool = sys.platform in ["wasi", "emscriptem"]
FPS: int = 60

LOGICAL_SIZE = pygame.Vector2(640, 640)
WINDOW_SIZE = LOGICAL_SIZE * 2
WINDOW: pygame.Window

EDGE: int = 6
BLOCK_SIZE: int = 8
