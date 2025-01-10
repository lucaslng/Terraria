from constants import BLOCK_SIZE
from game.model.blocks.block import Block
from sprites import sprites
from pygame import transform

class StoneBlock(Block):
	'''Stone block class'''

	def __init__(self):
		super().__init__(transform.scale(sprites["stone"], (BLOCK_SIZE, BLOCK_SIZE)))