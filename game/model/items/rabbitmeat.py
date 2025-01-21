from game.model.items.item import Item
from game.model.items.specialitems.edible import Edible
from game.model.items.utils.itemsenum import Items


class RabbitMeat(Item, Edible):
	'''Rabbit meat'''

	enum = Items.RabbitMeat
	healing = 3