from game.model.blocks.utils.blocktype import BlockType

class Tool:
	'''Class inherited by items which are a tool'''

	speed: float
	startingDurability: int
	blockType: BlockType

	def __init__(self):
		self.durability = self.startingDurability