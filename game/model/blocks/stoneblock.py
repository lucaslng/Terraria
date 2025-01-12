from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks
from game.model.blocks.utils.blocktype import BlockType

class StoneBlock(Block):
	'''Stone block class'''

	def __init__(self):
		super().__init__(0.95, 5.5, BlockType.PICKAXE, Blocks.Stone)