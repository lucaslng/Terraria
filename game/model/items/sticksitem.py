from game.model.items.item import Item
from game.model.items.specialitems.fuel import Fuel
from game.model.items.utils.itemsenum import Items


class SticksItem(Item, Fuel):
	'''sticks item class'''
	enum = Items.Sticks
	burnTime = 5.0