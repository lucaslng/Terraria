from pygame import mask

from game.model.blocks.utils.blocksenum import Blocks
from game.textures.sprites import sprites


class Block:
	'''Base block class'''
	
	isEmpty = False

	def __init__(self, enum: Blocks):
		self.mask = mask.from_surface(sprites[enum])
		self.enum = enum
