from math import dist, floor
import pygame as pg
from game.model.blocks.utils.inventoryblock import InventoryBlock
from game.model.entity.entities.dog import Dog
from game.model.entity.entities.rabbit import Rabbit
from game.model.items.inventory.slot import Slot
from game.model.items.inventory.inventorytype import InventoryType
from game.model.items.specialitems.edible import Edible
from game.model.items.specialitems.tool import Tool
from game.model.utils.bresenham import bresenham
import game.utils.saving as saving
from game.view import conversions, surfaces
from game.view.inventory.hoveredslot import getHoveredSlotSlot
from menu.death.deathScreen import deathScreen
from menu.pause.pause import pauseMenu
from sound import channels
import utils.userKeys as userKeys
from utils.constants import BLOCK_SIZE, FRAME, WORLD_HEIGHT, WORLD_WIDTH
from game.view.draw import draw
from game.model.model import Model
from utils.screens import Screens
from utils.clearscreen import clearScreen
from utils.updatescreen import updateScreen


def initGame():
	'''Initialize or reinitialize game components'''
	model = saving.load()
	if not model:
		print("Generating new world...")
		model = Model(WORLD_WIDTH, WORLD_HEIGHT)
	camera = FRAME.copy()
	camera.center = model.player.body.position[0] * BLOCK_SIZE, model.player.body.position[1] * BLOCK_SIZE

	inventories = {
			InventoryType.Player: (model.player.inventory, *InventoryType.Player.value),
			InventoryType.HelmetSlot: (model.player.helmetSlot, *InventoryType.HelmetSlot.value)
	}

	return model, camera, inventories

def game() -> Screens:
	'''Main game loop'''
	model, camera, inventories = initGame()
	
	leftMousePressedTime = 0

	def swapSlot(hoveredSlotData: tuple[InventoryType, int, int]) -> None:
		if hoveredSlotData is None:
			return
		
		hoveredSlotName, r, c = hoveredSlotData
		inventoryOrSlot = inventories[hoveredSlotName][0]
		
		if isinstance(inventoryOrSlot, Slot):
			targetSlot = inventoryOrSlot
		else:
			targetSlot = inventoryOrSlot[r][c]
		
		#Check conditions and perform swap
		if targetSlot.condition(model.player.cursorSlot):
			if (model.player.cursorSlot.item and 
				targetSlot.item == model.player.cursorSlot.item):
				#Stack similar items
				add = min(model.player.cursorSlot.item.stackSize - targetSlot.count, model.player.cursorSlot.count)
				extra = model.player.cursorSlot.count - add
				targetSlot.count += add
				model.player.cursorSlot.count = extra
				if model.player.cursorSlot.count == 0:
					model.player.cursorSlot.clear()
			else:
				#Swap different items
				if isinstance(inventoryOrSlot, Slot):
					inventoryOrSlot.item, model.player.cursorSlot.item = model.player.cursorSlot.item, inventoryOrSlot.item
					inventoryOrSlot.count, model.player.cursorSlot.count = model.player.cursorSlot.count, inventoryOrSlot.count
				else:
					inventoryOrSlot[r][c].item, model.player.cursorSlot.item = model.player.cursorSlot.item, inventoryOrSlot[r][c].item
					inventoryOrSlot[r][c].count, model.player.cursorSlot.count = model.player.cursorSlot.count, inventoryOrSlot[r][c].count
   
	def handleStackSplit(hoveredSlotData: tuple[InventoryType, int, int]) -> None:
		if hoveredSlotData is None:
			return

		hoveredSlotName, r, c = hoveredSlotData
  
		#Split if cursor is empty and clicked slot has items
		if (model.player.cursorSlot.item is None and 
			inventories[hoveredSlotName][0][r][c].item is not None):
			
			sourceSlot = inventories[hoveredSlotName][0][r][c]
			
			#Can't split single items
			if sourceSlot.count <= 1:
				return
				
			#Calculate split amounts (odd numbers keep the extra in source)
			splitAmount = floor(sourceSlot.count / 2)
			sourceSlot.count = sourceSlot.count - splitAmount
			
			#Put split portion in cursor
			model.player.cursorSlot.item = sourceSlot.item
			model.player.cursorSlot.count = splitAmount

	while True:
		clearScreen()
  
		pressedKeys = pg.key.get_pressed()
		if pressedKeys[userKeys.walkLeft]:
			model.player.walkLeft()
		if pressedKeys[userKeys.walkRight]:
			model.player.walkRight()
		if pressedKeys[userKeys.jump]:
			model.player.jump()
   
		if pressedKeys[userKeys.slot1]:
			model.player.heldSlotIndex = 0
		if pressedKeys[userKeys.slot2]:
			model.player.heldSlotIndex = 1
		if pressedKeys[userKeys.slot3]:
			model.player.heldSlotIndex = 2
		if pressedKeys[userKeys.slot4]:
			model.player.heldSlotIndex = 3
		if pressedKeys[userKeys.slot5]:
			model.player.heldSlotIndex = 4
		if pressedKeys[userKeys.slot6]:
			model.player.heldSlotIndex = 5
		if pressedKeys[userKeys.slot7]:
			model.player.heldSlotIndex = 6
		if pressedKeys[userKeys.slot8]:
			model.player.heldSlotIndex = 7
		if pressedKeys[userKeys.slot9]:
			model.player.heldSlotIndex = 8
		
		if pressedKeys[userKeys.consume]:
			if model.player.heldSlot.item and isinstance(model.player.heldSlot.item, Edible) and not channels.consume.get_busy():
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
				saving.save(model)
				return Screens.QUIT
			elif event.type == 101:
				model.spawnEntitiesRandom()
				pg.mixer.set_num_channels(len(model.entities) * 2) # set extra channels just to be safe
			elif event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					draw(model, camera, inventories)
					pause = pauseMenu(model, pg.image.tobytes(surfaces.everything, 'RGB'))   
					if pause:
						return pause
					else:
						continue 
				elif event.key == userKeys.interact:
					if len(inventories) > 2:
						inventories = {
							InventoryType.Player: (model.player.inventory, *InventoryType.Player.value),
							InventoryType.HelmetSlot: (model.player.helmetSlot, *InventoryType.HelmetSlot.value)
						}
					else:
						for r in range(3):
							for c in range(3):
								x = floor(model.player.body.position.x) - 1 + c
								y = floor(model.player.body.position.y) - 1 + r
								if isinstance(model.world[y][x], InventoryBlock):
									for inventory, inventoryType in model.world[y][x].inventories:
										if inventoryType in inventories:
											del inventories[inventoryType]
										else:
											slotSize, inventoryx, inventoryy = inventoryType.value
											inventories[inventoryType] = inventory, slotSize, inventoryx, inventoryy
				elif event.key == userKeys.interactEntity:
					if model.entities:
						model.entities.sort(key=lambda e: dist(e.body.position, model.player.body.position)) # sort by position to the player
						for i, entity in enumerate(model.entities):
							if dist(entity.body.position, model.player.body.position) > 2:
								break
							if isinstance(entity, Rabbit) or isinstance(entity, Dog):
								if entity.interact(model.player.damage):
									entity.body.apply_impulse_at_local_point((entity.body.position - model.player.body.position) * 40, (0, 0.5))
									if model.player.heldSlot.item and isinstance(model.player.heldSlot.item, Tool):
										model.player.heldSlot.item.durability -= 1
										if model.player.heldSlot.item.durability == 0:
											model.player.heldSlot.clear()
								if not entity.isAlive:
									if entity.droppedItem:
										model.player.inventory.addItem(entity.droppedItem)
									model.deleteEntity(i, entity)
							else:
								entity.interact()
			elif event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
					hoveredSlotData = getHoveredSlotSlot(inventories)
					if hoveredSlotData:
						leftMousePressedTime = pg.time.get_ticks()
						swapSlot(hoveredSlotData)
      
				elif event.button == 3:
					hoveredSlotData = getHoveredSlotSlot(inventories)
					if hoveredSlotData:
						handleStackSplit(hoveredSlotData)
                        
			elif event.type == pg.MOUSEBUTTONUP:
				if event.button == 1:
					hoveredSlotData = getHoveredSlotSlot(inventories)
					if hoveredSlotData:
						if pg.time.get_ticks() - leftMousePressedTime > 150:
							swapSlot(hoveredSlotData)
		
		blockFacingCoord = bresenham(model.world.array, *pg.mouse.get_pos(), *FRAME.center, camera)
  
		if blockFacingCoord and dist(map(lambda a: a + 0.5, blockFacingCoord), model.player.body.position) < model.player.reach:
			model.blockFacingCoord = blockFacingCoord
		else:
			model.blockFacingCoord = None
		
		for y in range(camera.top // BLOCK_SIZE, camera.bottom // BLOCK_SIZE + 1):
			for x in range(camera.left // BLOCK_SIZE, camera.right // BLOCK_SIZE + 1):
				if 0 <= y < model.world.height and 0 <= x < model.world.width:
					model.world[y][x].update()

		camera.center = model.player.body.position[0] * BLOCK_SIZE, model.player.body.position[1] * BLOCK_SIZE		
		draw(model, camera, inventories)
  
		#player death
		if not model.update():
			saving.clear()
			return deathScreen(pg.image.tobytes(surfaces.everything, 'RGB'))
		updateScreen()