from pygame import Rect
from constants import BLOCK_SIZE


def coordinate2Pixel(coordx: int, coordy: int, camera: Rect):
	return coordx * BLOCK_SIZE - camera.x, coordy * BLOCK_SIZE - camera.y