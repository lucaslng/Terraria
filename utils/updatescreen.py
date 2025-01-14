import pygame as pg
from utils.constants import FPS, clock

def updateScreen():
	pg.display.flip()
	clock.tick(FPS)