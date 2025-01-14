from pygame import SRCALPHA, Surface
from utils.constants import BLOCK_SIZE


BACK_TINT = Surface((BLOCK_SIZE, BLOCK_SIZE), SRCALPHA)
BACK_TINT.fill((0, 0, 0, 70))