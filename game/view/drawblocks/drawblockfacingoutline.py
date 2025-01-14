from pygame import Rect
import pygame as pg

from utils.constants import BLOCK_RECT
from game.view import conversions, surfaces


def drawBlockFacingOutline(coord: tuple[int, int], camera: Rect):
	'''Draw outline around block facing.'''

	rect = BLOCK_RECT.copy()
	rect.topleft = conversions.coordinate2Pixel(*coord, camera)

	pg.draw.rect(surfaces.world, (0, 0, 0, 200), rect, 2)