from game.model.items.item import Item
from game.model.items.specialitems.fuel import Fuel
from game.model.items.specialitems.placeable import Placeable
from game.model.items.specialitems.smeltable import Smeltable
from game.model.items.utils.itemsenum import Items


class PlanksItem(Item, Placeable, Fuel):
	'''Grass item class'''

	def __init__(self):
		super().__init__(Items.Planks)