from pygame import Rect
import pygame as pg

from constants import BLOCK_SIZE
from game.view import conversions, surfaces

_blockRect = pg.rect.Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE)

def drawBlockFacingOutline(coord: tuple[int, int], camera: Rect):
	'''Draw outline around block facing.'''

	rect = _blockRect.copy()
	rect.topleft = conversions.coordinate2Pixel(*coord, camera)

	pg.draw.rect(surfaces.blocks, (0, 0, 0, 200), rect, 2)