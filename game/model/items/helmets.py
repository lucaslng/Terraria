from game.model.items.item import Item
from game.model.items.specialitems.helmet import Helmet
from game.model.items.utils.itemsenum import Items


class GoldHelmet(Item, Helmet):
	'''Gold helmet item'''

	enum = Items.GoldHelmet
	stackSize = 1
	multiplier = 0.9
	startingDurability = 77

class IronHelmet(Item, Helmet):
	'''Iron helmet item'''

	enum = Items.IronHelmet
	stackSize = 1
	multiplier = 0.75
	startingDurability = 165

class DiamondHelmet(Item, Helmet):
	'''Diamond helmet item'''

	enum = Items.DiamondHelmet
	stackSize = 1
	multiplier = 0.55
	startingDurability = 363