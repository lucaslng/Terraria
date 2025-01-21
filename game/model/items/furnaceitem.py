from game.model.items.item import Item
from game.model.items.specialitems.placeable import Placeable
from game.model.items.utils.itemsenum import Items


class FurnaceItem(Item, Placeable):
	'''Furnace item class'''

	enum = Items.Furnace