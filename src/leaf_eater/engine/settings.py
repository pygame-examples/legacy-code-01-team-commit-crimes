import sys

import pygame

IS_WEB: bool = sys.platform in ["wasi", "emscriptem"]
FPS: int = 60

WINDOW_SIZE = pygame.Vector2(1024, 768)
LOGICAL_SIZE = pygame.Vector2(1024, 768)
WINDOW: pygame.Window

BLOCK_SIZE: int = 16
