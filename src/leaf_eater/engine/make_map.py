from typing import Any

import numpy as np


# found on some website
def perlin(m: int, n: int, gridsize=5) -> Any:
    linx = np.linspace(0, gridsize, m, endpoint=False)
    liny = np.linspace(0, gridsize, n, endpoint=False)
    y, x = np.meshgrid(liny, linx)
    # permutation table
    p = np.arange(256, dtype=int)
    np.random.shuffle(p)
    p = np.stack([p, p]).flatten()
    # coordinates of the top-left
    xi = x.astype(int)
    yi = y.astype(int)
    # internal coordinates
    xf = x - xi
    yf = y - yi
    # fade factors
    u = fade(xf)
    v = fade(yf)
    # noise components
    n00 = gradient(p[p[xi] + yi], xf, yf)
    n01 = gradient(p[p[xi] + yi + 1], xf, yf - 1)
    n11 = gradient(p[p[xi + 1] + yi + 1], xf - 1, yf - 1)
    n10 = gradient(p[p[xi + 1] + yi], xf - 1, yf)
    # combine noises
    x1 = lerp(n00, n10, u)
    x2 = lerp(n01, n11, u)  # FIX1: I was using n10 instead of n01
    return lerp(x1, x2, v)  # FIX2: I also had to reverse x1 and x2 here


def lerp(a: Any, b: Any, t: Any) -> Any:
    """linear interpolation"""
    return a + t * (b - a)


def fade(t: Any) -> Any:
    """6t^5 - 15t^4 + 10t^3"""
    return 6 * t**5 - 15 * t**4 + 10 * t**3


def gradient(h: Any, x: Any, y: Any) -> Any:
    """grad converts h to the right gradient vector and return the dot product with (x,y)"""
    vectors = np.array([[0, 1], [0, -1], [1, 0], [-1, 0]])
    g = vectors[h % 4]
    return g[:, :, 0] * x + g[:, :, 1] * y


def get_blocks(m: int, n: int, edge: int) -> Any:
    obm = (perlin(n, m) > 0).astype(int)
    binmap = obm + np.vstack((np.zeros(obm.shape[1]), obm[:-1]))
    binmap = binmap + np.vstack((obm[1:], np.zeros(obm.shape[1])))
    binmap = binmap + np.hstack((np.zeros((obm.shape[0], 1)), obm[:, :-1]))
    binmap = binmap + np.hstack((obm[:, 1:], np.zeros((obm.shape[0], 1))))
    binmap[binmap < 2] = 0
    binmap = binmap * obm
    binmap = (binmap > 0).astype(int)

    if edge == 0:
        return binmap
    else:
        final = np.zeros((n + 2 * edge, m + 2 * edge))
        final[edge:-edge, edge:-edge] = binmap
        return final


def get_blocks2(m: int, n: int, edge: int) -> Any:
    nx, ny = m + 2 * edge, n + 2 * edge
    xs, ys = nx - 1, ny - 1
    x, y = np.meshgrid(
        np.linspace(0, xs, nx),
        np.linspace(0, ys, ny),
    )
    dlr = np.minimum(x, xs - x)
    dtb = np.minimum(y, ys - y)
    dedge = np.minimum(dlr, dtb)
    if edge > 0:
        dampen = (dedge * 0.6 / edge) - 1.2
    else:
        dampen = dedge * 0.6 - 1.2
    dampen[dampen > 0] = 0

    blocks = (170 * (perlin(ny, nx, 5) + perlin(ny, nx, 10)/2 + dampen)).astype(int)
    blocks[blocks < 0] = 0

    return blocks


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 3:
        m = int(sys.argv[1])
        n = int(sys.argv[2])
        edge = int(sys.argv[3])
    elif len(sys.argv) > 2:
        m = int(sys.argv[1])
        n = int(sys.argv[2])
        edge = 2
    elif len(sys.argv) > 1:
        m = int(sys.argv[1])
        n = m
        edge = 2
    else:
        m = 6
        n = 8
        edge = 2

    # display and playback test code
    screensize = (1024, 768)
    bs = 16
    edge = 6
    px = int(screensize[0] // bs - edge * 2)
    py = int(screensize[1] // bs - edge * 2)
    import pygame

    map = get_blocks(screensize[0] // bs - edge * 2, screensize[1] // bs - edge * 2, edge)

    pygame.init()
    window = pygame.display.set_mode(screensize)
    done = False
    clock = pygame.Clock()
    while not done:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    done = True
                elif event.key == pygame.K_SPACE:
                    map = get_blocks(px, py, edge)
                elif event.key == pygame.K_z:
                    # map = (perlin(py, px) > 0).astype(int)
                    map = (100 * perlin(py, px)).astype(int)
                    map[map < 0] = 0
                    print(map)
                elif event.key == pygame.K_t:
                    map_max = 0
                    map_min = 0
                    for i in range(1000):
                        map = perlin(py, px)
                        map_max = max(map.max(), map_max)
                        map_min = min(map.min(), map_min)
                    print(map_min, map_max)
                elif event.key == pygame.K_2:
                    map = get_blocks2(px, py, edge)

        window.fill("black")
        for y in range(map.shape[0]):
            for x in range(map.shape[1]):
                if map[y, x]:
                    c = pygame.Color.from_hsva(map[y, x] + 60, 100, 100, 0)
                    r = pygame.Rect(x * bs, y * bs, bs - 1, bs - 1)
                    pygame.draw.rect(window, c, r)

        pygame.display.update()
    pygame.quit()
