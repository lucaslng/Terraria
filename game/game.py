from math import dist
import pygame as pg
from game.model.utils.bresenham import bresenham
import keys
from constants import BLOCK_SIZE, FRAME, WORLD_HEIGHT, WORLD_WIDTH, clock
from game.view.draw import draw
from game.model.model import Model
from screens import Screens
from utils.clearscreen import clearScreen
from utils.updatescreen import updateScreen

def Game():
	'''Main game loop'''
	model = Model(WORLD_WIDTH, WORLD_HEIGHT)
	model.start()

	camera = FRAME.copy()
	camera.center = model.player.position[0] * BLOCK_SIZE, model.player.position[1] * BLOCK_SIZE

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
		
		if pg.mouse.get_pressed()[0]:
			model.mineBlock()

		for event in pg.event.get():
			if event.type == pg.QUIT:
				return Screens.QUIT
			elif event.type == 101:
				print(f'fps: {round(clock.get_fps(), 2)}')
		
		blockFacingCoord = bresenham(model.world.array, *pg.mouse.get_pos(), *FRAME.center, camera)
		if blockFacingCoord and dist(map(lambda a: a + 0.5, blockFacingCoord), model.player.position) < model.player.reach:
			model.blockFacingCoord = blockFacingCoord
		else:
			model.blockFacingCoord = None

		model.update()
		
		camera.center = model.player.position[0] * BLOCK_SIZE, model.player.position[1] * BLOCK_SIZE
		
		draw(model, camera)
		
		updateScreen()