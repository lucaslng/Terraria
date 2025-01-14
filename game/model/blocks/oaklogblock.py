from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks
from game.model.blocks.utils.blocktype import BlockType


class LogBlock(Block):
	'''Class for log block'''

	def __init__(self):
		super().__init__(0.9, 2.5, BlockType.AXE, Blocks.Log)