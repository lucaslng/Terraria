from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks


class AirBlock(Block):
	'''Air block class'''

	def __init__(self):
		super().__init__(Blocks.Air)
		self.isEmpty = True