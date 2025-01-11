from constants import BLOCK_SIZE, FRAME
from game.model.items.inventory.slot import Slot
import pygame as pg

from game.textures.sprites import sprites
from game.view import surfaces
from game.view.inventory.drawslotcount import drawSlotCount
from game.view.inventory.drawslotitem import drawSlotItem

def drawHotbar(hotbar: list[Slot], heldSlotIndex: int) -> None:
	'''Draw player hotbar on screen'''

	assert 0 <= heldSlotIndex < len(hotbar)

	slotSize = int(BLOCK_SIZE * 1.5)
	
	startx = FRAME.centerx - (len(hotbar) * slotSize) // 2
	y = FRAME.height - int(slotSize * 1.5)

	for i, slot in enumerate(hotbar):
		x = startx + i * slotSize

		pg.draw.rect(surfaces.hud, (200, 200, 200), (x, y, slotSize, slotSize))

		if i == heldSlotIndex:
			pg.draw.rect(surfaces.hud, (80, 80, 80), (x, y, slotSize, slotSize), 5)
		else:
			pg.draw.rect(surfaces.hud, (40, 40, 40), (x, y, slotSize, slotSize), 3)

		if slot.item:
			slotCenter = x + slotSize // 2, y + slotSize // 2
			drawSlotItem(slot.item, slotSize, slotCenter)

			if slot.count > 1:
				drawSlotCount(slot.count, slotCenter)


		