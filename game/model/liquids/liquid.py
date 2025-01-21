from math import sqrt
from pymunk import Body, Circle, Space


class Liquid:
	'''Class for a liquid'''

	def __init__(self, x: int, y: int, mass: float, moment: float, space: Space, particleCount: int, density: float):
		length = sqrt(particleCount) # number of particles in each row / col
		size = 1 / length # distance from start of one particle to start of next particle
		radius = size * density
		self.particles = [LiquidParticle(x + (i % length) * size, y + (i / length) * size, mass, moment, space, radius) for i in range(particleCount)]


class LiquidParticle:
	'''class for one liquid particle'''

	def __init__(self, x: float, y: float, mass: float, moment: float, space: Space, radius: float):
		self.body = Body(mass, moment)
		self.body.position = x, y
		self.shape = Circle(self.body, radius)
		self.shape.elasticity = 0.93


class Water(Liquid):
	'''class for water'''

	def __init__(self, x: int, y: int, space: Space):
		super().__init__(x, y, 5, 100, space, 20, 0.8)