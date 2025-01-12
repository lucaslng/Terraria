import pygame as pg

from constants import SURF
from game.model.world import World
from game.view import surfaces
from game.view.drawblocks.drawblockfacingoutline import drawBlockFacingOutline
from game.view.drawblocks.drawblocksblocks import drawBlocksBlocks

def drawBlocks(world: World, blockFacingCoord: tuple[int, int] | None, camera: pg.Rect):
	'''Draw blocks'''
	
	drawBlocksBlocks(world, camera)
	if blockFacingCoord:
		drawBlockFacingOutline(blockFacingCoord, camera)
	
	SURF.blit(surfaces.blocks, (0, 0))