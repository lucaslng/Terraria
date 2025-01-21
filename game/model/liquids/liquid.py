from math import sqrt
from typing import Self, Type
from pymunk import Body, Circle, Space


class Liquid:
	'''Class for a liquid'''

	mass: float
	moment: float
	particleCount: int
	density: float
	elasticity: float

	def __init__(self, x: int, y: int, space: Space, sleep: bool=False):
		length = sqrt(self.particleCount) # number of particles in each row / col
		size = 1 / length # distance from start of one particle to start of next particle
		radius = size * self.density
		massPerParticle = self.mass / self.particleCount
		self.particles = [LiquidParticle(x + (i % length) * size, y + (i / length) * size, massPerParticle, self.moment, space, radius, self.elasticity, self.liquid(), sleep) for i in range(self.particleCount)]

	def liquid(self):
		return type(self)


class LiquidParticle:
	'''class for one liquid particle'''

	def __init__(self, startx: float, starty: float, mass: float, moment: float, space: Space, radius: float, elasticity: float, liquid: Type[Liquid], sleep: bool):
		x, y = startx + radius / 2, starty + radius / 2
		self.liquid = liquid
		self.body = Body(mass, moment)
		self.body.position = x, y
		self.shape = Circle(self.body, radius)
		self.shape.elasticity = elasticity
		space.add(self.body, self.shape)
		if sleep:
			self.body.sleep()
		


class Water(Liquid):
	'''class for water'''

	mass = 1
	moment = 200
	particleCount = 361
	density = 0.9
	elasticity = 0.95