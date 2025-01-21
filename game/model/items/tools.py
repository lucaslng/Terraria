from game.model.blocks.utils.blocktype import BlockType
from game.model.items.item import Item
from game.model.items.specialitems.tool import Tool
from game.model.items.utils.itemsenum import Items

# Wood
class WoodenPickaxe(Item, Tool):
	
	enum = Items.WoodenPickaxe
	stackSize = 1
	damage = 2
	speed = 1.5
	startingDurability = 59
	blockType = BlockType.PICKAXE

class WoodenAxe(Item, Tool):

	enum = Items.WoodenAxe
	stackSize = 1
	damage = 2
	speed = 1.5
	startingDurability = 59
	blockType = BlockType.AXE

class WoodenShovel(Item, Tool):

	enum = Items.WoodenShovel
	stackSize = 1
	damage = 2
	speed = 1.5
	startingDurability = 59
	blockType = BlockType.SHOVEL

class WoodenSword(Item, Tool):

	enum = Items.WoodenSword
	stackSize = 1
	damage = 4
	speed = 1.5
	startingDurability = 59
	blockType = BlockType.SWORD

# Stone
class StonePickaxe(Item, Tool):

	enum = Items.StonePickaxe
	stackSize = 1
	damage = 3
	speed = 3
	startingDurability = 132
	blockType = BlockType.PICKAXE

class StoneAxe(Item, Tool):
	enum = Items.StoneAxe
	stackSize = 1
	damage = 4
	speed = 3
	startingDurability = 132
	blockType = BlockType.AXE

class StoneShovel(Item, Tool):
	
	enum = Items.StoneShovel
	stackSize = 1
	damage = 3
	speed = 3
	startingDurability = 132
	blockType = BlockType.SHOVEL

class StoneSword(Item, Tool):
	
	enum = Items.StoneSword
	stackSize = 1
	damage = 5
	speed = 3
	startingDurability = 132
	blockType = BlockType.SWORD

# Iron
class IronPickaxe(Item, Tool):

	enum = Items.IronPickaxe
	stackSize = 1
	damage = 4
	speed = 4.5
	startingDurability = 250
	blockType = BlockType.PICKAXE

class IronAxe(Item, Tool):
	
	enum = Items.IronAxe
	stackSize = 1
	damage = 5
	speed = 4.5
	startingDurability = 250
	blockType = BlockType.AXE

class IronShovel(Item, Tool):
	
	enum = Items.IronShovel
	stackSize = 1
	damage = 4
	speed = 4.5
	startingDurability = 250
	blockType = BlockType.SHOVEL

class IronSword(Item, Tool):
	
	enum = Items.IronPickaxe
	stackSize = 1
	damage = 6
	speed = 4.5
	startingDurability = 250
	blockType = BlockType.SWORD

# Gold
class GoldPickaxe(Item, Tool):

	enum = Items.GoldPickaxe
	stackSize = 1
	damage = 2
	speed = 7.5
	startingDurability = 32
	blockType = BlockType.PICKAXE

class GoldAxe(Item, Tool):

	enum = Items.GoldAxe
	stackSize = 1
	damage = 3
	speed = 7.5
	startingDurability = 32
	blockType = BlockType.AXE

class GoldShovel(Item, Tool):
	
	enum = Items.GoldShovel
	stackSize = 1
	damage = 2
	speed = 7.5
	startingDurability = 32
	blockType = BlockType.SHOVEL

class GoldSword(Item, Tool):
	
	enum = Items.GoldSword
	stackSize = 1
	damage = 4
	speed = 7.5
	startingDurability = 32
	blockType = BlockType.SWORD

# Diamond
class DiamondPickaxe(Item, Tool):

	enum = Items.DiamondPickaxe
	stackSize = 1
	damage = 5
	speed = 6
	startingDurability = 1561
	blockType = BlockType.PICKAXE

class DiamondAxe(Item, Tool):
	
	enum = Items.DiamondAxe
	stackSize = 1
	damage = 6
	speed = 6
	startingDurability = 1561
	blockType = BlockType.AXE

class DiamondShovel(Item, Tool):
	
	enum = Items.DiamondShovel
	stackSize = 1
	damage = 5
	speed = 6
	startingDurability = 1561
	blockType = BlockType.SHOVEL

class DiamondSword(Item, Tool):
	
	enum = Items.DiamondSword
	stackSize = 1
	damage = 7
	speed = 6
	startingDurability = 1561
	blockType = BlockType.SWORD