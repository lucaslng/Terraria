from pygame import Rect
from constants import BLOCK_SIZE, FRAME
from game.model.light import Light
import pygame as pg

from game.view import conversions, surfaces

def drawLight(lightRadius: float, x: int, y: int):
	'''Draw a single light screen'''
	pg.draw.circle(surfaces.sunlight, (0, 0, 0, 0), (x, y), lightRadius * BLOCK_SIZE)

def drawPlayerLight(lightRadius: float):
	'''Draw light for the player'''
	
	drawLight(lightRadius, *FRAME.center)

def drawLights(lights: list[tuple[Light, int, int]], camera: Rect) -> None:
	'''Draw all visible lights in the world'''

	for lightData in lights:
		light, lightx, lighty = lightData
		drawLight(light.lightRadius, *conversions.coordinate2Pixel(lightx, lighty, camera))