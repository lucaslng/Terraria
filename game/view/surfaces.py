from pygame import SRCALPHA, Surface
from utils import colours
from utils.constants import BLOCK_SIZE, HEIGHT, WIDTH

world = Surface((WIDTH, HEIGHT), SRCALPHA)
blockBreak = world.copy()
sunlight = world.copy()
hud = world.copy()
health = Surface((BLOCK_SIZE * 18, BLOCK_SIZE))
health.set_colorkey(colours.BLACK)

minimap = Surface((200, 200), SRCALPHA)
minimapLight = minimap.copy()

deathSurf = world.copy()