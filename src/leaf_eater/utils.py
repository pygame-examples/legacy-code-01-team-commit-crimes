import numpy as np
import pygame


def create_fading_circle(radius, intensity=1.0):
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
                surface.set_at((x, y), (255, 255, 255, min(alpha * intensity, 255)))

    return surface
