from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks


class DirtBlock(Block):
	'''Class for normal dirt block'''
	
	def __init__(self):
		super().__init__(0.95, Blocks.Dirt)