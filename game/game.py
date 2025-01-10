import pygame as pg
from constants import WORLD_HEIGHT, WORLD_WIDTH, clock
from game.view.draw import draw
from game.model.model import Model
from screens import Screens
from utils.clearscreen import clearScreen
from utils.updatescreen import updateScreen

def game():

	'''main game loop'''
	model = Model(WORLD_WIDTH, WORLD_HEIGHT)
	model.start()

	while True:
		clearScreen()
		draw(model)

		for event in pg.event.get():
			if event.type == pg.QUIT:
				return Screens.QUIT
			elif event.type == 101:
				print(f'fps: {round(clock.get_fps(), 2)}')
		
		updateScreen()