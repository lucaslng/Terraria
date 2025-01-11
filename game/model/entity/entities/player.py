from game.model.entity.entity import Entity
from game.model.world import World

class Player(Entity):
	'''Player entity class'''
	
	def __init__(self, x: float, y: float, world: World):
		super().__init__(x, y, 4, 1, 1, 1600, 8, 60, 20, 0.8, world)