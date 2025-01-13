from game.model.blocks.block import Block
from game.model.blocks.utils.item2block import item2Block
from game.model.items.utils.itemsenum import Items


class Placeable:
	'''Items that have a corresponding block and can be placed in the world'''
	
	enum: Items

	def getBlock(self) -> Block:
		return item2Block[self.enum]