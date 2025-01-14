from pygame import Rect
from game.model.items.inventory.inventory import Inventory

from pygame import mouse

from game.model.items.inventory.inventorytype import InventoryType

def getHoveredSlotRect(*inventories: tuple[Inventory, int, int, int]) -> Rect | None:
	'''check whether the mouse is hovering over a slot and return the rect of the slot to be drawn. Returns none if the cursor is not hovering any slot. inventories is given in a tuple (inventory, slotSize, x, y)'''
	
	mousepos = mouse.get_pos()

	for inventory, slotSize, inventoryx, inventoryy in inventories:
		slotRect = Rect(0, 0, slotSize, slotSize)
		for r in range(inventory.rows):
			for c in range(inventory.cols):
				x = inventoryx + c * slotSize
				y = inventoryy + r * slotSize
				rect = slotRect.copy()
				rect.topleft = x, y
				if rect.collidepoint(*mousepos):
					return rect
	return None

def getHoveredSlotSlot(inventories: dict[InventoryType, tuple[Inventory, int, int, int]]) -> tuple[InventoryType, int, int] | None:
	'''check whether the mouse is hovering over a slot and returns the slot position. Returns none if the cursor is not hovering any slot.'''
	
	mousepos = mouse.get_pos()

	for name, inventorydata in inventories.items():
		inventory, slotSize, inventoryx, inventoryy = inventorydata
		slotRect = Rect(0, 0, slotSize, slotSize)
		for r in range(inventory.rows):
			for c in range(inventory.cols):
				x = inventoryx + c * slotSize
				y = inventoryy + r * slotSize
				rect = slotRect.copy()
				rect.topleft = x, y
				if rect.collidepoint(*mousepos):
					return name, r, c
	return None