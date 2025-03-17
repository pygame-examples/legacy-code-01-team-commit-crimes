import pygame


class Scene:
    """Base Screen class"""

    redirects: dict[str, type[None]]  # "circular imports"

    def startup(self):
        pass

    def process_event(self, event: pygame.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self) -> None:
        pass
