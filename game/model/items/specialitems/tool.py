from dataclasses import dataclass
from game.model.blocks.utils.blocktype import BlockType


@dataclass
class Tool:
	'''Class inherited by items which are a tool'''

	speed: float
	startingDurability: int
	blockType: BlockType

	def __post_init__(self):
		self.durability = self.startingDurability