from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks


class GrassBlock(Block):
	'''Class for grass dirt block'''
	
	def __init__(self):
		super().__init__(0.95, Blocks.Grass)