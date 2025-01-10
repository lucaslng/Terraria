import pygame as pg
from constants import FPS, clock

def updateScreen():
	pg.display.flip()
	clock.tick(FPS)