import pygame as pg

def initialize():
	'''initialize program'''
	pg.init()
	pg.font.init()
	pg.mixer.init()
	pg.mixer.set_reserved(0)
	pg.time.set_timer(101, 5000)