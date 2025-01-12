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

	isEmpty = False
	amountBroken = 0