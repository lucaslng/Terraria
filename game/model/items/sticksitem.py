from game.model.items.item import Item
from game.model.items.utils.itemsenum import Items


class SticksItem(Item):
	'''sticks item class'''

	def __init__(self) -> None:
		super().__init__(Items.Sticks)