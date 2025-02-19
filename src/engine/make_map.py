import numpy as np


def perlin(M, N):
    linx = np.linspace(0, 5, M, endpoint=False)
    liny = np.linspace(0, 5, N, endpoint=False)
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


def lerp(a, b, x):
    """linear interpolation"""
    return a + x * (b - a)


def fade(t):
    """6t^5 - 15t^4 + 10t^3"""
    return 6 * t**5 - 15 * t**4 + 10 * t**3


def gradient(h, x, y):
    """grad converts h to the right gradient vector and return the dot product with (x,y)"""
    vectors = np.array([[0, 1], [0, -1], [1, 0], [-1, 0]])
    g = vectors[h % 4]
    return g[:, :, 0] * x + g[:, :, 1] * y


def get_blocks(M, N, edge):
    obm = (perlin(N, M) > 0).astype(int)
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
        final = np.zeros((N + 2 * edge, M + 2 * edge))
        final[edge:-edge, edge:-edge] = binmap
        return final


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 3:
        M = int(sys.argv[1])
        N = int(sys.argv[2])
        edge = int(sys.argv[3])
    elif len(sys.argv) > 2:
        M = int(sys.argv[1])
        N = int(sys.argv[2])
        edge = 2
    elif len(sys.argv) > 1:
        M = int(sys.argv[1])
        N = M
        edge = 2
    else:
        M = 6
        N = 8
        edge = 2

    map = get_blocks(M, N, edge)

    print(map)
