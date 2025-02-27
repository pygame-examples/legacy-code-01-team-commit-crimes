from typing import Literal

import pygame


class Text:
    def __init__(
        self,
        text: str,
        position: pygame.Vector2 | tuple[float, float],
        *,
        is_selectable: bool = False,
        font_size: int = 20,
        anchor: Literal[
            "topleft", "midtop", "topright", "midright", "bottomright", "midbottom", "bottomleft", "midleft"
        ] = "topleft",
        font_family: str | None = None,
    ) -> None:
        self.text = text
        self.position = pygame.Vector2(position)
        self.color = "white"
        self.anchor = anchor

        if font_family is None:
            self.font = pygame.Font("graphics/MonospaceTypewriter.ttf", font_size)
        else:
            self.font = pygame.font.SysFont(font_family, font_size)

        self.is_selectable = is_selectable
        self.is_disabled = False

    @property
    def text_surface(self) -> pygame.Surface:
        return self.font.render(self.text, antialias=True, color=self.color)

    @property
    def rect(self) -> pygame.Rect:
        return self.text_surface.get_rect(**{self.anchor: self.position})

    @property
    def selector_rect(self) -> pygame.Rect:
        return self.rect.inflate(8, 8)

    def render(self, dest: pygame.Surface) -> None:
        dest.blit(self.text_surface, self.rect)

        if self.is_selectable:
            if self.is_disabled:
                pygame.draw.rect(dest, "gray20", self.selector_rect, width=2)
            else:
                pygame.draw.rect(dest, "white", self.selector_rect, width=2)

    def highlight(self, dest: pygame.Surface) -> None:
        pygame.draw.rect(dest, "orange", self.selector_rect, width=3)

    def disable(self):
        self.color = "gray20"
        self.is_disabled = True

    def enable(self):
        self.color = "white"
        self.is_disabled = False

    def check_select(self, position: pygame.Vector2) -> bool:
        can_be_selected = self.is_selectable and not self.is_disabled
        return can_be_selected and self.selector_rect.collidepoint(position)
