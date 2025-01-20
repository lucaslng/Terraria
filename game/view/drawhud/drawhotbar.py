from utils.constants import BLOCK_SIZE, FRAME
from game.model.items.inventory.slot import Slot
import pygame as pg

from game.view import surfaces
from game.view.inventory.drawslot import drawSlot


def drawHotbar(hotbar: list[Slot], heldSlotIndex: int) -> None:
	'''Draw player hotbar on screen'''

	assert 0 <= heldSlotIndex < len(hotbar)

	slotSize = int(BLOCK_SIZE * 1.5)

	for i, slot in enumerate(hotbar):
		x = i * slotSize

		if i == heldSlotIndex:
			pg.draw.rect(surfaces.hotbar, (150, 150, 150), (x, 0, slotSize, slotSize))
			pg.draw.rect(surfaces.hotbar, (0, 0, 0), (x, 0, slotSize, slotSize), 3)
		else:
			pg.draw.rect(surfaces.hotbar, (200, 200, 200), (x, 0, slotSize, slotSize))
			pg.draw.rect(surfaces.hotbar, (90, 90, 90), (x, 0, slotSize, slotSize), 2)

		drawSlot(surfaces.hotbar, slot, x, 0, slotSize)

		