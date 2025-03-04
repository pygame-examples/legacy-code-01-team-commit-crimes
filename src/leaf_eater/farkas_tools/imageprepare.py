import pygame
import os.path


def surftostr(surf: pygame.Surface, compress=2):
    multi = compress
    w = surf.get_width()
    h = surf.get_height()
    colors = []
    pixls = []

    for y in range(h):
        for x in range(w):
            col = tuple(surf.get_at((x, y)))

            if col not in colors:
                pixls.append(str(len(colors)))
                colors.append(col)
            else:
                for k, v in enumerate(colors):
                    if v == col:
                        pixls.append(str(k))

    pixlstr = "".join(pixls)
    string = ""
    for i in range(0, len(pixlstr)-len(pixlstr)%multi, multi):
        string += chr(int(pixlstr[i:i+multi])+32)

    if len(pixlstr)%multi != 0:
        string += chr(int(pixlstr[-len(pixlstr)%multi]+('0'*(multi-len(pixlstr)%multi)))+32)

    return colors, (w, h, compress), string


def strtosurf(string):
    w, h, multi = string[1]
    colors = string[0]
    pixlstr = string[2]
    surf = pygame.Surface((w, h), flags=pygame.SRCALPHA)

    for i in range(len(pixlstr)):
        num = str(ord(pixlstr[i])-32)
        cols = (multi-len(num))*'0'+num

        for m in range(multi):
            x = (i*multi+m) % w
            y = (i*multi+m)//w

            if x < w and y < h:
                surf.set_at((x, y), colors[int(cols[m])])
            else:
                break

    return surf


def paletteswap(string, palette):
    for x in range(len(string[0])):
        if len(palette) > x:
            string[0][x] = palette[x]
        else:
            break
    return string


def surf_slicer(width, height, wpad=0, hpad=0, outputlist=None, folders=(), name='', surface=None):
    if width <= 0 or height <= 0:
        raise Exception('need area!')

    if surface is None:
        img = pygame.image.load(os.path.join(*folders, name + '.png'))
    else:
        img = surface
    imgh = img.get_height()
    col = 0
    if outputlist is None:
        outputlist = []

    while imgh // height > 0:
        imgw = img.get_width()
        row = 0
        while imgw//width > 0:
            imgw -= width+wpad
            surface = img.subsurface(pygame.Rect(row * width + wpad, col * height + hpad, width, height))
            outputlist.append(surface)
            row += 1

        imgh -= height + hpad
        col += 1

    return outputlist


def imageload(folder, name):
    return pygame.image.load(os.path.join(folder, name + '.png'))
