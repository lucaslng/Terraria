from game.model.items.item import Item
from game.model.items.specialitems.fuel import Fuel
from game.model.items.utils.itemsenum import Items
from game.model.items.specialitems.smeltable import Smeltable


class CoalItem(Item, Fuel):
	'''coal item class'''	
	enum = Items.Coal
	burnTime = 80.0

class IronIngotItem(Item):
	'''iron ingot item class'''
	enum = Items.IronIngot

class GoldIngotItem(Item):
	'''gold ingot item class'''
	enum = Items.GoldIngot

class DiamondItem(Item):
	'''diamond item class'''
	enum = Items.Diamond