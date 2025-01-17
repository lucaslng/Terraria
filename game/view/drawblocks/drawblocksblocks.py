from pygame import Rect
import pygame as pg

from game.view import conversions, surfaces
from utils import colours
from utils.constants import BLOCK_RECT, BLOCK_SIZE
from game.model.blocks.airblock import AirBlock
from game.model.world import World
from game.view.drawblocks.drawblock import drawBlock


def drawBlocksBlocks(world: World, camera: Rect):
	for y in range(camera.top // BLOCK_SIZE, camera.bottom // BLOCK_SIZE + 1):
		for x in range(camera.left // BLOCK_SIZE, camera.right // BLOCK_SIZE + 1):
			if 0 <= y < world.height and 0 <= x < world.width:
				if not isinstance(world.back[y][x], AirBlock) and world[y][x].isEmpty:
					drawBlock(world.back[y][x], x, y, camera, isBack=True)
				if not isinstance(world[y][x], AirBlock):
					drawBlock(world[y][x], x, y, camera)
			else:
				rect = BLOCK_RECT.copy()
				rect.topleft = conversions.coordinate2Pixel(x, y, camera)
				pg.draw.rect(surfaces.world, colours.BLACK, rect)