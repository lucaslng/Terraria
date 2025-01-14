from pygame import SRCALPHA, Surface

from utils.constants import HEIGHT, WIDTH


world = Surface((WIDTH, HEIGHT), SRCALPHA)
blockBreak = world.copy()
sunlight = world.copy()
hud = world.copy()