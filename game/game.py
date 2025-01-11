import pygame as pg
from constants import WORLD_HEIGHT, WORLD_WIDTH, clock
from game.view.draw import draw
from game.model.model import Model
import keys
from screens import Screens
from utils.clearscreen import clearScreen
from utils.updatescreen import updateScreen

def Game():
	'''Main game loop'''
	model = Model(WORLD_WIDTH, WORLD_HEIGHT)
	model.start()

	while True:
		clearScreen()

		pressedKeys = pg.key.get_pressed()
		if pressedKeys[keys.walkLeft]:
			model.player.walkLeft()
		if pressedKeys[keys.walkRight]:
			model.player.walkRight()
		if pressedKeys[keys.jump]:
			model.player.jump()
			

		for event in pg.event.get():
			if event.type == pg.QUIT:
				return Screens.QUIT
			elif event.type == 101:
				print(f'fps: {round(clock.get_fps(), 2)}')
		
		model.update()
		draw(model)
		
		updateScreen()