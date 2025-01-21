from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks
from game.model.blocks.utils.blocktype import BlockType
from game.model.items.specialitems.smeltable import Smeltable


class PlanksBlock(Block, Smeltable):
	'''class for planks block'''

	def __init__(self):
		super().__init__(0.88, 2, BlockType.AXE, Blocks.Planks)