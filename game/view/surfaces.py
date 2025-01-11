from pygame import SRCALPHA, Surface

from constants import HEIGHT, WIDTH


blocks = Surface((WIDTH, HEIGHT), SRCALPHA)
sunlight = Surface((WIDTH, HEIGHT), SRCALPHA)
hud = Surface((WIDTH, HEIGHT), SRCALPHA)