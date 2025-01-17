from game.model.entity.entity import Entity
from game.model.world import World
import numpy as np


class Npc(Entity):
	'''non player character entity'''

	def __init__(self, x: float, y: float, world: World):
		super().__init__(x, y, 5, 1, 1, 20000, 4, 20, 10, 0.99, 18, world)
		self.npcColor: tuple[int, int, int] = tuple(np.random.choice(range(256), size=3))