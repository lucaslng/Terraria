from game.model.items.item import Item
from game.model.items.specialitems.fuel import Fuel
from game.model.items.utils.itemsenum import Items
from game.model.items.specialitems.smeltable import Smeltable


class CoalItem(Item, Fuel):
    '''coal item class'''
    
    enum = Items.Coal
    def __init__(self) -> None:
        Smeltable.__init__(self, burn_time=800, heat_output=1.2)

class IronIngotItem(Item, Smeltable):
	'''iron ingot item class'''

	enum = Items.IronIngot

class GoldIngotItem(Item, Smeltable):
	'''gold ingot item class'''

	enum = Items.GoldIngot

class DiamondItem(Item):
	'''diamond item class'''

	enum = Items.Diamond