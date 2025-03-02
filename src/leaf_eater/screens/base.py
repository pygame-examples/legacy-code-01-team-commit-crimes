import pygame


class Screen:
    """Base Screen class"""

    def startup(self):
        pass

    def process_event(self, event: pygame.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, dest: pygame.Surface) -> None:
        pass
