import pygame as pg
from constants import WORLD_HEIGHT, WORLD_WIDTH, clock
from game.view.draw import draw
from game.model.model import Model
import keys
from screens import Screens
from utils.clearscreen import clearScreen
from utils.updatescreen import updateScreen

def game():

	'''main game loop'''
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
		if pressedKeys[keys.slot1]:
			model.player.heldSlotIndex = 0
		if pressedKeys[keys.slot2]:
			model.player.heldSlotIndex = 1
		if pressedKeys[keys.slot3]:
			model.player.heldSlotIndex = 2
		if pressedKeys[keys.slot4]:
			model.player.heldSlotIndex = 3
		if pressedKeys[keys.slot5]:
			model.player.heldSlotIndex = 4
		if pressedKeys[keys.slot6]:
			model.player.heldSlotIndex = 5
		if pressedKeys[keys.slot7]:
			model.player.heldSlotIndex = 6
		if pressedKeys[keys.slot8]:
			model.player.heldSlotIndex = 7
		if pressedKeys[keys.slot9]:
			model.player.heldSlotIndex = 8
			

		for event in pg.event.get():
			if event.type == pg.QUIT:
				return Screens.QUIT
			elif event.type == 101:
				print(f'fps: {round(clock.get_fps(), 2)}')
		
		model.update()
		draw(model)
		
		updateScreen()