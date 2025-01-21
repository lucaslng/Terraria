from game.model.items.item import Item
from game.model.items.specialitems.placeable import Placeable
from game.model.items.utils.itemsenum import Items


class PoppyItem(Item, Placeable):
	'''Poppy item class'''

	enum = Items.Poppy

class CornflowerItem(Item, Placeable):
	'''Cornflower item class'''

	enum = Items.Cornflower

class DandelionItem(Item, Placeable):
	'''Dandelion item class'''

	enum = Items.Dandelion

class AlliumItem(Item, Placeable):
	'''Allium item class'''

	enum = Items.Allium