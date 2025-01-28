from game.model.items.item import Item
from game.model.items.specialitems.placeable import Placeable
from game.model.items.utils.itemsenum import Items


class ChestItem(Item, Placeable):
	'''CHest item class'''

	enum = Items.Chest