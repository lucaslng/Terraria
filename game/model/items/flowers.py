from game.model.items.item import Item
from game.model.items.specialitems.placeable import Placeable
from game.model.items.utils.itemsenum import Items


class PoppyItem(Item, Placeable):
	'''Poppy item class'''

	def __init__(self):
		super().__init__(Items.Poppy)

class CornflowerItem(Item, Placeable):
	'''Cornflower item class'''

	def __init__(self):
		super().__init__(Items.Cornflower)

class DandelionItem(Item, Placeable):
	'''Dandelion item class'''

	def __init__(self):
		super().__init__(Items.Dandelion)

class AlliumItem(Item, Placeable):
	'''Allium item class'''

	def __init__(self):
		super().__init__(Items.Allium)