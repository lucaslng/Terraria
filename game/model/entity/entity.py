from pygame import Surface, Vector2, mask

class Entity:
	'''Base class for all entities.'''

	def __init__(self, x: float, y: float, texture: Surface):
		self.position = Vector2(x=x, y=y)
		self.mask = mask.from_surface(texture)

	def update(self):
		'''Update the entity, should be called every frame'''
	

