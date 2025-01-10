import pygame as pg
from constants import WORLD_HEIGHT, WORLD_WIDTH
from game.draw import draw
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
		draw(model=model)

		for event in pg.event.get():
			if event.type == pg.QUIT:
				return Screens.QUIT
		
		updateScreen()