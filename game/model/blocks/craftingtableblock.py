from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks
from game.model.blocks.utils.blocktype import BlockType
from game.model.blocks.utils.interactable import Interactable


class CraftingTableBlock(Block, Interactable):
	'''Crafting table block class'''

	def __init__(self):
		super().__init__(0.94, 2.5, BlockType.AXE, Blocks.CraftingTable)
	
	def interact(self):
		'''open crafting table menu'''

		print("crafting table menu opened")