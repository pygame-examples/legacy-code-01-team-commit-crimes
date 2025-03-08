'''
This is the non _sdl2 variant with caching.
'''

import math
import pygame
from os.path import join


def rotated_collision(rect1, rect2):
    # input 2 rects with a rotations: [Rect, rot]
    # draw or rests first 2 return elements can be used with another

    rect1 = (pygame.Vector2(rect1[0].center), pygame.Vector2(rect1[0].topleft) - rect1[0].center), rect1[1]
    rect2 = (pygame.Vector2(rect2[0].center), pygame.Vector2(rect2[0].topleft) - rect2[0].center), rect2[1]
    rec = (rect1, rect2)
    for x in (0, 1):
        center = (rec[1-x][0][0]-rec[0-x][0][0]).rotate(rec[0-x][1])
        r = abs((rec[0-x][1] - rec[1-x][1] + 90) % 180 - 90)
        edges = (abs((rec[1-x][0][1].rotate(r)).elementwise()),
                 abs((rec[1-x][0][1].rotate(-r)).elementwise()))

        for y in (0, 1):
            if not ((-edges[1 - y][y] <= rec[0-x][0][1][y]-center[y] <= edges[1 - y][y]) or
                    (rec[0-x][0][1][y] <= -edges[1 - y][y]+center[y] <= -rec[0-x][0][1][y])):
                return False
    return True


class MultiSprite:
    screen = None
    screenrect = None
    toblit = []
    rect = pygame.Rect()

    @classmethod
    def setScreen(cls, screen: pygame.Surface):
        cls.screen = screen
        cls.screenrect = screen.get_rect()
        cls.screenrect.x, cls.screenrect.y = 0, 0

    @classmethod
    def flip(cls):
        # has to be in main loop before pygame.display.update() !
        # will draw above any non MSR draws

        cls.screen.fblits(cls.toblit)
        cls.toblit.clear()

    def __call__(self, folders=(), names=(), images=(), font=None, size=50, bold=False, italic=False, color='White', background=None, AA=False):
        self.__init__(folders=folders, names=names, images=images, font=font, size=size, bold=bold, italic=italic, color=color, background=background, AA=AA)

    def __init__(self, folders=(), names=(), images=(), font=None, size=50, bold=False, italic=False, color='White', background=None, AA=False):
        # file names come before images in indexing
        # don't mix names and images with font

        self.sprites = {}

        for k, name in enumerate(names):
            img = pygame.image.load(join(*folders, name + '.png')).convert_alpha()
            rect = img.get_rect()

            self.sprites[k] = (img, rect)

        num = len(self.sprites)

        for k, img in enumerate(images):
            img = img.convert_alpha()
            rect = img.get_rect()

            self.sprites[k+num] = (img, rect)

        if not names and not images:
            self.size = size
            self.bold = bold
            self.italic = italic
            self.color = color
            self.background = background
            self.AA = AA
            self.font = pygame.font.Font(join(*folders, font + '.ttf'), size)
            self.font.set_bold(bold)
            self.font.set_italic(italic)

            for char in ' !"#$%& \'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~\n':
                img = self.font.render(char, AA, color, background).convert_alpha()
                rect = img.get_rect()

                self.sprites[char] = (img, rect)

    def draw(self, name=0, scale=(1, 1), pos=(0, 0), relativeOffset=(-0.5, -0.5), offset=(0, 0), rotation=0, flip=(0, 0), alpha=1):
        # name = sprite index in order, scale relative, pos = origin point
        # relativeOffset relative shift from pos works with rotation, (-0.5, -0.5)=topleft, (0, 0)=center
        # offset pixel shift from pos works with rotation
        # returns: rect of drawn sprite with rotation, fully encapsulating rect, if it was drawn

        rotation = round(rotation - (rotation % 3)) % 360
        scale = round(scale[0], 2), round(scale[1], 2)
        alpha = round(alpha*51)

        rect = MultiSprite.rect
        rect.scale_by_ip(*scale)
        size = pygame.Vector2(rect.size)
        topleft = -pygame.Vector2(size.x * relativeOffset[0] + offset[0], size.y * relativeOffset[1] + offset[1]).rotate(-rotation) + size // -2 + pos
        rect.topleft = math.floor(topleft.x + 0.00001), math.floor(topleft.y + 0.00001)

        r = abs((rotation+90)%180-90)
        area = pygame.Vector2(rect.size)
        absrect = pygame.Rect()
        absrect.size = area.rotate(-r).x, area.rotate(r).y
        absrect.center = rect.center

        if rendered := MultiSprite.screenrect.colliderect(absrect) and alpha:

            try:
                MultiSprite.toblit.append((self.sprites[(name, *scale, rotation, *flip, alpha)], absrect.topleft))
            except KeyError:
                img = self.sprites[name][0].copy()
                img.set_alpha(alpha*5)
                img = pygame.transform.flip(img, *flip)
                img = pygame.transform.scale(img, (rect.w, rect.h))
                img = pygame.transform.rotate(img, rotation)

                self.sprites[(name, *scale, rotation, *flip, alpha)] = img
                MultiSprite.toblit.append((img, absrect.topleft))

        '''pygame.draw.rect(self.renderer, (255, 0, 255, 0), (pos, (5, 5)), width=1)
        pygame.draw.rect(self.renderer, (0, 0, 255, 0), absrect, width=1)
        pygame.draw.rect(self.renderer, (0, 255, 0, 0), rect, width=1)'''

        return rect, rotation, absrect, rendered

    def rects(self, name=0, scale=(1, 1), pos=(0, 0), relativeOffset=(-0.5, -0.5), offset=(0, 0), rotation=0, *args, **kwargs):
        # returns: rect of drawn sprite with rotation, fully encapsulating rect, if it would be drawn

        rotation = round(rotation - (rotation % 3)) % 360
        scale = round(scale[0], 2), round(scale[1], 2)

        rect = pygame.Rect()  # MultiSprite.rect
        rect.size = self.sprites[name][1].size
        rect.scale_by_ip(*scale)
        size = pygame.Vector2(rect.size)
        topleft = -pygame.Vector2(size.x * relativeOffset[0] + offset[0], size.y * relativeOffset[1] + offset[1]).rotate(-rotation) + size // -2 + pos
        rect.topleft = math.floor(topleft.x + 0.00001), math.floor(topleft.y + 0.00001)

        r = abs((rotation + 90) % 180 - 90)
        area = pygame.Vector2(rect.size)
        absrect = pygame.Rect()
        absrect.size = area.rotate(-r).x, area.rotate(r).y
        absrect.center = rect.center

        return rect, rotation, absrect, MultiSprite.screenrect.colliderect(absrect)

    def draw_only(self, name, rects, scale, flip=(0, 0), alpha=1, *args, **kwargs):
        # needs rects from draw or rects also the scale that was used there
        # returns: if it was rendered

        scale = round(scale[0], 2), round(scale[1], 2)
        alpha = round(alpha * 51)

        if rendered := MultiSprite.screenrect.colliderect(rects[2]) and alpha:

            try:
                MultiSprite.toblit.append((self.sprites[(name, *scale, rects[1], *flip, alpha)], rects[2].topleft))
            except KeyError:
                img = self.sprites[name][0].copy()
                img.set_alpha(alpha * 5)
                img = pygame.transform.flip(img, *flip)
                img = pygame.transform.scale(img, (rects[0].w, rects[0].h))
                img = pygame.transform.rotate(img, rects[1])

                self.sprites[(name, *scale, rects[1], *flip, alpha)] = img
                MultiSprite.toblit.append((img, rects[2].topleft))

        return rendered

    def add_char(self, char):
        # automatic, don't use
        img = self.font.render(char, self.AA, self.color, self.background).convert_alpha()
        rect = img.get_rect()

        self.sprites[char] = (img, rect)

    def write(self, text='', scale=(1, 1), pos=(0, 0), relativeOffset=(-0.5, -0.5), align=1, rotation=0, flip=(0, 0), alpha=1):
        # scaled from original given font size. pos = origin point
        # rotation rotates whole text, flip applied to characters

        width = 0
        enter = 0
        lines = text.split('\n')
        y = relativeOffset[1] * len(lines) + (len(lines) - 1) * 0.5

        linewidths = list(0 for _ in range(len(lines)))
        for k, line in enumerate(lines):
            for char in line:
                try:
                    linewidths[k] += int(self.sprites[char][1].w * scale[0])
                except KeyError:
                    self.add_char(char)
                    linewidths[k] += int(self.sprites[char][1].w * scale[0])
        widest = max(linewidths)

        if align == 1:  # left
            pos = (pos[0] + (widest * (-relativeOffset[0] - 0.5)), pos[1])
        elif align == -1:  # right
            pos = (pos[0] + (widest * (-relativeOffset[0] + 0.5)), pos[1])
        elif align == 0:  # center
            pos = (pos[0] + (widest * (-relativeOffset[0])), pos[1])

        for lk, line in enumerate(lines):
            for k, char in enumerate(line):
                if align == 1:  # left
                    w = int(self.sprites[line[k]][1].w * scale[0])
                    self.draw(name=line[k], scale=scale, pos=pos,
                              relativeOffset=(width / w - 0.5, y - enter / self.sprites[line[k]][1].h),
                              rotation=rotation, flip=flip, alpha=alpha)
                    width -= w

                elif align == -1:  # right
                    w = int(self.sprites[line[-k - 1]][1].w * scale[0])
                    self.draw(name=line[-k - 1], scale=scale, pos=pos,
                              relativeOffset=(width / w + 0.5, y - enter / self.sprites[line[-k - 1]][1].h),
                              rotation=rotation, flip=flip, alpha=alpha)
                    width += w

                elif align == 0:  # center
                    w = int(self.sprites[line[k]][1].w * scale[0])
                    self.draw(name=line[k], scale=scale, pos=pos,
                              relativeOffset=(width / w - 0.5, y - enter / self.sprites[line[k]][1].h),
                              offset=(linewidths[lk] * 0.5, 0), rotation=rotation, flip=flip, alpha=alpha)
                    width -= w

            width = 0
            enter += self.sprites['A'][1].h

        return linewidths

    def write_clamped(self, text='', width=1, scale=(1, 1), pos=(0, 0), relativeOffset=(-0.5, -0.5), align=1, rotation=0, flip=(0, 0), alpha=1):
        # scaled from original given font size. pos = origin point
        # rotation rotates whole text, flip applied to characters

        current_line = ""
        current_width = 0
        result = ""
        for char in text:
            try:
                char_w = int(self.sprites[char][1].w * scale[0])
            except KeyError:
                self.add_char(char)
                char_w = int(self.sprites[char][1].w * scale[0])
            # Check if adding this character would exceed the max_width
            if current_width + char_w > width:
                # Find the last space in the current line to break the line
                last_space_index = current_line.rfind(' ')
                if last_space_index != -1:
                    # Break the line at the last space
                    result += current_line[:last_space_index] + '\n'
                    # Start the new line with the remainder after the space
                    current_line = current_line[last_space_index + 1:] + char
                    current_width = sum(int(self.sprites[char][1].w * scale[0]) for c in current_line)
                else:
                    # No spaces, force break the line
                    result += current_line + '\n'
                    if char != ' ':
                        current_line = char
                        current_width = char_w
                    else:
                        current_line = ''
                        current_width = 0
            else:
                current_line += char
                current_width += char_w
        # Add the remaining line if there's any text left
        result += current_line

        lines = result.split('\n')
        y = relativeOffset[1] * len(lines) + (len(lines) - 1) * 0.5

        linewidths = list(0 for line in range(len(lines)))
        for k, line in enumerate(lines):
            for char in line:
                linewidths[k] += int(self.sprites[char][1].w * scale[0])
        widest = max(linewidths)

        if align == 1:  # left
            pos = (pos[0] + (widest * (-relativeOffset[0] - 0.5)), pos[1])
        elif align == -1:  # right
            pos = (pos[0] + (widest * (-relativeOffset[0] + 0.5)), pos[1])
        elif align == 0:  # center
            pos = (pos[0] + (widest * (-relativeOffset[0])), pos[1])

        width = 0
        enter = 0
        for lk, line in enumerate(lines):
            for k, char in enumerate(line):
                if align == 1:  # left
                    w = int(self.sprites[line[k]][1].w * scale[0])
                    self.draw(name=line[k], scale=scale, pos=pos,
                              relativeOffset=(width / w - 0.5, y - enter / self.sprites[line[k]][1].h),
                              rotation=rotation, flip=flip, alpha=alpha)
                    width -= w

                elif align == -1:  # right
                    w = int(self.sprites[line[-k - 1]][1].w * scale[0])
                    self.draw(name=line[-k - 1], scale=scale, pos=pos,
                              relativeOffset=(width / w + 0.5, y - enter / self.sprites[line[-k - 1]][1].h),
                              rotation=rotation, flip=flip, alpha=alpha)
                    width += w

                elif align == 0:  # center
                    w = int(self.sprites[line[k]][1].w * scale[0])
                    self.draw(name=line[k], scale=scale, pos=pos,
                              relativeOffset=(width / w - 0.5, y - enter / self.sprites[line[k]][1].h),
                              offset=(linewidths[lk] * 0.5, 0), rotation=rotation, flip=flip, alpha=alpha)
                    width -= w

            width = 0
            enter += self.sprites['A'][1].h

        return linewidths

    def __len__(self):
        return len(self.sprites)
