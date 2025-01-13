from math import dist, floor
import pygame as pg
from game.model.blocks.utils.inventoryblock import InventoryBlock
from game.model.items.inventory.inventorytype import InventoryType
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
			InventoryType.Player:
				(
					model.player.inventory,
					*InventoryType.Player.value
				),
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
			inventoryTypes = model.mineBlock()
			if inventoryTypes:
				for inventoryType in inventoryTypes:
					if inventoryType in inventories:
						del inventories[inventoryType]
		elif pg.mouse.get_pressed()[2]:
			model.placeBlock(*conversions.pixel2Coordinate(*pg.mouse.get_pos(), camera))

		for event in pg.event.get():
			if event.type == pg.QUIT:
				return Screens.QUIT
			elif event.type == 101:
				print(f'fps: {round(clock.get_fps(), 2)}')
			elif event.type == pg.KEYDOWN and event.key == keys.interact:
				if len(inventories) > 1:
					inventories = {InventoryType.Player: inventories[InventoryType.Player]}
				else:
					for r in range(3):
						for c in range(3):
							x = floor(model.player.position.x) - 1 + c
							y = floor(model.player.position.y) - 1 + r
							if isinstance(model.world[y][x], InventoryBlock):
								print("interacted")
								for inventory, inventoryType in model.world[y][x].inventories:
									if inventoryType in inventories:
										del inventories[inventoryType]
									else:
										slotSize, inventoryx, inventoryy = inventoryType.value
										inventories[inventoryType] = inventory, slotSize, inventoryx, inventoryy
			elif event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
					hoveredSlotData = getHoveredSlotSlot(inventories)
					if hoveredSlotData:
						leftMousePressedTime = pg.time.get_ticks()
						hoveredSlotName, r, c = hoveredSlotData
						# print(f'hovered slot: {inventories[hoveredSlotName][0][r][c]}, cursor slot: {model.player.cursorSlot}')
						if inventories[hoveredSlotName][0][r][c].condition(model.player.cursorSlot.item):
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
							if inventories[hoveredSlotName][0][r][c].condition(model.player.cursorSlot.item):
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