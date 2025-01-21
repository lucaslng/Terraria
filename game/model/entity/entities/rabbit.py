from random import choice

from pymunk import Space
from game.model.entity.entity import Entity
from game.model.items.rabbitmeat import RabbitMeat
from game.model.world import World
from sound.sounds import sounds

class Rabbit(Entity):
	'''Rabbit entity'''

	mass = 3
	width = 0.8
	height = 0.8
	walkForce = 4
	jumpImpulse = 40
	jumpSpeed = 10
	maxHealth = 3
	updateDistance = 10
	pathFindToPlayer = False

	def __init__(self, x: float, y: float, world: World, space: Space):
		super().__init__(x, y, world, space)
		self.isScared = False
		self.droppedItem = RabbitMeat()
	
	def interact(self, damage: float) -> bool:
		self.isScared = True
		return self.takeDamage(damage)

	def takeDamage(self, amount: float) -> bool:
		if super().takeDamage(amount):
			choice(sounds["rabbit"]["hurt"]).play()
			return True
		return False
	
	def update(self, goal: tuple[float, float]) -> None:
		self.updateFallDamage()
		
		if self.isScared:
			super().update(goal)