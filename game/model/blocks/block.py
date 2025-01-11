from pygame import mask

from game.model.blocks.utils.blocksenum import Blocks
from game.textures.sprites import sprites


class Block:
	'''Base block class'''
	
	isEmpty = False

	def __init__(self, friction: float, enum: Blocks):
		self.friction = friction
		self.mask = mask.from_surface(sprites[enum])
		self.enum = enum
