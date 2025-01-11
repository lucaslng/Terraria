from game.model.items.inventory.inventory import Inventory


def drawInventory(inventory: Inventory, inventoryx: int, inventoryy: int, slotSize: int) -> None:
	'''Draw player inventory on topleft of screen'''

	for r, row in enumerate(inventory.array):
		for c, slot in enumerate(row):
			x = inventoryx + c * slotSize
			y = inventoryy + r * slotSize

