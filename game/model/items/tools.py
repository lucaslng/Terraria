from game.model.blocks.utils.blocktype import BlockType
from game.model.items.item import Item
from game.model.items.specialitems.tool import Tool
from game.model.items.utils.itemsenum import Items

# Wood
class WoodenPickaxe(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.WoodenPickaxe, 1, 2)
		Tool.__init__(self, 1.5, 59, BlockType.PICKAXE)

class WoodenAxe(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.WoodenAxe, 1, 2)
		Tool.__init__(self, 1.5, 59, BlockType.AXE)

class WoodenShovel(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.WoodenShovel, 1, 2)
		Tool.__init__(self, 1.5, 59, BlockType.SHOVEL)

class WoodenSword(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.WoodenSword, 1, 4)
		Tool.__init__(self, 1.5, 59, BlockType.SWORD)

# Stone
class StonePickaxe(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.StonePickaxe, 1, 3)
		Tool.__init__(self, 3, 132, BlockType.PICKAXE)

class StoneAxe(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.StoneAxe, 1, 4)
		Tool.__init__(self, 3, 131, BlockType.AXE)

class StoneShovel(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.StoneShovel, 1, 3)
		Tool.__init__(self, 3, 131, BlockType.SHOVEL)

class StoneSword(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.StoneSword, 1, 5)
		Tool.__init__(self, 3, 131, BlockType.SWORD)

# Iron
class IronPickaxe(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.IronPickaxe, 1, 4)
		Tool.__init__(self, 4.5, 250, BlockType.PICKAXE)

class IronAxe(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.IronAxe, 1, 5)
		Tool.__init__(self, 4.5, 250, BlockType.AXE)

class IronShovel(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.IronShovel, 1, 4)
		Tool.__init__(self, 4.5, 250, BlockType.SHOVEL)

class IronSword(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.IronSword, 1, 6)
		Tool.__init__(self, 4.5, 250, BlockType.SWORD)

# Gold
class GoldPickaxe(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.GoldPickaxe, 1, 2)
		Tool.__init__(self, 7.5, 32, BlockType.PICKAXE)

class GoldAxe(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.GoldAxe, 1, 3)
		Tool.__init__(self, 7.5, 32, BlockType.AXE)

class GoldShovel(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.GoldShovel, 1, 2)
		Tool.__init__(self, 7.5, 32, BlockType.SHOVEL)

class GoldSword(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.GoldSword, 1, 4)
		Tool.__init__(self, 7.5, 32, BlockType.SWORD)

# Diamond
class DiamondPickaxe(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.DiamondPickaxe, 1, 5)
		Tool.__init__(self, 6, 1561, BlockType.PICKAXE)

class DiamondAxe(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.DiamondAxe, 1, 6)
		Tool.__init__(self, 6, 1561, BlockType.AXE)

class DiamondShovel(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.DiamondShovel, 1, 6)
		Tool.__init__(self, 6, 1561, BlockType.SHOVEL)

class DiamondSword(Item, Tool):
	def __init__(self):
		Item.__init__(self, Items.DiamondSword, 1, 7)
		Tool.__init__(self, 6, 1561, BlockType.SWORD)