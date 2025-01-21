from game.model.items.item import Item
from game.model.items.utils.itemsenum import Items
from game.model.items.specialitems.smeltable import Smeltable


class CoalItem(Item, Smeltable):
    '''coal item class'''
    
    def __init__(self) -> None:
        Item.__init__(self, Items.Coal)
        Smeltable.__init__(self, burn_time=800, heat_output=1.2)

class IronIngotItem(Item):
	'''iron ingot item class'''

	def __init__(self) -> None:
		super().__init__(Items.IronIngot)

class GoldIngotItem(Item):
	'''gold ingot item class'''

	def __init__(self) -> None:
		super().__init__(Items.GoldIngot)

class DiamondItem(Item):
	'''diamond item class'''

	def __init__(self) -> None:
		super().__init__(Items.Diamond)