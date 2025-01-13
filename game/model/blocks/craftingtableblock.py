from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks
from game.model.blocks.utils.blocktype import BlockType
from game.model.blocks.utils.inventoryblock import InventoryBlock
from game.model.items.inventory.inventory import Inventory
from game.model.items.inventory.inventorytype import InventoryType


class CraftingTableBlock(Block, InventoryBlock):
	'''Crafting table block class'''

	def __init__(self):
		self.craftingInInventory = Inventory(3, 3)
		self.craftingOutInventory = Inventory(1, 1, lambda other: other.item is None)
		super().__init__(0.94, 2.5, BlockType.AXE, Blocks.CraftingTable)
	
	@property
	def inventories(self) -> tuple[Inventory, InventoryType]:
		return (self.craftingInInventory, InventoryType.CraftingIn), (self.craftingOutInventory, InventoryType.CraftingOut)
	
	def __del__(self):
		print("del")
		del self.craftingInInventory
		del self.craftingOutInventory