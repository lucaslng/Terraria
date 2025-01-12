from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks
from game.model.blocks.utils.blocktype import BlockType


class AirBlock(Block):
	'''Air block class'''

	def __init__(self):
		super().__init__(0, 0, BlockType.NONE, Blocks.Air)
		self.isEmpty = True