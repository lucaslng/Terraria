import pygame as pg

from constants import BLOCK_SIZE, FRAME
from game.model.model import Model
from game.view.drawblocks import drawBlocks

def draw(model: Model):
	'''Draw everything'''

	camera = FRAME.copy()
	camera.center = model.player.position * BLOCK_SIZE
	drawBlocks(model.world, camera)