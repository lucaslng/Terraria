from game.model.items.item import Item
from game.model.items.specialitems.placeable import Placeable
from game.model.items.utils.itemsenum import Items
from game.model.light import Light


class TorchItem(Item, Placeable, Light):
	'''Torch item class'''

	lightRadius = 4

	def __init__(self):
		super().__init__(Items.Torch)