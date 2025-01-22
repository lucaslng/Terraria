from pygame import Rect
from pymunk import Vec2d
import pygame as pg

from game.events import DRAWEXPLOSION
from game.view import conversions, surfaces
from utils.constants import BLOCK_SIZE


def drawExplosion(pos: Vec2d, radius: float, width: int, camera: Rect):
	'''Draws the explosion circle, uses an event to call itself in the next frame'''
	ppos = conversions.coordinate2Pixel(*pos, camera)
	pg.draw.circle(surfaces.world, (200, 200, 200), ppos, radius * BLOCK_SIZE, width)
	if width > 0:
		pg.event.post(pg.event.Event(DRAWEXPLOSION, pos=pos, radius=radius+0.5, width=width-1))