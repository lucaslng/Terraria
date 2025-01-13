from collections.abc import Callable

from game.model.items.inventory.slot import Slot
from game.model.items.item import Item
from game.model.items.logitem import LogItem
from game.model.items.planksitem import PlanksItem


Recipe = Callable[[list[list[Slot]]], tuple[Item, int] | None]


def woodenPlanks(items: list[list[Slot]]) -> tuple[Item, int] | None:
	'''wooden planks recipe'''
	
	filledSlots = 0
	
	for row in items:
		for slot in row:
			if slot.item:
				filledSlots += 1
				filledSlot = slot

	if filledSlots == 1 and isinstance(filledSlot.item, LogItem):
		return PlanksItem(), filledSlot.count * 4


recipes: tuple[Recipe] = (
	woodenPlanks
)