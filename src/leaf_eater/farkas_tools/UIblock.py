import math
import pygame
from .multi_sprite_renderer_hardware import MultiSprite as Msr


def box_slicer(topleft_wh: pygame.Vector2, bottomright_wh: pygame.Vector2, rect: pygame.Rect, scale=(1, 1)):
    scale = pygame.Vector2(scale)
    topleft_wh = pygame.Vector2(topleft_wh.x*scale[0], topleft_wh.y*scale[1])
    bottomright_wh = pygame.Vector2(bottomright_wh.x*scale[0], bottomright_wh.y*scale[1])
    outputlist = (
                  p1 := pygame.Rect(rect.topleft, topleft_wh),
                  p2 := pygame.Rect(p1.topright, (rect.w-topleft_wh.x-bottomright_wh.x, topleft_wh.y)),
                  p3 := pygame.Rect(p2.topright, (bottomright_wh.x, topleft_wh.y)),
                  p8 := pygame.Rect(p1.bottomleft, (topleft_wh.x, rect.h-topleft_wh.y-bottomright_wh.y)),
                  p9 := pygame.Rect(p1.bottomright, (p2.w, p8.h)),
                  p4 := pygame.Rect(p3.bottomleft, (p3.w, p8.h)),
                  p7 := pygame.Rect(p8.bottomleft, (p1.w, bottomright_wh.y)),
                  p6 := pygame.Rect(p7.topright, (p2.w, p7.h)),
                  p5 := pygame.Rect(p6.topright, bottomright_wh)
    )

    return outputlist


class UIblock:
    def __init__(self, msr, topleft_wh, bottomright_wh, name=0, include_border=True, wh=(100, 100), scale=(1, 1), pos=(0, 0), relativeOffset=(-0.5, -0.5), alpha=1):
        """
        topleft_wh defines the top and left border's width and height
        bottomright_wh defines the bottom and right border's width and height
        wh=rect size
        include_border = border's size will be or not included in the wh rect size
        scale scales the borders size
        """
        self.msr = msr
        self.include_border = include_border
        self._topleft_wh = pygame.Vector2(topleft_wh)
        self._bottomright_wh = pygame.Vector2(bottomright_wh)
        self.width, self.height = wh

        self._name = name
        self.scale = scale
        self.pos = pygame.Vector2(pos)
        self.relativeOffset = relativeOffset
        self.alpha = alpha

        self.parts = self._repart()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.parts = self._repart()

    @property
    def topleft_wh(self):
        return self._topleft_wh

    @topleft_wh.setter
    def topleft_wh(self, value):
        self._topleft_wh = value
        self.parts = self._repart()

    @property
    def bottomright_wh(self):
        return self._bottomright_wh

    @bottomright_wh.setter
    def bottomright_wh(self, value):
        self._bottomright_wh = value
        self.parts = self._repart()

    def _repart(self):
        return box_slicer(self.topleft_wh, self.bottomright_wh, pygame.Rect(0, 0, self.msr.sprites[self.name][1].w, self.msr.sprites[self.name][1].h))

    def drawpart(self, source, dest):
        if Msr.screenrect.colliderect(dest):
            self.msr.sprites[self.name][0].draw(srcrect=source, dstrect=dest)


    def draw(self, rect=None):
        """
        if rect is given it will be used as destination
        """
        if rect is None:

            rect = pygame.Rect(0, 0, self.width, self.height)
            size = pygame.Vector2(rect.size)
            topleft = -pygame.Vector2(size.x * self.relativeOffset[0], size.y * self.relativeOffset[1]) + size // -2 + self.pos
            rect.topleft = math.floor(topleft.x + 0.00001), math.floor(topleft.y + 0.00001)

        if self.include_border:
            dests = box_slicer(self.topleft_wh, self.bottomright_wh, rect, self.scale)

            if self.alpha > 0:
                alpha = 255 * self.alpha
                for k, source in enumerate(self.parts):
                    self.msr.sprites[self.name][0].alpha = alpha
                    self.drawpart(source, dests[k])

            return dests[4]

        else:
            outer = pygame.Rect((rect.x-self.topleft_wh.x*self.scale[0], rect.y-self.topleft_wh.y*self.scale[1]),
                                (rect.w+(self.topleft_wh.x+self.bottomright_wh.x)*self.scale[0], rect.h+(self.topleft_wh.y+self.bottomright_wh.y)*self.scale[1]))

            dests = box_slicer(self.topleft_wh, self.bottomright_wh, outer, self.scale)

            if self.alpha > 0:
                alpha = 255 * self.alpha
                for k, source in enumerate(self.parts):
                    self.msr.sprites[self.name][0].alpha = alpha
                    self.drawpart(source, dests[k])

            return outer
