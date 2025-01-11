from pygame import Surface, mask
import pymunk as pm

class Entity(pm.Body):
	'''Base class for all entities.'''

	def __init__(self, x: float, y: float, mass: float, width: float, height: float):
		super().__init__()
		self.position = x, y
		self.mass = mass
		self.width = width
		self.height = height

	def update(self):
		'''Update the entity, should be called every frame'''
	

