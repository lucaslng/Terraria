from math import dist
from random import random, choice
from game.model.entity.entity import Entity
from game.model.world import World
from sound.sounds import sounds

class Dog(Entity):
	'''dog entity that attacks player'''

	def __init__(self, x: float, y: float, world: World) -> None:
		super().__init__(x, y, 8, 1, 1, 20000, 4, 60, 20, 0.99, 10, world)
		self.updateDistance = 30

	def interact(self, damage: int):
		return self.takeDamage(damage)
	
	def takeDamage(self, amount: int) -> bool:
		if super().takeDamage(amount):
			choice(sounds["dog"]["hurt"]).play()
			return True
		return False
	
	def update(self, goal: tuple[float, float]) -> None:
		self.updateFallDamage()
		if dist(self.position, goal) < self.updateDistance // 2 and random() > 0.99:
			choice(sounds["dog"]["growl"]).play()
		super().update(goal)