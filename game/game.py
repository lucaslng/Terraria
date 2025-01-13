from math import dist, floor
import pygame as pg
from game.model.blocks.utils.interactable import Interactable
from game.model.utils.bresenham import bresenham
from game.view import conversions
from game.view.inventory.hoveredslot import getHoveredSlotSlot
import keys
from constants import BLOCK_SIZE, FRAME, WORLD_HEIGHT, WORLD_WIDTH, clock
from game.view.draw import draw
from game.model.model import Model
from screens import Screens
from utils.clearscreen import clearScreen
from utils.updatescreen import updateScreen

def game():
	'''Main game loop'''
	model = Model(WORLD_WIDTH, WORLD_HEIGHT)
	model.start()

	camera = FRAME.copy()
	camera.center = model.player.position[0] * BLOCK_SIZE, model.player.position[1] * BLOCK_SIZE

	inventories = {
			"player":
				(
					model.player.inventory,
					BLOCK_SIZE + 2,
					15,
					80,
				)
		}
	
	leftMousePressedTime = 0

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
		elif pg.mouse.get_pressed()[2]:
			model.placeBlock(*conversions.pixel2Coordinate(*pg.mouse.get_pos(), camera))

		for event in pg.event.get():
			if event.type == pg.QUIT:
				return Screens.QUIT
			elif event.type == 101:
				print(f'fps: {round(clock.get_fps(), 2)}')
			elif event.type == pg.KEYDOWN and event.key == keys.interact:
				for r in range(3):
					for c in range(3):
						x = floor(model.player.position.x) - 1 + c
						y = floor(model.player.position.y) - 1 + r
						if isinstance(model.world[y][x], Interactable):
							model.world[y][x].interact()
			elif event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
					hoveredSlotData = getHoveredSlotSlot(inventories)
					if hoveredSlotData:
						leftMousePressedTime = pg.time.get_ticks()
						hoveredSlotName, r, c = hoveredSlotData
						# print(f'hovered slot: {inventories[hoveredSlotName][0][r][c]}, cursor slot: {model.player.cursorSlot}')
						if model.player.cursorSlot.item and inventories[hoveredSlotName][0][r][c].item == model.player.cursorSlot.item:
							add = min(model.player.cursorSlot.item.stackSize - inventories[hoveredSlotName][0][r][c].count, model.player.cursorSlot.count)
							extra = model.player.cursorSlot.count - add
							inventories[hoveredSlotName][0][r][c].count += add
							model.player.cursorSlot.count = extra
							if model.player.cursorSlot.count == 0:
								model.player.cursorSlot.clear()
						else:
							inventories[hoveredSlotName][0][r][c], model.player.cursorSlot = model.player.cursorSlot, inventories[hoveredSlotName][0][r][c]
						# print(f'hovered slot: {inventories[hoveredSlotName][0][r][c]}, cursor slot: {model.player.cursorSlot}')
			elif event.type == pg.MOUSEBUTTONUP:
				if event.button == 1:
					hoveredSlotData = getHoveredSlotSlot(inventories)
					if hoveredSlotData:
						if pg.time.get_ticks() - leftMousePressedTime > 150:
							hoveredSlotName, r, c = hoveredSlotData
							# print(f'hovered slot: {inventories[hoveredSlotName][0][r][c]}, cursor slot: {model.player.cursorSlot}')
							if model.player.cursorSlot.item and inventories[hoveredSlotName][0][r][c].item == model.player.cursorSlot.item:
								add = min(model.player.cursorSlot.item.stackSize - inventories[hoveredSlotName][0][r][c].count, model.player.cursorSlot.count)
								extra = model.player.cursorSlot.count - add
								inventories[hoveredSlotName][0][r][c].count += add
								model.player.cursorSlot.count = extra
								if model.player.cursorSlot.count == 0:
									model.player.cursorSlot.clear()
							else:
								inventories[hoveredSlotName][0][r][c], model.player.cursorSlot = model.player.cursorSlot, inventories[hoveredSlotName][0][r][c]
							# print(f'hovered slot: {inventories[hoveredSlotName][0][r][c]}, cursor slot: {model.player.cursorSlot}')
		
		blockFacingCoord = bresenham(model.world.array, *pg.mouse.get_pos(), *FRAME.center, camera)
		if blockFacingCoord and dist(map(lambda a: a + 0.5, blockFacingCoord), model.player.position) < model.player.reach:
			model.blockFacingCoord = blockFacingCoord
		else:
			model.blockFacingCoord = None

		model.update()
		
		camera.center = model.player.position[0] * BLOCK_SIZE, model.player.position[1] * BLOCK_SIZE
		
		draw(model, camera, inventories)
		
		updateScreen()