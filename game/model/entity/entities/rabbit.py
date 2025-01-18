from game.model.entity.entity import Entity
from game.model.world import World

class Rabbit(Entity):
	'''Rabbit entity'''

	def __init__(self, x: float, y: float, world: World):
		super().__init__(x, y, 3, 0.8, 0.8, 20000, 4, 20, 10, 0.99, 3, world)
		self.pathFindToPlayer = False
		self.updateDistance = 3
		self.isScared = False
		# self.droppedItem = 
	
	def interact(self, damage: int) -> None:
		print("attacked rabbit")
		self.isScared = True
		self.health -= damage
	
	def update(self, goal: tuple[float, float]) -> None:
		if self.isScared:
			super().update(goal)