from game.model.items.item import Item
from game.model.items.specialitems.placeable import Placeable
from game.model.items.utils.itemsenum import Items


class IronOreItem(Item, Placeable):
	'''iron ore item class'''

	def __init__(self):
		super().__init__(Items.IronOre)

class GoldOreItem(Item, Placeable):
	'''gold ore item class'''

	def __init__(self):
		super().__init__(Items.GoldOre)