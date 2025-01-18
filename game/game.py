from math import dist, floor
import pygame as pg
from game.model.blocks.utils.inventoryblock import InventoryBlock
from game.model.entity.entities.rabbit import Rabbit
from game.model.items.inventory.inventorytype import InventoryType
from game.model.items.specialitems.edible import Edible
from game.model.utils.bresenham import bresenham
from game.view import conversions
from game.view.inventory.hoveredslot import getHoveredSlotSlot
from sound import channels, sounds
import utils.keys as keys
from utils.constants import BLOCK_SIZE, FRAME, WORLD_HEIGHT, WORLD_WIDTH
from game.view.draw import draw
from game.model.model import Model
from utils.screens import Screens
from utils.clearscreen import clearScreen
from utils.updatescreen import updateScreen


def game():
	'''Main game loop'''
	model = Model(WORLD_WIDTH, WORLD_HEIGHT)
	model.start()

	camera = FRAME.copy()
	camera.center = model.player.position[0] * BLOCK_SIZE, model.player.position[1] * BLOCK_SIZE

	inventories = {InventoryType.Player: (model.player.inventory, *InventoryType.Player.value)}
	
	leftMousePressedTime = 0

	def swapSlot(hoveredSlotData: tuple[InventoryType, int, int]) -> None:
		if hoveredSlotData is None:
			return
  
		hoveredSlotName, r, c = hoveredSlotData
		if inventories[hoveredSlotName][0][r][c].condition(model.player.cursorSlot):
			if model.player.cursorSlot.item and inventories[hoveredSlotName][0][r][c].item == model.player.cursorSlot.item:
				add = min(model.player.cursorSlot.item.stackSize - inventories[hoveredSlotName][0][r][c].count, model.player.cursorSlot.count)
				extra = model.player.cursorSlot.count - add
				inventories[hoveredSlotName][0][r][c].count += add
				model.player.cursorSlot.count = extra
				if model.player.cursorSlot.count == 0:
					model.player.cursorSlot.clear()
			else:
				inventories[hoveredSlotName][0][r][c], model.player.cursorSlot = model.player.cursorSlot, inventories[hoveredSlotName][0][r][c]
   
	def handleStackSplit(hoveredSlotData: tuple[InventoryType, int, int]) -> None:
		if hoveredSlotData is None:
			return

		hoveredSlotName, r, c = hoveredSlotData
  
		#Split if cursor is empty and clicked slot has items
		if (model.player.cursorSlot.item is None and 
			inventories[hoveredSlotName][0][r][c].item is not None):
			
			source_slot = inventories[hoveredSlotName][0][r][c]
			
			#Can't split single items
			if source_slot.count <= 1:
				return
				
			#Calculate split amounts (odd numbers keep the extra in source)
			split_amount = floor(source_slot.count / 2)
			source_slot.count = source_slot.count - split_amount
			
			#Put split portion in cursor
			model.player.cursorSlot.item = source_slot.item
			model.player.cursorSlot.count = split_amount

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
		
		if pressedKeys[keys.consume]:
			if model.player.heldSlot.item and isinstance(model.player.heldSlot.item, Edible) and not channels.consume.get_busy():
				channels.consume.play(sounds.consume)
				model.player.consume()
		
		if pg.mouse.get_pressed()[0]:
			#Check if the cursor is hovering over any inventory slot
			hoveredSlotData = getHoveredSlotSlot(inventories)
			
			#Only mine blocks if we're not hovering over an inventory slot
			if not hoveredSlotData:
				inventoryTypes = model.mineBlock()
				if inventoryTypes:
					for inventoryType in inventoryTypes:
						if inventoryType in inventories:
							del inventories[inventoryType]
      
		elif pg.mouse.get_pressed()[2]:
			if not getHoveredSlotSlot(inventories):
				model.placeBlock(*conversions.pixel2Coordinate(*pg.mouse.get_pos(), camera))

		for event in pg.event.get():
			if event.type == pg.QUIT:
				return Screens.QUIT
    
			elif event.type == pg.KEYDOWN:
				if event.key == keys.interact:
					if len(inventories) > 1:
						inventories = {InventoryType.Player: inventories[InventoryType.Player]}
					else:
						for r in range(3):
							for c in range(3):
								x = floor(model.player.position.x) - 1 + c
								y = floor(model.player.position.y) - 1 + r
								if isinstance(model.world[y][x], InventoryBlock):
									for inventory, inventoryType in model.world[y][x].inventories:
										if inventoryType in inventories:
											del inventories[inventoryType]
										else:
											slotSize, inventoryx, inventoryy = inventoryType.value
											inventories[inventoryType] = inventory, slotSize, inventoryx, inventoryy
				elif event.key == keys.interactEntity:
					if model.entities:
						model.entities.sort(key=lambda e: dist(e.position, model.player.position)) # sort by position to the player
						if dist(model.entities[0].position, model.player.position) < 1.5:
							if isinstance(model.entities[0], Rabbit):
								model.entities[0].interact(model.player.damage)
								if not model.entities[0].isAlive:
									if model.entities[0].droppedItem:
										model.player.inventory.addItem(model.entities[0].droppedItem)
									model.deleteEntity(0, model.entities[0])
							else:
								model.entities[0].interact()
			elif event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
					hoveredSlotData = getHoveredSlotSlot(inventories)
					if hoveredSlotData:
						leftMousePressedTime = pg.time.get_ticks()
						swapSlot(hoveredSlotData)
      
				elif event.button == 3:
						handleStackSplit(hoveredSlotData)
                        
			elif event.type == pg.MOUSEBUTTONUP:
				if event.button == 1:
					hoveredSlotData = getHoveredSlotSlot(inventories)
					if hoveredSlotData:
						if pg.time.get_ticks() - leftMousePressedTime > 150:
							swapSlot(hoveredSlotData)
		
		blockFacingCoord = bresenham(model.world.array, *pg.mouse.get_pos(), *FRAME.center, camera)
  
		if blockFacingCoord and dist(map(lambda a: a + 0.5, blockFacingCoord), model.player.position) < model.player.reach:
			model.blockFacingCoord = blockFacingCoord
		else:
			model.blockFacingCoord = None
		
		for y in range(camera.top // BLOCK_SIZE, camera.bottom // BLOCK_SIZE + 1):
			for x in range(camera.left // BLOCK_SIZE, camera.right // BLOCK_SIZE + 1):
				model.world[y][x].update()

		if not model.update():
			print("player died")
			return Screens.MENU
		camera.center = model.player.position[0] * BLOCK_SIZE, model.player.position[1] * BLOCK_SIZE		
		draw(model, camera, inventories)
		updateScreen()