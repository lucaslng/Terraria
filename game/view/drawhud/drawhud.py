from game.model.items.inventory.inventory import Inventory
from game.model.model import Model
from game.view.drawhud.drawhealth import drawHealth
from game.view.drawhud.drawhotbar import drawHotbar
from game.view.inventory.drawhoveredslot import drawHoveredSlotOutline
from game.view.inventory.drawinventory import drawInventory
from game.view.inventory.drawslot import drawSlot
from game.view.inventory.hoveredslot import getHoveredSlotRect

import pygame as pg


def drawHUD(model: Model, inventories: dict[str, tuple[Inventory, int, int, int]]):
	'''Draw HUD'''

	drawHealth(model.player.health, model.player.maxHealth)
	drawInventory(*inventories["player"])
	drawHotbar(model.player.hotbar, model.player.heldSlotIndex)
	
	hoveredSlotRect = getHoveredSlotRect(*(v for v in inventories.values()))
	if hoveredSlotRect:
		drawHoveredSlotOutline(hoveredSlotRect)
	
	if model.player.cursorSlot.item:
		drawSlot(model.player.cursorSlot, *pg.mouse.get_pos(), inventories["player"][1], center=True)