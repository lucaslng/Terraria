from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks

class CobblestoneBlock(Block):
	'''Cobblestone block class'''

	def __init__(self):
		super().__init__(0.95, Blocks.Cobblestone)