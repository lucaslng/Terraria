from math import sqrt
from pymunk import Body, Circle, Space


class Liquid:
	'''Class for a liquid'''

	mass: float
	moment: float
	particleCount: int
	density: float
	elasticity: float

	def __init__(self, x: int, y: int, space: Space):
		length = sqrt(self.particleCount) # number of particles in each row / col
		size = 1 / length # distance from start of one particle to start of next particle
		radius = size * self.density
		self.particles = [LiquidParticle(x + (i % length) * size, y + (i / length) * size, self.mass, self.moment, space, radius, self.elasticity) for i in range(self.particleCount)]


class LiquidParticle:
	'''class for one liquid particle'''

	def __init__(self, startx: float, starty: float, mass: float, moment: float, space: Space, radius: float, elasticity: float):
		x, y = startx + radius / 2, starty + radius / 2
		self.body = Body(mass, moment)
		self.body.position = x, y
		self.shape = Circle(self.body, radius)
		self.shape.elasticity = elasticity
		space.add(self.body, self.shape)


class Water(Liquid):
	'''class for water'''

	mass = 1
	moment = 200
	particleCount = 400
	density = 0.9
	elasticity = 0.9

	def __init__(self, x: int, y: int, space: Space) -> None:
		super().__init__(x, y, space)