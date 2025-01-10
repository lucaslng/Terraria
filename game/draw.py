import pygame as pg

from constants import SURF

def draw(model):
	'''Draw everything'''
	pg.draw.rect(SURF, (255,0,0), (0,0,500,500))