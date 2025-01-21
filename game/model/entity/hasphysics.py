import pymunk as pm

class HasPhysics:
	'''Base class for all things that have physics'''

	def __init__(self, x: float, y: float, mass: float, friction: float, width: float, height: float, space: pm.Space):
		self.body = pm.Body()
		self.body.position = x, y
		self.body.mass = mass
		self.width = width
		self.height = height

		self.shape = pm.Poly.create_box(self.body, (width, height))
		self.shape.mass = mass
		self.shape.friction = friction

		space.add(self.body, self.shape)
	
	def update(self):
		pass