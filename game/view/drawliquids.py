from game.model.liquids.liquid import Liquid
import pygame as pg

from game.view import conversions, surfaces
from utils import colours
from utils.constants import BLOCK_SIZE


def drawLiquids(liquids: list[Liquid], camera: pg.Rect):
	'''draw the liquids in the world'''

	for liquid in liquids:
		for liquidParticle in liquid.particles:
			pg.draw.circle(surfaces.world, colours.BLUE, conversions.coordinate2Pixel(*liquidParticle.body.position, camera), liquidParticle.shape.radius * BLOCK_SIZE * 5)