import pygame as pg

from constants import BLOCK_SIZE, SURF
from game.view import conversions, surfaces

def drawSunlight(lightmap: list[list[int]], camera: pg.Rect) -> None:
	'''Draw sunlight'''

	for y in range(camera.top // BLOCK_SIZE, camera.bottom // BLOCK_SIZE + 1):
		for x in range(camera.left // BLOCK_SIZE, camera.right // BLOCK_SIZE + 1):
			pg.draw.rect(surfaces.sunlight, (0, 0, 0, lightmap[y][x]), pg.Rect(*conversions.coordinate2Pixel(x, y, camera), BLOCK_SIZE, BLOCK_SIZE))
	
	SURF.blit(surfaces.sunlight, (0, 0))