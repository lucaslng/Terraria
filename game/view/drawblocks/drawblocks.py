import pygame as pg

from game.model.world import World
from game.view.drawblocks.drawblockfacingoutline import drawBlockFacingOutline
from game.view.drawblocks.drawblocksblocks import drawBlocksBlocks

def drawBlocks(world: World, blockFacingCoord: tuple[int, int] | None, camera: pg.Rect):
	'''Draw blocks'''
	
	drawBlocksBlocks(world, camera)
	
	if blockFacingCoord:
		drawBlockFacingOutline(blockFacingCoord, camera)