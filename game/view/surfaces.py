from pygame import SRCALPHA, Surface
from utils import colours
from utils.constants import BLOCK_SIZE, FRAME

everything = Surface(FRAME.size)
everything.set_alpha(None)
world = Surface(FRAME.size, SRCALPHA)
blockBreak = world.copy()
sunlight = world.copy()
dialogue = world.copy()
hud = world.copy()
hud = Surface((FRAME.width, int(FRAME.height * 0.6)), SRCALPHA)
hotbar = Surface((int(BLOCK_SIZE * 13.5), int(BLOCK_SIZE * 1.5)))
hotbar.set_colorkey(colours.WEIRD)
hotbar.set_alpha(None)

minimap = Surface((200, 200), SRCALPHA)
minimapLight = minimap.copy()

deathSurf = world.copy()
pauseSurf = world.copy()