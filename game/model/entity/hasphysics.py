import pymunk as pm

class HasPhysics(pm.Body):
	'''Base class for all things that have physics'''

	def __init__(self, x: float, y: float, mass: float, width: float, height: float):
		super().__init__()
		self.position = x, y
		self.mass = mass
		self.width = width
		self.height = height

