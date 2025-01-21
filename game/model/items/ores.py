from game.model.items.ingots import GoldIngotItem, IronIngotItem
from game.model.items.item import Item
from game.model.items.specialitems.placeable import Placeable
from game.model.items.specialitems.smeltable import Smeltable
from game.model.items.utils.itemsenum import Items


class IronOreItem(Item, Placeable, Smeltable):
	'''iron ore item class'''
	enum = Items.IronOre
	resultItem = IronIngotItem()

class GoldOreItem(Item, Placeable, Smeltable):
	'''gold ore item class'''
	enum = Items.GoldOre
	resultItem = GoldIngotItem()