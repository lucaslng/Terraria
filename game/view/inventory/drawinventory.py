from game.model.items.inventory.inventory import Inventory
from game.view import surfaces
from game.view.inventory.drawslot import drawSlot

import pygame as pg


def drawInventory(inventory: Inventory, inventoryx: int, inventoryy: int, slotSize: int) -> None:
	'''Draw player inventory on topleft of screen'''

	for r, row in enumerate(inventory.array):
		for c, slot in enumerate(row):
			x = inventoryx + c * slotSize
			y = inventoryy + r * slotSize

			pg.draw.rect(surfaces.hud, (200, 200, 200, 160), (x, y, slotSize, slotSize))

			pg.draw.rect(surfaces.hud, (90, 90, 90), (x, y, slotSize, slotSize), 2)

			drawSlot(slot, x, y, slotSize)

