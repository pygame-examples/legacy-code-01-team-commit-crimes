from itertools import cycle

import numpy as np
import pygame
from pygame._sdl2.video import Renderer, Texture

pygame.init()
screen = pygame.Window()
renderer = Renderer(screen, accelerated=1)
clock = pygame.Clock()


def create_fading_circle(radius):
    """
    Creates a Pygame surface with a circle where the alpha decreases from 255 at the center to 0 at the edge.

    :param radius: Radius of the circle
    :return: A Pygame surface with the fading circle
    """
    diameter = int(radius * 2)
    surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)

    for y in range(diameter):
        for x in range(diameter):
            dx = x - radius
            dy = y - radius
            distance = np.sqrt(dx**2 + dy**2)
            if distance <= radius:
                alpha = max(0, int(255 * (1 - distance / radius)))
                surface.set_at((x, y), (255, 255, 255, alpha))

    return surface


surf = pygame.image.load("assets/bug_alpha.png")
surf = pygame.transform.scale_by(surf, 0.25)

bloom = create_fading_circle(surf.get_width() / 2)
size = surf.get_size()
surf.blit(bloom, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

texture = Texture.from_surface(renderer, surf)

temp = pygame.Surface((300, 200))
temp.fill("green")
rectangle = Texture.from_surface(renderer, temp)


temp = pygame.Surface(screen.size, pygame.SRCALPHA)
temp.fill("black")
temp.set_alpha(200)
overlay = Texture.from_surface(renderer, temp)

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            raise SystemExit
    renderer.clear()

    renderer.blit(rectangle, pygame.Rect(300, 200, 300, 200))
    renderer.blit(overlay, pygame.Rect(0, 0, *screen.size))
    renderer.blit(texture, pygame.Rect(100, 100, *size))

    renderer.present()
