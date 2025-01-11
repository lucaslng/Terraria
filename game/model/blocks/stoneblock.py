from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks

class StoneBlock(Block):
	'''Stone block class'''

	def __init__(self):
		super().__init__(Blocks.Stone)