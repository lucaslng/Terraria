from game.model.blocks.block import Block
from game.model.blocks.utils.blocksenum import Blocks
from game.model.blocks.utils.blocktype import BlockType


class PoppyBlock(Block):
	'''Class for Poppy block'''

	isEmpty = True
	isFragile = True
	
	def __init__(self):
		super().__init__(0.95, 0.1, BlockType.NONE, Blocks.Poppy)

class DandelionBlock(Block):
	'''Class for Dandelion block'''

	isEmpty = True
	isFragile = True
	
	def __init__(self):
		super().__init__(0.95, 0.1, BlockType.NONE, Blocks.Dandelion)

class CornflowerBlock(Block):
	'''Class for Cornflower block'''

	isEmpty = True
	isFragile = True
	
	def __init__(self):
		super().__init__(0.95, 0.1, BlockType.NONE, Blocks.Cornflower)

class AlliumBlock(Block):
	'''Class for Allium block'''

	isEmpty = True
	isFragile = True
	
	def __init__(self):
		super().__init__(0.95, 0.1, BlockType.NONE, Blocks.Allium)