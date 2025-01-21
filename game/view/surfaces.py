from pygame import SRCALPHA, Surface
from utils import colours
from utils.constants import BLOCK_SIZE, HEIGHT, WIDTH

all = Surface((WIDTH, HEIGHT))
world = Surface((WIDTH, HEIGHT), SRCALPHA)
blockBreak = world.copy()
sunlight = world.copy()
dialogue = world.copy()
hud = world.copy()
hud = Surface((WIDTH, int(HEIGHT * 0.6)), SRCALPHA)
hotbar = Surface((int(BLOCK_SIZE * 13.5), int(BLOCK_SIZE * 1.5)))
hotbar.set_colorkey(colours.WEIRD)

minimap = Surface((200, 200), SRCALPHA)
minimapLight = minimap.copy()

deathSurf = world.copy()
pauseSurf = world.copy()