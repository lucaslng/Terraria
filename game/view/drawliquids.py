from game.model.liquids.liquid import Liquid
import pygame as pg

from game.view import conversions, surfaces
from utils import colours
from utils.constants import BLOCK_SIZE, FRAME


def drawLiquids(liquids: list[Liquid], camera: pg.Rect):
	'''draw the liquids in the world'''
	
	for liquid in liquids:
		for liquidParticle in liquid.particles:
			pos = conversions.coordinate2Pixel(*liquidParticle.body.position, camera)
			if FRAME.collidepoint(*pos):
				pg.draw.circle(surfaces.world, colours.BLUE, pos, liquidParticle.shape.radius * BLOCK_SIZE * 5)