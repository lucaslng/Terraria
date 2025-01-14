from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks
from game.model.blocks.utils.blocktype import BlockType
from game.model.blocks.utils.inventoryblock import InventoryBlock
from game.model.items.recipes.recipes import recipes
from game.model.items.inventory.inventory import Inventory
from game.model.items.inventory.inventorytype import InventoryType


class CraftingTableBlock(Block, InventoryBlock):
	'''Crafting table block class'''

	def __init__(self):
		self.craftingInInventory = Inventory(3, 3)
		self.craftingOutInventory = Inventory(1, 1, lambda other: other.item is None) # dont allow swapping items into this slot
		super().__init__(0.94, 2.5, BlockType.AXE, Blocks.CraftingTable)
	
	@property
	def inventories(self) -> tuple[Inventory, InventoryType]:
		return (self.craftingInInventory, InventoryType.CraftingIn), (self.craftingOutInventory, InventoryType.CraftingOut)
	
	def update(self) -> None:
		self.craftingOutInventory[0][0].clear()
		for recipe in recipes:
			output = recipe(self.craftingInInventory.array)
			if output:
				item, count = output
				self.craftingOutInventory[0][0].item = item
				self.craftingOutInventory[0][0].count = count
				return