from collections.abc import Callable

from game.model.items.inventory.slot import Slot
from game.model.items.item import Item
from game.model.items.utils.itemsenum import Items


Recipe = Callable[[list[list[Slot]]], tuple[Item, int] | None]


def woodenPlanks(items: list[list[Slot]]) -> tuple[Item, int] | None:
	'''wooden planks recipe'''
	
	filledSlots = 0
	
	for row in items:
		for slot in row:
			if slot.item:
				filledSlots += 1
				filledSlot = slot

	if filledSlots == 1 and filledSlot.item.enum == Items.Log:
		from game.model.items.planksitem import PlanksItem
		return PlanksItem(), filledSlot.count * 4

def sticks(items: list[list[Slot]]) -> tuple[Item, int] | None:
	'''sticks recipe'''

	filledSlots = 0
	for row in items:
		for slot in row:
			if slot.item:
				if slot.item.enum != Items.Planks:
					return None
				filledSlots += 1
	
	if filledSlots == 2:
		for r in range(2):
			for c, slot in enumerate(items[r]):
				slotBelow = items[r + 1][c]
				if slot.item and slotBelow.item:
					from game.model.items.sticksitem import SticksItem
					return SticksItem(), min(slot.count, slotBelow.count) * 4


recipes: list[Recipe] = [
	woodenPlanks,
	sticks,
]