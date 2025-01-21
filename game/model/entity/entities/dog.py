from math import dist
from random import random, choice

from game.model.entity.entity import Entity
from sound.sounds import sounds

class Dog(Entity):
	'''dog entity that attacks player'''

	mass = 8
	walkSpeed = 4
	jumpImpulse = 60
	jumpSpeed = 20
	maxHealth = 10
	updateDistance = 30

	def interact(self, damage: float):
		return self.takeDamage(damage)
	
	def takeDamage(self, amount: float) -> bool:
		if super().takeDamage(amount):
			choice(sounds["dog"]["hurt"]).play()
			return True
		return False
	
	def update(self, goal: tuple[float, float]) -> None:
		self.updateFallDamage()
		if dist(self.body.position, goal) < self.updateDistance // 2 and random() > 0.99:
			choice(sounds["dog"]["growl"]).play()
		super().update(goal)