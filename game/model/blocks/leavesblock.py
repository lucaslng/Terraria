from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks
from game.model.blocks.utils.blocktype import BlockType


class LeavesBlock(Block):
	'''Class for leaves block'''

	def __init__(self):
		super().__init__(0.96, 1, BlockType.SWORD, Blocks.Leaves)