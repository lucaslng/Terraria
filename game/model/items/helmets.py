from game.model.items.item import Item
from game.model.items.specialitems.helmet import Helmet
from game.model.items.utils.itemsenum import Items


class GoldHelmet(Item, Helmet):
	'''Gold helmet item'''

	multiplier = 0.9
	startingDurability = 77

	def __init__(self) -> None:
		super().__init__(Items.GoldHelmet, stackSize=1)	

class IronHelmet(Item, Helmet):
	'''Iron helmet item'''

	multiplier = 0.7
	startingDurability = 165

	def __init__(self) -> None:
		super().__init__(Items.IronHelmet, stackSize=1)

class DiamondHelmet(Item, Helmet):
	'''Diamond helmet item'''

	multiplier = 0.5
	startingDurability = 363

	def __init__(self) -> None:
		super().__init__(Items.DiamondHelmet, stackSize=1)	