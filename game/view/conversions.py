from pygame import Rect
from utils.constants import BLOCK_SIZE


def coordinate2Pixel(coordx: int, coordy: int, camera: Rect) -> tuple[int, int]:
	'''Convert world coordinate to on screen pixels'''

	return coordx * BLOCK_SIZE - camera.x, coordy * BLOCK_SIZE - camera.y

def pixel2Coordinate(pixelx: int, pixely: int, camera: Rect) -> tuple[int, int]:
	'''Convert on screen pixels to world coordinate'''

	return (pixelx + camera.x) // BLOCK_SIZE, (pixely + camera.y) // BLOCK_SIZE

def pixel2worldPixel(pixelx: int, pixely: int, camera: Rect) -> tuple[int, int]:
	'''Convert on screen pixels to world pixels'''
	
	return pixelx + camera.x, pixely + camera.y