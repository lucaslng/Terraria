from game.model.items.item import Item
from game.model.items.specialitems.placeable import Placeable
from game.model.items.utils.itemsenum import Items


class DirtItem(Item, Placeable):
	'''Dirt item class'''

	def __init__(self):
		super().__init__(Items.Dirt)