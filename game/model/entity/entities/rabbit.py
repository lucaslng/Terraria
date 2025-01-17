from random import choice
from game.model.entity.entity import Entity
from game.model.items.rabbitmeat import RabbitMeat
from game.model.world import World
from sound.sounds import sounds

class Rabbit(Entity):
	'''Rabbit entity'''

	def __init__(self, x: float, y: float, world: World):
		super().__init__(x, y, 3, 0.8, 0.8, 20000, 4, 40, 10, 0.99, 3, world)
		self.pathFindToPlayer = False
		self.updateDistance = 10
		self.isScared = False
		self.droppedItem = RabbitMeat()
	
	def interact(self, damage: int) -> None:
		self.isScared = True
		self.takeDamage(damage)

	def takeDamage(self, amount: int) -> bool:
		if super().takeDamage(amount):
			choice(sounds["rabbit"]["hurt"]).play()
			return True
		return False
	
	def update(self, goal: tuple[float, float]) -> None:
		self.updateFallDamage()
		
		if self.isScared:
			super().update(goal)