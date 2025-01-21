from game.model.items.item import Item
from game.model.items.specialitems.placeable import Placeable
from game.model.items.utils.itemsenum import Items
from game.model.light import Light


class TorchItem(Item, Placeable, Light):
	'''Torch item class'''

	enum = Items.Torch
	lightRadius = 4
