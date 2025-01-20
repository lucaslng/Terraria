from game.model.items.item import Item
from game.model.items.specialitems.helmet import Helmet
from game.model.items.utils.itemsenum import Items


class GoldHelmet(Item, Helmet):
	'''Gold helmet item'''

	def __init__(self) -> None:
		super().__init__(Items.GoldHelmet, stackSize=1)	
		Helmet.__init__(self, 0.9, 77)

class IronHelmet(Item, Helmet):
	'''Iron helmet item'''

	def __init__(self) -> None:
		super().__init__(Items.IronHelmet, stackSize=1)
		Helmet.__init__(self, 0.75, 165)

class DiamondHelmet(Item, Helmet):
	'''Diamond helmet item'''

	def __init__(self) -> None:
		super().__init__(Items.DiamondHelmet, stackSize=1)	
		Helmet.__init__(self, 0.55, 363)