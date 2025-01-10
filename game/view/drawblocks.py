import pygame as pg

from constants import BLOCK_SIZE, SURF
from game.model.blocks.airblock import AirBlock
from game.model.world import World
from game.view import surfaces
from game.view.drawblock import drawBlock

def drawBlocks(world: World, camera: pg.Rect):
	'''Draw blocks'''

	for y in range(camera.top // BLOCK_SIZE, camera.bottom // BLOCK_SIZE + 1):
		for x in range(camera.left // BLOCK_SIZE, camera.right // BLOCK_SIZE + 1):
			if not isinstance(world.back[y][x], AirBlock) and not world[y][x].isEmpty:
				drawBlock(world[y][x], x, y, camera, isBack=True)
			if not isinstance(world[y][x], AirBlock):
				drawBlock(world[y][x], x, y, camera)
	
	SURF.blit(surfaces.blocks, (0, 0))