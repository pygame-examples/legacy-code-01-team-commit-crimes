import asyncio
import sys

from src.leaf_eater import Game
from src.leaf_eater.engine import settings

if __name__ == "__main__":
    fullscreen = False
    if len(sys.argv) > 1 and not settings.IS_WEB:
        fullscreen = sys.argv[1] == "full"

    game = Game(fullscreen=fullscreen)
    asyncio.run(game.run())
