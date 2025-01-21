import pygame as pg


def initialize():
	'''initialize program'''
	pg.init()
	pg.font.init()
	pg.mixer.init()
	pg.mixer.set_reserved(1)
	pg.mixer.set_num_channels(1000)
	pg.time.set_timer(101, 5000)
	
	pg.mixer.music.set_volume(0.4)
	pg.mixer.music.load('assets/music.mp3')
	pg.mixer.music.play(loops=-1, fade_ms=1000)

	with open()