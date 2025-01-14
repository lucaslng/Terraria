from utils.constants import BLOCK_SIZE, FRAME
from game.model.items.inventory.slot import Slot
import pygame as pg

from game.view import surfaces
from game.view.inventory.drawslot import drawSlot


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
			pg.draw.rect(surfaces.hud, (0, 0, 0), (x, y, slotSize, slotSize), 2)
		else:
			pg.draw.rect(surfaces.hud, (90, 90, 90), (x, y, slotSize, slotSize), 2)

		drawSlot(slot, x, y, slotSize)

		