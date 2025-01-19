from game.model.items.item import Item
from game.model.items.utils.itemsenum import Items


class CoalItem(Item):
	'''Coal item class'''

	def __init__(self) -> None:
		super().__init__(Items.Coal)

class IronIngotItem(Item):
	'''iron ingot item class'''

	def __init__(self) -> None:
		super().__init__(Items.IronIngot)

class GoldIngotItem(Item):
	'''gold ingot item class'''

	def __init__(self) -> None:
		super().__init__(Items.GoldIngot)

class DiamondItem(Item):
	'''diamond item class'''

	def __init__(self) -> None:
		super().__init__(Items.Diamond)