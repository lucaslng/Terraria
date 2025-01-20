from pygame import Surface
from game.model.items.inventory.slot import Slot
from game.view.inventory.drawslotcount import drawSlotCount
from game.view.inventory.drawslotitem import drawSlotItem


def drawSlot(surface: Surface, slot: Slot, x: int, y: int, slotSize: int, center: bool = False) -> None:
	'''Draw slot at x, y without rectangle around it'''

	if slot.item:
		if center:
			slotCenter = x, y
		else:
			slotCenter = x + slotSize // 2, y + slotSize // 2
		drawSlotItem(surface, slot.item, slotSize, slotCenter)

		if slot.count > 1:
			drawSlotCount(surface, slot.count, slotCenter)