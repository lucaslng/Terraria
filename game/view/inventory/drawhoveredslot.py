from pygame import Rect
import pygame as pg

from game.view import surfaces
from utils import colours


def drawHoveredSlotOutline(rect: Rect) -> None:
	'''Draw the outline around the hovered slot'''
	
	pg.draw.rect(surfaces.hud, colours.BLACK, rect, 4)