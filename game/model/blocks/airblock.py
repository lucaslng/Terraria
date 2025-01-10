from pygame import SRCALPHA, Surface
from game.model.blocks.block import Block


class AirBlock(Block):
	'''Air block class'''

	def __init__(self):
		super().__init__(Surface((0,0), SRCALPHA))