from game.view import surfaces
from utils.constants import BLOCK_SIZE
from game.model.items.inventory.inventory import Inventory
from game.model.items.inventory.inventorytype import InventoryType
from game.model.model import Model
from game.view.drawhud.drawhealth import drawHealth
from game.view.drawhud.drawhotbar import drawHotbar
from game.view.inventory.drawhoveredslot import drawHoveredSlotOutline
from game.view.inventory.drawinventory import drawInventory
from game.view.inventory.drawhelmetslot import drawHelmetSlot
from game.view.inventory.drawslot import drawSlot
from game.view.inventory.hoveredslot import getHoveredSlotRect

import pygame as pg


def drawHUD(model: Model, inventories: dict[InventoryType, tuple[Inventory, int, int, int]]):
	'''Draw all HUD on the screen'''

	drawHealth(model.player.health, model.player.maxHealth)
	drawHotbar(model.player.hotbar, model.player.heldSlotIndex)
 
	for inventoryKey, inventoryData in inventories.items():
		if inventoryKey == InventoryType.HelmetSlot:
			slot, slotSize, x, y = inventoryData
			drawHelmetSlot(slot, slotSize, x, y)
		else:
			drawInventory(*inventoryData)
	
	hoveredSlotRect = getHoveredSlotRect(*(v for v in inventories.values()))
	if hoveredSlotRect:
		drawHoveredSlotOutline(hoveredSlotRect)
	
	if model.player.cursorSlot.item:
		drawSlot(surfaces.hud, model.player.cursorSlot, *pg.mouse.get_pos(), BLOCK_SIZE + 2, center=True)