import pygame as pg
from constants import clock

def updateScreen():
	pg.display.flip()
	clock.tick()