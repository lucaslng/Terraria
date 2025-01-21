from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks
from game.model.blocks.utils.blocktype import BlockType
from game.model.light import Light


class TorchBlock(Block, Light):
	'''Class for torch block'''

	lightRadius = 4
	isEmpty = True
	isFragile = True

	def __init__(self):
		super().__init__(0, 1, BlockType.NONE, Blocks.Torch)