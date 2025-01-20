from game.model.entity.entity import Entity
from game.model.world import World


class Dog(Entity):
	'''dog entity that attacks player'''

	def __init__(self, x: float, y: float, world: World) -> None:
		super().__init__(x, y, 8, 1, 1, 20000, 4, 60, 20, 0.99, 10, world)
		self.updateDistance = 30

	def interact(self, damage: int):
		self.health -= damage
	
	def update(self, goal: tuple[float, float]) -> None:
		self.updateFallDamage()
		super().update(goal)