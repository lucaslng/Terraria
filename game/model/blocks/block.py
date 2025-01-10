from pygame import Surface, mask


class Block:
	'''Base block class'''
	
	def __init__(self, texture: Surface):
		self.mask = mask.from_surface(texture)
