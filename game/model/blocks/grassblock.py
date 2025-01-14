from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks
from game.model.blocks.utils.blocktype import BlockType


class GrassBlock(Block):
	'''Class for grass dirt block'''
	
	def __init__(self):
		super().__init__(0.95, 1.5, BlockType.SHOVEL, Blocks.Grass)