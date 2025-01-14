from game.model.blocks.utils.blocktype import BlockType
from game.model.items.item import Item
from game.model.items.specialitems.tool import Tool
from game.model.items.utils.itemsenum import Items


class WoodenPickaxe(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.WoodenPickaxe, 1)
		Tool.__init__(self, 1.5, 59, BlockType.PICKAXE)

class WoodenAxe(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.WoodenAxe, 1)
		Tool.__init__(self, 1.5, 59, BlockType.AXE)

class WoodenShovel(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.WoodenShovel, 1)
		Tool.__init__(self, 1.5, 59, BlockType.SHOVEL)

class WoodenSword(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.WoodenSword, 1)
		Tool.__init__(self, 1, 59, BlockType.SWORD)