from dataclasses import dataclass
from game.model.blocks.utils.blocksenum import Blocks
from game.model.blocks.utils.blocktype import BlockType


@dataclass
class Block:
	'''Base block class'''
	
	friction: float
	hardness: float
	blockType: BlockType
	enum: Blocks

	isFragile = False
	isEmpty = False
	amountBroken = 0

	def update(self) -> None:
		'''Update the block'''
		pass