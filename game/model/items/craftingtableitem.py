from game.model.items.item import Item
from game.model.items.specialitems.placeable import Placeable
from game.model.items.utils.itemsenum import Items


class CraftingTableItem(Item, Placeable):
	'''Crafting table item class'''

	enum = Items.CraftingTable
	stackSize = 1