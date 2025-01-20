from game.model.items.item import Item
from game.model.items.specialitems.helmet import Helmet


class GoldHelmet(Item, Helmet):
	'''Gold helmet item'''

	multiplier = 0.9